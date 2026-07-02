import numpy as np
from ..detector import LANDMARK_INDICES

def forehead_width(pts: np.ndarray) -> float:
    """forehead width (left_brow_outer → right_brow_outer) / face width"""
    forehead_w = np.linalg.norm(pts[LANDMARK_INDICES["left_brow_outer"]] - pts[LANDMARK_INDICES["right_brow_outer"]])
    face_width = np.linalg.norm(pts[LANDMARK_INDICES["left_cheek"]] - pts[LANDMARK_INDICES["right_cheek"]])
    return float(forehead_w / face_width)

def brow_height(pts: np.ndarray) -> float:
    """
    avg distance from lower brow edge to upper eyelid / eye width
    use left_brow_inner y vs left_eye_top y, same for right
    """
    # brow_inner y - eye_top y (positive because brow is above eye in image coordinates)
    # Actually y is top-down, so eye_top y - brow_inner y ?
    # Let's use absolute difference for distance.
    left_dist = abs(pts[LANDMARK_INDICES["left_brow_inner"]][1] - pts[LANDMARK_INDICES["left_eye_top"]][1])
    right_dist = abs(pts[LANDMARK_INDICES["right_brow_inner"]][1] - pts[LANDMARK_INDICES["right_eye_top"]][1])
    
    left_eye_width = np.linalg.norm(pts[LANDMARK_INDICES["left_eye_outer"]] - pts[LANDMARK_INDICES["left_eye_inner"]])
    right_eye_width = np.linalg.norm(pts[LANDMARK_INDICES["right_eye_outer"]] - pts[LANDMARK_INDICES["right_eye_inner"]])
    
    avg_dist = (left_dist + right_dist) / 2
    avg_eye_width = (left_eye_width + right_eye_width) / 2
    
    return float(avg_dist / avg_eye_width)

if __name__ == "__main__":
    dummy_pts = np.random.rand(478, 2) * 100
    print(f"Forehead Width: {forehead_width(dummy_pts)}")
    print(f"Brow Height: {brow_height(dummy_pts)}")
