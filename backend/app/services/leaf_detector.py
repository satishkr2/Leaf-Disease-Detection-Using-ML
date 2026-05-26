"""Leaf vs non-leaf binary classifier — runs before disease prediction."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

import cv2
import numpy as np

from app.config import get_settings

settings = get_settings()

LEAF_LABEL = "leaf"
NON_LEAF_LABEL = "non_leaf"
DEFAULT_LABELS = [LEAF_LABEL, NON_LEAF_LABEL]


class LeafDetectorService:
    _instance = None
    _model = None
    _labels: list = DEFAULT_LABELS

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self) -> bool:
        if self._model is not None:
            return True

        model_path = Path(settings.leaf_detector_path)
        labels_path = Path(settings.leaf_detector_labels_path)

        if labels_path.exists():
            with open(labels_path, encoding="utf-8") as f:
                self._labels = json.load(f)

        if model_path.exists():
            try:
                import tensorflow as tf

                self._model = tf.keras.models.load_model(str(model_path))
                return True
            except Exception as exc:
                print(f"Leaf detector load error: {exc}")

        self._model = None
        return False

    def _read_image(self, image_path: str) -> np.ndarray:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        return image

    def _heuristic_check(self, image: np.ndarray) -> Tuple[bool, float, str]:
        """
        OpenCV heuristic when ML model is unavailable.
        Estimates green leaf-like area and color distribution.
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([25, 35, 35])
        upper = np.array([90, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        green_ratio = float(np.count_nonzero(mask)) / (mask.size + 1e-6)
        h_mean = float(hsv[:, :, 0].mean())
        s_mean = float(hsv[:, :, 1].mean())

        # Strong green coverage → likely leaf
        score = green_ratio * 0.7 + (1.0 if 30 <= h_mean <= 85 else 0.3) * 0.2
        score += min(s_mean / 255.0, 1.0) * 0.1
        score = min(score, 0.98)

        is_leaf = green_ratio >= 0.08 and score >= 0.45 and 25 <= h_mean <= 95
        return is_leaf, score if is_leaf else 1.0 - score, "heuristic"

    def _model_check(self, image: np.ndarray) -> Tuple[bool, float, str]:
        import tensorflow as tf
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

        resized = cv2.resize(image, (224, 224))
        batch = np.expand_dims(resized.astype(np.float32), axis=0)
        batch = preprocess_input(batch)

        preds = self._model.predict(batch, verbose=0)[0]
        leaf_idx = self._labels.index(LEAF_LABEL) if LEAF_LABEL in self._labels else 0
        leaf_prob = float(preds[leaf_idx])
        is_leaf = leaf_prob >= settings.leaf_detector_threshold
        return is_leaf, leaf_prob if is_leaf else 1.0 - leaf_prob, "model"

    def check_image(self, image_path: str) -> Dict:
        """
        Returns dict with is_leaf, confidence (0-100), label, method.
        """
        self.load_model()
        image = self._read_image(image_path)

        if self._model is not None:
            is_leaf, confidence, method = self._model_check(image)
        else:
            is_leaf, confidence, method = self._heuristic_check(image)

        label = LEAF_LABEL if is_leaf else NON_LEAF_LABEL
        return {
            "is_leaf": is_leaf,
            "label": label,
            "confidence": round(confidence * 100, 2),
            "method": method,
            "model_loaded": self._model is not None,
        }


leaf_detector_service = LeafDetectorService()
