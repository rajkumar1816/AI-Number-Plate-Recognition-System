import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Union

import cv2
from PIL import Image
from config.constants import IMAGE_STORAGE, VIDEO_STORAGE, CROP_STORAGE, DATA_DIR

INDIAN_STATE_MAPPING = {
    "TS": "Telangana",
    "AP": "Andhra Pradesh",
    "KA": "Karnataka",
    "TN": "Tamil Nadu",
    "MH": "Maharashtra",
    "DL": "Delhi",
    "KL": "Kerala",
    "WB": "West Bengal",
    "OD": "Odisha",
    "GJ": "Gujarat",
    "RJ": "Rajasthan",
    "UP": "Uttar Pradesh",
    "PB": "Punjab",
    "HR": "Haryana",
    "CH": "Chandigarh",
    "JK": "Jammu and Kashmir",
}


def ensure_directories() -> None:
    for directory in [IMAGE_STORAGE, VIDEO_STORAGE, CROP_STORAGE, DATA_DIR]:
        os.makedirs(directory, exist_ok=True)


def save_uploaded_image(uploaded_file: Union[bytes, object]) -> Path:
    ensure_directories()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = Path(getattr(uploaded_file, "name", "uploaded_image")).stem
    extension = Path(getattr(uploaded_file, "name", "uploaded_image.jpg")).suffix or ".jpg"
    output_path = IMAGE_STORAGE / f"{filename}_{timestamp}{extension}"

    image_bytes = uploaded_file.read() if hasattr(uploaded_file, "read") else uploaded_file
    with open(output_path, "wb") as file_pointer:
        file_pointer.write(image_bytes)

    try:
        Image.open(output_path).verify()
    except Exception as error:
        raise ValueError("Invalid image file") from error

    return output_path


def save_frame_image(frame: object, prefix: str = "webcam") -> Path:
    ensure_directories()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = IMAGE_STORAGE / f"{prefix}_{timestamp}.jpg"
    cv2.imwrite(str(output_path), frame)
    return output_path


def get_plate_information(plate_text: str) -> Dict[str, str]:
    cleaned = re.sub(r"[^A-Z0-9]", "", plate_text.upper() if plate_text else "")
    state_code = cleaned[:2] if len(cleaned) >= 2 else ""
    region_code = cleaned[2:4] if len(cleaned) >= 4 else ""

    state = INDIAN_STATE_MAPPING.get(state_code, "Unknown")
    country = "India" if state_code in INDIAN_STATE_MAPPING else "Unknown"
    district = f"RTO Zone {region_code}" if region_code.isdigit() and region_code else "Unknown"

    return {
        "country": country,
        "state": state,
        "state_code": state_code,
        "district": district,
    }


def save_uploaded_image(uploaded_file: Union[bytes, object]) -> Path:
    ensure_directories()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = Path(getattr(uploaded_file, "name", "uploaded_image")).stem
    extension = Path(getattr(uploaded_file, "name", "uploaded_image.jpg")).suffix or ".jpg"
    output_path = IMAGE_STORAGE / f"{filename}_{timestamp}{extension}"

    image_bytes = uploaded_file.read() if hasattr(uploaded_file, "read") else uploaded_file
    with open(output_path, "wb") as file_pointer:
        file_pointer.write(image_bytes)

    try:
        Image.open(output_path).verify()
    except Exception as error:
        raise ValueError("Invalid image file") from error

    return output_path


def save_frame_image(frame: object, prefix: str = "webcam") -> Path:
    ensure_directories()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = IMAGE_STORAGE / f"{prefix}_{timestamp}.jpg"
    cv2.imwrite(str(output_path), frame)
    return output_path
