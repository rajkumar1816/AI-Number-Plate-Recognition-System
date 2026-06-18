import re
from typing import Tuple, List, Dict

from config.constants import VALID_PLATE_PATTERN


def normalize_plate_text(raw_text: str) -> str:
    if raw_text is None:
        return ""
    cleaned = re.sub(r"[^A-Za-z0-9]", "", raw_text).upper()
    return cleaned


def validate_plate_text(cleaned_text: str) -> Tuple[bool, str]:
    cleaned = normalize_plate_text(cleaned_text)
    corrected = correct_plate_ocr_text(cleaned)
    is_valid = bool(re.match(VALID_PLATE_PATTERN, corrected))
    return is_valid, corrected


def correct_plate_ocr_text(cleaned_text: str) -> str:
    """Correct common OCR misreads in plate text before validation."""
    if not cleaned_text:
        return ""

    # Correct characters based on their expected position in Indian plate format.
    # Format: XXNNXXNNNN or XXNNNXXNNNN for extended series.
    mapping_letters = {
        "0": "O",
        "1": "I",
        "2": "Z",
        "5": "S",
        "8": "B",
    }
    mapping_digits = {
        "O": "0",
        "Q": "0",
        "D": "0",
        "B": "8",
        "S": "5",
        "Z": "2",
        "G": "6",
        "I": "1",
        "L": "1",
        "T": "1",
        "A": "4",
    }

    length = len(cleaned_text)
    if length not in {10, 11}:
        return cleaned_text

    if length == 10:
        letter_positions = {0, 1, 4, 5}
        digit_positions = {2, 3, 6, 7, 8, 9}
    else:
        letter_positions = {0, 1, 4, 5, 6}
        digit_positions = {2, 3, 7, 8, 9, 10}

    corrected_chars: List[str] = []
    for idx, ch in enumerate(cleaned_text):
        if idx in letter_positions and ch.isdigit():
            corrected_chars.append(mapping_letters.get(ch, ch))
        elif idx in digit_positions and ch.isalpha():
            corrected_chars.append(mapping_digits.get(ch, ch))
        else:
            corrected_chars.append(ch)

    return "".join(corrected_chars)


def combine_ocr_segments(results: List[Dict]) -> str:
    """Combine multiple OCR segments into a single candidate string.

    The function sorts detected text segments by their horizontal position (centroid x)
    and concatenates them (removing internal spaces) to form a single plate candidate.
    This helps when EasyOCR returns plate parts separately (e.g. 'KA 01', 'AB', '1234').
    """
    entries: List[Tuple[float, float, str]] = []
    for res in results:
        bbox = res.get("bbox")
        xs: List[float] = []
        ys: List[float] = []
        # bbox can be a list of 4 points [[x,y], ...] or a flat [x1,y1,x2,y2]
        if isinstance(bbox, (list, tuple)) and len(bbox) > 0:
            # point-list format
            if all(isinstance(pt, (list, tuple)) and len(pt) >= 2 for pt in bbox):
                xs = [float(pt[0]) for pt in bbox]
                ys = [float(pt[1]) for pt in bbox]
            # flat xyxy format
            elif len(bbox) == 4 and all(isinstance(v, (int, float)) for v in bbox):
                xs = [float(bbox[0]), float(bbox[2])]
                ys = [float(bbox[1]), float(bbox[3])]

        cx = sum(xs) / len(xs) if xs else 0.0
        cy = sum(ys) / len(ys) if ys else 0.0
        text = str(res.get("text", ""))
        entries.append((cy, cx, text))

    # sort primarily by vertical position (top to bottom), then left to right
    entries.sort(key=lambda t: (t[0], t[1]))
    combined = "".join([t.replace(" ", "") for _, _, t in entries])
    return combined
