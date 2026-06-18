import re
from config.constants import VALID_PLATE_PATTERN


def clean_plate_text(raw_text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]", "", raw_text).upper()
    return cleaned


def is_valid_plate(plate_text: str) -> bool:
    return bool(re.match(VALID_PLATE_PATTERN, plate_text))
