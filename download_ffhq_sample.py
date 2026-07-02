"""
Скачивает 500 случайных изображений лиц из FFHQ через HuggingFace datasets.
Сохраняет в папку ffhq_sample/
"""

from datasets import load_dataset
from pathlib import Path
from PIL import Image
import random

OUTPUT_DIR = Path("ffhq_sample")
OUTPUT_DIR.mkdir(exist_ok=True)

N_SAMPLES = 500

print("Загружаю датасет FFHQ (может занять несколько минут)...")
ds = load_dataset("Vincento/FFHQ_Flickr_Faces_512", split="train", streaming=True)

count = 0
for item in ds:
    if count >= N_SAMPLES:
        break
    img = item["image"]
    img.save(OUTPUT_DIR / f"face_{count:04d}.jpg")
    count += 1
    if count % 50 == 0:
        print(f"Скачано: {count}/{N_SAMPLES}")

print(f"Готово. Сохранено {count} изображений в {OUTPUT_DIR}/")
