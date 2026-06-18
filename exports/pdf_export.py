from pathlib import Path
from typing import List, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def export_records_to_pdf(records: List[Dict[str, object]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [Paragraph("ANPR Scan Report", styles["Title"]), Spacer(1, 12)]

    if not records:
        elements.append(Paragraph("No records available.", styles["Normal"]))
    else:
        data = [
            [
                "ID",
                "Image",
                "Plate",
                "Confidence",
                "Date",
                "Time",
                "Image Path",
                "Crop Path",
            ]
        ]
        for record in records:
            data.append([
                record.get("id", ""),
                record.get("image_name", ""),
                record.get("plate_number", ""),
                f"{record.get('confidence', 0.0):.2f}",
                record.get("date", ""),
                record.get("time", ""),
                record.get("image_path", ""),
                record.get("cropped_path", ""),
            ])

        table = Table(data, repeatRows=1, hAlign="LEFT")
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ])
        )
        elements.append(table)

    document.build(elements)
    return output_path
