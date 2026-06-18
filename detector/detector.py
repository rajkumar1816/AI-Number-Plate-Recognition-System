import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
from ultralytics import YOLO

from config.constants import CROP_STORAGE
from utils.logger import setup_logger
from utils.helpers import ensure_directories

logger = setup_logger()


class YOLODetector:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.model_path = self._resolve_model_path(model_name)
        self.model = self._load_model()

    def _resolve_model_path(self, model_name: str) -> Path:
        path = Path(model_name)
        if not path.is_absolute():
            path = Path(__file__).resolve().parent.parent / model_name
        if path.exists():
            return path

        # If the configured model is the default generic YOLOv8n, try local trained weights.
        if path.name == "yolov8n.pt":
            candidate_dir = Path(__file__).resolve().parent.parent / "runs" / "detect"
            local_weights = sorted(
                candidate_dir.rglob("best.pt"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if local_weights:
                selected = local_weights[0]
                logger.warning(
                    "Default YOLO model not found or generic; switching to local trained weights %s",
                    selected,
                )
                return selected

        return path

    def _load_model(self) -> Optional[YOLO]:
        try:
            return YOLO(str(self.model_path))
        except Exception as error:
            logger.exception("Failed to load YOLO model %s", self.model_name)
            return None

    def detect_plate(
        self,
        image_path: Union[str, Path],
        conf_threshold: float = 0.3,
    ) -> List[Dict[str, Any]]:
        if self.model is None:
            logger.warning("YOLO model is not available. Skipping detection.")
            return []

        image_path = str(image_path)
        raw_results = self.model(image_path, imgsz=640, conf=conf_threshold, verbose=False)
        detections: List[Dict[str, Any]] = []

        if not raw_results:
            return detections

        result = raw_results[0]
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return detections

        for box in boxes:
            xyxy = box.xyxy[0].cpu().numpy().tolist()
            x1, y1, x2, y2 = [int(max(0, coordinate)) for coordinate in xyxy]
            confidence = float(box.conf[0].cpu().numpy())
            class_id = int(box.cls[0].cpu().numpy()) if box.cls is not None else None
            detections.append(
                {
                    "bbox": (x1, y1, x2, y2),
                    "confidence": confidence,
                    "class_id": class_id,
                }
            )

        detections.sort(key=lambda item: item["confidence"], reverse=True)
        return detections

    def crop_plate(
        self,
        image_path: Union[str, Path],
        bbox: Tuple[int, int, int, int],
        output_name: Optional[str] = None,
    ) -> Optional[Path]:
        image_path = str(image_path)
        image = cv2.imread(image_path)
        if image is None:
            logger.error("Unable to read image for cropping: %s", image_path)
            return None

        x1, y1, x2, y2 = bbox
        crop_region = image[y1:y2, x1:x2]
        ensure_directories()
        if output_name is None:
            output_name = f"plate_crop_{Path(image_path).stem}.jpg"
        output_path = Path(output_name)
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), crop_region)
        return output_path

    def annotate_plate(
        self,
        image_path: Union[str, Path],
        bbox: Tuple[int, int, int, int],
        label: str,
        output_path: Union[str, Path],
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 3,
    ) -> Optional[Path]:
        image_path = str(image_path)
        image = cv2.imread(image_path)
        if image is None:
            logger.error("Unable to read image for annotation: %s", image_path)
            return None

        x1, y1, x2, y2 = bbox
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        text_thickness = 2
        text_size, baseline = cv2.getTextSize(label, font, font_scale, text_thickness)
        text_width, text_height = text_size

        text_offset_x = x1
        text_offset_y = y1 - 10
        if text_offset_y - text_height - baseline < 0:
            text_offset_y = y1 + text_height + baseline + 10

        cv2.rectangle(
            image,
            (text_offset_x, text_offset_y - text_height - baseline),
            (text_offset_x + text_width + 10, text_offset_y + baseline),
            color,
            cv2.FILLED,
        )
        cv2.putText(
            image,
            label,
            (text_offset_x + 5, text_offset_y),
            font,
            font_scale,
            (255, 255, 255),
            text_thickness,
            cv2.LINE_AA,
        )

        output_path = Path(output_path)
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), image)
        return output_path

    def fallback_detect_plate(self, image_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        A simple OpenCV contour-based fallback to find rectangular regions
        that resemble a license plate. Returns a list of detections with
        a guessed confidence so the pipeline can continue.
        """
        image_path = str(image_path)
        image = cv2.imread(image_path)
        if image is None:
            return []

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Edge-preserving blur and adaptive threshold
        blurred = cv2.bilateralFilter(gray, 9, 75, 75)
        edged = cv2.Canny(blurred, 50, 200)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates: List[tuple[int, tuple[int, int, int, int]]] = []

        h_img, w_img = gray.shape[:2]
        for cnt in contours:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.06 * peri, True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect = w / float(h) if h > 0 else 0
                area = w * h
                # Heuristic filters for plate-like rectangles
                if 2.0 < aspect < 6.5 and area > (w_img * h_img) * 0.001:
                    score = float(min(1.0, aspect / 6.5 + (area / (w_img * h_img))))
                    candidates.append((int(score * 100), (x, y, x + w, y + h)))

        if not candidates:
            return []

        # pick highest score
        candidates.sort(key=lambda t: t[0], reverse=True)
        best = candidates[0]
        conf = best[0] / 100.0
        x1, y1, x2, y2 = best[1]
        return [{"bbox": (x1, y1, x2, y2), "confidence": conf, "class_id": 0}]
