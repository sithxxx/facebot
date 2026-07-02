import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import logging
import os
from typing import Tuple, Optional
from .detector import LANDMARK_INDICES, FaceDetector, MODEL_PATH

logger = logging.getLogger(__name__)

# Constants for validation
MIN_LAPLACIAN_VAR = 100.0  # Threshold for blur detection
MIN_FACE_AREA_RATIO = 0.15 # 15% of image area
MAX_FRONTALITY_DEV = 0.25  # 25% of face width

def validate_image(image_path: str) -> Tuple[bool, str]:
    """
    Checks before processing. Thresholds are the module-level constants:
    1. Blur:        Laplacian variance < MIN_LAPLACIAN_VAR (100.0)      → "too_blurry"
    2. Face present: no landmarks detected                              → "no_face"
    3. Single face:  more than 1 face detected                         → "multiple_faces"
    4. Face size:   face bbox < MIN_FACE_AREA_RATIO (15%) of image area → "too_small"
    5. Frontality:  nose_x deviation from eye midpoint
                    > MAX_FRONTALITY_DEV (25%) of face width            → "not_frontal"

    Returns (is_valid: bool, error_code: str). error_code is "" when valid.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False, "Could not read image"

        h, w, _ = img.shape
        img_area = h * w

        # 1. Blur Detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < MIN_LAPLACIAN_VAR:
            return False, "too_blurry"

        # Initialize MediaPipe Tasks FaceLandmarker for more checks
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=2 # Check for multiple faces
        )
        
        with vision.FaceLandmarker.create_from_options(options) as landmarker:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
            results = landmarker.detect(mp_image)

            if not results.face_landmarks:
                return False, "no_face"

            # 4. Multiple faces check
            if len(results.face_landmarks) > 1:
                return False, "multiple_faces"

            landmarks = results.face_landmarks[0]
            pts = np.array([[lm.x * w, lm.y * h] for lm in landmarks])

            # 2. Face Size Check
            x_min, y_min = np.min(pts, axis=0)
            x_max, y_max = np.max(pts, axis=0)
            face_area = (x_max - x_min) * (y_max - y_min)
            if (face_area / img_area) < MIN_FACE_AREA_RATIO:
                return False, "too_small"

            # 3. Frontality Check
            left_eye_inner = pts[LANDMARK_INDICES["left_eye_inner"]]
            right_eye_inner = pts[LANDMARK_INDICES["right_eye_inner"]]
            nose_bridge = pts[LANDMARK_INDICES["nose_bridge"]]
            
            eye_midpoint_x = (left_eye_inner[0] + right_eye_inner[0]) / 2
            face_width = np.linalg.norm(pts[LANDMARK_INDICES["left_cheek"]] - pts[LANDMARK_INDICES["right_cheek"]])
            
            deviation = abs(nose_bridge[0] - eye_midpoint_x)
            if (deviation / face_width) > MAX_FRONTALITY_DEV:
                return False, "not_frontal"

        return True, ""

    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return False, f"Validation failed: {str(e)}"
