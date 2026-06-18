from pathlib import Path
from typing import Dict, List

import pandas as pd

from database.db import get_connection


def load_history_dataframe(database_path: Path) -> pd.DataFrame:
    connection = get_connection(database_path)
    try:
        query = "SELECT date, plate_number, confidence FROM vehicle_records"
        return pd.read_sql_query(query, connection)
    finally:
        connection.close()


def get_daily_scan_counts(database_path: Path) -> pd.DataFrame:
    df = load_history_dataframe(database_path)
    if df.empty:
        return pd.DataFrame(columns=["date", "count"])

    daily = (
        df.groupby("date")
        .size()
        .reset_index(name="count")
        .sort_values("date")
    )
    return daily


def get_monthly_scan_counts(database_path: Path) -> pd.DataFrame:
    df = load_history_dataframe(database_path)
    if df.empty:
        return pd.DataFrame(columns=["month", "count"])

    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    monthly = (
        df.groupby("month")
        .size()
        .reset_index(name="count")
        .sort_values("month")
    )
    return monthly


def get_top_vehicles(database_path: Path, top_n: int = 10) -> pd.DataFrame:
    df = load_history_dataframe(database_path)
    if df.empty:
        return pd.DataFrame(columns=["plate_number", "count"])

    top = (
        df.groupby("plate_number")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(top_n)
    )
    return top


def get_accuracy_trends(database_path: Path) -> pd.DataFrame:
    df = load_history_dataframe(database_path)
    if df.empty:
        return pd.DataFrame(columns=["date", "average_confidence"])

    trends = (
        df.groupby("date")["confidence"]
        .mean()
        .reset_index(name="average_confidence")
        .sort_values("date")
    )
    return trends
