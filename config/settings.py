import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

@dataclass
class AppSettings:
    APP_NAME: str
    CONFIDENCE_THRESHOLD: float
    DATABASE_PATH: Path
    MODEL_NAME: str


def load_settings() -> AppSettings:
    return AppSettings(
        APP_NAME=os.getenv("APP_NAME", "AI Number Plate Recognition System"),
        CONFIDENCE_THRESHOLD=float(os.getenv("CONFIDENCE_THRESHOLD", 0.3)),
        DATABASE_PATH=BASE_DIR / os.getenv("DATABASE_PATH", "data/vehicle_records.db"),
        MODEL_NAME=os.getenv("MODEL_NAME", "yolov8n.pt"),
    )
