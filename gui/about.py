"""
about.py

About window for the Face Recognition
Attendance System.
"""

import customtkinter as ctk


APP_BG  = "#07111F"
CARD_BG = "#101E33"
BORDER  = "#22324A"
TEXT    = "#F8FAFC"
MUTED   = "#94A3B8"
PRIMARY = "#2563EB"
ACCENT  = "#0EA5E9"


class AboutWindow(ctk.CTkToplevel):
    """
    Modal About window displaying app info,
    tech stack, and version.
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.title("About — Vision Attendance")
        self.geometry("480x580")
        self.resizable(False, False)
        self.configure(fg_color=APP_BG)
        self.grab_set()
        self.focus_force()

        self.grid_columnconfigure(0, weight=1)

        # ------------------------------------------------
        # LOGO / TITLE BLOCK
        # ------------------------------------------------

        logo_frame = ctk.CTkFrame(
            self,
            fg_color=CARD_BG,
            corner_radius=0,
        )
        logo_frame.grid(row=0, column=0, sticky="ew")
        logo_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            logo_frame,
            text="◉",
            font=ctk.CTkFont(size=52),
            text_color=PRIMARY,
        ).grid(row=0, column=0, pady=(32, 4))

        ctk.CTkLabel(
            logo_frame,
            text="VISION ATTENDANCE",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT,
        ).grid(row=1, column=0, pady=(0, 4))

        ctk.CTkLabel(
            logo_frame,
            text="AI Face Recognition Attendance System",
            font=ctk.CTkFont(size=13),
            text_color=MUTED,
        ).grid(row=2, column=0, pady=(0, 8))

        version_badge = ctk.CTkLabel(
            logo_frame,
            text="  v1.0.0  ",
            corner_radius=8,
            fg_color="#0B2A1A",
            text_color="#4ADE80",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        version_badge.grid(row=3, column=0, pady=(0, 28))

        # ------------------------------------------------
        # INFO CARDS
        # ------------------------------------------------

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, padx=28, pady=20, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)

        sections = [
            (
                "🧠  AI Engine",
                "InsightFace  ·  ArcFace model\n"
                "Real-time multi-face detection & recognition",
            ),
            (
                "🖥   GUI Framework",
                "CustomTkinter  ·  Modern dark-mode UI\n"
                "OpenCV for live camera rendering",
            ),
            (
                "🗄   Database",
                "SQLite  ·  Lightweight local storage\n"
                "Excel export via OpenPyXL",
            ),
            (
                "📊  Analytics",
                "Matplotlib  ·  Daily & per-user charts\n"
                "Real-time attendance insights",
            ),
        ]

        for row_idx, (title, desc) in enumerate(sections):
            card = ctk.CTkFrame(
                body,
                fg_color=CARD_BG,
                corner_radius=10,
                border_width=1,
                border_color=BORDER,
            )
            card.grid(
                row=row_idx, column=0,
                pady=(0, 10), sticky="ew"
            )
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=ACCENT,
                anchor="w",
            ).grid(row=0, column=0, padx=16, pady=(12, 2), sticky="w")

            ctk.CTkLabel(
                card,
                text=desc,
                font=ctk.CTkFont(size=12),
                text_color=MUTED,
                justify="left",
                anchor="w",
            ).grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")

        # ------------------------------------------------
        # CLOSE BUTTON
        # ------------------------------------------------

        ctk.CTkButton(
            self,
            text="Close",
            height=40,
            fg_color=PRIMARY,
            hover_color="#1D4ED8",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.destroy,
        ).grid(row=2, column=0, padx=28, pady=(0, 28), sticky="ew")
