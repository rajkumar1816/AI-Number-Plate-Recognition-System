import streamlit as st
from datetime import date
from pathlib import Path
from typing import Optional

from database.db import delete_vehicle_record, fetch_history_records
from exports.csv_export import export_records_to_csv
from exports.pdf_export import export_records_to_pdf
from config.settings import AppSettings


def history_page(settings: AppSettings) -> None:
    st.markdown('<div class="page-card"><div class="page-title">History</div><div class="section-subtitle">Search or export saved scan records.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-card">', unsafe_allow_html=True)

    plate_query = st.text_input("Plate number")
    date_filter = st.date_input("Date filter", value=date.today())
    show_all = st.checkbox("Show all records", value=False)

    filter_date = None if show_all else date_filter.strftime("%Y-%m-%d")
    records = fetch_history_records(settings.DATABASE_PATH, plate_query.strip(), filter_date)

    st.markdown("---")
    if not records:
        st.info("No history records found.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    if records:
        export_csv_path = Path("storage") / "reports" / "vehicle_history.csv"
        export_pdf_path = Path("storage") / "reports" / "vehicle_history.pdf"

        col_action_csv, col_action_pdf = st.columns([1, 1])
        with col_action_csv:
            if st.button("Export CSV"):
                output_path = export_records_to_csv(records, export_csv_path)
                st.success(f"Exported history to {output_path}")
        with col_action_pdf:
            if st.button("Export PDF"):
                output_path = export_records_to_pdf(records, export_pdf_path)
                st.success(f"Exported history to {output_path}")

        st.markdown('</div>', unsafe_allow_html=True)

        for record in records:
            container = st.container()
            with container:
                cols = st.columns([2, 2, 1, 1, 1])
                cols[0].write(f"**{record['plate_number']}**")
                cols[1].write(f"{record['date']} {record['time']}")
                cols[2].write(f"Confidence: {record['confidence']:.2f}")
                cols[3].write(record['image_name'])
                if cols[4].button("Delete", key=f"delete_{record['id']}"):
                    if delete_vehicle_record(settings.DATABASE_PATH, record['id']):
                        st.success(f"Deleted record {record['id']}.")
                        st.experimental_rerun()
                    else:
                        st.error("Unable to delete record.")
    else:
        st.info("No history records found.")
        st.markdown('</div>', unsafe_allow_html=True)
