"""
Прогоняет все фото из ffhq_sample/ через текущий пайплайн детекции и метрик,
собирает raw_value по каждой из 20 метрик, считает реальные median/std,
выводит готовый блок кода для norms.py
"""

import sys
from pathlib import Path
import numpy as np
import logging
from collections import defaultdict

logging.basicConfig(level=logging.WARNING)  # приглушаем мусорные логи MediaPipe

sys.path.insert(0, str(Path(__file__).parent.parent))

from face_analysis.detector import detect_face
from face_analysis.metrics.symmetry import (
    face_symmetry, face_proportions, vertical_balance, jaw_cheek_balance
)
from face_analysis.metrics.eyes import eye_size, eye_spacing, eye_tilt, eye_shape
from face_analysis.metrics.nose import nose_width, nose_length, nose_to_mouth_ratio
from face_analysis.metrics.jaw_chin import (
    chin_length, chin_contour, mouth_width, jaw_to_mouth, biocular_width
)
from face_analysis.metrics.lips import lip_fullness, lip_proportions
from face_analysis.metrics.forehead import forehead_width, brow_height

IMAGES_DIR = Path(__file__).parent / "ffhq_sample"
OUTPUT_FILE = Path(__file__).parent / "norms_recalculated.py"

# имя метрики -> функция расчёта
METRIC_FUNCTIONS = {
    "face_symmetry": face_symmetry,
    "face_proportions": face_proportions,
    "vertical_balance": vertical_balance,
    "jaw_cheek_balance": jaw_cheek_balance,
    "eye_size": eye_size,
    "eye_spacing": eye_spacing,
    "eye_tilt": eye_tilt,
    "nose_width": nose_width,
    "mouth_width": mouth_width,
    "nose_length": nose_length,
    "chin_length": chin_length,
    "chin_contour": chin_contour,
    "nose_to_mouth_ratio": nose_to_mouth_ratio,
    "biocular_width": biocular_width,
    "forehead_width": forehead_width,
    "lip_fullness": lip_fullness,
    "lip_proportions": lip_proportions,
    "jaw_to_mouth": jaw_to_mouth,
    "eye_shape": eye_shape,
    "brow_height": brow_height,
}


def main():
    image_paths = sorted(IMAGES_DIR.glob("*.jpg")) + sorted(IMAGES_DIR.glob("*.png"))

    if not image_paths:
        print(f"ОШИБКА: не найдено изображений в {IMAGES_DIR}/")
        print("Сначала запусти download_ffhq_sample.py")
        return

    print(f"Найдено {len(image_paths)} изображений. Начинаю обработку...\n")

    results = defaultdict(list)
    processed = 0
    failed = 0

    for i, img_path in enumerate(image_paths):
        landmarks = detect_face(str(img_path))

        if landmarks is None:
            failed += 1
            continue

        pts = landmarks.points

        for metric_name, func in METRIC_FUNCTIONS.items():
            try:
                value = func(pts)
                if np.isfinite(value):
                    results[metric_name].append(value)
            except Exception as e:
                # пропускаем единичные сбои расчёта, не останавливаем весь прогон
                pass

        processed += 1
        if processed % 50 == 0:
            print(f"Обработано: {processed}/{len(image_paths)} (ошибок детекции: {failed})")

    print(f"\nГотово. Успешно обработано: {processed}, ошибок детекции лица: {failed}\n")
    print("=" * 70)
    print("РЕЗУЛЬТАТЫ — реальные median/std по твоим формулам:")
    print("=" * 70)

    norms_code_lines = []
    norms_code_lines.append('NORMS = {')
    norms_code_lines.append('    "male": {')

    for metric_name in METRIC_FUNCTIONS.keys():
        values = results[metric_name]
        if len(values) < 10:
            print(f"  {metric_name:25} — ПРОПУЩЕНО (мало валидных значений: {len(values)})")
            continue

        values_arr = np.array(values)
        median = float(np.median(values_arr))
        std = float(np.std(values_arr))
        n = len(values_arr)

        print(f"  {metric_name:25} median={median:.4f}  std={std:.4f}  (n={n})")

        norms_code_lines.append(
            f'        "{metric_name}": {{"median": {median:.4f}, "std": {std:.4f}}},'
        )

    norms_code_lines.append('    },')
    norms_code_lines.append('    "female": {')
    norms_code_lines.append('        # TODO: повтори процесс на датасете женских лиц')
    norms_code_lines.append('        # или используй те же значения как временное приближение')
    norms_code_lines.append('    },')
    norms_code_lines.append('}')

    output_code = "\n".join(norms_code_lines)

    OUTPUT_FILE.write_text(output_code, encoding="utf-8")
    print(f"\nГотовый код норм сохранён в: {OUTPUT_FILE}")
    print("Скопируй содержимое в face_analysis/norms.py, заменив старый словарь NORMS.")


if __name__ == "__main__":
    main()
