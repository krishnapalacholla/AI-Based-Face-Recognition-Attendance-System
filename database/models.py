"""
models.py

Data models for the Face Recognition Attendance System.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ==================================================
# ATTENDANCE RECORD
# ==================================================

@dataclass
class AttendanceRecord:
    """
    Represents a single attendance record
    stored in the database.
    """

    id: Optional[int]
    name: str
    date: str
    time: str

    # --------------------------------------------------
    # CLASS METHOD — FROM ROW
    # --------------------------------------------------

    @classmethod
    def from_row(cls, row) -> "AttendanceRecord":
        """
        Create an AttendanceRecord from a
        sqlite3.Row or tuple.
        """
        if hasattr(row, "keys"):
            return cls(
                id=row["id"],
                name=row["name"],
                date=row["date"],
                time=row["time"],
            )
        return cls(
            id=row[0],
            name=row[1],
            date=row[2],
            time=row[3],
        )

    # --------------------------------------------------
    # TO DICT
    # --------------------------------------------------

    def to_dict(self) -> dict:
        """Return record as a dictionary."""
        return {
            "id":   self.id,
            "name": self.name,
            "date": self.date,
            "time": self.time,
        }

    # --------------------------------------------------
    # TO TUPLE
    # --------------------------------------------------

    def to_tuple(self) -> tuple:
        """Return record as a tuple."""
        return (
            self.id,
            self.name,
            self.date,
            self.time,
        )

    # --------------------------------------------------
    # DATETIME OBJECT
    # --------------------------------------------------

    def get_datetime(self) -> Optional[datetime]:
        """Return a datetime object for this record."""
        try:
            return datetime.strptime(
                f"{self.date} {self.time}",
                "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            return None

    def __str__(self) -> str:
        return (
            f"AttendanceRecord("
            f"id={self.id}, "
            f"name={self.name!r}, "
            f"date={self.date!r}, "
            f"time={self.time!r})"
        )


# ==================================================
# ADMIN USER
# ==================================================

@dataclass
class AdminUser:
    """
    Represents an administrator account.
    """

    id: Optional[int]
    username: str
    password_hash: str
    created_at: str = field(default="")

    @classmethod
    def from_row(cls, row) -> "AdminUser":
        """Create an AdminUser from a sqlite3.Row."""
        if hasattr(row, "keys"):
            return cls(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                created_at=row.get("created_at", ""),
            )
        return cls(
            id=row[0],
            username=row[1],
            password_hash=row[2],
            created_at=row[3] if len(row) > 3 else "",
        )

    def __str__(self) -> str:
        return (
            f"AdminUser("
            f"id={self.id}, "
            f"username={self.username!r})"
        )
