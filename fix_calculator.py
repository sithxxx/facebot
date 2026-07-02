with open('face_analysis/calculator.py', 'w') as f:
    f.write('''from typing import List, Dict
import numpy as np
import logging
from .models import FaceLandmarks, MetricResult, FullAnalysisResult
from .norms import NORMS
from .scorer import raw_to_score
from .metrics import symmetry, eyes, nose, jaw_chin, lips, forehead
from face_analysis.beauty_predictor import BeautyPredictor

_predictor = BeautyPredictor()  # загружается один раз при старте

logger = logging.getLogger(__name__)

# Metric weights for overall score
WEIGHTS = {
    "face_symmetry": 1.5,
    "face_proportions": 1.3,
    "jaw_cheek_balance": 1.2,
    "chin_contour": 1.1,
    "chin_length": 1.1,
}

# Mapping of internal names to Russian names and descriptions
METRIC_INFO = {
    "face_symmetry": ("Симметрия лица", "Равномерность левой и правой сторон лица"),
    "face_proportions": ("Пропорции лица", "Отношение высоты лица к ширине скул"),
    "vertical_balance": ("Вертикальный баланс", "Баланс средней и нижней третей лица"),
    "jaw_cheek_balance": ("Баланс челюсти и скул", "Соотношение ширины скул и челюсти"),
    "eye_size": ("Размер глаз", "Относительный размер глаз к ширине лица"),
    "eye_spacing": ("Расстояние между глазами", "Расстояние между внутренними уголками глаз"),
    "eye_tilt": ("Наклон глаз", "Угол наклона глаз (охотничий взгляд)"),
    "nose_width": ("Ширина носа", "Относительная ширина крыльев носа"),
    "mouth_width": ("Ширина рта", "Относительная ширина рта к ширине скул"),
    "nose_length": ("Длина носа", "Относительная длина носа к высоте лица"),
    "chin_length": ("Длина подбородка", "Относительная длина подбородка"),
    "chin_contour": ("Контур подбородка", "Угол и форма челюсти"),
    "nose_to_mouth_ratio": ("Соотношение носа и рта", "Пропорция ширины носа к ширине рта"),
    "biocular_width": ("Биокулярная ширина", "Расстояние между внешними уголками глаз"),
    "forehead_width": ("Ширина лба", "Относительная ширина лба"),
    "lip_fullness": ("Полнота губ", "Общая высота губ к ширине рта"),
    "lip_proportions": ("Пропорции губ", "Соотношение верхней и нижней губы"),
    "jaw_to_mouth": ("Челюсть к рту", "Соотношение ширины челюсти к ширине рта"),
    "eye_shape": ("Форма глаз", "Отношение высоты глаза к его ширине"),
    "brow_height": ("Высота бровей", "Расстояние от бровей до век"),
}

def analyze_face(landmarks: FaceLandmarks, gender: str = "male", photo_path: str = None) -> FullAnalysisResult:
    """
    Runs all 20 metric functions, scores each one,
    computes weighted overall score, identifies strengths/weaknesses.
    """
    pts = landmarks.points
    
    # Mapping of metric names to functions
    metric_funcs = {
        "face_symmetry": symmetry.face_symmetry,
        "face_proportions": symmetry.face_proportions,
        "vertical_balance": symmetry.vertical_balance,
        "jaw_cheek_balance": symmetry.jaw_cheek_balance,
        "eye_size": eyes.eye_size,
        "eye_spacing": eyes.eye_spacing,
        "eye_tilt": eyes.eye_tilt,
        "eye_shape": eyes.eye_shape,
        "nose_width": nose.nose_width,
        "nose_length": nose.nose_length,
        "nose_to_mouth_ratio": nose.nose_to_mouth_ratio,
        "chin_length": jaw_chin.chin_length,
        "chin_contour": jaw_chin.chin_contour,
        "mouth_width": jaw_chin.mouth_width,
        "jaw_to_mouth": jaw_chin.jaw_to_mouth,
        "biocular_width": jaw_chin.biocular_width,
        "lip_fullness": lips.lip_fullness,
        "lip_proportions": lips.lip_proportions,
        "forehead_width": forehead.forehead_width,
        "brow_height": forehead.brow_height,
    }
    
    results: List[MetricResult] = []
    total_weighted_score = 0.0
    total_weight = 0.0
    
    for name, func in metric_funcs.items():
        try:
            raw_val = func(pts)
            score, sigma = raw_to_score(raw_val, name, gender)
            
            name_ru, description = METRIC_INFO[name]
            norm_val = NORMS.get(gender, NORMS.get("male")).get(name, {}).get("median", 0.0)
            
            results.append(MetricResult(
                name=name,
                name_ru=name_ru,
                raw_value=raw_val,
                norm_value=norm_val,
                sigma_deviation=sigma,
                score=score,
                description=description
            ))
            
            weight = WEIGHTS.get(name, 1.0)
            total_weighted_score += score * weight
            total_weight += weight
            
        except Exception as e:
            logger.error(f"Error calculating metric {name}: {str(e)}")
            
    geometry_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    # Sort results by score to find strengths and weaknesses
    sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
    top_strengths = [r.name_ru for r in sorted_results[:3]] if len(sorted_results) >= 3 else []
    top_weaknesses = [r.name_ru for r in sorted_results[-3:]][::-1] if len(sorted_results) >= 3 else []
    
    result = FullAnalysisResult(
        metrics=results,
        overall_score=float(geometry_score),
        top_strengths=top_strengths,
        top_weaknesses=top_weaknesses,
        gender=gender
    )
    
    if photo_path:
        try:
            ml_score = _predictor.predict(photo_path)
            result.overall_score = 0.6 * ml_score + 0.4 * float(geometry_score)
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            result.overall_score = float(geometry_score)
    else:
        result.overall_score = float(geometry_score)

    return result
''')
