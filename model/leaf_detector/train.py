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
EPOCHS = 12
LABELS = ["leaf", "non_leaf"]


def train():
    if not DATA_DIR.exists() or not (DATA_DIR / "leaf").exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_DIR}. Run: python model/leaf_detector/prepare_dataset.py"
        )

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

    callbacks = [
        EarlyStopping(patience=4, restore_best_weights=True, monitor="val_accuracy"),
        ReduceLROnPlateau(factor=0.5, patience=2),
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
