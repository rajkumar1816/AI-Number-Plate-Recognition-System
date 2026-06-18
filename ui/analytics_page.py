import streamlit as st

from analytics.analytics import (
    get_accuracy_trends,
    get_daily_scan_counts,
    get_monthly_scan_counts,
    get_top_vehicles,
)
from analytics.charts import plot_bar_chart, plot_line_chart


def analytics_page(settings) -> None:
    st.markdown('<div class="page-card"><div class="page-title">Analytics</div><div class="section-subtitle">Scan trends and performance overview.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-card">', unsafe_allow_html=True)

    with st.expander("Daily scans"):
        daily = get_daily_scan_counts(settings.DATABASE_PATH)
        if daily.empty:
            st.info("No scan data yet.")
        else:
            st.pyplot(plot_bar_chart(daily, "date", "count", "Daily Scan Count"))

    with st.expander("Monthly scans"):
        monthly = get_monthly_scan_counts(settings.DATABASE_PATH)
        if monthly.empty:
            st.info("No monthly scan data available.")
        else:
            st.pyplot(plot_bar_chart(monthly, "month", "count", "Monthly Scan Count"))

    with st.expander("Top vehicles"):
        top = get_top_vehicles(settings.DATABASE_PATH)
        if top.empty:
            st.info("No registered vehicles yet.")
        else:
            st.pyplot(plot_bar_chart(top, "plate_number", "count", "Top Detected Vehicles"))

    with st.expander("Accuracy trends"):
        trends = get_accuracy_trends(settings.DATABASE_PATH)
        if trends.empty:
            st.info("No confidence trend data available.")
        else:
            st.pyplot(plot_line_chart(trends, "date", "average_confidence", "Average Confidence Trend"))
