import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from .models import FaceLandmarks

MODEL_PATH = os.path.join(os.path.dirname(__file__), "face_landmarker.task")

LANDMARK_INDICES = {
    "left_eye_inner": 133,
    "left_eye_outer": 33,
    "right_eye_inner": 362,
    "right_eye_outer": 263,
    "left_eye_top": 159,
    "left_eye_bottom": 145,
    "right_eye_top": 386,
    "right_eye_bottom": 374,
    "nose_bridge": 168,
    "nose_tip": 1,
    "left_nose_wing": 129,
    "right_nose_wing": 358,
    "left_cheek": 234,
    "right_cheek": 454,
    "left_jaw": 132,
    "right_jaw": 361,
    "mouth_left": 61,
    "mouth_right": 291,
    "upper_lip_top": 0,
    "upper_lip_bottom": 13,
    "lower_lip_top": 14,
    "lower_lip_bottom": 17,
    "chin_bottom": 152,
    "left_brow_outer": 46,
    "right_brow_outer": 276,
    "left_brow_inner": 105,
    "right_brow_inner": 334,
}

class FaceDetector:
    def __init__(self):
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)
        self.face_mesh = True  # For compatibility with test_detector.py

    def detect(self, image: np.ndarray) -> FaceLandmarks | None:
        try:
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
            results = self.landmarker.detect(mp_image)
            
            if not results.face_landmarks:
                return None
            
            landmarks = results.face_landmarks[0]
            h, w, _ = image.shape
            pts = np.array([[lm.x * w, lm.y * h] for lm in landmarks])
            
            return FaceLandmarks(points=pts, image_width=w, image_height=h)
        except Exception:
            return None

def detect_face(image_source) -> FaceLandmarks | None:
    if isinstance(image_source, str):
        if not os.path.exists(image_source):
            return None
        image = cv2.imread(image_source)
        if image is None:
            return None
    elif isinstance(image_source, np.ndarray):
        image = image_source
    else:
        return None
        
    detector = FaceDetector()
    return detector.detect(image)
