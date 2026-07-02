import asyncio
import logging
import traceback
from aiogram import Bot
from aiogram.types import FSInputFile
from bot.config import MAX_QUEUE_SIZE
from bot.services.analysis_service import run_analysis
from bot.services.file_service import delete_file, get_temp_path
from bot.database import repository
from bot.locales import ru

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
    message_id = job['message_id']
    job_id = job.get('db_job_id')
    
    try:
        # Update DB status
        if job_id:
            await repository.update_job_status(job_id, "processing")
            
        # Edit status message: "🔍 Обнаруживаю точки лица..."
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=ru.STATUS_DETECTING)
        
        output_pdf_path = get_temp_path(user_id, ".pdf")
        
        # Edit status message: "📐 Считаю метрики..."
        # (Inside run_analysis, we can't easily yield progress without making it a generator, 
        # so we'll just update once before calling run_analysis)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=ru.STATUS_METRICS + "\n" + ru.STATUS_GENERATING)
        
        # Run pipeline
        final_pdf_path, analysis_result = await run_analysis(photo_path, gender, output_pdf_path)
        
        logging.info(
            f"Analysis complete — user={job['user_id']} | "
            f"overall={analysis_result.overall_score} | "
            f"ml={analysis_result.ml_score} | "
            f"geo={analysis_result.geometry_score} | "
            f"ml_weight={analysis_result.ml_weight}"
        )
        
        # Edit status message: "📄 Создаю PDF..."
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=ru.STATUS_PDF)
        
        # Send PDF to user
        pdf_file = FSInputFile(final_pdf_path, filename="Face_Analysis_Report.pdf")
        await bot.send_document(
            chat_id=chat_id, 
            document=pdf_file,
            caption="🎉 Твой персональный разбор готов!"
        )
        
        # Send tier message
        from bot.services.tier_service import get_tier_position_message
        tier_message = get_tier_position_message(analysis_result.overall_score, gender)
        await bot.send_message(chat_id=chat_id, text=tier_message, parse_mode="HTML")
        
        # Final message update
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=ru.STATUS_DONE)
        
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

    except Exception as e:
        logging.error(f"JOB FAILED for user {job['user_id']}: {e}")
        logging.error(traceback.format_exc())
        await bot.send_message(job['chat_id'], "😔 Произошла ошибка при анализе.")
        
    except ValueError as e:
        error_str = str(e)
        user_msg = ru.PHOTO_ERRORS.get(error_str, ru.ERROR_GENERAL)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ Ошибка: {user_msg}")
        if job_id:
            await repository.update_job_status(job_id, "failed", error_msg=error_str)
            
    except Exception as e:
        logging.error(f"Error processing job for user {user_id}: {e}", exc_info=True)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=ru.ERROR_GENERAL)
        if job_id:
            await repository.update_job_status(job_id, "failed", error_msg=str(e))
            
    finally:
        # Cleanup temp files
        delete_file(photo_path)
        try:
            delete_file(output_pdf_path)
        except Exception:
            pass
