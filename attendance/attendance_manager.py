import sqlite3
from datetime import datetime
from pathlib import Path


class AttendanceManager:
    """
    Manage attendance records using SQLite.
    """

    def __init__(self):

        # -------------------------
        # Database Folder
        # -------------------------
        database_folder = Path("database")

        database_folder.mkdir(
            exist_ok=True
        )

        # -------------------------
        # Database Path
        # -------------------------
        self.database_path = (
            database_folder
            / "attendance.db"
        )

        # -------------------------
        # Create Table
        # -------------------------
        self.create_table()

    # --------------------------------------------------
    # DATABASE CONNECTION
    # --------------------------------------------------

    def get_connection(self):
        """
        Return SQLite database connection.
        """

        return sqlite3.connect(
            self.database_path
        )

    # --------------------------------------------------
    # CREATE TABLE
    # --------------------------------------------------

    def create_table(self):
        """
        Create attendance table.
        """

        connection = self.get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL
            )
            """
        )

        connection.commit()

        connection.close()

        print(
            "Attendance database initialized."
        )

    # --------------------------------------------------
    # CHECK ATTENDANCE
    # --------------------------------------------------

    def is_attendance_marked(
        self,
        name,
        date
    ):
        """
        Check whether attendance is already marked.
        """

        connection = self.get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM attendance
            WHERE name = ?
            AND date = ?
            """,
            (
                name,
                date
            )
        )

        record = cursor.fetchone()

        connection.close()

        return record is not None

    # --------------------------------------------------
    # MARK ATTENDANCE
    # --------------------------------------------------

    def mark_attendance(self, name):
        """
        Mark attendance for recognized user.
        """

        if name == "Unknown":

            return False

        # -------------------------
        # Current Date And Time
        # -------------------------
        current_datetime = datetime.now()

        current_date = (
            current_datetime.strftime(
                "%Y-%m-%d"
            )
        )

        current_time = (
            current_datetime.strftime(
                "%H:%M:%S"
            )
        )

        # -------------------------
        # Duplicate Check
        # -------------------------
        if self.is_attendance_marked(
            name,
            current_date
        ):

            print(
                f"Attendance already marked "
                f"for {name} today."
            )

            return False

        # -------------------------
        # Insert Record
        # -------------------------
        connection = self.get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO attendance (
                name,
                date,
                time
            )
            VALUES (?, ?, ?)
            """,
            (
                name,
                current_date,
                current_time
            )
        )

        connection.commit()

        connection.close()

        print(
            f"Attendance marked successfully: "
            f"{name} | "
            f"{current_date} | "
            f"{current_time}"
        )

        return True

    # --------------------------------------------------
    # GET ATTENDANCE RECORDS
    # --------------------------------------------------

    def get_attendance_records(self):
        """
        Return all attendance records.
        """

        connection = self.get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                name,
                date,
                time
            FROM attendance
            ORDER BY date DESC, time DESC
            """
        )

        records = cursor.fetchall()

        connection.close()

        return records

    # --------------------------------------------------
    # VIEW ATTENDANCE
    # --------------------------------------------------

    def view_attendance(self):
        """
        Display attendance records.
        """

        records = (
            self.get_attendance_records()
        )

        print("\n")
        print("=" * 65)
        print("ATTENDANCE RECORDS")
        print("=" * 65)

        if len(records) == 0:

            print(
                "No attendance records found."
            )

            print("=" * 65)

            return

        print(
            f"{'ID':<8}"
            f"{'NAME':<20}"
            f"{'DATE':<20}"
            f"{'TIME':<15}"
        )

        print("-" * 65)

        for record in records:

            record_id = record[0]
            name = record[1]
            date = record[2]
            time = record[3]

            print(
                f"{record_id:<8}"
                f"{name:<20}"
                f"{date:<20}"
                f"{time:<15}"
            )

        print("=" * 65)

        print(
            f"Total Attendance Records: "
            f"{len(records)}"
        )

    # --------------------------------------------------
    # EXPORT ATTENDANCE TO EXCEL
    # --------------------------------------------------

    def export_to_excel(self):
        """
        Export attendance records to a styled Excel file.
        Delegates to ExcelManager.
        """
        records = self.get_attendance_records()

        if not records:
            print("No attendance records available for export.")
            return False

        from attendance.excel_manager import ExcelManager
        path = ExcelManager().export(records)
        return bool(path)