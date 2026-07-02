import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import numpy as np
import cv2

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class BeautyModel(nn.Module):
    # та же архитектура что при обучении
    def __init__(self):
        super().__init__()
        self.backbone = models.efficientnet_b3(weights=None)
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.backbone(x).squeeze(1)


class BeautyPredictor:
    def __init__(self, model_path: str = "face_analysis/beauty_model.pth"):
        self.model = BeautyModel().to(DEVICE)
        checkpoint = torch.load(model_path, map_location=DEVICE)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])

    def predict(self, image) -> float:
        """
        Принимает путь к фото (str), BGR-массив OpenCV (np.ndarray) или PIL.Image.
        Лучше всего подавать выровненный кроп лица (см. alignment.align_and_crop),
        чтобы вход совпадал с обучением (SCUT-FBP5500).
        Возвращает балл 1.0 – 10.0.
        """
        if isinstance(image, str):
            img = Image.open(image).convert("RGB")
        elif isinstance(image, np.ndarray):
            # OpenCV BGR → RGB PIL
            img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        else:
            img = image.convert("RGB")
        tensor = self.transform(img).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            score_normalized = self.model(tensor).item()

        # конвертируем 0–1 → 1–10
        return round(1.0 + score_normalized * 9.0, 2)
import logging

# Global singleton — loaded once at bot startup
_predictor_instance: BeautyPredictor | None = None

def get_predictor() -> BeautyPredictor | None:
    """
    Returns the global BeautyPredictor instance.
    Initializes on first call.
    If model file is missing or load fails — logs a warning and returns None.
    None triggers fallback to geometry-only scoring.
    """
    global _predictor_instance
    if _predictor_instance is None:
        try:
            _predictor_instance = BeautyPredictor()
            logging.info(f"BeautyPredictor loaded successfully on {DEVICE}")
        except FileNotFoundError:
            logging.warning(
                "beauty_model.pth not found — falling back to geometry score. "
                "Place the model file at face_analysis/beauty_model.pth"
            )
        except Exception as e:
            logging.warning(
                f"BeautyPredictor failed to load: {e} — using geometry fallback"
            )
    return _predictor_instance


def predict_safe(image_path: str) -> float | None:
    """
    Safe wrapper around BeautyPredictor.predict().
    Returns float (score 1.0–10.0) or None if model is unavailable or raises.
    Never raises an exception — all errors are caught and logged.
    """
    predictor = get_predictor()
    if predictor is None:
        return None
    try:
        return predictor.predict(image_path)
    except Exception as e:
        logging.warning(f"BeautyPredictor.predict() failed: {e}")
        return None
