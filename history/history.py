from typing import List

from config.settings import AppSettings
from database.db import fetch_history_records


def get_scan_history(settings: AppSettings, plate_query: str = "", date_filter: str | None = None) -> List[dict]:
    return fetch_history_records(settings.DATABASE_PATH, plate_query, date_filter)
