"""PDF report generation for predictions."""
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_prediction_pdf(prediction: dict, username: str = "Guest") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=22,
        textColor=colors.HexColor("#166534"),
        spaceAfter=12,
    )
    story = []

    story.append(Paragraph("Plant Leaf Disease Detection Report", title_style))
    story.append(
        Paragraph(
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} | User: {username}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.3 * inch))

    data = [
        ["Field", "Details"],
        ["Disease", prediction.get("disease_name", "N/A")],
        ["Confidence", f"{prediction.get('confidence', 0)}%"],
        ["Description", prediction.get("description", "")[:200]],
        ["Symptoms", prediction.get("symptoms", "")[:200]],
        ["Causes", prediction.get("causes", "")[:200]],
        ["Prevention", prediction.get("prevention", "")[:200]],
        ["Treatment", prediction.get("prescription", "")[:200]],
    ]

    table = Table(data, colWidths=[1.5 * inch, 4.5 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#166534")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f0fdf4")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            "<i>Disclaimer: This report is AI-generated for educational purposes. "
            "Consult local agricultural experts before applying treatments.</i>",
            styles["Italic"],
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
