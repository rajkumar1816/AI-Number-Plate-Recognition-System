import time
from pathlib import Path
from typing import Optional

import cv2
import streamlit as st
from PIL import Image

from config.settings import AppSettings
from database.db import insert_vehicle_record, is_plate_blacklisted
from detector.detector import YOLODetector
from ocr.ocr_engine import read_plate_text
from ocr.text_cleaner import normalize_plate_text, validate_plate_text
from preprocessing.image_processor import preprocess_image
from utils.helpers import save_frame_image
from utils.logger import setup_logger

logger = setup_logger()


def process_webcam_frame(
    settings: AppSettings,
    frame: object,
    detector: YOLODetector,
) -> Optional[dict]:
    image_path = save_frame_image(frame, prefix="webcam")
    detections = detector.detect_plate(image_path, conf_threshold=settings.CONFIDENCE_THRESHOLD)
    if not detections:
        return None

    best_detection = detections[0]
    bbox = best_detection["bbox"]
    crop_path = detector.crop_plate(
        image_path,
        bbox,
        Path("storage") / "crops" / f"webcam_crop_{time.time_ns()}.jpg",
    )
    if crop_path is None:
        return None

    preprocess_image(crop_path)
    ocr_results = read_plate_text(str(crop_path))
    if not ocr_results:
        return None

    best_result = max(ocr_results, key=lambda item: item["confidence"])
    cleaned_text = normalize_plate_text(best_result["text"])
    valid_plate, normalized_text = validate_plate_text(cleaned_text)

    insert_vehicle_record(
        settings.DATABASE_PATH,
        image_name=image_path.name,
        plate_number=normalized_text,
        confidence=best_result["confidence"],
        image_path=str(image_path),
        cropped_path=str(crop_path),
    )

    return {
        "image_path": image_path,
        "crop_path": crop_path,
        "raw_text": best_result["text"],
        "normalized_plate": normalized_text,
        "confidence": best_result["confidence"],
        "valid_plate": valid_plate,
    }


def live_camera_page(settings: AppSettings) -> None:
    st.markdown('<div class="page-card"><div class="page-title">Live Camera</div><div class="section-subtitle">Real-time webcam detection with automatic save.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-card">', unsafe_allow_html=True)

    if "camera_running" not in st.session_state:
        st.session_state.camera_running = False

    detector = YOLODetector(settings.MODEL_NAME)

    if st.button("Start Webcam"):
        st.session_state.camera_running = True
    if st.button("Stop Webcam"):
        st.session_state.camera_running = False

    frame_placeholder = st.empty()
    status_placeholder = st.empty()
    result_placeholder = st.empty()

    if st.session_state.camera_running:
        status_placeholder.info("Webcam running... Press Stop Webcam to end session.")
        capture = cv2.VideoCapture(0)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not capture.isOpened():
            status_placeholder.error("Unable to access the webcam.")
            st.session_state.camera_running = False
            return

        last_detection_time = 0.0
        detection_interval = 3.0

        try:
            while st.session_state.camera_running:
                ret, frame = capture.read()
                if not ret:
                    status_placeholder.error("Failed to read webcam frame.")
                    logger.error("Webcam frame read failed")
                    break

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(rgb_frame, caption="Live webcam feed", use_column_width=True)

                current_time = time.time()
                if current_time - last_detection_time >= detection_interval:
                    last_detection_time = current_time
                    result = process_webcam_frame(settings, frame, detector)

                    if result:
                        result_placeholder.markdown("### Detected Plate")
                        result_placeholder.write(f"**Plate:** {result['normalized_plate']}")
                        result_placeholder.write(f"**Confidence:** {result['confidence']:.2f}")
                        result_placeholder.write(f"**Valid:** {result['valid_plate']}")
                        if is_plate_blacklisted(settings.DATABASE_PATH, result['normalized_plate']):
                            result_placeholder.error("Blacklisted vehicle detected on live feed!")
                        result_placeholder.image(Image.open(result["crop_path"]), caption="Detected crop", use_column_width=False)
                    else:
                        result_placeholder.info("No plate detected in the latest sampled frame.")

                time.sleep(0.5)
        finally:
            capture.release()
            st.session_state.camera_running = False
            status_placeholder.warning("Webcam session ended.")
    else:
        status_placeholder.info("Press Start Webcam to begin live detection.")
