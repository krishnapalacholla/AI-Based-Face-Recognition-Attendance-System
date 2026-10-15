"""
settings.py

Settings window for the Face Recognition
Attendance System.

Allows administrators to change:
  - Recognition threshold
  - Confirmation frames
  - Camera index
  - Admin password
  - Theme
  - Database backup / restore
"""

import shutil
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from database.database import get_setting, set_setting


class SettingsWindow(ctk.CTkToplevel):
    """
    A modal-style settings window.
    """

    # --------------------------------------------------
    # COLOURS
    # --------------------------------------------------

    APP_BG   = "#07111F"
    CARD_BG  = "#101E33"
    BORDER   = "#22324A"
    TEXT     = "#F8FAFC"
    MUTED    = "#94A3B8"
    PRIMARY  = "#2563EB"
    SUCCESS  = "#16A34A"
    DANGER   = "#DC2626"
    ACCENT   = "#0EA5E9"

    def __init__(self, parent, on_save=None):
        super().__init__(parent)

        self.on_save = on_save

        # --------------------------------------------------
        # WINDOW
        # --------------------------------------------------

        self.title("Settings")
        self.geometry("600x700")
        self.minsize(560, 640)
        self.resizable(True, True)
        self.configure(fg_color=self.APP_BG)
        self.grab_set()
        self.focus_force()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------

        header = ctk.CTkFrame(
            self,
            fg_color=self.CARD_BG,
            corner_radius=0,
            border_width=0,
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="⚙   Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.TEXT,
        ).grid(row=0, column=0, padx=28, pady=20, sticky="w")

        # --------------------------------------------------
        # SCROLLABLE BODY
        # --------------------------------------------------

        self.body = ctk.CTkScrollableFrame(
            self,
            fg_color=self.APP_BG,
            corner_radius=0,
        )
        self.body.grid(
            row=1, column=0,
            padx=0, pady=0,
            sticky="nsew"
        )
        self.body.grid_columnconfigure(0, weight=1)

        # --------------------------------------------------
        # LOAD CURRENT SETTINGS
        # --------------------------------------------------

        self._threshold_val = float(
            get_setting("recognition_threshold", "0.45")
        )
        self._conf_frames_val = int(
            get_setting("confirmation_frames", "5")
        )
        self._camera_val = int(
            get_setting("camera_index", "0")
        )
        self._reg_images_val = int(
            get_setting("registration_images", "5")
        )

        # --------------------------------------------------
        # BUILD SECTIONS
        # --------------------------------------------------

        self._build_recognition_section()
        self._build_camera_section()
        self._build_security_section()
        self._build_database_section()

        # --------------------------------------------------
        # SAVE BUTTON
        # --------------------------------------------------

        footer = ctk.CTkFrame(
            self,
            fg_color=self.CARD_BG,
            corner_radius=0,
        )
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            footer,
            text="💾  Save Settings",
            height=44,
            fg_color=self.PRIMARY,
            hover_color="#1D4ED8",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._save_settings,
        ).grid(row=0, column=0, padx=28, pady=16, sticky="ew")

    # ==================================================
    # SECTION BUILDER HELPER
    # ==================================================

    def _section(self, title: str) -> ctk.CTkFrame:
        """Create a titled card section and return its body frame."""

        card = ctk.CTkFrame(
            self.body,
            fg_color=self.CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=self.BORDER,
        )
        card.grid(
            row=self._row,
            column=0,
            padx=24,
            pady=(0, 16),
            sticky="ew",
        )
        card.grid_columnconfigure(0, weight=1)
        self._row += 1

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.ACCENT,
        ).grid(row=0, column=0, padx=18, pady=(14, 4), sticky="w")

        sep = ctk.CTkFrame(
            card,
            height=1,
            fg_color=self.BORDER,
        )
        sep.grid(row=1, column=0, padx=18, pady=(0, 10), sticky="ew")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.grid(row=2, column=0, padx=18, pady=(0, 14), sticky="ew")
        body.grid_columnconfigure(1, weight=1)

        return body

    # ==================================================
    # RECOGNITION SECTION
    # ==================================================

    def _build_recognition_section(self):
        self._row = 0

        # padding above first section
        ctk.CTkLabel(self.body, text="", height=8).grid(row=self._row, column=0)
        self._row += 1

        body = self._section("🧠  Recognition Engine")

        # --- Threshold ---
        ctk.CTkLabel(
            body,
            text="Confidence Threshold",
            text_color=self.TEXT,
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self._threshold_label = ctk.CTkLabel(
            body,
            text=f"{self._threshold_val:.2f}",
            text_color=self.PRIMARY,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._threshold_label.grid(row=0, column=1, sticky="e", pady=(0, 4))

        self._threshold_slider = ctk.CTkSlider(
            body,
            from_=0.1,
            to=0.9,
            number_of_steps=80,
            command=self._on_threshold_change,
        )
        self._threshold_slider.set(self._threshold_val)
        self._threshold_slider.grid(
            row=1, column=0, columnspan=2,
            sticky="ew", pady=(0, 12)
        )

        ctk.CTkLabel(
            body,
            text="Higher = stricter matching (fewer false positives)",
            text_color=self.MUTED,
            font=ctk.CTkFont(size=11),
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 12))

        # --- Confirmation frames ---
        ctk.CTkLabel(
            body,
            text="Confirmation Frames",
            text_color=self.TEXT,
            font=ctk.CTkFont(size=13),
        ).grid(row=3, column=0, sticky="w", pady=(0, 4))

        self._conf_label = ctk.CTkLabel(
            body,
            text=str(self._conf_frames_val),
            text_color=self.PRIMARY,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._conf_label.grid(row=3, column=1, sticky="e")

        self._conf_slider = ctk.CTkSlider(
            body,
            from_=1,
            to=15,
            number_of_steps=14,
            command=self._on_conf_change,
        )
        self._conf_slider.set(self._conf_frames_val)
        self._conf_slider.grid(
            row=4, column=0, columnspan=2,
            sticky="ew", pady=(4, 4)
        )

        ctk.CTkLabel(
            body,
            text="Frames needed to confirm identity before marking attendance",
            text_color=self.MUTED,
            font=ctk.CTkFont(size=11),
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # --- Registration images ---
        ctk.CTkLabel(
            body,
            text="Registration Images",
            text_color=self.TEXT,
            font=ctk.CTkFont(size=13),
        ).grid(row=6, column=0, sticky="w", pady=(6, 4))

        self._reg_images_label = ctk.CTkLabel(
            body,
            text=str(self._reg_images_val),
            text_color=self.PRIMARY,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._reg_images_label.grid(row=6, column=1, sticky="e")

        self._reg_images_slider = ctk.CTkSlider(
            body,
            from_=3,
            to=20,
            number_of_steps=17,
            command=self._on_reg_images_change,
        )
        self._reg_images_slider.set(self._reg_images_val)
        self._reg_images_slider.grid(
            row=7, column=0, columnspan=2,
            sticky="ew", pady=(4, 4)
        )

        ctk.CTkLabel(
            body,
            text="Number of face images to capture during registration (recommended: 5)",
            text_color=self.MUTED,
            font=ctk.CTkFont(size=11),
        ).grid(row=8, column=0, columnspan=2, sticky="w", pady=(0, 4))

    # ==================================================
    # CAMERA SECTION
    # ==================================================

    def _build_camera_section(self):
        body = self._section("📷  Camera")
        body.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            body,
            text="Camera Index",
            text_color=self.TEXT,
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=0, sticky="w")

        self._camera_entry = ctk.CTkEntry(
            body,
            width=80,
            placeholder_text="0",
        )
        self._camera_entry.insert(0, str(self._camera_val))
        self._camera_entry.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            body,
            text="0 = default webcam, 1 = second camera, etc.",
            text_color=self.MUTED,
            font=ctk.CTkFont(size=11),
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

    # ==================================================
    # SECURITY SECTION
    # ==================================================

    def _build_security_section(self):
        body = self._section("🔐  Security")
        body.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            body,
            text="New Admin Password",
            text_color=self.TEXT,
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self._new_pw_entry = ctk.CTkEntry(
            body,
            show="*",
            placeholder_text="Leave blank to keep current",
        )
        self._new_pw_entry.grid(
            row=0, column=1, sticky="ew", pady=(0, 6)
        )

        ctk.CTkLabel(
            body,
            text="Confirm Password",
            text_color=self.TEXT,
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, sticky="w", pady=(0, 6))

        self._confirm_pw_entry = ctk.CTkEntry(
            body,
            show="*",
            placeholder_text="Repeat new password",
        )
        self._confirm_pw_entry.grid(
            row=1, column=1, sticky="ew", pady=(0, 6)
        )

    # ==================================================
    # DATABASE SECTION
    # ==================================================

    def _build_database_section(self):
        body = self._section("🗄   Database")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            body,
            text="⬆  Backup Database",
            fg_color=self.SUCCESS,
            hover_color="#15803D",
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._backup_database,
        ).grid(row=0, column=0, padx=(0, 6), pady=4, sticky="ew")

        ctk.CTkButton(
            body,
            text="⬇  Restore Database",
            fg_color="#7C3AED",
            hover_color="#5B21B6",
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._restore_database,
        ).grid(row=0, column=1, padx=(6, 0), pady=4, sticky="ew")

        ctk.CTkLabel(
            body,
            text="Backup copies the SQLite database to a chosen folder.",
            text_color=self.MUTED,
            font=ctk.CTkFont(size=11),
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

    # ==================================================
    # CALLBACKS
    # ==================================================

    def _on_threshold_change(self, value):
        self._threshold_val = round(float(value), 2)
        self._threshold_label.configure(
            text=f"{self._threshold_val:.2f}"
        )

    def _on_conf_change(self, value):
        self._conf_frames_val = int(value)
        self._conf_label.configure(
            text=str(self._conf_frames_val)
        )

    def _on_reg_images_change(self, value):
        self._reg_images_val = int(value)
        self._reg_images_label.configure(
            text=str(self._reg_images_val)
        )

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------

    def _save_settings(self):
        # Recognition
        set_setting("recognition_threshold", str(self._threshold_val))
        set_setting("confirmation_frames",   str(self._conf_frames_val))
        set_setting("registration_images",   str(self._reg_images_val))

        # Camera
        try:
            cam_idx = int(self._camera_entry.get().strip() or "0")
        except ValueError:
            cam_idx = 0
        set_setting("camera_index", str(cam_idx))

        # Password
        new_pw = self._new_pw_entry.get().strip()
        conf_pw = self._confirm_pw_entry.get().strip()

        if new_pw:
            if new_pw != conf_pw:
                messagebox.showerror(
                    "Error",
                    "Passwords do not match.",
                    parent=self,
                )
                return
            set_setting("admin_password", new_pw)

        messagebox.showinfo(
            "Settings Saved",
            "Settings have been saved successfully.",
            parent=self,
        )

        if self.on_save:
            self.on_save()

        self.destroy()

    # --------------------------------------------------
    # BACKUP
    # --------------------------------------------------

    def _backup_database(self):
        src = Path("database") / "attendance.db"
        if not src.exists():
            messagebox.showerror(
                "Error",
                "Database file not found.",
                parent=self,
            )
            return

        dest_dir = filedialog.askdirectory(
            title="Choose backup destination",
            parent=self,
        )
        if not dest_dir:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = Path(dest_dir) / f"attendance_backup_{timestamp}.db"

        shutil.copy2(str(src), str(dest))

        messagebox.showinfo(
            "Backup Successful",
            f"Database backed up to:\n{dest}",
            parent=self,
        )

    # --------------------------------------------------
    # RESTORE
    # --------------------------------------------------

    def _restore_database(self):
        src = filedialog.askopenfilename(
            title="Select backup .db file",
            filetypes=[("SQLite Database", "*.db")],
            parent=self,
        )
        if not src:
            return

        confirm = messagebox.askyesno(
            "Confirm Restore",
            "This will replace the current database.\n"
            "Are you sure?",
            parent=self,
        )
        if not confirm:
            return

        dest = Path("database") / "attendance.db"
        shutil.copy2(src, str(dest))

        messagebox.showinfo(
            "Restore Successful",
            "Database has been restored successfully.\n"
            "Please restart the application.",
            parent=self,
        )
