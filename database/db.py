import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.constants import DATA_DIR
from utils.helpers import ensure_directories
from utils.logger import setup_logger

logger = setup_logger()

SCHEMA_FILE = Path(__file__).resolve().parent / "schema.sql"


def get_connection(database_path: Path) -> sqlite3.Connection:
    ensure_directories()
    return sqlite3.connect(database_path)


def initialize_database(database_path: Path) -> None:
    ensure_directories()
    if not database_path.parent.exists():
        database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection(database_path)
    try:
        with open(SCHEMA_FILE, "r", encoding="utf-8") as file_handle:
            schema_sql = file_handle.read()
        connection.executescript(schema_sql)
        connection.commit()
    finally:
        connection.close()


def fetch_dashboard_metrics(database_path: Path) -> Dict[str, Any]:
    metrics = {
        "total_scans": 0,
        "todays_scans": 0,
        "average_confidence": 0.0,
        "most_detected_vehicle": "N/A",
        "recent_activity": [],
    }

    query_total = "SELECT COUNT(1) FROM vehicle_records"
    query_today = "SELECT COUNT(1) FROM vehicle_records WHERE date = ?"
    query_average = "SELECT AVG(confidence) FROM vehicle_records"
    query_top_plate = "SELECT plate_number, COUNT(1) AS count FROM vehicle_records GROUP BY plate_number ORDER BY count DESC LIMIT 1"
    query_recent = "SELECT date, time, plate_number, confidence FROM vehicle_records ORDER BY id DESC LIMIT 5"

    today_value = datetime.now().strftime("%Y-%m-%d")

    connection = get_connection(database_path)
    try:
        cursor = connection.cursor()
        cursor.execute(query_total)
        metrics["total_scans"] = cursor.fetchone()[0] or 0

        cursor.execute(query_today, (today_value,))
        metrics["todays_scans"] = cursor.fetchone()[0] or 0

        cursor.execute(query_average)
        average_confidence = cursor.fetchone()[0]
        metrics["average_confidence"] = float(average_confidence or 0.0)

        cursor.execute(query_top_plate)
        top_row = cursor.fetchone()
        if top_row:
            metrics["most_detected_vehicle"] = top_row[0]

        cursor.execute(query_recent)
        rows = cursor.fetchall()
        metrics["recent_activity"] = [
            {
                "date": row[0],
                "time": row[1],
                "plate_number": row[2],
                "confidence": float(row[3]) if row[3] is not None else 0.0,
            }
            for row in rows
        ]
    finally:
        connection.close()

    return metrics


def insert_vehicle_record(
    database_path: Path,
    image_name: str,
    plate_number: str,
    confidence: float,
    image_path: str,
    cropped_path: str,
) -> Optional[int]:
    insert_sql = (
        "INSERT INTO vehicle_records (image_name, plate_number, confidence, date, time, image_path, cropped_path) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)"
    )
    now = datetime.now()
    date_value = now.strftime("%Y-%m-%d")
    time_value = now.strftime("%H:%M:%S")

    connection = get_connection(database_path)
    try:
        cursor = connection.cursor()
        cursor.execute(
            insert_sql,
            (
                image_name,
                plate_number,
                confidence,
                date_value,
                time_value,
                image_path,
                cropped_path,
            ),
        )
        connection.commit()
        return cursor.lastrowid
    except sqlite3.Error as error:
        logger.error("Failed to insert vehicle record: %s", error)
        return None
    finally:
        connection.close()


def fetch_history_records(
    database_path: Path,
    plate_query: str = "",
    date_filter: str | None = None,
) -> List[Dict[str, Any]]:
    query = (
        "SELECT id, image_name, plate_number, confidence, date, time, image_path, cropped_path "
        "FROM vehicle_records WHERE 1=1"
    )
    params: list[object] = []

    if plate_query:
        query += " AND plate_number LIKE ?"
        params.append(f"%{plate_query}%")

    if date_filter:
        query += " AND date = ?"
        params.append(date_filter)

    query += " ORDER BY id DESC"

    connection = get_connection(database_path)
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "image_name": row[1],
                "plate_number": row[2],
                "confidence": float(row[3]) if row[3] is not None else 0.0,
                "date": row[4],
                "time": row[5],
                "image_path": row[6],
                "cropped_path": row[7],
            }
            for row in rows
        ]
    finally:
        connection.close()


def delete_vehicle_record(database_path: Path, record_id: int) -> bool:
    delete_sql = "DELETE FROM vehicle_records WHERE id = ?"
    connection = get_connection(database_path)
    try:
        cursor = connection.cursor()
        cursor.execute(delete_sql, (record_id,))
        connection.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        return False
    finally:
        connection.close()


def add_blacklist_plate(database_path: Path, plate_number: str) -> bool:
    insert_sql = (
        "INSERT OR IGNORE INTO blacklist_vehicles (plate_number, added_at) VALUES (?, ?)"
    )
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    connection = get_connection(database_path)
    try:
        cursor = connection.cursor()
        cursor.execute(insert_sql, (plate_number, now))
        connection.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        return False
    finally:
        connection.close()


def fetch_blacklist(database_path: Path) -> List[Dict[str, Any]]:
    query = "SELECT id, plate_number, added_at FROM blacklist_vehicles ORDER BY id DESC"
    connection = get_connection(database_path)
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [
            {"id": row[0], "plate_number": row[1], "added_at": row[2]} for row in rows
        ]
    finally:
        connection.close()


def remove_blacklist_plate(database_path: Path, record_id: int) -> bool:
    delete_sql = "DELETE FROM blacklist_vehicles WHERE id = ?"
    connection = get_connection(database_path)
    try:
        cursor = connection.cursor()
        cursor.execute(delete_sql, (record_id,))
        connection.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        return False
    finally:
        connection.close()


def is_plate_blacklisted(database_path: Path, plate_number: str) -> bool:
    query = "SELECT 1 FROM blacklist_vehicles WHERE plate_number = ? LIMIT 1"
    connection = get_connection(database_path)
    try:
        cursor = connection.cursor()
        cursor.execute(query, (plate_number,))
        return cursor.fetchone() is not None
    finally:
        connection.close()
