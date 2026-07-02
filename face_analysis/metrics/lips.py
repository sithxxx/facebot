import numpy as np
from ..detector import LANDMARK_INDICES

def lip_fullness(pts: np.ndarray) -> float:
    """total lip height (upper_lip_top → lower_lip_bottom) / mouth_width"""
    lip_height = np.linalg.norm(pts[LANDMARK_INDICES["upper_lip_top"]] - pts[LANDMARK_INDICES["lower_lip_bottom"]])
    mouth_width_val = np.linalg.norm(pts[LANDMARK_INDICES["mouth_left"]] - pts[LANDMARK_INDICES["mouth_right"]])
    return float(lip_height / mouth_width_val)

def lip_proportions(pts: np.ndarray) -> float:
    """upper lip height / lower lip height"""
    upper_lip_height = np.linalg.norm(pts[LANDMARK_INDICES["upper_lip_top"]] - pts[LANDMARK_INDICES["upper_lip_bottom"]])
    lower_lip_height = np.linalg.norm(pts[LANDMARK_INDICES["lower_lip_top"]] - pts[LANDMARK_INDICES["lower_lip_bottom"]])
    
    return float(upper_lip_height / lower_lip_height)

if __name__ == "__main__":
    dummy_pts = np.random.rand(478, 2) * 100
    print(f"Lip Fullness: {lip_fullness(dummy_pts)}")
    print(f"Lip Proportions: {lip_proportions(dummy_pts)}")
