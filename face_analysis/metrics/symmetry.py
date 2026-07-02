import numpy as np
from ..detector import LANDMARK_INDICES

def face_symmetry(pts: np.ndarray) -> float:
    """
    Compares 5 bilateral landmark pairs.
    For each pair: compute distance from each point to the vertical midline.
    Symmetry = 1 - mean(|left_dist - right_dist| / face_width)
    Midline defined by nose_bridge (168) and chin_bottom (152).
    Returns value in [0, 1], higher = more symmetric.
    """
    # Landmarks for midline
    nose_bridge = pts[LANDMARK_INDICES["nose_bridge"]]
    chin_bottom = pts[LANDMARK_INDICES["chin_bottom"]]
    
    # Calculate midline vector (v) and a point on the line (p)
    p = nose_bridge
    v = chin_bottom - nose_bridge
    v_norm = v / np.linalg.norm(v)
    
    # Pairs: (left, right)
    pairs = [
        (LANDMARK_INDICES["left_eye_outer"], LANDMARK_INDICES["right_eye_outer"]),
        (LANDMARK_INDICES["left_eye_inner"], LANDMARK_INDICES["right_eye_inner"]),
        (LANDMARK_INDICES["left_nose_wing"], LANDMARK_INDICES["right_nose_wing"]),
        (LANDMARK_INDICES["left_cheek"], LANDMARK_INDICES["right_cheek"]),
        (LANDMARK_INDICES["left_jaw"], LANDMARK_INDICES["right_jaw"]),
    ]
    
    face_width = np.linalg.norm(pts[LANDMARK_INDICES["left_cheek"]] - pts[LANDMARK_INDICES["right_cheek"]])
    
    dist_diffs = []
    for left_idx, right_idx in pairs:
        left_pt = pts[left_idx]
        right_pt = pts[right_idx]
        
        # Distance to midline: |(p-q) - ((p-q)·v_norm)v_norm|
        def dist_to_line(q):
            vec = q - p
            proj = np.dot(vec, v_norm) * v_norm
            return np.linalg.norm(vec - proj)
        
        left_dist = dist_to_line(left_pt)
        right_dist = dist_to_line(right_pt)
        
        dist_diffs.append(abs(left_dist - right_dist))
        
    symmetry = 1.0 - (np.mean(dist_diffs) / face_width)
    return float(np.clip(symmetry, 0, 1))

def face_proportions(pts: np.ndarray) -> float:
    """
    face_height (nose_bridge → chin_bottom) / cheekbone_width (left_cheek → right_cheek)
    """
    height = np.linalg.norm(pts[LANDMARK_INDICES["nose_bridge"]] - pts[LANDMARK_INDICES["chin_bottom"]])
    width = np.linalg.norm(pts[LANDMARK_INDICES["left_cheek"]] - pts[LANDMARK_INDICES["right_cheek"]])
    return float(height / width)

def vertical_balance(pts: np.ndarray) -> float:
    """
    middle_third (nose_bridge → nose_base) / lower_third (nose_base → chin_bottom)
    nose_base = midpoint between left_nose_wing and right_nose_wing at nose tip y-level
    """
    nose_bridge = pts[LANDMARK_INDICES["nose_bridge"]]
    chin_bottom = pts[LANDMARK_INDICES["chin_bottom"]]
    
    left_wing = pts[LANDMARK_INDICES["left_nose_wing"]]
    right_wing = pts[LANDMARK_INDICES["right_nose_wing"]]
    nose_tip = pts[LANDMARK_INDICES["nose_tip"]]
    
    nose_base = np.array([(left_wing[0] + right_wing[0]) / 2, nose_tip[1]])
    
    middle_third = np.linalg.norm(nose_bridge - nose_base)
    lower_third = np.linalg.norm(nose_base - chin_bottom)
    
    return float(middle_third / lower_third)

def jaw_cheek_balance(pts: np.ndarray) -> float:
    """
    cheekbone_width (left_cheek → right_cheek) / jaw_width (left_jaw → right_jaw)
    """
    cheek_width = np.linalg.norm(pts[LANDMARK_INDICES["left_cheek"]] - pts[LANDMARK_INDICES["right_cheek"]])
    jaw_width = np.linalg.norm(pts[LANDMARK_INDICES["left_jaw"]] - pts[LANDMARK_INDICES["right_jaw"]])
    return float(cheek_width / jaw_width)

if __name__ == "__main__":
    dummy_pts = np.random.rand(478, 2) * 100
    print(f"Face Symmetry: {face_symmetry(dummy_pts)}")
    print(f"Face Proportions: {face_proportions(dummy_pts)}")
    print(f"Vertical Balance: {vertical_balance(dummy_pts)}")
    print(f"Jaw-Cheek Balance: {jaw_cheek_balance(dummy_pts)}")
