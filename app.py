import streamlit as st

from config.settings import AppSettings, load_settings
from database.db import initialize_database
from ui.analytics_page import analytics_page
from ui.blacklist_page import blacklist_page
from ui.dashboard import dashboard_page
from ui.history_page import history_page
from ui.live_camera_page import live_camera_page
from ui.upload_page import upload_page
from ui.video_detection_page import video_detection_page
from ui.settings_page import settings_page


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp, .css-18e3th9, .css-1d391kg, .stAppViewContainer, .main {
            background: linear-gradient(180deg, #FBF7FF 0%, #F3E8FF 60%, #E9D5FF 100%);
            color: #1f2937;
        }
        .stSidebar, .stSidebar .css-1d391kg {
            background: rgba(245, 238, 255, 0.95);
            border-right: 1px solid rgba(167, 139, 250, 0.14);
        }
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(135deg, #C4B5FD 0%, #A78BFA 100%);
            color: #1f1f1f;
            border: none;
            box-shadow: 0 8px 20px rgba(167, 139, 250, 0.18);
        }
        .stButton>button:hover, .stDownloadButton>button:hover {
            opacity: 0.98;
            transform: translateY(-1px);
        }
        .stTextInput>div>div>input, .stSelectbox>div>div>div>div, .stFileUploader>div>div {
            background: #ffffff;
            color: #1f2937;
            border: 1px solid rgba(167, 139, 250, 0.15);
            border-radius: 12px;
        }
        .stMarkdown, .stCaption, .stText, .stHeader, .stSubheader, .stCheckbox, .stRadio {
            color: #1f2937;
        }
        .page-card, .page-card-small {
            border-radius: 16px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid rgba(167, 139, 250, 0.12);
            box-shadow: 0 12px 40px rgba(167, 139, 250, 0.06);
            margin-bottom: 20px;
        }
        .page-title {
            font-size: 2.0rem;
            font-weight: 700;
            margin-bottom: 6px;
            color: #3f3f46;
        }
        .section-subtitle {
            color: #6b7280;
            margin-top: 0;
            margin-bottom: 16px;
        }
        .metric-card {
            border-radius: 12px;
            padding: 16px;
            background: linear-gradient(180deg, #ffffff, #fbf7ff);
            color: #111827;
            border: 1px solid rgba(167, 139, 250, 0.10);
            min-height: 110px;
        }
        .metric-label {
            color: #6b7280;
            margin-bottom: 6px;
            display: block;
            font-size: 0.9rem;
        }
        .metric-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #111827;
        }
        .status-pill {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 0.9rem;
            background: rgba(167, 139, 250, 0.12);
            color: #6d28d9;
            margin-top: 10px;
        }
        .stFileUploader { border-radius: 12px; }
        .stApp, .stAppViewContainer, .main, .block-container { position: relative; z-index: 1; }
        .bg-photo { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
        .bg-photo .layer { position: absolute; inset: 0; background-size: cover; background-position: center; opacity: 0.48; filter: saturate(1.05) blur(6px); transform-origin: center; }
        .bg-photo .p1 { background-image: url('https://images.unsplash.com/photo-1505755592928-22b4e5f1d7a7?q=80&w=1400&auto=format&fit=crop'); transform: scale(1.05); opacity: 0.42; }
        .bg-photo .p2 { background-image: url('https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1400&auto=format&fit=crop'); mix-blend-mode: screen; opacity: 0.28; filter: blur(10px) saturate(1.02); }
        .bg-photo .p3 { background-image: url('https://images.unsplash.com/photo-1496307042754-b4aa456c4a2d?q=80&w=1400&auto=format&fit=crop'); right: -10%; bottom: -10%; width: 120%; height: 120%; opacity: 0.20; filter: blur(18px) saturate(1.05); }
        .bg-photo .layer { will-change: transform; }
        @keyframes photoFloatA { 0% { transform: translateY(0) scale(1);} 50% { transform: translateY(-14px) scale(1.01);} 100% { transform: translateY(0) scale(1);} }
        @keyframes photoFloatB { 0% { transform: translateY(0) scale(1);} 50% { transform: translateY(-6px) scale(1.005);} 100% { transform: translateY(0) scale(1);} }
        .bg-photo .p1 { animation: photoFloatA 28s ease-in-out infinite; }
        .bg-photo .p2 { animation: photoFloatB 36s ease-in-out infinite; }
        .bg-photo .p3 { animation: photoFloatA 44s ease-in-out infinite; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="bg-photo" aria-hidden="true">
            <div class="layer p1"></div>
            <div class="layer p2"></div>
            <div class="layer p3"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


PAGE_ROUTES = {
    "Dashboard": dashboard_page,
    "Upload Image": upload_page,
    "History": history_page,
    "Analytics": analytics_page,
    "Blacklist": blacklist_page,
    "Video Detection": video_detection_page,
    "Live Camera": live_camera_page,
    "Settings": settings_page,
}


def main() -> None:
    settings: AppSettings = load_settings()
    st.set_page_config(
        page_title=settings.APP_NAME,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    initialize_database(settings.DATABASE_PATH)
    apply_theme()

    st.sidebar.title(settings.APP_NAME)
    st.sidebar.markdown("<div style='padding: 0 0 12px 0; color: #94a3b8;'>AI-powered license plate detection with history, analytics, blacklist, and video support.</div>", unsafe_allow_html=True)
    page: str = st.sidebar.selectbox("Navigation", list(PAGE_ROUTES.keys()))
    PAGE_ROUTES[page](settings)


if __name__ == "__main__":
    main()