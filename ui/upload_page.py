import streamlit as st
from pathlib import Path
from PIL import Image

from config.settings import AppSettings
from database.db import insert_vehicle_record, is_plate_blacklisted
from detector.detector import YOLODetector
from ocr.ocr_engine import read_plate_text
from ocr.text_cleaner import normalize_plate_text, validate_plate_text, combine_ocr_segments
from preprocessing.image_processor import preprocess_image
from utils.helpers import get_plate_information, save_uploaded_image
from utils.logger import setup_logger

logger = setup_logger()


def upload_page(settings: AppSettings) -> None:
    st.markdown('<div class="page-card"><div class="page-title">Upload Image</div><div class="section-subtitle">Upload a vehicle photo and detect the license plate.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-card">', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        try:
            saved_path = save_uploaded_image(uploaded_file)
            image = Image.open(saved_path)
            st.image(image, caption="Uploaded image", width=720)
            st.success("Image uploaded successfully.")

            detector = YOLODetector(settings.MODEL_NAME)

            if detector.model is None:
                st.warning(
                    "YOLO model could not be loaded. "
                    "Check that `MODEL_NAME` in `.env` points to a valid model file such as `yolov8n.pt`."
                )
                st.stop()

            st.success(f"YOLO model loaded: {detector.model_path.name}")

            if st.button("Detect Number Plate"):
                logger.info("Starting upload detection for %s", saved_path)
                with st.spinner("Running YOLO detection..."):
                    detections = detector.detect_plate(saved_path, conf_threshold=settings.CONFIDENCE_THRESHOLD)
                    fallback_used = False
                    if not detections:
                        # Try OpenCV contour-based fallback
                        fallback = detector.fallback_detect_plate(saved_path)
                        if fallback:
                            detections = fallback
                            fallback_used = True
                        else:
                            st.error("No number plates detected in the image.")
                            if settings.MODEL_NAME == "yolov8n.pt":
                                st.info(
                                    "The app is currently using the default generic YOLOv8 model. "
                                    "For better plate detection, set `MODEL_NAME=runs/detect/plates_10epochs/weights/best.pt` "
                                    "in your `.env` file and restart the app."
                                )
                            else:
                                st.info(
                                    "Try uploading a clearer image with a visible license plate, "
                                    "or use a custom model trained for license plate detection."
                                )
                            return

                    best_detection = detections[0]
                    bbox = best_detection["bbox"]
                    crop_name = Path(saved_path).stem + "_plate_crop.jpg"
                    crop_path = detector.crop_plate(
                        saved_path,
                        bbox,
                        Path("storage") / "crops" / crop_name,
                    )

                    if crop_path is None:
                        st.error("Failed to crop the detected plate.")
                        return

                    if fallback_used:
                        st.info("YOLO returned no detections; used OpenCV fallback to localize plate.")

                    preprocess_image(crop_path)
                    ocr_results = read_plate_text(str(crop_path))
                    if not ocr_results:
                        st.error("OCR failed on the cropped plate. Try a clearer image.")
                        return

                    # Try to combine segmented OCR results into a full plate first
                    combined_text = combine_ocr_segments(ocr_results)
                    cleaned_text = normalize_plate_text(combined_text)
                    valid_plate, normalized_text = validate_plate_text(cleaned_text)
                    confidence_score = max(item.get("confidence", 0.0) for item in ocr_results) * 100

                    # If combining didn't yield a valid plate, fall back to the single best OCR result
                    if not valid_plate:
                        best_result = max(ocr_results, key=lambda item: item["confidence"])
                        raw_text = best_result["text"]
                        cleaned_text = normalize_plate_text(raw_text)
                        valid_plate, normalized_text = validate_plate_text(cleaned_text)
                        confidence_score = best_result["confidence"] * 100

                    info = get_plate_information(normalized_text)
                    annotated_name = Path(saved_path).stem + "_annotated.jpg"
                    annotated_path = detector.annotate_plate(
                        saved_path,
                        bbox,
                        f"{normalized_text} ({confidence_score:.0f}%)",
                        Path("storage") / "images" / annotated_name,
                    )

                    record_id = insert_vehicle_record(
                        settings.DATABASE_PATH,
                        image_name=Path(saved_path).name,
                        plate_number=normalized_text,
                        confidence=confidence_score,
                        image_path=str(saved_path),
                        cropped_path=str(crop_path),
                    )

                    st.markdown("### Detection Result")
                    st.image(Image.open(saved_path), caption="Original Image", width=720)
                    if annotated_path is not None:
                        st.image(Image.open(annotated_path), caption="Detected Image with Bounding Box", width=720)
                    st.image(Image.open(crop_path), caption="Cropped Number Plate", use_column_width=False)

                    st.markdown("### Plate Information")
                    st.write(f"**Vehicle Number:** {normalized_text}")
                    st.write(f"**Country:** {info['country']}")
                    st.write(f"**State:** {info['state']}")
                    st.write(f"**State Code:** {info['state_code']}")
                    st.write(f"**District:** {info['district']}")
                    st.write(f"**Confidence:** {confidence_score:.1f}%")

                    if record_id is not None:
                        st.success("Scan saved to history.")
                        logger.info("Saved scan record id=%s plate=%s", record_id, normalized_text)
                    else:
                        st.warning("Unable to save scan history.")
                        logger.warning("Failed to save scan for plate=%s", normalized_text)

                    if is_plate_blacklisted(settings.DATABASE_PATH, normalized_text):
                        st.error("Blacklisted vehicle detected! Immediate attention required.")
                        logger.warning("Blacklisted plate detected: %s", normalized_text)

                    if valid_plate:
                        st.success("Detected number plate is valid.")
                    else:
                        st.warning("Detected text is not a valid Indian number plate.")
            st.markdown('</div>', unsafe_allow_html=True)
        except ValueError as error:
            st.error(str(error))
        except Exception:
            st.error("Unable to process the uploaded image. Please try a different file.")
