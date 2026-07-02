from typing import Dict, Tuple
from .norms import NORMS

# +1 = higher raw value → higher score
# -1 = lower raw value → higher score
#  0 = closer to median → higher score (for proportions)
SCORE_DIRECTION = {
    "face_symmetry":       +1,
    "face_proportions":     0,
    "vertical_balance":     0,
    "jaw_cheek_balance":   -1,  # wider jaw relative to cheeks = more masculine (lower ratio = more jaw)
    "eye_size":            +1,
    "eye_spacing":          0,
    "eye_tilt":            +1,
    "nose_width":          -1,  # narrower nose → higher score
    "mouth_width":          0,
    "nose_length":          0,
    "chin_length":         +1,
    "chin_contour":        +1,
    "nose_to_mouth_ratio":  0,
    "biocular_width":       0,
    "forehead_width":       0,
    "lip_fullness":        +1,
    "lip_proportions":      0,
    "jaw_to_mouth":         0,
    "eye_shape":           +1,
    "brow_height":          0,
}

def raw_to_score(raw_value: float, metric_name: str, gender: str) -> Tuple[float, float]:
    """
    Convert raw metric value to 1–10 score using sigma deviation.
    
    Args:
        raw_value: The measured value.
        metric_name: Key in NORMS and SCORE_DIRECTION.
        gender: "male" or "female".
        
    Returns:
        (score, sigma_deviation)
    """
    norm = NORMS[gender][metric_name]
    median = norm["median"]
    std = norm["std"]
    direction = SCORE_DIRECTION[metric_name]
    
    sigma = (raw_value - median) / std

    # Map the sigma deviation onto the full 1–10 range, clamped at ±3σ
    # (~99.7% of the population). Two cases depending on direction:
    if direction == 0:
        # Proximity metric: the median IS the ideal. Exactly at the median
        # → 10; |3σ| or more away → 1, symmetric in both directions.
        deviation = min(abs(sigma), 3.0)
        score = 10.0 - (deviation / 3.0) * 9.0
    else:
        # Directional metric: more (+1) or less (-1) is better. The
        # population median maps to the midpoint (5.5); +3σ in the good
        # direction → 10, -3σ → 1.
        directional_sigma = max(-3.0, min(3.0, sigma * direction))
        score = 5.5 + (directional_sigma / 3.0) * 4.5

    score = max(1.0, min(10.0, score))
    return round(score, 2), round(sigma, 2)
