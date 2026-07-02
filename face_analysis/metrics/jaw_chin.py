import numpy as np
from ..detector import LANDMARK_INDICES

def chin_length(pts: np.ndarray) -> float:
    """lower_lip_bottom → chin_bottom / face_height"""
    chin_len = np.linalg.norm(pts[LANDMARK_INDICES["lower_lip_bottom"]] - pts[LANDMARK_INDICES["chin_bottom"]])
    face_height = np.linalg.norm(pts[LANDMARK_INDICES["nose_bridge"]] - pts[LANDMARK_INDICES["chin_bottom"]])
    return float(chin_len / face_height)

def chin_contour(pts: np.ndarray) -> float:
    """
    Угол подбородка в градусах, нормализованный.
    Чем шире/тупее угол — тем более квадратная челюсть.
    """
    left_jaw = pts[LANDMARK_INDICES["left_jaw"]]
    right_jaw = pts[LANDMARK_INDICES["right_jaw"]]
    chin_bottom = pts[LANDMARK_INDICES["chin_bottom"]]
    
    v1 = left_jaw - chin_bottom
    v2 = right_jaw - chin_bottom
    
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    cos_angle = np.clip(cos_angle, -1.0, 1.0)  # защита от погрешностей округления
    
    angle_degrees = np.degrees(np.arccos(cos_angle))
    
    # нормализуем в диапазон, сопоставимый с нормой 0.6305 (~125.8°)
    # делим угол на 180, чтобы получить значение 0–1 как в примере отчёта
    normalized = angle_degrees / 180.0
    
    return float(normalized)

def mouth_width(pts: np.ndarray) -> float:
    """mouth_left → mouth_right / face width (cheeks)"""
    mouth_w = np.linalg.norm(pts[LANDMARK_INDICES["mouth_left"]] - pts[LANDMARK_INDICES["mouth_right"]])
    face_width = np.linalg.norm(pts[LANDMARK_INDICES["left_cheek"]] - pts[LANDMARK_INDICES["right_cheek"]])
    return float(mouth_w / face_width)

def jaw_to_mouth(pts: np.ndarray) -> float:
    """jaw_width / mouth_width"""
    jaw_width = np.linalg.norm(pts[LANDMARK_INDICES["left_jaw"]] - pts[LANDMARK_INDICES["right_jaw"]])
    mouth_width_val = np.linalg.norm(pts[LANDMARK_INDICES["mouth_left"]] - pts[LANDMARK_INDICES["mouth_right"]])
    return float(jaw_width / mouth_width_val)

def biocular_width(pts: np.ndarray) -> float:
    """left_eye_outer → right_eye_outer / face width"""
    biocular_w = np.linalg.norm(pts[LANDMARK_INDICES["left_eye_outer"]] - pts[LANDMARK_INDICES["right_eye_outer"]])
    face_width = np.linalg.norm(pts[LANDMARK_INDICES["left_cheek"]] - pts[LANDMARK_INDICES["right_cheek"]])
    return float(biocular_w / face_width)

if __name__ == "__main__":
    dummy_pts = np.random.rand(478, 2) * 100
    print(f"Chin Length: {chin_length(dummy_pts)}")
    print(f"Chin Contour: {chin_contour(dummy_pts)}")
    print(f"Mouth Width: {mouth_width(dummy_pts)}")
    print(f"Jaw to Mouth: {jaw_to_mouth(dummy_pts)}")
    print(f"Biocular Width: {biocular_width(dummy_pts)}")
