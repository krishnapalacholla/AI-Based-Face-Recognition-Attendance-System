"""
pdf_manager.py

Exports attendance records to a styled PDF file
using the ReportLab library.
"""

from datetime import datetime
from pathlib import Path
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)


EXPORT_FOLDER = Path("attendance_exports")

# Colour palette (matches dashboard theme)
NAVY   = colors.HexColor("#07111F")
BLUE   = colors.HexColor("#2563EB")
LIGHT  = colors.HexColor("#EEF4FB")
WHITE  = colors.white
GREY   = colors.HexColor("#94A3B8")
BLACK  = colors.HexColor("#0F172A")


class PdfManager:
    """
    Exports attendance records to a clean,
    branded PDF report.
    """

    def export(self, records: List[tuple]) -> str:
        """
        Generate a PDF from the given records.

        Args:
            records: list of (id, name, date, time) tuples

        Returns:
            Absolute path to the saved PDF, or "" on failure.
        """
        if not records:
            return ""

        EXPORT_FOLDER.mkdir(exist_ok=True)

        timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name   = f"attendance_{timestamp}.pdf"
        output_path = EXPORT_FOLDER / file_name

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles  = getSampleStyleSheet()
        story   = []

        # ---- Title ----
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Title"],
            fontSize=20,
            textColor=BLUE,
            spaceAfter=4,
        )
        story.append(Paragraph("Vision Attendance", title_style))

        sub_style = ParagraphStyle(
            "Sub",
            parent=styles["Normal"],
            fontSize=11,
            textColor=GREY,
            spaceAfter=16,
        )
        generated = datetime.now().strftime("%d %B %Y  %H:%M:%S")
        story.append(Paragraph(f"AI Face Recognition Attendance Report  ·  Generated: {generated}", sub_style))
        story.append(Spacer(1, 0.4 * cm))

        # ---- Summary ----
        total_records = len(records)
        unique_users  = len({r[1] for r in records})

        summary_data = [
            ["Total Records", str(total_records)],
            ["Unique Users",  str(unique_users)],
            ["Generated",     generated],
        ]
        summary_table = Table(summary_data, colWidths=[5 * cm, 10 * cm])
        summary_table.setStyle(TableStyle([
            ("FONTNAME",   (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE",   (0, 0), (-1, -1), 10),
            ("TEXTCOLOR",  (0, 0), (0, -1), GREY),
            ("TEXTCOLOR",  (1, 0), (1, -1), BLACK),
            ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT, WHITE]),
            ("BOX",        (0, 0), (-1, -1), 0.5, GREY),
            ("INNERGRID",  (0, 0), (-1, -1), 0.25, GREY),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.6 * cm))

        # ---- Attendance table ----
        header = ["ID", "Name", "Date", "Time"]
        table_data = [header] + [list(r) for r in records]

        col_widths = [1.5 * cm, 6 * cm, 4.5 * cm, 4 * cm]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)

        table.setStyle(TableStyle([
            # Header
            ("BACKGROUND",   (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR",    (0, 0), (-1, 0), WHITE),
            ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, 0), 11),
            ("ALIGN",        (0, 0), (-1, 0), "CENTER"),
            ("TOPPADDING",   (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING",(0, 0), (-1, 0), 10),

            # Data rows
            ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",     (0, 1), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
            ("TEXTCOLOR",    (0, 1), (-1, -1), BLACK),
            ("ALIGN",        (0, 1), (-1, -1), "CENTER"),
            ("ALIGN",        (1, 1), (1, -1), "LEFT"),
            ("TOPPADDING",   (0, 1), (-1, -1), 7),
            ("BOTTOMPADDING",(0, 1), (-1, -1), 7),
            ("LEFTPADDING",  (0, 0), (-1, -1), 8),

            # Border
            ("BOX",          (0, 0), (-1, -1), 0.75, GREY),
            ("INNERGRID",    (0, 0), (-1, -1), 0.25, GREY),
        ]))

        story.append(table)

        # ---- Build ----
        doc.build(story)

        print(f"PDF exported to: {output_path}")
        return str(output_path)
