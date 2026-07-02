import numpy as np
from ..detector import LANDMARK_INDICES

def nose_width(pts: np.ndarray) -> float:
    """alar width (left_nose_wing → right_nose_wing) / face width"""
    alar_width = np.linalg.norm(pts[LANDMARK_INDICES["left_nose_wing"]] - pts[LANDMARK_INDICES["right_nose_wing"]])
    face_width = np.linalg.norm(pts[LANDMARK_INDICES["left_cheek"]] - pts[LANDMARK_INDICES["right_cheek"]])
    return float(alar_width / face_width)

def nose_length(pts: np.ndarray) -> float:
    """nose_bridge to nose_base / face_height"""
    nose_bridge = pts[LANDMARK_INDICES["nose_bridge"]]
    left_wing = pts[LANDMARK_INDICES["left_nose_wing"]]
    right_wing = pts[LANDMARK_INDICES["right_nose_wing"]]
    nose_tip = pts[LANDMARK_INDICES["nose_tip"]]
    
    nose_base = np.array([(left_wing[0] + right_wing[0]) / 2, nose_tip[1]])
    
    nose_len = np.linalg.norm(nose_bridge - nose_base)
    face_height = np.linalg.norm(pts[LANDMARK_INDICES["nose_bridge"]] - pts[LANDMARK_INDICES["chin_bottom"]])
    
    return float(nose_len / face_height)

def nose_to_mouth_ratio(pts: np.ndarray) -> float:
    """nose_width / mouth_width"""
    alar_width = np.linalg.norm(pts[LANDMARK_INDICES["left_nose_wing"]] - pts[LANDMARK_INDICES["right_nose_wing"]])
    mouth_width_val = np.linalg.norm(pts[LANDMARK_INDICES["mouth_left"]] - pts[LANDMARK_INDICES["mouth_right"]])
    return float(alar_width / mouth_width_val)

if __name__ == "__main__":
    dummy_pts = np.random.rand(478, 2) * 100
    print(f"Nose Width: {nose_width(dummy_pts)}")
    print(f"Nose Length: {nose_length(dummy_pts)}")
    print(f"Nose to Mouth Ratio: {nose_to_mouth_ratio(dummy_pts)}")
