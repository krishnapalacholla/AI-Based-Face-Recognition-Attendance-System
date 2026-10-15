"""
dashboard.py

Main GUI dashboard for the Face Recognition Attendance System.

Improvements over v1:
  - Sidebar navigation with active-page highlight
  - Multiple pages: Dashboard, Attendance Records, Analytics, Settings, About
  - Attendance table with search + date filter + delete
  - Settings & Analytics windows wired in
  - Confidence threshold & confirmation frames read from DB settings
  - Responsive camera feed
  - Smooth animations on stat-card updates
  - PDF/Excel export from records page
  - Better spacing & typography throughout
"""

from pathlib import Path
import sqlite3
import threading
import subprocess
import sys
from datetime import datetime

import cv2
import numpy as np
import customtkinter as ctk
from PIL import Image
from tkinter import messagebox

from registration.register_user import register_user
from recognition.face_recognizer import FaceRecognizer
from attendance.attendance_manager import AttendanceManager
from database.database import initialize_database, get_setting


# ==================================================
# DESIGN TOKENS
# ==================================================

APP_BG        = "#07111F"
SIDEBAR_BG    = "#0A1628"
CARD_BG       = "#101E33"
CARD_HOVER    = "#142640"
PRIMARY       = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
SUCCESS       = "#16A34A"
DANGER        = "#DC2626"
WARNING       = "#D97706"
TEXT          = "#F8FAFC"
MUTED         = "#94A3B8"
BORDER        = "#22324A"
ACCENT        = "#0EA5E9"
GREEN         = "#4ADE80"


class AttendanceDashboard(ctk.CTk):
    """
    Main GUI dashboard for the Face Recognition
    Attendance System.
    """

    def __init__(self):
        super().__init__()

        # --------------------------------------------------
        # INIT DB
        # --------------------------------------------------
        initialize_database()

        # --------------------------------------------------
        # APPEARANCE
        # --------------------------------------------------
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=APP_BG)

        # --------------------------------------------------
        # WINDOW
        # --------------------------------------------------
        self.title("Vision Attendance | AI Face Recognition System")
        self.geometry("1440x860")
        self.minsize(1100, 700)

        # Bring window to front
        self.lift()
        self.attributes("-topmost", True)
        self.after_idle(self.attributes, "-topmost", False)
        self.focus_force()

        # Handle clean exit to release webcam hardware lock
        self.protocol("WM_DELETE_WINDOW", self._on_app_close)

        # --------------------------------------------------
        # STATE
        # --------------------------------------------------
        self.camera            = None
        self.camera_running    = False
        self.recognizer        = None
        self.current_camera_image = None
        self.current_page      = None

        # Pre-load InsightFace AI models in background for instant camera startup
        threading.Thread(target=self._preload_ai_engine, daemon=True).start()

        # --------------------------------------------------
        # LAYOUT
        # --------------------------------------------------
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()

        # --------------------------------------------------
        # SHOW DEFAULT PAGE
        # --------------------------------------------------
        self._show_page("dashboard")

        # --------------------------------------------------
        # CLOSE EVENT
        # --------------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ======================================================
    # SIDEBAR
    # ======================================================

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=265,
            corner_radius=0,
            fg_color=SIDEBAR_BG,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        # Row 7 expands to push the bottom group down
        self.sidebar.grid_rowconfigure(7, weight=1)

        # ---- Logo ----
        ctk.CTkLabel(
            self.sidebar,
            text="◉  VISION",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=TEXT,
        ).grid(row=0, column=0, padx=24, pady=(32, 2), sticky="w")

        ctk.CTkLabel(
            self.sidebar,
            text="ATTENDANCE",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=PRIMARY,
        ).grid(row=1, column=0, padx=24, pady=(0, 6), sticky="w")

        ctk.CTkLabel(
            self.sidebar,
            text="AI Face Recognition System",
            font=ctk.CTkFont(size=11),
            text_color=MUTED,
        ).grid(row=2, column=0, padx=24, pady=(0, 24), sticky="w")

        # Divider
        ctk.CTkFrame(
            self.sidebar, height=1, fg_color=BORDER
        ).grid(row=3, column=0, padx=20, pady=(0, 16), sticky="ew")

        # ---- Navigation buttons ----
        self._nav_buttons: dict = {}

        nav_items = [
            ("dashboard",  "🏠",  "Dashboard"),
            ("camera",     "📷",  "Live Recognition"),
            ("register",   "＋",  "Register User"),
            ("records",    "▤",   "Attendance Records"),
            ("analytics",  "📊",  "Analytics"),
        ]

        for row_offset, (page_id, icon, label) in enumerate(nav_items, start=4):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}   {label}",
                anchor="w",
                height=44,
                corner_radius=8,
                fg_color="transparent",
                hover_color=CARD_BG,
                text_color=MUTED,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda pid=page_id: self._show_page(pid),
            )
            btn.grid(
                row=row_offset, column=0,
                padx=14, pady=3, sticky="ew"
            )
            self._nav_buttons[page_id] = btn

        # ---- Bottom group ----
        ctk.CTkFrame(
            self.sidebar, height=1, fg_color=BORDER
        ).grid(row=9, column=0, padx=20, pady=(0, 12), sticky="ew")

        bottom_items = [
            ("settings", "⚙",  "Settings"),
            ("about",    "ℹ",  "About"),
        ]
        for row_offset, (page_id, icon, label) in enumerate(bottom_items, start=10):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}   {label}",
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                hover_color=CARD_BG,
                text_color=MUTED,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda pid=page_id: self._show_page(pid),
            )
            btn.grid(
                row=row_offset, column=0,
                padx=14, pady=2, sticky="ew"
            )
            self._nav_buttons[page_id] = btn

        ctk.CTkButton(
            self.sidebar,
            text="  ⏻   Exit",
            anchor="w",
            height=42,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#3B0000",
            text_color=MUTED,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_close,
        ).grid(row=12, column=0, padx=14, pady=(2, 28), sticky="ew")

    # ======================================================
    # CONTENT AREA
    # ======================================================

    def _build_content_area(self):
        self.content = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=APP_BG,
        )
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    # ======================================================
    # PAGE ROUTING
    # ======================================================

    def _show_page(self, page_id: str):
        # Stop camera if switching away from camera page
        if page_id != "camera" and self.camera_running:
            self._stop_recognition()

        # Highlight active nav button
        for pid, btn in self._nav_buttons.items():
            if pid == page_id:
                btn.configure(
                    fg_color=PRIMARY,
                    text_color=TEXT,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=MUTED,
                )

        # Clear content
        for w in self.content.winfo_children():
            w.destroy()

        self.current_page = page_id

        # Dispatch
        if page_id == "dashboard":
            self._page_dashboard()
        elif page_id == "camera":
            self._page_camera()
        elif page_id == "register":
            self._page_register()
        elif page_id == "records":
            self._page_records()
        elif page_id == "analytics":
            self._open_analytics()
            self._show_page("dashboard")
        elif page_id == "settings":
            self._open_settings()
            self._show_page("dashboard")
        elif page_id == "about":
            self._open_about()
            self._show_page("dashboard")

    # ======================================================
    # PAGE — DASHBOARD
    # ======================================================

    def _page_dashboard(self):
        frame = self._page_frame()

        # ---- Header ----
        self._page_header(
            frame,
            "AI Attendance Dashboard",
            "Welcome back, Admin  ·  " + datetime.now().strftime("%A, %d %B %Y"),
        )

        # ---- Stat cards ----
        stats_row = ctk.CTkFrame(frame, fg_color="transparent")
        stats_row.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        for c in range(4):
            stats_row.grid_columnconfigure(c, weight=1, uniform="sc")

        user_count       = self._count_users()
        today_count      = self._count_today()
        total_records    = self._count_total()
        rate             = self._attendance_rate(user_count, today_count)

        cards_data = [
            ("Registered Users",  str(user_count),    PRIMARY,  "👤"),
            ("Present Today",     str(today_count),   SUCCESS,  "✅"),
            ("Total Records",     str(total_records), ACCENT,   "📋"),
            ("Attendance Rate",   f"{rate}%",         WARNING,  "📈"),
        ]

        self._stat_cards = []
        for col, (label, value, color, icon) in enumerate(cards_data):
            lbl = self._stat_card(stats_row, col, icon, label, value, color)
            self._stat_cards.append(lbl)

        # ---- Body: quick-action cards ----
        body = ctk.CTkFrame(frame, fg_color="transparent")
        body.grid(row=2, column=0, sticky="nsew")
        frame.grid_rowconfigure(2, weight=1)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        quick_actions = [
            (
                "📷  Start Recognition",
                "Launch the live AI camera to detect and mark\nattendance automatically.",
                PRIMARY,
                "#1D4ED8",
                lambda: self._show_page("camera"),
                0, 0,
            ),
            (
                "＋  Register New User",
                "Capture face images to enroll a new person\ninto the recognition system.",
                "#059669",
                "#047857",
                lambda: self._show_page("register"),
                0, 1,
            ),
            (
                "▤  View Attendance",
                "Browse, search and filter all attendance\nrecords with date and name filters.",
                "#7C3AED",
                "#5B21B6",
                lambda: self._show_page("records"),
                1, 0,
            ),
            (
                "📊  Analytics",
                "Visualise daily and per-user attendance\ntrends with interactive charts.",
                "#D97706",
                "#B45309",
                self._open_analytics,
                1, 1,
            ),
        ]

        for text, desc, fg, hover, cmd, r, c in quick_actions:
            # Frame card — CTkButton in v6 does not support wraplength
            card = ctk.CTkFrame(
                body,
                fg_color=CARD_BG,
                corner_radius=14,
                border_width=1,
                border_color=BORDER,
            )
            card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            card.grid_rowconfigure(1, weight=1)

            ctk.CTkLabel(
                card,
                text=text,
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=TEXT,
                anchor="w",
            ).grid(row=0, column=0, padx=20, pady=(22, 4), sticky="w")

            ctk.CTkLabel(
                card,
                text=desc,
                font=ctk.CTkFont(size=12),
                text_color=MUTED,
                anchor="w",
                justify="left",
                wraplength=280,
            ).grid(row=1, column=0, padx=20, pady=(0, 12), sticky="nw")

            ctk.CTkButton(
                card,
                text="Open →",
                height=34,
                width=110,
                fg_color=fg,
                hover_color=hover,
                font=ctk.CTkFont(size=12, weight="bold"),
                corner_radius=8,
                command=cmd,
            ).grid(row=2, column=0, padx=20, pady=(0, 18), sticky="w")

    # ======================================================
    # PAGE — LIVE CAMERA / RECOGNITION
    # ======================================================

    def _page_camera(self):
        frame = self._page_frame()
        frame.grid_rowconfigure(2, weight=1)

        self._page_header(
            frame,
            "Live AI Recognition",
            "Camera feed with real-time face detection and attendance marking",
        )

        # ---- Controls row ----
        ctrl = ctk.CTkFrame(frame, fg_color="transparent")
        ctrl.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        self._recognition_btn = ctk.CTkButton(
            ctrl,
            text="▶  Start Recognition",
            height=42,
            fg_color=SUCCESS,
            hover_color="#15803D",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._toggle_recognition,
        )
        self._recognition_btn.pack(side="left")

        self._cam_status_label = ctk.CTkLabel(
            ctrl,
            text="  ●  Camera Offline",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=MUTED,
        )
        self._cam_status_label.pack(side="left", padx=16)

        # ---- Body: camera + identity panel ----
        body = ctk.CTkFrame(frame, fg_color="transparent")
        body.grid(row=2, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=3, uniform="cam")
        body.grid_columnconfigure(1, weight=1, uniform="cam")
        body.grid_rowconfigure(0, weight=1)

        # Camera card
        cam_card = ctk.CTkFrame(
            body,
            fg_color=CARD_BG,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        cam_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        cam_card.grid_rowconfigure(1, weight=1)
        cam_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            cam_card,
            text="LIVE AI FACE SCAN",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT,
        ).grid(row=0, column=0, padx=18, pady=(16, 8), sticky="w")

        import tkinter as tk
        self.camera_canvas = tk.Canvas(
            cam_card,
            bg="#101E33",
            highlightthickness=0,
        )
        self.camera_canvas.grid(
            row=1, column=0, padx=12, pady=(0, 12), sticky="nsew"
        )
        self._show_canvas_text("CAMERA OFFLINE", "Press 'Start Recognition'\nto activate the AI camera")

        # Identity panel
        id_card = ctk.CTkFrame(
            body,
            fg_color=CARD_BG,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        id_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        id_card.grid_rowconfigure(1, weight=1)
        id_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            id_card,
            text="IDENTITY\nVERIFICATION",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT,
            justify="left",
        ).grid(row=0, column=0, padx=18, pady=(16, 8), sticky="w")

        self.activity_label = ctk.CTkLabel(
            id_card,
            text=(
                "●  SYSTEM ONLINE\n\n"
                "AI ENGINE\n"
                "InsightFace ready\n\n"
                "RECOGNITION STATE\n"
                "Waiting for scan\n\n"
                "ATTENDANCE STATE\n"
                "No active identity"
            ),
            justify="left",
            anchor="nw",
            wraplength=220,
            text_color=MUTED,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.activity_label.grid(
            row=1, column=0, padx=18, pady=(0, 18), sticky="nsew"
        )

    # ======================================================
    # PAGE — REGISTER USER
    # ======================================================

    def _page_register(self):
        frame = self._page_frame()

        self._page_header(
            frame,
            "Register New User",
            "Capture face images to enroll a user into the AI recognition system",
        )
        frame.grid_rowconfigure(2, weight=1)

        # ---- Form card ----
        card = ctk.CTkFrame(
            frame,
            fg_color=CARD_BG,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        card.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card,
            text="User Name",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT,
        ).grid(row=0, column=0, padx=24, pady=(24, 8), sticky="w")

        self._reg_name_entry = ctk.CTkEntry(
            card,
            placeholder_text="e.g.  Alice Johnson",
            height=42,
            font=ctk.CTkFont(size=13),
        )
        self._reg_name_entry.grid(
            row=0, column=1, padx=(0, 24), pady=(24, 8), sticky="ew"
        )

        ctk.CTkLabel(
            card,
            text="Instructions",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT,
        ).grid(row=1, column=0, padx=24, pady=(8, 8), sticky="w")

        reg_img_count = get_setting("registration_images", "5")
        ctk.CTkLabel(
            card,
            text=(
                "A webcam window will open.\n"
                f"Press  SPACE  to capture each image ({reg_img_count} images total).\n"
                "Look straight, slightly left, right, up, and down.\n"
                "Press  Q  to quit early."
            ),
            font=ctk.CTkFont(size=12),
            text_color=MUTED,
            justify="left",
        ).grid(row=1, column=1, padx=(0, 24), pady=(8, 24), sticky="w")

        # ---- Buttons ----
        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew")

        self._reg_start_btn = ctk.CTkButton(
            btn_row,
            text="📷  Open Camera & Register",
            height=46,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            command=self._start_registration,
        )
        self._reg_start_btn.pack(side="left")

        self._reg_status = ctk.CTkLabel(
            btn_row,
            text="",
            text_color=MUTED,
            font=ctk.CTkFont(size=13),
        )
        self._reg_status.pack(side="left", padx=20)

        # ---- Registered users list ----
        list_card = ctk.CTkFrame(
            frame,
            fg_color=CARD_BG,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        list_card.grid(row=3, column=0, sticky="nsew", pady=(20, 0))
        frame.grid_rowconfigure(3, weight=1)
        list_card.grid_columnconfigure(0, weight=1)
        list_card.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(list_card, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=18, pady=(14, 8), sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr,
            text="Registered Users",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            hdr,
            text="↺  Refresh",
            width=100,
            height=32,
            fg_color=CARD_BG,
            hover_color=CARD_HOVER,
            border_width=1,
            border_color=BORDER,
            font=ctk.CTkFont(size=12),
            command=self._refresh_user_list,
        ).grid(row=0, column=1, sticky="e")

        self._user_list_frame = ctk.CTkScrollableFrame(
            list_card,
            fg_color="transparent",
        )
        self._user_list_frame.grid(
            row=1, column=0, padx=8, pady=(0, 8), sticky="nsew"
        )
        self._user_list_frame.grid_columnconfigure(0, weight=1)

        self._refresh_user_list()

    def _refresh_user_list(self):
        """Rebuild the registered users list."""
        for w in self._user_list_frame.winfo_children():
            w.destroy()

        from registration.user_manager import UserManager
        users = UserManager().list_users()

        if not users:
            ctk.CTkLabel(
                self._user_list_frame,
                text="No users registered yet.",
                text_color=MUTED,
                font=ctk.CTkFont(size=13),
            ).grid(row=0, column=0, pady=20)
            return

        # Header row
        for col, header in enumerate(["Name", "Images", "Action"]):
            ctk.CTkLabel(
                self._user_list_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=MUTED,
            ).grid(row=0, column=col, padx=12, pady=(8, 4), sticky="w")

        self._user_list_frame.grid_columnconfigure(0, weight=1)
        self._user_list_frame.grid_columnconfigure(1, weight=0)
        self._user_list_frame.grid_columnconfigure(2, weight=0)

        from registration.user_manager import UserManager
        mgr = UserManager()

        for row_idx, user in enumerate(users, start=1):
            img_count = mgr.get_image_count(user)

            ctk.CTkLabel(
                self._user_list_frame,
                text=user,
                font=ctk.CTkFont(size=13),
                text_color=TEXT,
                anchor="w",
            ).grid(row=row_idx, column=0, padx=12, pady=6, sticky="w")

            ctk.CTkLabel(
                self._user_list_frame,
                text=f"{img_count} images",
                font=ctk.CTkFont(size=12),
                text_color=MUTED,
            ).grid(row=row_idx, column=1, padx=12, pady=6)

            ctk.CTkButton(
                self._user_list_frame,
                text="🗑  Delete",
                width=90,
                height=30,
                fg_color=DANGER,
                hover_color="#B91C1C",
                font=ctk.CTkFont(size=12),
                command=lambda u=user: self._delete_user(u),
            ).grid(row=row_idx, column=2, padx=12, pady=6)

    def _delete_user(self, user_name: str):
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete user '{user_name}' and all their face images?\n"
            "This cannot be undone.",
        )
        if not confirm:
            return
        from registration.user_manager import UserManager
        ok = UserManager().delete_user(user_name)
        if ok:
            messagebox.showinfo(
                "Deleted",
                f"User '{user_name}' has been removed.",
            )
            self._refresh_user_list()

    def _start_registration(self):
        user_name = self._reg_name_entry.get().strip()
        if not user_name:
            self._reg_status.configure(
                text="⚠  Please enter a user name.", text_color=WARNING
            )
            return

        self._reg_start_btn.configure(state="disabled")
        self._reg_status.configure(
            text="📷  Camera opening…", text_color=MUTED
        )

        def run():
            result = register_user(user_name=user_name)
            self.after(0, self._on_registration_done, user_name, result)

        threading.Thread(target=run, daemon=True).start()

    def _on_registration_done(self, user_name: str, result: bool):
        self._reg_start_btn.configure(state="normal")
        if result:
            self._reg_status.configure(
                text=f"✅  {user_name} registered successfully!",
                text_color=GREEN,
            )
            self._refresh_user_list()
        else:
            self._reg_status.configure(
                text="❌  Registration cancelled or failed.",
                text_color=DANGER,
            )

    # ======================================================
    # PAGE — ATTENDANCE RECORDS
    # ======================================================

    def _page_records(self):
        frame = self._page_frame()
        frame.grid_rowconfigure(3, weight=1)

        self._page_header(
            frame,
            "Attendance Records",
            "Browse, search and export all attendance history",
        )

        # ---- Filter bar ----
        filter_bar = ctk.CTkFrame(frame, fg_color=CARD_BG, corner_radius=10)
        filter_bar.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        filter_bar.grid_columnconfigure(1, weight=1)
        filter_bar.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            filter_bar,
            text="🔍",
            font=ctk.CTkFont(size=16),
            text_color=MUTED,
        ).grid(row=0, column=0, padx=(14, 4), pady=12)

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._apply_filters())

        ctk.CTkEntry(
            filter_bar,
            placeholder_text="Search by name…",
            textvariable=self._search_var,
            height=36,
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=1, padx=(0, 14), pady=10, sticky="ew")

        ctk.CTkLabel(
            filter_bar,
            text="Date:",
            text_color=MUTED,
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=2, padx=(0, 6))

        self._date_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="YYYY-MM-DD  (leave blank for all)",
            width=220,
            height=36,
            font=ctk.CTkFont(size=13),
        )
        self._date_entry.grid(row=0, column=3, padx=(0, 10), pady=10, sticky="ew")

        ctk.CTkButton(
            filter_bar,
            text="Filter",
            width=80,
            height=36,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            font=ctk.CTkFont(size=13),
            command=self._apply_filters,
        ).grid(row=0, column=4, padx=(0, 8))

        ctk.CTkButton(
            filter_bar,
            text="Clear",
            width=70,
            height=36,
            fg_color=CARD_BG,
            hover_color=CARD_HOVER,
            border_width=1,
            border_color=BORDER,
            font=ctk.CTkFont(size=13),
            command=self._clear_filters,
        ).grid(row=0, column=5, padx=(0, 14))

        # ---- Export buttons ----
        export_bar = ctk.CTkFrame(frame, fg_color="transparent")
        export_bar.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkButton(
            export_bar,
            text="⬇  Export Excel",
            height=38,
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._export_excel,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            export_bar,
            text="⬇  Export PDF",
            height=38,
            fg_color="#7C3AED",
            hover_color="#5B21B6",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._export_pdf,
        ).pack(side="left")

        self._records_count_label = ctk.CTkLabel(
            export_bar,
            text="",
            text_color=MUTED,
            font=ctk.CTkFont(size=12),
        )
        self._records_count_label.pack(side="right")

        # ---- Table ----
        table_card = ctk.CTkFrame(
            frame,
            fg_color=CARD_BG,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        table_card.grid(row=3, column=0, sticky="nsew")
        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(1, weight=1)

        # Table header row (fixed)
        hdr = ctk.CTkFrame(table_card, fg_color=SIDEBAR_BG, corner_radius=0, height=40)
        hdr.grid(row=0, column=0, sticky="ew", padx=0)
        hdr.grid_propagate(False)
        for col, (label, w) in enumerate([
            ("ID", 60), ("Name", 200), ("Date", 140), ("Time", 120), ("Action", 100)
        ]):
            hdr.grid_columnconfigure(col, weight=1 if label == "Name" else 0, minsize=w)
            ctk.CTkLabel(
                hdr,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=MUTED,
            ).grid(row=0, column=col, padx=14, pady=10, sticky="w")

        # Scrollable rows
        self._records_scroll = ctk.CTkScrollableFrame(
            table_card,
            fg_color="transparent",
        )
        self._records_scroll.grid(
            row=1, column=0, sticky="nsew", padx=0, pady=0
        )
        for col, (_, w) in enumerate([
            ("ID", 60), ("Name", 200), ("Date", 140), ("Time", 120), ("Action", 100)
        ]):
            self._records_scroll.grid_columnconfigure(
                col, weight=1 if col == 1 else 0, minsize=w
            )

        # Load & display
        self._all_records = self._fetch_records()
        self._filtered_records = self._all_records[:]
        self._render_records_table()

    def _fetch_records(self):
        db_path = Path("database") / "attendance.db"
        if not db_path.exists():
            return []
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name, date, time FROM attendance "
                "ORDER BY date DESC, time DESC"
            )
            rows = cur.fetchall()
            conn.close()
            return rows
        except sqlite3.Error:
            return []

    def _apply_filters(self):
        query = self._search_var.get().strip().lower()
        date  = self._date_entry.get().strip()
        self._filtered_records = [
            r for r in self._all_records
            if (not query or query in r[1].lower())
            and (not date  or r[2] == date)
        ]
        self._render_records_table()

    def _clear_filters(self):
        self._search_var.set("")
        self._date_entry.delete(0, "end")
        self._filtered_records = self._all_records[:]
        self._render_records_table()

    def _render_records_table(self):
        for w in self._records_scroll.winfo_children():
            w.destroy()

        records = self._filtered_records
        self._records_count_label.configure(
            text=f"{len(records)} record{'s' if len(records) != 1 else ''}"
        )

        if not records:
            ctk.CTkLabel(
                self._records_scroll,
                text="No records found.",
                text_color=MUTED,
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, columnspan=5, pady=40)
            return

        for row_idx, record in enumerate(records):
            row_id, name, date, time = record
            bg = CARD_BG if row_idx % 2 == 0 else "#0C1929"

            row_frame = ctk.CTkFrame(
                self._records_scroll,
                fg_color=bg,
                corner_radius=0,
                height=40,
            )
            row_frame.grid(row=row_idx, column=0, columnspan=5, sticky="ew")
            row_frame.grid_propagate(False)
            for col, (val, cw) in enumerate([
                (str(row_id), 60),
                (name, 200),
                (date, 140),
                (time, 120),
            ]):
                row_frame.grid_columnconfigure(
                    col, weight=1 if col == 1 else 0, minsize=cw
                )
                ctk.CTkLabel(
                    row_frame,
                    text=val,
                    font=ctk.CTkFont(size=12),
                    text_color=TEXT if col == 1 else MUTED,
                    anchor="w",
                ).grid(row=0, column=col, padx=14, pady=8, sticky="w")

            # Delete button
            row_frame.grid_columnconfigure(4, weight=0, minsize=100)
            ctk.CTkButton(
                row_frame,
                text="Delete",
                width=70,
                height=26,
                fg_color="transparent",
                hover_color=DANGER,
                border_width=1,
                border_color=DANGER,
                text_color=DANGER,
                font=ctk.CTkFont(size=11),
                command=lambda rid=row_id: self._delete_record(rid),
            ).grid(row=0, column=4, padx=10, pady=6)

    def _delete_record(self, record_id: int):
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete attendance record #{record_id}?",
        )
        if not confirm:
            return
        db_path = Path("database") / "attendance.db"
        try:
            conn = sqlite3.connect(str(db_path))
            conn.execute("DELETE FROM attendance WHERE id = ?", (record_id,))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
            return
        self._all_records      = self._fetch_records()
        self._filtered_records = self._all_records[:]
        self._render_records_table()

    def _export_excel(self):
        from attendance.excel_manager import ExcelManager
        records = self._fetch_records()
        path = ExcelManager().export(records)
        if path:
            messagebox.showinfo(
                "Export Successful",
                f"Excel file saved:\n{path}",
            )
        else:
            messagebox.showwarning(
                "No Data",
                "No attendance records to export.",
            )

    def _export_pdf(self):
        records = self._fetch_records()
        if not records:
            messagebox.showwarning("No Data", "No records to export.")
            return
        from attendance.pdf_manager import PdfManager
        path = PdfManager().export(records)
        if path:
            messagebox.showinfo("Export Successful", f"PDF saved:\n{path}")

    # ======================================================
    # RECOGNITION ENGINE
    # ======================================================

    def _toggle_recognition(self):
        if self.camera_running:
            self._stop_recognition()
        else:
            self._start_recognition()

    def _show_canvas_text(self, title="CAMERA OFFLINE", msg=""):
        if hasattr(self, "camera_canvas") and self.camera_canvas:
            try:
                self.camera_canvas.delete("all")
                w = max(320, self.camera_canvas.winfo_width())
                h = max(240, self.camera_canvas.winfo_height())
                cx = w // 2
                cy = h // 2
                full_text = f"▣\n\n{title}\n\n{msg}".strip()
                self.camera_canvas.create_text(
                    cx, cy,
                    text=full_text,
                    fill="#94A3B8",
                    font=("Segoe UI", 13, "bold"),
                    justify="center"
                )
            except Exception:
                pass

    def _preload_ai_engine(self):
        try:
            threshold = float(get_setting("recognition_threshold", "0.45"))
            conf_frames = int(get_setting("confirmation_frames", "5"))
            self.recognizer = FaceRecognizer(threshold=threshold, confirmation_frames=conf_frames)
            print("[OK] AI Engine pre-loaded successfully.")
        except Exception as e:
            print(f"AI Preload Notice: {e}")

    def _start_recognition(self):
        try:
            threshold = float(
                get_setting("recognition_threshold", "0.45")
            )
            conf_frames = int(
                get_setting("confirmation_frames", "5")
            )
            self._cam_index = int(
                get_setting("camera_index", "0")
            )

            if not hasattr(self, "recognizer") or self.recognizer is None:
                self.recognizer = FaceRecognizer(
                    threshold=threshold,
                    confirmation_frames=conf_frames,
                )

            self.camera_running = True
            self.camera = None
            self._raw_frame = None
            self._latest_face_boxes = []
            self._ai_fps = 0.0

            self._show_canvas_text("CONNECTING TO WEBCAM...", "Please wait a moment")

            self._latest_activity_info = (
                "◉  CAMERA INITIALIZING\n\n"
                "Connecting to webcam...",
                ACCENT,
            )

            self._recognition_btn.configure(
                text="■  Stop Recognition",
                fg_color=DANGER,
                hover_color="#B91C1C",
            )
            self._cam_status_label.configure(
                text="  ●  Camera Starting",
                text_color=ACCENT,
            )
            self.activity_label.configure(
                text=self._latest_activity_info[0],
                text_color=self._latest_activity_info[1],
            )

            # Thread 1: Camera Capture Loop (30 FPS buffer flusher)
            self._cap_thread = threading.Thread(
                target=self._camera_capture_loop,
                daemon=True,
            )
            self._cap_thread.start()

            # Thread 2: AI Face Recognition Loop (Async inference)
            self._ai_thread = threading.Thread(
                target=self._ai_inference_loop,
                daemon=True,
            )
            self._ai_thread.start()

            # Main GUI Render Loop (Smooth ImageTk rendering)
            self._render_camera_loop()

        except Exception as e:
            self.activity_label.configure(
                text=f"Error: {e}", text_color=DANGER
            )

    def _stop_recognition(self):
        self.camera_running = False
        self.current_camera_image = None
        self._raw_frame = None
        self._latest_face_boxes = []

        self._show_canvas_text("CAMERA OFFLINE", "Press 'Start Recognition'\nto activate the AI camera")
        if hasattr(self, "_recognition_btn"):
            self._recognition_btn.configure(
                text="▶  Start Recognition",
                fg_color=SUCCESS,
                hover_color="#15803D",
            )
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

    def _on_app_close(self):
        self.camera_running = False
        if hasattr(self, "camera") and self.camera:
            try:
                self.camera.release()
            except Exception:
                pass
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
        self.destroy()
        sys.exit(0)

    def _compare_embedding(self, live_embedding):
        if live_embedding is None or not hasattr(self, "recognizer") or self.recognizer is None:
            return "Unknown", 0.0

        live = np.asarray(live_embedding, dtype=np.float32).flatten()
        norm = np.linalg.norm(live)
        if norm == 0:
            return "Unknown", 0.0
        live = live / norm

        best_name  = "Unknown"
        best_dist  = float("inf")

        embeddings = getattr(self.recognizer, "embeddings", {})
        for user_name, stored_list in embeddings.items():
            for stored in stored_list:
                s = np.asarray(stored, dtype=np.float32).flatten()
                sn = np.linalg.norm(s)
                if sn == 0:
                    continue
                s = s / sn
                if s.shape != live.shape:
                    continue
                sim  = float(np.dot(live, s))
                sim  = max(-1.0, min(1.0, sim))
                dist = 1.0 - sim
                if dist < best_dist:
                    best_dist = dist
                    best_name = user_name

        if best_dist == float("inf"):
            return "Unknown", 0.0

        score = max(0.0, min(100.0, (1.0 - best_dist) * 100.0))
        threshold = float(get_setting("recognition_threshold", "0.45"))
        if score < threshold * 100.0:
            best_name = "Unknown"
        return best_name, score

    def _camera_capture_loop(self):
        import sys
        import time

        try:
            self.camera = cv2.VideoCapture(self._cam_index)
            if not self.camera or not self.camera.isOpened():
                self.camera = cv2.VideoCapture(self._cam_index, cv2.CAP_DSHOW)

            if not self.camera or not self.camera.isOpened():
                self._latest_activity_info = (
                    "❌  Camera failed to open.\nCheck webcam connection.",
                    DANGER,
                )
                self.after(0, lambda: self._show_canvas_text("CAMERA FAILED TO OPEN", "Check webcam connection or permissions"))
                self.camera_running = False
                return

            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            threshold = float(get_setting("recognition_threshold", "0.45"))
            conf_frames = int(get_setting("confirmation_frames", "5"))

            self._latest_activity_info = (
                "◉  AI ACTIVE\n\n"
                "Scanning for registered faces…\n\n"
                f"Threshold: {threshold:.2f}\n"
                f"Confirm frames: {conf_frames}",
                GREEN,
            )
            self.after(0, lambda: self._cam_status_label.configure(
                text="  ●  Camera Active",
                text_color=GREEN
            ))
        except Exception as e:
            import traceback
            with open("render_error.log", "a") as f:
                f.write(f"Camera Init Error: {e}\n" + traceback.format_exc() + "\n")
            self._latest_activity_info = (f"Camera Init Error: {e}", DANGER)
            self.camera_running = False
            return

        failed_reads = 0
        while self.camera_running and self.camera and self.camera.isOpened():
            success, frame = self.camera.read()
            if success and frame is not None:
                self._raw_frame = frame
                failed_reads = 0
            else:
                failed_reads += 1
                if failed_reads > 50:
                    self._latest_activity_info = (
                        "❌  Camera feed lost.\nPlease check webcam connection.",
                        DANGER,
                    )
                    self.camera_running = False
                    break
                time.sleep(0.02)

        if self.camera:
            self.camera.release()
            self.camera = None

    def _ai_inference_loop(self):
        import time
        last_time = datetime.now()
        fps = 0.0

        while self.camera_running:
            if not hasattr(self, "_raw_frame") or self._raw_frame is None:
                time.sleep(0.02)
                continue

            frame = self._raw_frame.copy()
            try:
                now = datetime.now()
                dt = (now - last_time).total_seconds()
                if dt > 0:
                    fps = 0.9 * fps + 0.1 * (1.0 / dt)
                last_time = now

                if not hasattr(self, "recognizer") or self.recognizer is None:
                    break

                faces = self.recognizer.detector.detect_faces(frame)
                visible_names = set()
                face_boxes = []

                for face in faces:
                    x1, y1, x2, y2 = map(int, face.bbox)
                    h, w = frame.shape[:2]
                    x1 = max(0, min(x1, w - 1))
                    y1 = max(0, min(y1, h - 1))
                    x2 = max(0, min(x2, w - 1))
                    y2 = max(0, min(y2, h - 1))

                    name, score = "Unknown", 0.0
                    confirmed = False

                    if face.embedding is not None:
                        name, score = self._compare_embedding(face.embedding)

                    if name != "Unknown":
                        visible_names.add(name)
                        confirmed = self.recognizer.update_recognition_count(name)
                        conf_count = min(
                            self.recognizer.recognition_counts.get(name, 0),
                            self.recognizer.confirmation_frames,
                        )

                        if confirmed:
                            already = name in self.recognizer.session_attendance
                            if not already:
                                marked = self.recognizer.attendance_manager.mark_attendance(name)
                                self.recognizer.session_attendance.add(name)
                                status = "PRESENT — RECORDED" if marked else "PRESENT — ALREADY MARKED"
                            else:
                                status = "PRESENT — VERIFIED"

                            self._latest_activity_info = (
                                f"✅  CONFIRMED\n\n"
                                f"IDENTITY\n{name.upper()}\n\n"
                                f"CONFIDENCE\n{score:.1f}%\n\n"
                                f"ATTENDANCE\n{status}",
                                GREEN,
                            )
                        else:
                            self._latest_activity_info = (
                                f"◉  SCANNING\n\n"
                                f"IDENTITY\n{name.upper()}\n\n"
                                f"CONFIDENCE\n{score:.1f}%\n\n"
                                f"PROGRESS\n{conf_count} / "
                                f"{self.recognizer.confirmation_frames}",
                                ACCENT,
                            )
                    else:
                        self._latest_activity_info = (
                            "⚠  UNKNOWN FACE\n\n"
                            "No registered identity matched.\n\n"
                            "Please register this person.",
                            DANGER,
                        )

                    face_boxes.append({
                        "bbox": (x1, y1, x2, y2),
                        "name": name,
                        "score": score,
                        "confirmed": confirmed
                    })

                self.recognizer.reset_missing_users(visible_names)
                self._latest_face_boxes = face_boxes
                self._ai_fps = fps

            except Exception as e:
                print(f"AI Inference Error: {e}")

            time.sleep(0.03)

    def _render_camera_loop(self):
        from PIL import ImageTk

        if not self.camera_running:
            return

        if not hasattr(self, "_raw_frame") or self._raw_frame is None:
            if self.camera_running:
                self.after(30, self._render_camera_loop)
            return

        try:
            frame = self._raw_frame.copy()
            h, w = frame.shape[:2]

            face_boxes = getattr(self, "_latest_face_boxes", [])
            for item in face_boxes:
                x1, y1, x2, y2 = item["bbox"]
                name = item["name"]
                score = item["score"]
                confirmed = item["confirmed"]

                color = (
                    (0, 255, 0)   if confirmed else
                    (0, 200, 255) if name != "Unknown" else
                    (0, 0, 255)
                )
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                label_txt = (
                    f"{name}  {score:.1f}%  CONFIRMED" if confirmed else
                    f"{name}  {score:.1f}%" if name != "Unknown" else
                    "Unknown"
                )
                (tw, th), _ = cv2.getTextSize(
                    label_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2
                )
                ly1 = max(0, y1 - th - 12)
                ly2 = max(th + 8, y1)
                cv2.rectangle(
                    frame,
                    (x1, ly1),
                    (min(w - 1, x1 + tw + 10), ly2),
                    color, -1,
                )
                cv2.putText(
                    frame, label_txt,
                    (x1 + 5, max(th + 4, y1 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (255, 255, 255), 2,
                )

            ai_fps = getattr(self, "_ai_fps", 0.0)
            cv2.putText(
                frame, f"AI ATTENDANCE  |  {ai_fps:.1f} FPS",
                (15, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.55, (0, 255, 100), 2,
            )

            cw = self.camera_canvas.winfo_width()
            ch = self.camera_canvas.winfo_height()
            if cw < 50 or ch < 50:
                cw = 640
                ch = 480
            cx = cw // 2
            cy = ch // 2
            
            frame_resized = cv2.resize(frame, (cw, ch))
            rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            img_tk = ImageTk.PhotoImage(image=img, master=self.camera_canvas)

            self.camera_canvas.delete("all")
            self.camera_canvas.create_image(cx, cy, anchor="center", image=img_tk)
            self.camera_canvas.image = img_tk

        except Exception as e:
            import traceback
            with open("render_error.log", "a") as f:
                f.write(f"Render Error: {e}\n" + traceback.format_exc() + "\n")
            print(f"Render Loop Error: {e}")

        try:
            if hasattr(self, "_latest_activity_info") and self._latest_activity_info:
                txt, color = self._latest_activity_info
                self.activity_label.configure(text=txt, text_color=color)
        except Exception:
            pass

        if self.camera_running:
            self.after(30, self._render_camera_loop)

    # ======================================================
    # OPEN WINDOWS
    # ======================================================

    def _open_analytics(self):
        from gui.analytics import AnalyticsWindow
        AnalyticsWindow(self)

    def _open_settings(self):
        from gui.settings import SettingsWindow
        SettingsWindow(self)

    def _open_about(self):
        from gui.about import AboutWindow
        AboutWindow(self)

    # ======================================================
    # HELPERS — STATS
    # ======================================================

    def _count_users(self) -> int:
        ds = Path("dataset")
        if not ds.exists():
            return 0
        return sum(
            1 for f in ds.iterdir()
            if f.is_dir() and list(f.glob("*.jpg"))
        )

    def _count_today(self) -> int:
        db = Path("database") / "attendance.db"
        if not db.exists():
            return 0
        try:
            conn = sqlite3.connect(str(db))
            cur  = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM attendance "
                "WHERE date = DATE('now','localtime')"
            )
            result = cur.fetchone()
            conn.close()
            return result[0] if result else 0
        except sqlite3.Error:
            return 0

    def _count_total(self) -> int:
        db = Path("database") / "attendance.db"
        if not db.exists():
            return 0
        try:
            conn = sqlite3.connect(str(db))
            cur  = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM attendance")
            result = cur.fetchone()
            conn.close()
            return result[0] if result else 0
        except sqlite3.Error:
            return 0

    def _attendance_rate(self, users: int, today: int) -> int:
        if users == 0:
            return 0
        return min(100, round(today / users * 100))

    # ======================================================
    # HELPERS — LAYOUT
    # ======================================================

    def _page_frame(self) -> ctk.CTkFrame:
        """Return a fresh page frame filling the content area."""
        f = ctk.CTkFrame(
            self.content,
            fg_color=APP_BG,
            corner_radius=0,
        )
        f.grid(row=0, column=0, sticky="nsew", padx=28, pady=24)
        f.grid_columnconfigure(0, weight=1)
        return f

    def _page_header(self, parent, title: str, subtitle: str = ""):
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr,
            text=title,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        if subtitle:
            ctk.CTkLabel(
                hdr,
                text=subtitle,
                font=ctk.CTkFont(size=13),
                text_color=MUTED,
                anchor="w",
            ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Online badge
        ctk.CTkLabel(
            hdr,
            text="  ●  AI ONLINE  ",
            corner_radius=10,
            fg_color="#0B2A1A",
            text_color=GREEN,
            font=ctk.CTkFont(size=11, weight="bold"),
        ).grid(row=0, column=1, sticky="e")

    def _stat_card(
        self,
        parent,
        col: int,
        icon: str,
        label: str,
        value: str,
        color: str,
    ) -> ctk.CTkLabel:
        """Create and grid a stat card; return the value label."""
        card = ctk.CTkFrame(
            parent,
            height=110,
            corner_radius=14,
            fg_color=CARD_BG,
            border_width=1,
            border_color=BORDER,
        )
        pad_l = 0 if col == 0 else 8
        pad_r = 0 if col == 3 else 8
        card.grid(row=0, column=col, padx=(pad_l, pad_r), sticky="nsew")
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=f"{icon}  {label}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=MUTED,
        ).pack(pady=(18, 4))

        val_lbl = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=color,
        )
        val_lbl.pack()

        return val_lbl

    # ======================================================
    # CLOSE
    # ======================================================

    def _on_close(self):
        self.camera_running = False
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        self.destroy()


# ==================================================
# ENTRY POINT
# ==================================================

def run_dashboard():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = AttendanceDashboard()
    app.mainloop()


if __name__ == "__main__":
    run_dashboard()