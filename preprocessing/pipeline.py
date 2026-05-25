"""
OpenCV image preprocessing pipeline for plant leaf disease detection.
Steps: resize, denoise, background cleaning, color normalization, edge detection, segmentation.
"""
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import cv2
import numpy as np


def resize_image(image: np.ndarray, size: tuple[int, int] = (224, 224)) -> np.ndarray:
    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)


def reduce_noise(image: np.ndarray) -> np.ndarray:
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)


def clean_background(image: np.ndarray) -> np.ndarray:
    """Remove light background using adaptive thresholding mask."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, _, _ = cv2.split(lab)
    blurred = cv2.GaussianBlur(l_channel, (5, 5), 0)
    _, mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask_inv = cv2.bitwise_not(mask)
    kernel = np.ones((3, 3), np.uint8)
    mask_inv = cv2.morphologyEx(mask_inv, cv2.MORPH_CLOSE, kernel, iterations=2)
    result = cv2.bitwise_and(image, image, mask=mask_inv)
    result[mask_inv == 0] = [0, 0, 0]
    return result


def normalize_color(image: np.ndarray) -> np.ndarray:
    """CLAHE on L channel in LAB color space."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    merged = cv2.merge([l, a, b])
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


def detect_edges(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def segment_leaf(image: np.ndarray) -> np.ndarray:
    """HSV green mask segmentation for leaf region."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([25, 40, 40])
    upper_green = np.array([90, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    segmented = cv2.bitwise_and(image, image, mask=mask)
    if np.count_nonzero(mask) < 100:
        return image
    return segmented


def run_preprocessing_pipeline(
    image_path: Union[str, Path],
    output_dir: Union[str, Path, None] = None,
    save_intermediate: bool = True,
) -> Dict[str, Any]:
    """
    Run full preprocessing pipeline and optionally save step images.
    Returns processed image array, paths, and step names.
    """
    image_path = Path(image_path)
    output_dir = Path(output_dir) if output_dir else image_path.parent / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    steps = [
        ("original", image),
        ("resized", resize_image(image.copy(), (256, 256))),
        ("denoised", None),
        ("background_cleaned", None),
        ("color_normalized", None),
        ("edges", None),
        ("segmented", None),
        ("final", None),
    ]

    working = image.copy()
    working = resize_image(working, (256, 256))
    steps[1] = ("resized", working.copy())

    denoised = reduce_noise(working)
    steps[2] = ("denoised", denoised.copy())
    working = denoised

    bg_clean = clean_background(working)
    steps[3] = ("background_cleaned", bg_clean.copy())
    working = bg_clean

    normalized = normalize_color(working)
    steps[4] = ("color_normalized", normalized.copy())
    working = normalized

    edges = detect_edges(working)
    steps[5] = ("edges", edges.copy())

    segmented = segment_leaf(working)
    steps[6] = ("segmented", segmented.copy())
    working = segmented

    final = resize_image(working, (224, 224))
    steps[7] = ("final", final.copy())

    step_paths: List[str] = []
    step_names: List[str] = []

    if save_intermediate:
        stem = image_path.stem
        for name, img in steps:
            if img is not None:
                out_path = output_dir / f"{stem}_{name}.jpg"
                cv2.imwrite(str(out_path), img)
                step_paths.append(str(out_path))
                step_names.append(name.replace("_", " ").title())

    return {
        "processed_image": final,
        "processed_path": step_paths[-1] if step_paths else None,
        "step_paths": step_paths,
        "step_names": step_names,
        "steps": [s[0] for s in steps if s[1] is not None],
    }
