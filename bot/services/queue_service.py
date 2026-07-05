import asyncio
import logging
import traceback
from aiogram import Bot
from aiogram.types import FSInputFile
from bot.config import MAX_QUEUE_SIZE
from bot.services.analysis_service import run_analysis
from bot.services.file_service import delete_file, get_temp_path
from bot.database import repository
from bot.locales import get_locale

# Global queue
analysis_queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)

async def add_job(job: dict) -> int:
    """Adds a job to the queue. Returns current queue size (approximate position)."""
    if analysis_queue.full():
        raise asyncio.QueueFull("The analysis queue is currently full.")
    await analysis_queue.put(job)
    return analysis_queue.qsize()

async def start_worker(bot: Bot, n_workers: int = 3):
    """Starts N concurrent worker coroutines to process the queue."""
    workers = []
    for i in range(n_workers):
        worker = asyncio.create_task(_worker_loop(f"worker-{i}", bot))
        workers.append(worker)
    logging.info(f"Started {n_workers} background workers.")
    return workers

async def _worker_loop(name: str, bot: Bot):
    while True:
        try:
            job = await analysis_queue.get()
            try:
                logging.info(f"[{name}] Starting job for user {job.get('user_id')}")
                await _process_job(job, bot)
            except Exception as e:
                logging.error(f"[{name}] Unexpected error in worker loop: {e}", exc_info=True)
            finally:
                analysis_queue.task_done()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logging.error(f"[{name}] Queue get error: {e}", exc_info=True)

async def _process_job(job: dict, bot: Bot):
    
    user_id = job['user_id']
    chat_id = job['chat_id']
    photo_path = job['photo_path']
    gender = job['gender']
    lang = job.get('lang', 'ru')
    message_id = job['message_id']
    job_id = job.get('db_job_id')
    L = get_locale(lang)

    try:
        # Update DB status
        if job_id:
            await repository.update_job_status(job_id, "processing")

        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=L.STATUS_DETECTING)

        output_pdf_path = get_temp_path(user_id, ".pdf")

        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=L.STATUS_METRICS + "\n" + L.STATUS_GENERATING)

        # Run pipeline
        final_pdf_path, analysis_result = await run_analysis(photo_path, gender, output_pdf_path, lang)
        
        logging.info(
            f"Analysis complete — user={job['user_id']} | "
            f"overall={analysis_result.overall_score} | "
            f"ml={analysis_result.ml_score} | "
            f"geo={analysis_result.geometry_score} | "
            f"ml_weight={analysis_result.ml_weight}"
        )
        
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=L.STATUS_PDF)

        # Send PDF to user
        pdf_file = FSInputFile(final_pdf_path, filename="Face_Analysis_Report.pdf")
        await bot.send_document(
            chat_id=chat_id,
            document=pdf_file,
            caption=L.PDF_CAPTION
        )

        # Send tier message
        from bot.services.tier_service import get_tier_position_message
        tier_message = get_tier_position_message(analysis_result.overall_score, gender, lang)
        await bot.send_message(chat_id=chat_id, text=tier_message, parse_mode="HTML")

        # Final message update
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=L.STATUS_DONE)
        
        # Save completed job to DB
        if job_id:
            import json
            import dataclasses
            # Convert dataclass to dict for JSON storage
            metrics_dict = dataclasses.asdict(analysis_result)
            await repository.update_job_status(
                job_id, 
                "done", 
                overall_score=analysis_result.overall_score,
                metrics_json=metrics_dict
            )
            
        await repository.increment_total_analyses(user_id)

        # Promote leaderboard score if this beat the user's previous best.
        if analysis_result.overall_score is not None:
            improved = await repository.update_best_score(user_id, analysis_result.overall_score, gender)
            logging.info(
                f"Leaderboard: user={user_id} score={analysis_result.overall_score} "
                f"{'improved best' if improved else 'no change'}"
            )

    # ValueError carries validation codes (no_face, too_blurry, ...) and MUST
    # come before the broad Exception — the old order made this branch dead
    # code and users always saw the generic error.
    except ValueError as e:
        error_str = str(e)
        user_msg = L.PHOTO_ERRORS.get(error_str, L.ERROR_GENERAL)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ {user_msg}")
        if job_id:
            await repository.update_job_status(job_id, "failed", error_msg=error_str)

    except Exception as e:
        logging.error(f"JOB FAILED for user {user_id}: {e}")
        logging.error(traceback.format_exc())
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=L.ANALYSIS_ERROR)
        if job_id:
            await repository.update_job_status(job_id, "failed", error_msg=str(e))
            
    finally:
        # Cleanup temp files
        delete_file(photo_path)
        try:
            delete_file(output_pdf_path)
        except Exception:
            pass
