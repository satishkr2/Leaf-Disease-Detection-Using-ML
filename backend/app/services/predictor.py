"""ML model loading and inference service."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

# Add project root for preprocessing import
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.pipeline import run_preprocessing_pipeline  # noqa: E402

from app.config import get_settings
from app.services.disease_service import disease_service

settings = get_settings()

# Default classes for demo when model not trained
DEFAULT_CLASSES = [
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Potato___Early_blight",
    "Potato___healthy",
    "Pepper__bell___Bacterial_spot",
    "Tomato___healthy",
]


class PredictorService:
    _instance = None
    _model = None
    _class_labels: List[str] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self) -> bool:
        if self._model is not None:
            return True

        labels_path = Path(settings.class_labels_path)
        if labels_path.exists():
            with open(labels_path, encoding="utf-8") as f:
                self._class_labels = json.load(f)
        else:
            self._class_labels = DEFAULT_CLASSES

        model_path = Path(settings.model_path)
        if model_path.exists():
            try:
                import tensorflow as tf

                self._model = tf.keras.models.load_model(str(model_path))
                return True
            except Exception as e:
                print(f"Model load error: {e}")

        self._model = None
        return False

    def _heuristic_predict(self, image_array: np.ndarray) -> Tuple[str, float, List[Dict]]:
        """Fallback prediction using green pixel analysis when model unavailable."""
        mean = image_array.mean(axis=(0, 1))
        green_ratio = mean[1] / (mean.sum() + 1e-6)
        brownish = mean[0] > mean[1] and mean[2] < mean[1]

        if green_ratio > 0.38 and not brownish:
            label = "Tomato___healthy"
            conf = 0.72 + green_ratio * 0.15
        elif brownish and mean[0] > 100:
            label = "Tomato___Early_blight"
            conf = 0.68
        elif mean[2] > mean[1]:
            label = "Tomato___Late_blight"
            conf = 0.65
        else:
            label = "Potato___Early_blight"
            conf = 0.61

        conf = min(conf, 0.95)
        top = [{"label": label, "confidence": round(conf * 100, 2)}]
        for c in self._class_labels:
            if c != label:
                top.append({"label": c, "confidence": round(np.random.uniform(1, 15), 2)})
        top = sorted(top, key=lambda x: x["confidence"], reverse=True)[:5]
        return label, conf, top

    def predict(self, image_path: str, output_dir: str) -> dict:
        self.load_model()

        pipeline_result = run_preprocessing_pipeline(
            image_path, output_dir=output_dir, save_intermediate=True
        )
        processed = pipeline_result["processed_image"]
        img = processed.astype(np.float32) / 255.0
        batch = np.expand_dims(img, axis=0)

        if self._model is not None:
            # MobileNetV2 expects preprocess_input scaling (RGB in [0, 255])
            try:
                from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

                batch = preprocess_input(batch * 255.0)
            except ImportError:
                batch = (batch - 0.5) * 2.0

            preds = self._model.predict(batch, verbose=0)[0]
            idx = int(np.argmax(preds))
            confidence = float(preds[idx])
            label = self._class_labels[idx] if idx < len(self._class_labels) else DEFAULT_CLASSES[0]
            top_predictions = [
                {
                    "label": self._class_labels[i]
                    if i < len(self._class_labels)
                    else f"class_{i}",
                    "confidence": round(float(preds[i]) * 100, 2),
                }
                for i in np.argsort(preds)[::-1][:5]
            ]
        else:
            label, confidence, top_predictions = self._heuristic_predict(processed)

        info = disease_service.format_response(label, confidence)
        info["preprocessing_steps"] = pipeline_result.get("step_names", [])
        info["processed_image_path"] = pipeline_result.get("processed_path")
        info["top_predictions"] = top_predictions
        info["model_loaded"] = self._model is not None
        return info


predictor_service = PredictorService()
