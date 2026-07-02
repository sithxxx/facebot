"""
Recompute facial-metric norms PER GENDER from a gender-labeled face dataset.

Replaces the old calculate_norms.py flow, which ran mixed-gender FFHQ and
mislabeled the result as "male". Here we stream a dataset that ships gender
labels, run the SAME 20 metric functions used at inference, and compute
median/std separately for male and female. Output is written to norms.py.

Usage:
    venv/bin/python recompute_norms.py
"""

import sys
from pathlib import Path
from collections import defaultdict

import numpy as np
import cv2
import logging

logging.basicConfig(level=logging.ERROR)  # silence MediaPipe chatter

sys.path.insert(0, str(Path(__file__).parent))

from datasets import load_dataset

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

# ─── Dataset config ───────────────────────────────────────────────
# CelebA (aligned, frontal faces) with the binary "Male" attribute:
#   Male ==  1  → male
#   Male == -1  → female
DATASET_NAME = "tpremoli/CelebA-attrs"
DATASET_SPLIT = "train"
IMAGE_KEY = "image"
GENDER_KEY = "Male"


def to_gender(value) -> str | None:
    """Map CelebA's 'Male' attribute (1 / -1) to 'male' / 'female'."""
    try:
        v = int(value)
    except (TypeError, ValueError):
        return None
    if v == 1:
        return "male"
    if v == -1:
        return "female"
    return None


TARGET_PER_GENDER = 400   # how many valid faces to collect per gender
MAX_SCANNED = 20000       # hard cap on images streamed, safety valve

OUTPUT_FILE = Path(__file__).parent / "face_analysis" / "norms.py"

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

# Metric order preserved for stable output.
METRIC_ORDER = list(METRIC_FUNCTIONS.keys())


def pil_to_bgr(img):
    arr = np.array(img.convert("RGB"))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def main():
    print(f"Streaming {DATASET_NAME} (split={DATASET_SPLIT})...")
    ds = load_dataset(DATASET_NAME, split=DATASET_SPLIT, streaming=True)

    # results[gender][metric] -> list of raw values
    results = {"male": defaultdict(list), "female": defaultdict(list)}
    counts = {"male": 0, "female": 0}
    scanned = 0

    for item in ds:
        scanned += 1
        if scanned > MAX_SCANNED:
            print("Hit MAX_SCANNED cap.")
            break
        if counts["male"] >= TARGET_PER_GENDER and counts["female"] >= TARGET_PER_GENDER:
            break

        gender = to_gender(item.get(GENDER_KEY))
        if gender is None or counts[gender] >= TARGET_PER_GENDER:
            continue

        try:
            bgr = pil_to_bgr(item[IMAGE_KEY])
        except Exception:
            continue

        landmarks = detect_face(bgr)
        if landmarks is None:
            continue
        pts = landmarks.points

        # Only count a face once it yields at least the symmetry metric.
        any_ok = False
        for name, func in METRIC_FUNCTIONS.items():
            try:
                v = func(pts)
                if np.isfinite(v):
                    results[gender][name].append(float(v))
                    any_ok = True
            except Exception:
                pass
        if any_ok:
            counts[gender] += 1
            total = counts["male"] + counts["female"]
            if total % 50 == 0:
                print(f"Collected M={counts['male']} F={counts['female']} (scanned {scanned})")

    print(f"\nDone. Collected male={counts['male']}, female={counts['female']} "
          f"(scanned {scanned}).\n")

    # ─── Build norms.py ───────────────────────────────────────────
    lines = []
    lines.append('"""')
    lines.append("Normative facial-metric values, computed PER GENDER from a")
    lines.append(f"gender-labeled dataset ({DATASET_NAME}) using the same metric")
    lines.append("functions used at inference. Regenerate with recompute_norms.py.")
    lines.append('"""')
    lines.append("")
    lines.append("NORMS = {")
    for gender in ("male", "female"):
        lines.append(f'    "{gender}": {{')
        for metric in METRIC_ORDER:
            vals = np.array(results[gender][metric])
            if len(vals) < 30:
                print(f"  WARNING {gender}/{metric}: only {len(vals)} values")
                if len(vals) == 0:
                    continue
            median = float(np.median(vals))
            std = float(np.std(vals))
            print(f"  {gender:6} {metric:22} median={median:.4f} std={std:.4f} (n={len(vals)})")
            lines.append(f'        "{metric}": {{"median": {median:.4f}, "std": {std:.4f}}},')
        lines.append("    },")
    lines.append("}")

    OUTPUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
