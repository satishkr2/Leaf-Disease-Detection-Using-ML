"""
Train binary Leaf vs Non-Leaf classifier (MobileNetV2 transfer learning).

Usage:
  python model/leaf_detector/prepare_dataset.py
  python model/leaf_detector/train.py
"""
import json
from pathlib import Path

import tensorflow as tf

try:
    import matplotlib.pyplot as plt

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "dataset" / "leaf_binary"
SAVE_DIR = Path(__file__).parent / "saved_models"
PLOTS_DIR = Path(__file__).parent / "plots"

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 20
LABELS = ["leaf", "non_leaf"]
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def count_images(folder: Path) -> int:
    """Count images in folder and all nested subfolders (e.g. leaf/tomato_early/)."""
    if not folder.exists():
        return 0
    return sum(
        1
        for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXT
    )


def print_dataset_summary():
    leaf_dir = DATA_DIR / "leaf"
    non_dir = DATA_DIR / "non_leaf"
    n_leaf = count_images(leaf_dir)
    n_non = count_images(non_dir)
    print("\n=== Dataset summary ===")
    print(f"  Path: {DATA_DIR}")
    print(f"  leaf:     {n_leaf:,} images (includes all subfolders under leaf/)")
    print(f"  non_leaf: {n_non:,} images")
    if leaf_dir.exists():
        for sub in sorted(leaf_dir.iterdir()):
            if sub.is_dir():
                print(f"    - {sub.name}: {count_images(sub):,}")
    if n_leaf == 0 or n_non == 0:
        raise FileNotFoundError(
            "Need images in BOTH dataset/leaf_binary/leaf/ and dataset/leaf_binary/non_leaf/"
        )
    ratio = n_leaf / max(n_non, 1)
    if ratio > 3 or ratio < 1 / 3:
        print(
            f"\n  Warning: class imbalance (leaf:non_leaf ≈ {ratio:.1f}:1). "
            "Add more non_leaf photos (faces, sky, objects, soil) for best results."
        )
    print()
    return n_leaf, n_non


def train():
    if not DATA_DIR.exists() or not (DATA_DIR / "leaf").exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_DIR}. "
            "Use dataset/leaf_binary/leaf/ and dataset/leaf_binary/non_leaf/"
        )

    n_leaf, n_non = print_dataset_summary()

    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    train_gen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=25,
        width_shift_range=0.15,
        height_shift_range=0.15,
        zoom_range=0.2,
        horizontal_flip=True,
        validation_split=0.2,
    )
    val_gen = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.2)

    train_flow = train_gen.flow_from_directory(
        DATA_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training",
        shuffle=True,
    )
    val_flow = val_gen.flow_from_directory(
        DATA_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
        shuffle=False,
    )

    base = MobileNetV2(weights="imagenet", include_top=False, input_shape=(*IMG_SIZE, 3))
    base.trainable = False
    x = GlobalAveragePooling2D()(base.output)
    x = Dropout(0.3)(x)
    outputs = Dense(2, activation="softmax")(x)
    model = Model(base.input, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    # Balance loss when leaf >> non_leaf (common with PlantVillage-only leaf folders)
    total = n_leaf + n_non
    class_weight = {
        0: total / (2 * n_leaf),  # index 0 = leaf (alphabetical)
        1: total / (2 * n_non),  # index 1 = non_leaf
    }
    # flow_from_directory: class_indices leaf=0, non_leaf=1 typically
    if train_flow.class_indices.get("non_leaf") == 0:
        class_weight = {0: total / (2 * n_non), 1: total / (2 * n_leaf)}

    print(f"Class indices: {train_flow.class_indices}")
    print(f"Class weights: {class_weight}")

    callbacks = [
        EarlyStopping(patience=6, restore_best_weights=True, monitor="val_accuracy"),
        ReduceLROnPlateau(factor=0.5, patience=3),
        ModelCheckpoint(
            str(SAVE_DIR / "leaf_detector.h5"),
            save_best_only=True,
            monitor="val_accuracy",
            mode="max",
        ),
    ]

    history = model.fit(
        train_flow,
        validation_data=val_flow,
        epochs=EPOCHS,
        class_weight=class_weight,
        callbacks=callbacks,
        verbose=1,
    )

    if HAS_MATPLOTLIB:
        plt.figure(figsize=(10, 4))
        plt.subplot(1, 2, 1)
        plt.plot(history.history["accuracy"], label="train")
        plt.plot(history.history["val_accuracy"], label="val")
        plt.title("Leaf detector accuracy")
        plt.legend()
        plt.subplot(1, 2, 2)
        plt.plot(history.history["loss"], label="train")
        plt.plot(history.history["val_loss"], label="val")
        plt.title("Leaf detector loss")
        plt.legend()
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / "leaf_detector_training.png", dpi=150)
        plt.close()

    class_names = [k for k, v in sorted(train_flow.class_indices.items(), key=lambda x: x[1])]
    with open(SAVE_DIR / "leaf_detector_labels.json", "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)

    print(f"Saved model to {SAVE_DIR / 'leaf_detector.h5'}")
    print(f"Classes: {class_names}")


if __name__ == "__main__":
    train()
