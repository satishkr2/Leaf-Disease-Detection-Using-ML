"""
Prepare binary dataset for leaf vs non-leaf training.

Structure:
  dataset/leaf_binary/leaf/
  dataset/leaf_binary/non_leaf/

Sources:
  - leaf: copies from PlantVillage folders (if present)
  - non_leaf: synthetic placeholders + optional user images
"""
import random
import shutil
from pathlib import Path

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LEAF_BINARY_DIR = PROJECT_ROOT / "dataset" / "leaf_binary"
LEAF_DIR = LEAF_BINARY_DIR / "leaf"
NON_LEAF_DIR = LEAF_BINARY_DIR / "non_leaf"
PLANTVILLAGE = PROJECT_ROOT / "dataset" / "plantvillage"

MAX_PER_CLASS = 400
SYNTHETIC_COUNT = 120


def _clear_dir(d: Path):
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*"):
        if f.is_file():
            f.unlink()


def copy_plantvillage_leaves():
    count = 0
    if not PLANTVILLAGE.exists():
        return count
    for class_dir in PLANTVILLAGE.iterdir():
        if not class_dir.is_dir():
            continue
        for img in class_dir.glob("*"):
            if img.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue
            if count >= MAX_PER_CLASS:
                return count
            dest = LEAF_DIR / f"pv_{count:05d}{img.suffix.lower()}"
            shutil.copy2(img, dest)
            count += 1
    return count


def _synthetic_leaf(i: int) -> np.ndarray:
    img = np.ones((256, 256, 3), dtype=np.uint8) * 240
    center = (random.randint(80, 176), random.randint(80, 176))
    axes = (random.randint(60, 110), random.randint(40, 90))
    angle = random.randint(-30, 30)
    color = (
        random.randint(30, 90),
        random.randint(100, 200),
        random.randint(30, 90),
    )
    cv2.ellipse(img, center, axes, angle, 0, 360, color, -1)
    cv2.GaussianBlur(img, (5, 5), 0, dst=img)
    return img


def _synthetic_non_leaf(i: int) -> np.ndarray:
    kind = i % 5
    img = np.zeros((256, 256, 3), dtype=np.uint8)
    if kind == 0:  # sky
        img[:] = (235, 180, 120)
    elif kind == 1:  # soil
        img[:] = (50, 80, 120)
    elif kind == 2:  # gray wall
        v = random.randint(80, 180)
        img[:] = (v, v, v)
    elif kind == 3:  # random noise
        img = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    else:  # face-ish tone
        img[:] = (180, 160, 140)
        cv2.circle(img, (128, 128), 60, (200, 180, 160), -1)
    return img


def generate_synthetic():
    leaf_start = len(list(LEAF_DIR.glob("*")))
    for i in range(SYNTHETIC_COUNT):
        cv2.imwrite(str(LEAF_DIR / f"syn_leaf_{leaf_start + i:04d}.jpg"), _synthetic_leaf(i))

    for i in range(SYNTHETIC_COUNT):
        cv2.imwrite(str(NON_LEAF_DIR / f"syn_non_{i:04d}.jpg"), _synthetic_non_leaf(i))


def main():
    _clear_dir(LEAF_DIR)
    _clear_dir(NON_LEAF_DIR)

    n_leaf = copy_plantvillage_leaves()
    print(f"Copied {n_leaf} leaf images from PlantVillage")

    generate_synthetic()
    n_leaf_total = len(list(LEAF_DIR.glob("*")))
    n_non = len(list(NON_LEAF_DIR.glob("*")))
    print(f"Dataset ready at {LEAF_BINARY_DIR}")
    print(f"  leaf: {n_leaf_total} images")
    print(f"  non_leaf: {n_non} images")
    print("Add your own non-leaf photos to dataset/leaf_binary/non_leaf/ for better accuracy.")


if __name__ == "__main__":
    main()
