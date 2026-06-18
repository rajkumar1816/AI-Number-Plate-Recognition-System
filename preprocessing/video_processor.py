import cv2
from pathlib import Path
from typing import List, Optional

from detector.detector import YOLODetector
from ocr.ocr_engine import read_plate_text
from ocr.text_cleaner import normalize_plate_text, validate_plate_text
from utils.helpers import save_frame_image


def process_video_file(
    video_path: Path,
    detector: YOLODetector,
    confidence_threshold: float,
    max_frames: int = 100,
) -> List[dict]:
    capture = cv2.VideoCapture(str(video_path))
    results: List[dict] = []
    frame_index = 0

    while capture.isOpened() and frame_index < max_frames:
        success, frame = capture.read()
        if not success:
            break

        frame_path = save_frame_image(frame, prefix=f"video_frame_{frame_index}")
        detections = detector.detect_plate(frame_path, conf_threshold=confidence_threshold)
        if detections:
            best_detection = detections[0]
            crop_path = detector.crop_plate(
                frame_path,
                best_detection["bbox"],
                Path("storage") / "crops" / f"video_crop_{frame_index}.jpg",
            )
            if crop_path is not None:
                ocr_results = read_plate_text(str(crop_path))
                if ocr_results:
                    best_result = max(ocr_results, key=lambda item: item["confidence"])
                    cleaned_text = normalize_plate_text(best_result["text"])
                    valid_plate, normalized_text = validate_plate_text(cleaned_text)
                    results.append(
                        {
                            "frame_index": frame_index,
                            "plate_number": normalized_text,
                            "confidence": best_result["confidence"],
                            "valid_plate": valid_plate,
                            "frame_path": str(frame_path),
                            "crop_path": str(crop_path),
                        }
                    )
        frame_index += 1

    capture.release()
    return results
