import numpy as np
from ..detector import LANDMARK_INDICES

def eye_size(pts: np.ndarray) -> float:
    """avg eye width (outer-inner corner) / face width"""
    left_width = np.linalg.norm(pts[LANDMARK_INDICES["left_eye_outer"]] - pts[LANDMARK_INDICES["left_eye_inner"]])
    right_width = np.linalg.norm(pts[LANDMARK_INDICES["right_eye_outer"]] - pts[LANDMARK_INDICES["right_eye_inner"]])
    face_width = np.linalg.norm(pts[LANDMARK_INDICES["left_cheek"]] - pts[LANDMARK_INDICES["right_cheek"]])
    return float((left_width + right_width) / (2 * face_width))

def eye_spacing(pts: np.ndarray) -> float:
    """distance between inner eye corners / face width"""
    spacing = np.linalg.norm(pts[LANDMARK_INDICES["left_eye_inner"]] - pts[LANDMARK_INDICES["right_eye_inner"]])
    face_width = np.linalg.norm(pts[LANDMARK_INDICES["left_cheek"]] - pts[LANDMARK_INDICES["right_cheek"]])
    return float(spacing / face_width)

def eye_tilt(pts: np.ndarray) -> float:
    """
    For each eye: (outer_corner_y - inner_corner_y) / eye_width
    Positive = outer corner higher (hunter eyes), negative = droopy
    Return average of both eyes.
    """
    left_width = np.linalg.norm(pts[LANDMARK_INDICES["left_eye_outer"]] - pts[LANDMARK_INDICES["left_eye_inner"]])
    right_width = np.linalg.norm(pts[LANDMARK_INDICES["right_eye_outer"]] - pts[LANDMARK_INDICES["right_eye_inner"]])
    
    # MediaPipe y-axis is top-to-bottom, so lower y means higher position.
    # Formula: (inner_y - outer_y) / width to get positive for "hunter eyes"
    left_tilt = (pts[LANDMARK_INDICES["left_eye_inner"]][1] - pts[LANDMARK_INDICES["left_eye_outer"]][1]) / left_width
    right_tilt = (pts[LANDMARK_INDICES["right_eye_inner"]][1] - pts[LANDMARK_INDICES["right_eye_outer"]][1]) / right_width
    
    return float((left_tilt + right_tilt) / 2)

def eye_shape(pts: np.ndarray) -> float:
    """avg eye height (top-bottom) / avg eye width — aspect ratio"""
    left_height = np.linalg.norm(pts[LANDMARK_INDICES["left_eye_top"]] - pts[LANDMARK_INDICES["left_eye_bottom"]])
    right_height = np.linalg.norm(pts[LANDMARK_INDICES["right_eye_top"]] - pts[LANDMARK_INDICES["right_eye_bottom"]])
    
    left_width = np.linalg.norm(pts[LANDMARK_INDICES["left_eye_outer"]] - pts[LANDMARK_INDICES["left_eye_inner"]])
    right_width = np.linalg.norm(pts[LANDMARK_INDICES["right_eye_outer"]] - pts[LANDMARK_INDICES["right_eye_inner"]])
    
    return float(((left_height / left_width) + (right_height / right_width)) / 2)

if __name__ == "__main__":
    dummy_pts = np.random.rand(478, 2) * 100
    print(f"Eye Size: {eye_size(dummy_pts)}")
    print(f"Eye Spacing: {eye_spacing(dummy_pts)}")
    print(f"Eye Tilt: {eye_tilt(dummy_pts)}")
    print(f"Eye Shape: {eye_shape(dummy_pts)}")
