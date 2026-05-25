"""
Download a subset of PlantVillage dataset for training.
Uses tensorflow_datasets or manual Kaggle instructions as fallback.
"""
import shutil
from pathlib import Path

DATASET_DIR = Path(__file__).parent.parent / "dataset" / "plantvillage"

TARGET_CLASSES = [
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Potato___Early_blight",
    "Potato___healthy",
    "Pepper__bell___Bacterial_spot",
    "Tomato___healthy",
]


def download_via_tfds():
    """Attempt download using TensorFlow Datasets plant_village subset."""
    try:
        import tensorflow_datasets as tfds
    except ImportError:
        print("Install: pip install tensorflow-datasets")
        return False

    print("Downloading PlantVillage via TFDS (this may take a while)...")
    ds, info = tfds.load("plant_village", split="train", with_info=True, as_supervised=True)

    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    class_map = {i: name for i, name in enumerate(info.features["label"].names)}

    counts = {c: 0 for c in TARGET_CLASSES}
    max_per_class = 200

    for image, label in tfds.as_numpy(ds):
        class_name = class_map[int(label)]
        if class_name not in TARGET_CLASSES:
            continue
        if counts[class_name] >= max_per_class:
            continue

        class_dir = DATASET_DIR / class_name
        class_dir.mkdir(parents=True, exist_ok=True)
        from PIL import Image

        img = Image.fromarray(image)
        img.save(class_dir / f"{counts[class_name]:05d}.jpg")
        counts[class_name] += 1

        if all(v >= max_per_class for v in counts.values()):
            break

    print("Download complete:", counts)
    return True


def print_manual_instructions():
    print(
        """
╔══════════════════════════════════════════════════════════════════╗
║  MANUAL DATASET SETUP (PlantVillage)                             ║
╠══════════════════════════════════════════════════════════════════╣
║  1. Download from Kaggle:                                        ║
║     https://www.kaggle.com/datasets/abdallahalidev/plantvillage  ║
║  2. Extract and copy these folders to:                           ║
║     dataset/plantvillage/                                        ║
║     - Tomato___Early_blight                                      ║
║     - Tomato___Late_blight                                       ║
║     - Potato___Early_blight                                      ║
║     - Potato___healthy                                           ║
║     - Pepper__bell___Bacterial_spot                              ║
║     - Tomato___healthy                                           ║
║  3. Run: python model/train.py                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""
    )


def create_demo_structure():
    """Create minimal demo folders for project structure validation."""
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    for cls in TARGET_CLASSES:
        (DATASET_DIR / cls).mkdir(parents=True, exist_ok=True)
    readme = DATASET_DIR / "README.txt"
    readme.write_text(
        "Place PlantVillage class images in subfolders matching class names.\n"
        "See model/download_dataset.py for download instructions.\n"
    )
    print(f"Created demo structure at {DATASET_DIR}")


if __name__ == "__main__":
    create_demo_structure()
    try:
        download_via_tfds()
    except Exception as e:
        print(f"Auto-download failed: {e}")
        print_manual_instructions()
