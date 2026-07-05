import asyncio
import logging
from face_analysis.validator import validate_image
from face_analysis.detector import detect_face
from face_analysis.calculator import analyze_face
from report.pdf.builder import build_report

async def run_analysis(photo_path: str, gender: str, output_path: str, lang: str = "ru"):
    """
    Runs full pipeline in executor (to avoid blocking event loop).
    Returns (pdf_path, analysis_result). Raises ValueError with a bare
    validation code (no_face, too_blurry, ...) so the queue can map it to a
    localized user message.
    """
    loop = asyncio.get_running_loop()

    # 1. Validate image
    is_valid, error_reason = await loop.run_in_executor(None, validate_image, photo_path)
    if not is_valid:
        raise ValueError(error_reason)

    # 2. Get landmarks
    landmarks = await loop.run_in_executor(None, detect_face, photo_path)
    if not landmarks:
        raise ValueError("no_face")

    # 3. Analyze face
    analysis_result = await loop.run_in_executor(
        None, analyze_face, landmarks, gender, photo_path,
    )

    # 4. Build report (localized)
    final_pdf_path = await loop.run_in_executor(
        None, build_report, analysis_result, photo_path, output_path, lang,
    )

    return final_pdf_path, analysis_result
