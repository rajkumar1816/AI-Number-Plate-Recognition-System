from pathlib import Path
from typing import Any, Dict, List, Union

import cv2
import easyocr
import numpy as np


def read_plate_text(image_source: Union[str, Path, np.ndarray], languages: List[str] = ["en"]) -> List[Dict[str, Any]]:
    reader = easyocr.Reader(languages, gpu=False)

    if isinstance(image_source, (str, Path)):
        image = cv2.imread(str(image_source))
    else:
        image = image_source

    if image is None:
        return []

    if isinstance(image, np.ndarray) and image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif isinstance(image, np.ndarray) and image.ndim == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)

    try:
        results = reader.readtext(image, detail=1, paragraph=False)
    except Exception:
        return []

    return [
        {
            "bbox": result[0],
            "text": result[1],
            "confidence": float(result[2]),
        }
        for result in results
    ]
