from typing import List

from database.db import fetch_history_records
from config.settings import AppSettings


def search_by_plate(settings: AppSettings, query: str) -> List[dict]:
    return fetch_history_records(settings.DATABASE_PATH, plate_query=query)
