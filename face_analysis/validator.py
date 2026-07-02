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
MIN_FACE_SHARPNESS = 20.0  # Laplacian variance on the size-normalized face crop
MIN_FACE_AREA_RATIO = 0.15 # 15% of image area
MAX_FRONTALITY_DEV = 0.25  # 25% of face width

FACE_CROP_WIDTH = 256      # normalize the face crop before measuring sharpness


def _face_sharpness(img: np.ndarray, pts: np.ndarray) -> float:
    """
    Laplacian variance measured ONLY on the face crop, resized to a fixed
    width. Whole-image variance was resolution-dependent and dominated by
    background/skin smoothness — it rejected perfectly sharp selfies where
    the face fills the frame (calibration: sharp faces >= 47, blurred <= 9).
    """
    x0, y0 = np.maximum(pts.min(axis=0).astype(int), 0)
    x1, y1 = pts.max(axis=0).astype(int)
    face = img[y0:y1, x0:x1]
    if face.size == 0:
        return 0.0
    scale = FACE_CROP_WIDTH / face.shape[1]
    face = cv2.resize(face, (FACE_CROP_WIDTH, max(1, int(face.shape[0] * scale))))
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def validate_image(image_path: str) -> Tuple[bool, str]:
    """
    Checks before processing (order matters — face is detected first, then
    quality is judged on the face itself). Error codes:
    1. Face present: no landmarks detected                         → "no_face"
    2. Single face:  more than 1 face detected                     → "multiple_faces"
    3. Face size:    face bbox < MIN_FACE_AREA_RATIO (15%) of area → "too_small"
    4. Frontality:   nose deviation > MAX_FRONTALITY_DEV (25%)     → "not_frontal"
    5. Sharpness:    face-crop Laplacian var < MIN_FACE_SHARPNESS  → "too_blurry"

    Returns (is_valid: bool, error_code: str). error_code is "" when valid.
    Every rejection is logged with the measured value.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            logger.info("Validation rejected: unreadable image %s", image_path)
            return False, "Could not read image"

        h, w, _ = img.shape
        img_area = h * w

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
                logger.info("Validation rejected: no_face")
                return False, "no_face"

            if len(results.face_landmarks) > 1:
                logger.info("Validation rejected: multiple_faces (%d)", len(results.face_landmarks))
                return False, "multiple_faces"

            landmarks = results.face_landmarks[0]
            pts = np.array([[lm.x * w, lm.y * h] for lm in landmarks])

            # Face size
            x_min, y_min = np.min(pts, axis=0)
            x_max, y_max = np.max(pts, axis=0)
            face_area = (x_max - x_min) * (y_max - y_min)
            area_ratio = face_area / img_area
            if area_ratio < MIN_FACE_AREA_RATIO:
                logger.info("Validation rejected: too_small (face %.1f%% of image)", area_ratio * 100)
                return False, "too_small"

            # Frontality
            left_eye_inner = pts[LANDMARK_INDICES["left_eye_inner"]]
            right_eye_inner = pts[LANDMARK_INDICES["right_eye_inner"]]
            nose_bridge = pts[LANDMARK_INDICES["nose_bridge"]]

            eye_midpoint_x = (left_eye_inner[0] + right_eye_inner[0]) / 2
            face_width = np.linalg.norm(pts[LANDMARK_INDICES["left_cheek"]] - pts[LANDMARK_INDICES["right_cheek"]])

            deviation = abs(nose_bridge[0] - eye_midpoint_x)
            if (deviation / face_width) > MAX_FRONTALITY_DEV:
                logger.info("Validation rejected: not_frontal (dev %.1f%%)", deviation / face_width * 100)
                return False, "not_frontal"

            # Sharpness — on the face crop, size-normalized
            sharpness = _face_sharpness(img, pts)
            if sharpness < MIN_FACE_SHARPNESS:
                logger.info("Validation rejected: too_blurry (face sharpness %.1f < %.1f)",
                            sharpness, MIN_FACE_SHARPNESS)
                return False, "too_blurry"

        return True, ""

    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return False, f"Validation failed: {str(e)}"
