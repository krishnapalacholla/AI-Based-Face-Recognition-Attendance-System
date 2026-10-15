"""
excel_manager.py

Handles Excel export of attendance records,
separated from AttendanceManager for clean architecture.
"""

from datetime import datetime
from pathlib import Path
from typing import List

from openpyxl import Workbook
from openpyxl.styles import (
    Font,
    Alignment,
    PatternFill,
    Border,
    Side,
)
from openpyxl.utils import get_column_letter


EXPORT_FOLDER = Path("attendance_exports")


class ExcelManager:
    """
    Exports attendance records to a styled Excel file.
    """

    # --------------------------------------------------
    # THEME COLOURS
    # --------------------------------------------------

    HEADER_FILL  = "1E3A5F"   # deep navy
    HEADER_FONT  = "FFFFFF"   # white
    ROW_EVEN     = "EEF4FB"   # light blue-grey
    ROW_ODD      = "FFFFFF"   # white
    ACCENT       = "2563EB"   # primary blue

    # --------------------------------------------------
    # EXPORT
    # --------------------------------------------------

    def export(self, records: List[tuple]) -> str:
        """
        Export records to a styled .xlsx file.

        Args:
            records: list of (id, name, date, time) tuples

        Returns:
            Absolute path string of the saved file,
            or empty string on failure.
        """
        if not records:
            print("No attendance records to export.")
            return ""

        EXPORT_FOLDER.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name  = f"attendance_{timestamp}.xlsx"
        output_path = EXPORT_FOLDER / file_name

        workbook  = Workbook()
        worksheet = workbook.active
        worksheet.title = "Attendance"

        # --------------------------------------------------
        # HEADER ROW
        # --------------------------------------------------

        headers = ["ID", "Name", "Date", "Time"]
        worksheet.append(headers)

        header_font = Font(
            name="Calibri",
            bold=True,
            color=self.HEADER_FONT,
            size=12,
        )
        header_fill = PatternFill(
            fill_type="solid",
            fgColor=self.HEADER_FILL,
        )
        header_align = Alignment(
            horizontal="center",
            vertical="center",
        )
        thin = Side(border_style="thin", color="CCCCCC")
        border = Border(
            left=thin,
            right=thin,
            top=thin,
            bottom=thin,
        )

        for cell in worksheet[1]:
            cell.font      = header_font
            cell.fill      = header_fill
            cell.alignment = header_align
            cell.border    = border

        worksheet.row_dimensions[1].height = 30

        # --------------------------------------------------
        # DATA ROWS
        # --------------------------------------------------

        for row_num, record in enumerate(records, start=2):
            worksheet.append(list(record))

            fill_color = (
                self.ROW_EVEN
                if row_num % 2 == 0
                else self.ROW_ODD
            )
            row_fill = PatternFill(
                fill_type="solid",
                fgColor=fill_color,
            )
            data_font  = Font(name="Calibri", size=11)
            data_align = Alignment(
                horizontal="center",
                vertical="center",
            )

            for cell in worksheet[row_num]:
                cell.fill      = row_fill
                cell.font      = data_font
                cell.alignment = data_align
                cell.border    = border

            worksheet.row_dimensions[row_num].height = 22

        # --------------------------------------------------
        # COLUMN WIDTHS
        # --------------------------------------------------

        col_widths = [10, 28, 18, 16]
        for idx, width in enumerate(col_widths, start=1):
            worksheet.column_dimensions[
                get_column_letter(idx)
            ].width = width

        # --------------------------------------------------
        # FREEZE HEADER
        # --------------------------------------------------

        worksheet.freeze_panes = "A2"

        # --------------------------------------------------
        # AUTO-FILTER
        # --------------------------------------------------

        worksheet.auto_filter.ref = (
            f"A1:D{len(records) + 1}"
        )

        # --------------------------------------------------
        # SUMMARY SHEET
        # --------------------------------------------------

        summary_sheet = workbook.create_sheet("Summary")
        self._build_summary_sheet(summary_sheet, records)

        # --------------------------------------------------
        # SAVE
        # --------------------------------------------------

        workbook.save(str(output_path))

        print(f"Attendance exported to: {output_path}")
        return str(output_path)

    # --------------------------------------------------
    # SUMMARY SHEET
    # --------------------------------------------------

    def _build_summary_sheet(
        self,
        ws,
        records: List[tuple]
    ):
        """Build a per-user attendance summary sheet."""

        # Count per user
        user_counts: dict = {}
        for record in records:
            name = record[1]
            user_counts[name] = user_counts.get(name, 0) + 1

        ws.append(["Name", "Total Days Present"])

        header_font = Font(bold=True, size=12)
        for cell in ws[1]:
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        for user, count in sorted(user_counts.items()):
            ws.append([user, count])

        ws.column_dimensions["A"].width = 28
        ws.column_dimensions["B"].width = 22
