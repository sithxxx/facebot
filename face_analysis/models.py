from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class FaceLandmarks:
    """
    Dataclass for face landmarks.
    
    Attributes:
        points: (478, 2) numpy array of pixel coordinates.
        image_width: Width of the image in pixels.
        image_height: Height of the image in pixels.
    """
    points: np.ndarray
    image_width: int
    image_height: int

@dataclass
class MetricResult:
    """
    Result of a single metric calculation.
    
    Attributes:
        name: Internal name of the metric.
        name_ru: Russian display name of the metric.
        raw_value: The calculated value of the metric.
        norm_value: The population median for this metric.
        sigma_deviation: How many standard deviations the raw value is from the norm.
        score: Calculated score from 1.0 to 10.0.
        description: A brief description of what the metric measures.
    """
    name: str
    name_ru: str
    raw_value: float
    norm_value: float
    sigma_deviation: float
    score: float
    description: str

@dataclass
class FullAnalysisResult:
    """
    Complete analysis result for a face.
    
    Attributes:
        metrics: List of MetricResult objects.
        overall_score: Weighted average score.
        top_strengths: Names of the top 3 scoring metrics.
        top_weaknesses: Names of the bottom 3 scoring metrics.
        gender: Gender used for normative value lookup.
    """
    metrics: List[MetricResult]
    overall_score: float
    geometry_score: float       # ← NEW: pure geometry score (for debugging + PDF detail)
    ml_score: float | None      # ← NEW: raw ML model score (None if model unavailable)
    ml_weight: float            # ← NEW: actual ML weight used in final score (0.0–1.0)
    top_strengths: List[str]
    top_weaknesses: List[str]
    gender: str
