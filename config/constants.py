from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
IMAGE_STORAGE = STORAGE_DIR / "images"
VIDEO_STORAGE = STORAGE_DIR / "videos"
CROP_STORAGE = STORAGE_DIR / "crops"
LOG_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
DATABASE_FILE = DATA_DIR / "vehicle_records.db"

VALID_PLATE_PATTERN = r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$"
