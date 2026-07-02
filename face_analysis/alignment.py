"""
Face alignment + cropping for the ML beauty model.

The beauty model (beauty_predictor.py) was trained on SCUT-FBP5500, whose
images are tight, frontal, roughly upright face crops, then resized to
224x224. At inference we instead receive a raw photo (background, body,
arbitrary framing). Feeding that straight in is a train/inference
distribution mismatch — empirically it shifts the predicted score by
2–3 points out of 10.

align_and_crop() reproduces the training framing as closely as we can:
roll-align so the eye line is horizontal, then take a square crop tight
around the face landmarks. Resize to 224x224 stays in the model transform.
"""

import cv2
import numpy as np

from .detector import LANDMARK_INDICES


def _eye_centers(points: np.ndarray):
    """Return (left_eye_center, right_eye_center) in image coordinates."""
    li, lo = LANDMARK_INDICES["left_eye_inner"], LANDMARK_INDICES["left_eye_outer"]
    ri, ro = LANDMARK_INDICES["right_eye_inner"], LANDMARK_INDICES["right_eye_outer"]
    left = (points[li] + points[lo]) / 2.0
    right = (points[ri] + points[ro]) / 2.0
    return left, right


def align_and_crop(image_bgr: np.ndarray, points: np.ndarray, pad: float = 0.30):
    """
    Roll-align the face so the eyes are horizontal, then crop a square box
    around all landmarks with `pad` fractional padding.

    Args:
        image_bgr: original image (BGR, as read by cv2.imread).
        points: (N, 2) landmark coordinates in the same image space.
        pad: extra margin around the landmark bounding box, as a fraction
             of its width/height (0.30 ≈ include forehead/chin/cheeks).

    Returns:
        A square BGR crop (np.ndarray) approximating SCUT framing, or None
        if the input is unusable.
    """
    if image_bgr is None or points is None or len(points) == 0:
        return None

    h, w = image_bgr.shape[:2]
    left_eye, right_eye = _eye_centers(points)

    # Angle of the eye line; rotating by it makes the eyes horizontal.
    dx = float(right_eye[0] - left_eye[0])
    dy = float(right_eye[1] - left_eye[1])
    angle = np.degrees(np.arctan2(dy, dx))
    eyes_center = (
        float((left_eye[0] + right_eye[0]) / 2.0),
        float((left_eye[1] + right_eye[1]) / 2.0),
    )

    M = cv2.getRotationMatrix2D(eyes_center, angle, 1.0)
    rotated = cv2.warpAffine(image_bgr, M, (w, h), flags=cv2.INTER_LINEAR)

    # Apply the same affine transform to the landmarks.
    pts_h = np.hstack([points, np.ones((len(points), 1))])
    rpts = (M @ pts_h.T).T

    x0, y0 = rpts.min(axis=0)
    x1, y1 = rpts.max(axis=0)
    bw, bh = x1 - x0, y1 - y0
    x0 -= bw * pad
    x1 += bw * pad
    y0 -= bh * pad
    y1 += bh * pad

    # Make the box square (around its center) so the model's Resize to
    # 224x224 does not distort the face aspect ratio.
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    half = max(x1 - x0, y1 - y0) / 2.0
    sx0 = int(max(0, round(cx - half)))
    sy0 = int(max(0, round(cy - half)))
    sx1 = int(min(w, round(cx + half)))
    sy1 = int(min(h, round(cy + half)))

    if sx1 <= sx0 or sy1 <= sy0:
        return None

    crop = rotated[sy0:sy1, sx0:sx1]
    if crop.size == 0:
        return None
    return crop
