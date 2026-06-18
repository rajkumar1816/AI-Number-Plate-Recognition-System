import cv2
from pathlib import Path
from typing import Optional


def preprocess_image(image_path: Path, output_path: Optional[Path] = None) -> Path:
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Cannot open image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)
    enhanced = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2,
    )

    if output_path is None:
        output_path = image_path

    cv2.imwrite(str(output_path), enhanced)
    return output_path
