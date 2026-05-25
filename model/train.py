"""
Train and compare CNN transfer learning models for plant leaf disease detection.
Models: MobileNetV2, ResNet50, EfficientNetB0
Dataset: PlantVillage-style folder structure (class subfolders)
"""
import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from tensorflow.keras.applications import (
    EfficientNetB0,
    MobileNetV2,
    ResNet50,
)
from tensorflow.keras.applications.efficientnet import preprocess_input as eff_preprocess
from tensorflow.keras.applications.mobilenet_v2 import (
    preprocess_input as mobilenet_preprocess,
)
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Target classes (subset of PlantVillage)
TARGET_CLASSES = [
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Potato___Early_blight",
    "Potato___healthy",
    "Pepper__bell___Bacterial_spot",
    "Tomato___healthy",
]

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 15
DATASET_DIR = Path(__file__).parent.parent / "dataset" / "plantvillage"
SAVE_DIR = Path(__file__).parent / "saved_models"
PLOTS_DIR = Path(__file__).parent / "plots"
SAVE_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def get_data_generators():
    """Create train/val generators with augmentation."""
    if not DATASET_DIR.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATASET_DIR}. "
            "Run: python model/download_dataset.py or place PlantVillage folders there."
        )

    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode="nearest",
        validation_split=0.2,
    )
    val_datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.2)

    train_gen = train_datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training",
        shuffle=True,
    )
    val_gen = val_datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
        shuffle=False,
    )
    return train_gen, val_gen


def build_model(base_name: str, num_classes: int) -> Model:
    """Build transfer learning model with frozen base initially."""
    inputs = tf.keras.Input(shape=(*IMG_SIZE, 3))

    if base_name == "mobilenet":
        base = MobileNetV2(weights="imagenet", include_top=False, input_tensor=inputs)
        preprocess = mobilenet_preprocess
    elif base_name == "resnet":
        base = ResNet50(weights="imagenet", include_top=False, input_tensor=inputs)
        preprocess = resnet_preprocess
    else:
        base = EfficientNetB0(weights="imagenet", include_top=False, input_tensor=inputs)
        preprocess = eff_preprocess

    base.trainable = False
    x = GlobalAveragePooling2D()(base.output)
    x = Dropout(0.3)(x)
    outputs = Dense(num_classes, activation="softmax")(x)
    model = Model(inputs, outputs, name=f"{base_name}_plant_disease")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def plot_history(history, model_name: str):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(history.history["accuracy"], label="Train")
    axes[0].plot(history.history["val_accuracy"], label="Val")
    axes[0].set_title(f"{model_name} - Accuracy")
    axes[0].legend()
    axes[1].plot(history.history["loss"], label="Train")
    axes[1].plot(history.history["val_loss"], label="Val")
    axes[1].set_title(f"{model_name} - Loss")
    axes[1].legend()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"{model_name}_training.png", dpi=150)
    plt.close()


def evaluate_model(model, val_gen, class_names: list, model_name: str) -> dict:
    val_gen.reset()
    preds = model.predict(val_gen, verbose=0)
    y_pred = np.argmax(preds, axis=1)
    y_true = val_gen.classes[: len(y_pred)]

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=class_names, yticklabels=class_names)
    plt.title(f"{model_name} Confusion Matrix")
    plt.ylabel("True")
    plt.xlabel("Predicted")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"{model_name}_confusion_matrix.png", dpi=150)
    plt.close()

    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
    return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "report": report}


def train_and_compare():
    train_gen, val_gen = get_data_generators()
    class_indices = train_gen.class_indices
    class_names = [k for k, v in sorted(class_indices.items(), key=lambda x: x[1])]
    num_classes = len(class_names)

    callbacks = [
        EarlyStopping(patience=5, restore_best_weights=True, monitor="val_accuracy"),
        ReduceLROnPlateau(factor=0.5, patience=3, min_lr=1e-7),
    ]

    models_to_train = ["mobilenet", "resnet", "efficientnet"]
    results = {}

    for name in models_to_train:
        print(f"\n{'='*50}\nTraining {name}\n{'='*50}")
        model = build_model(name, num_classes)
        checkpoint = ModelCheckpoint(
            str(SAVE_DIR / f"{name}_model.h5"),
            save_best_only=True,
            monitor="val_accuracy",
            mode="max",
        )
        history = model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=EPOCHS,
            callbacks=callbacks + [checkpoint],
            verbose=1,
        )
        plot_history(history, name)
        metrics = evaluate_model(model, val_gen, class_names, name)
        results[name] = metrics
        print(f"{name} - Acc: {metrics['accuracy']:.4f}, F1: {metrics['f1']:.4f}")

    best = max(results, key=lambda k: results[k]["f1"])
    print(f"\nBest model: {best} (F1: {results[best]['f1']:.4f})")

    import shutil

    shutil.copy(SAVE_DIR / f"{best}_model.h5", SAVE_DIR / "best_model.h5")
    with open(SAVE_DIR / "class_labels.json", "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)
    with open(SAVE_DIR / "comparison_results.json", "w", encoding="utf-8") as f:
        json.dump(
            {k: {m: v for m, v in val.items() if m != "report"} for k, val in results.items()},
            f,
            indent=2,
        )

    print(f"Saved best model to {SAVE_DIR / 'best_model.h5'}")
    return results


if __name__ == "__main__":
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    train_and_compare()
