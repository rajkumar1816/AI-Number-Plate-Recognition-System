import streamlit as st
from pathlib import Path

from config.settings import AppSettings
from database.db import insert_vehicle_record, is_plate_blacklisted
from detector.detector import YOLODetector
from preprocessing.video_processor import process_video_file
from utils.logger import setup_logger

logger = setup_logger()


def video_detection_page(settings: AppSettings) -> None:
    st.markdown('<div class="page-card"><div class="page-title">Video Detection</div><div class="section-subtitle">Upload a video to process plate detection across frames.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-card">', unsafe_allow_html=True)

    uploaded_video = st.file_uploader("Choose a video", type=["mp4", "mov", "avi"])
    if uploaded_video is None:
        st.info("Upload a video file to start detection.")
        return

    video_path = Path("storage") / "videos" / uploaded_video.name
    with open(video_path, "wb") as file_handle:
        file_handle.write(uploaded_video.read())

    st.success("Video uploaded successfully.")
    detector = YOLODetector(settings.MODEL_NAME)
    if st.button("Start Video Detection"):
        with st.spinner("Processing video frames..."):
            results = process_video_file(video_path, detector, settings.CONFIDENCE_THRESHOLD)
            if not results:
                st.warning("No plates detected in the first frames.")
                return

            st.markdown("### Detection Summary")
            for item in results:
                blacklisted = is_plate_blacklisted(settings.DATABASE_PATH, item['plate_number'])
                st.write(
                    f"Frame {item['frame_index']}: {item['plate_number']} "
                    f"(Confidence: {item['confidence']:.2f}, Valid: {item['valid_plate']})"
                    + (" — BLACKLISTED" if blacklisted else "")
                )
                if item['valid_plate']:
                    insert_vehicle_record(
                        settings.DATABASE_PATH,
                        video_path.name,
                        item['plate_number'],
                        item['confidence'],
                        str(video_path),
                        item['crop_path'],
                    )
                if blacklisted:
                    st.error("Blacklisted vehicle detected in video!")
