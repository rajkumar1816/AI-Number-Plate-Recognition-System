import csv
from pathlib import Path
from typing import List, Dict


def export_records_to_csv(records: List[Dict[str, object]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "image_name",
        "plate_number",
        "confidence",
        "date",
        "time",
        "image_path",
        "cropped_path",
    ]

    with open(output_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record)

    return output_path
