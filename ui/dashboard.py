import streamlit as st

from database.db import fetch_dashboard_metrics


def dashboard_page(settings) -> None:
    st.markdown('<div class="page-card"><div class="page-title">Dashboard</div><div class="section-subtitle">Business metrics and recent activity</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="page-card">', unsafe_allow_html=True)

    metrics = fetch_dashboard_metrics(settings.DATABASE_PATH)
    total_scans = metrics["total_scans"]
    todays_scans = metrics["todays_scans"]
    avg_confidence = metrics["average_confidence"] * 100.0
    most_detected = metrics["most_detected_vehicle"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><span class="metric-label">Total scans</span><div class="metric-value">{total_scans}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><span class="metric-label">Today\'s scans</span><div class="metric-value">{todays_scans}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><span class="metric-label">Average confidence</span><div class="metric-value">{avg_confidence:.1f}%</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><span class="metric-label">Most detected vehicle</span><div class="metric-value">{most_detected}</div></div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="page-card"><div class="section-subtitle">Recent activity</div>', unsafe_allow_html=True)

    if metrics["recent_activity"]:
        for item in metrics["recent_activity"]:
            st.write(
                f"{item['date']} {item['time']} — Plate: {item['plate_number']} — Confidence: {item['confidence']:.2f}"
            )
    else:
        st.info("No scan history available yet.")
    st.markdown('</div>', unsafe_allow_html=True)
