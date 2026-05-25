"""Disease information lookup service."""
import json
from pathlib import Path


class DiseaseInfoService:
    def __init__(self):
        info_path = (
            Path(__file__).resolve().parents[3] / "model" / "data" / "disease_info.json"
        )
        with open(info_path, encoding="utf-8") as f:
            self._data = json.load(f)

    def get_info(self, class_label: str) -> dict:
        key = class_label.replace(" ", "_")
        if key in self._data:
            return self._data[key]
        for k, v in self._data.items():
            if k != "default" and k.lower() in class_label.lower():
                return v
        return self._data["default"]

    def format_response(self, class_label: str, confidence: float) -> dict:
        info = self.get_info(class_label)
        return {
            "disease_name": info.get("display_name", class_label.replace("___", " ")),
            "confidence": round(confidence * 100, 2),
            "description": info["description"],
            "symptoms": info["symptoms"],
            "causes": info["causes"],
            "prevention": info["prevention"],
            "prescription": info["prescription"],
            "class_label": class_label,
        }


disease_service = DiseaseInfoService()
