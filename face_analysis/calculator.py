from typing import List, Dict
import numpy as np
import cv2
import logging
from .models import FaceLandmarks, MetricResult, FullAnalysisResult
from .norms import NORMS
from .scorer import raw_to_score
from .metrics import symmetry, eyes, nose, jaw_chin, lips, forehead
import os

ML_WEIGHT = float(os.getenv("ML_WEIGHT", "0.6"))

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

# English display names/descriptions (used for lang="en" reports).
METRIC_INFO_EN = {
    "face_symmetry": ("Face Symmetry", "Evenness of the left and right sides of the face"),
    "face_proportions": ("Face Proportions", "Face height to cheekbone width ratio"),
    "vertical_balance": ("Vertical Balance", "Balance of the middle and lower thirds of the face"),
    "jaw_cheek_balance": ("Jaw-Cheek Balance", "Cheekbone to jaw width ratio"),
    "eye_size": ("Eye Size", "Eye size relative to face width"),
    "eye_spacing": ("Eye Spacing", "Distance between the inner eye corners"),
    "eye_tilt": ("Eye Tilt", "Eye tilt angle (hunter eyes)"),
    "nose_width": ("Nose Width", "Relative width of the nose wings"),
    "mouth_width": ("Mouth Width", "Mouth width relative to cheekbone width"),
    "nose_length": ("Nose Length", "Nose length relative to face height"),
    "chin_length": ("Chin Length", "Relative chin length"),
    "chin_contour": ("Chin Contour", "Jaw angle and shape"),
    "nose_to_mouth_ratio": ("Nose-Mouth Ratio", "Nose width to mouth width proportion"),
    "biocular_width": ("Biocular Width", "Distance between the outer eye corners"),
    "forehead_width": ("Forehead Width", "Relative forehead width"),
    "lip_fullness": ("Lip Fullness", "Total lip height to mouth width"),
    "lip_proportions": ("Lip Proportions", "Upper to lower lip ratio"),
    "jaw_to_mouth": ("Jaw to Mouth", "Jaw width to mouth width ratio"),
    "eye_shape": ("Eye Shape", "Eye height to width ratio"),
    "brow_height": ("Brow Height", "Distance from brows to eyelids"),
}

def analyze_face(landmarks: FaceLandmarks, gender: str = "male", photo_path: str = None) -> FullAnalysisResult:
    """
    Runs all 20 metric functions, scores each one,
    computes weighted overall score, identifies strengths/weaknesses.
    """
    # Normalize gender once so the norm lookup is consistent and never
    # silently scores women against male norms. Anything unexpected is
    # logged loudly instead of quietly falling back.
    gender = (gender or "").strip().lower()
    if gender not in NORMS:
        logger.warning(f"Unknown gender {gender!r}; defaulting to 'male' norms")
        gender = "male"

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
            name_en, description_en = METRIC_INFO_EN[name]
            norm_val = NORMS[gender].get(name, {}).get("median", 0.0)

            results.append(MetricResult(
                name=name,
                name_ru=name_ru,
                raw_value=raw_val,
                norm_value=norm_val,
                sigma_deviation=sigma,
                score=score,
                description=description,
                name_en=name_en,
                description_en=description_en,
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
    
    ml_score = None
    ml_weight_used = 0.0
    overall_score = float(geometry_score)

    if photo_path:
        from face_analysis.beauty_predictor import get_predictor
        from face_analysis.alignment import align_and_crop
        predictor = get_predictor()
        if predictor is not None:
            try:
                # Feed the model an aligned, tight face crop so the input
                # matches the SCUT-FBP5500 framing it was trained on.
                # Fall back to the raw photo if cropping fails.
                image_bgr = cv2.imread(photo_path)
                face_crop = align_and_crop(image_bgr, pts) if image_bgr is not None else None
                if face_crop is None:
                    logger.warning("Face crop failed; feeding raw photo to ML model")
                ml_input = face_crop if face_crop is not None else photo_path
                ml_score = predictor.predict(ml_input)
                ml_weight_used = ML_WEIGHT
                overall_score = ml_weight_used * ml_score + (1.0 - ml_weight_used) * geometry_score
                logging.info(
                    f"Score breakdown — ML={ml_score:.2f} (w={ml_weight_used}), "
                    f"geo={geometry_score:.2f} (w={1.0 - ml_weight_used}), overall={overall_score:.2f}"
                )
            except Exception as e:
                logger.error(f"Error in ML prediction: {e}")
                logging.info(f"Score breakdown — geo={geometry_score:.2f} (ML failed, geometry fallback)")
        else:
            logging.info(f"Score breakdown — geo={geometry_score:.2f} (ML model not loaded, geometry fallback)")
    else:
        logging.info(f"Score breakdown — geo={geometry_score:.2f} (No photo_path, geometry fallback)")

    return FullAnalysisResult(
        metrics=results,
        overall_score=round(overall_score, 2),
        geometry_score=round(geometry_score, 2),
        ml_score=round(ml_score, 2) if ml_score is not None else None,
        ml_weight=ml_weight_used,
        top_strengths=top_strengths,
        top_weaknesses=top_weaknesses,
        gender=gender,
    )
