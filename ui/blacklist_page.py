import streamlit as st
from typing import Optional

from config.settings import AppSettings
from database.db import (
    add_blacklist_plate,
    fetch_blacklist,
    remove_blacklist_plate,
)
from ocr.text_cleaner import normalize_plate_text, validate_plate_text


def blacklist_page(settings: AppSettings) -> None:
    st.markdown('<div class="page-card"><div class="page-title">Blacklist</div><div class="section-subtitle">Manage suspicious vehicles and alerts.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-card">', unsafe_allow_html=True)

    new_plate = st.text_input("Blacklist plate number")
    if st.button("Add to blacklist"):
        cleaned_text = normalize_plate_text(new_plate)
        valid_plate, normalized_plate = validate_plate_text(cleaned_text)
        if not valid_plate:
            st.error("Enter a valid Indian number plate (e.g. MH12DE1433).")
        else:
            if add_blacklist_plate(settings.DATABASE_PATH, normalized_plate):
                st.success(f"Added {normalized_plate} to blacklist.")
            else:
                st.warning(f"{normalized_plate} is already blacklisted or could not be added.")

    st.markdown("---")
    st.subheader("Current blacklist")
    blacklist_items = fetch_blacklist(settings.DATABASE_PATH)
    if not blacklist_items:
        st.info("No blacklisted vehicles yet.")
        return

    for item in blacklist_items:
        cols = st.columns([3, 2, 1])
        cols[0].write(f"**{item['plate_number']}**")
        cols[1].write(item["added_at"])
        if cols[2].button("Remove", key=f"remove_{item['id']}"):
            if remove_blacklist_plate(settings.DATABASE_PATH, item["id"]):
                st.success(f"Removed {item['plate_number']} from blacklist.")
                st.experimental_rerun()
            else:
                st.error("Failed to remove the blacklist entry.")
