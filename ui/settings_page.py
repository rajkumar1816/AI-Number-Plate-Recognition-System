import streamlit as st


def settings_page(settings) -> None:
    st.markdown('<div class="page-card"><div class="page-title">Settings</div><div class="section-subtitle">Adjust model and scan configuration.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-card">', unsafe_allow_html=True)
    st.slider("Confidence threshold", min_value=0.0, max_value=1.0, value=float(settings.CONFIDENCE_THRESHOLD), step=0.05)
    st.checkbox("Auto-save detection records", value=True)
