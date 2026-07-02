import asyncio
import logging
import traceback
import os
from face_analysis.validator import validate_image
from face_analysis.detector import detect_face
from face_analysis.calculator import analyze_face
from report.pdf.builder import build_report

async def run_analysis(photo_path: str, gender: str, output_path: str) -> str:
    try:
        logging.info(f"Step 1: validating {photo_path}")
        # validate_image(...)
        
        logging.info("Step 2: getting landmarks")
        # get_landmarks(...)
        
        logging.info("Step 3: analyzing face")
        # analyze_face(...)
        
        logging.info("Step 4: building report")
        # build_report(...)
        
    except Exception as e:
        logging.error(f"ANALYSIS FAILED: {e}")
        logging.error(traceback.format_exc())
        raise
    """
    Runs full pipeline in executor (to avoid blocking event loop).
    Returns the path to the generated PDF.
    """
    loop = asyncio.get_running_loop()
    
    # 1. Validate image
    is_valid, error_reason = await loop.run_in_executor(None, validate_image, photo_path)
    if not is_valid:
        raise ValueError(f"Image validation failed: {error_reason}")
        
    # 2. Get landmarks
    landmarks = await loop.run_in_executor(None, detect_face, photo_path)
    if not landmarks:
        raise ValueError("no_face")
        
    # 3. Analyze face
    analysis_result = await loop.run_in_executor(
        None,
        analyze_face,
        landmarks,
        gender,
        photo_path,    # ← add this line only
    )
    
    # 4. Build report
    final_pdf_path = await loop.run_in_executor(
        None, 
        build_report, 
        analysis_result, 
        photo_path, 
        output_path
    )
    
    return final_pdf_path, analysis_result
