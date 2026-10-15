"""
login.py

Login window for Vision Attendance.
Accepts an optional on_success callback that is
called (with no arguments) after a successful login,
instead of showing the old placeholder messagebox.
"""

import customtkinter as ctk
from tkinter import messagebox

from database.database import get_setting


class LoginWindow(ctk.CTk):

    # Default credentials (can be overridden via Settings)
    DEFAULT_USER = "admin"
    DEFAULT_PASS = "admin123"

    def __init__(self, on_success=None):
        super().__init__()

        # Callback fired on successful login
        self.on_success = on_success

        # --------------------------------------------------
        # WINDOW
        # --------------------------------------------------
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Vision Attendance — Login")
        self.geometry("500x620")
        self.resizable(False, False)
        self.configure(fg_color="#07111F")

        # Centre on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 500) // 2
        y = (self.winfo_screenheight() - 620) // 2
        self.geometry(f"500x620+{x}+{y}")

        # Bring window to front
        self.lift()
        self.attributes("-topmost", True)
        self.after_idle(self.attributes, "-topmost", False)
        self.focus_force()

        self._build_ui()

        # Enter key triggers login
        self.bind("<Return>", lambda _: self._on_login())

    # --------------------------------------------------
    # BUILD UI
    # --------------------------------------------------

    def _build_ui(self):

        # ---- Logo / title ----
        ctk.CTkLabel(
            self,
            text="◉",
            font=ctk.CTkFont(size=48),
            text_color="#2563EB",
        ).pack(pady=(52, 4))

        ctk.CTkLabel(
            self,
            text="VISION ATTENDANCE",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#F8FAFC",
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            self,
            text="AI Face Recognition Attendance System",
            font=ctk.CTkFont(size=13),
            text_color="#94A3B8",
        ).pack(pady=(0, 32))

        # ---- Card ----
        card = ctk.CTkFrame(
            self,
            width=400,
            corner_radius=16,
            fg_color="#101E33",
            border_width=1,
            border_color="#22324A",
        )
        card.pack(padx=50)
        card.pack_propagate(False)
        card.configure(height=290)

        # Username
        ctk.CTkLabel(
            card,
            text="Username",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#94A3B8",
            anchor="w",
        ).pack(anchor="w", padx=28, pady=(28, 4))

        self.username = ctk.CTkEntry(
            card,
            width=344,
            height=42,
            placeholder_text="Enter username",
            font=ctk.CTkFont(size=13),
        )
        self.username.pack()
        self.username.focus()

        # Password
        ctk.CTkLabel(
            card,
            text="Password",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#94A3B8",
            anchor="w",
        ).pack(anchor="w", padx=28, pady=(16, 4))

        self.password = ctk.CTkEntry(
            card,
            width=344,
            height=42,
            show="*",
            placeholder_text="Enter password",
            font=ctk.CTkFont(size=13),
        )
        self.password.pack()

        # Show password toggle
        self.show_var = ctk.BooleanVar()
        ctk.CTkCheckBox(
            card,
            text="Show Password",
            variable=self.show_var,
            command=self._toggle_password,
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8",
        ).pack(anchor="w", padx=28, pady=(12, 0))

        # ---- Error label ----
        self._error_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#F87171",
        )
        self._error_label.pack(pady=(10, 0))

        # ---- Login button ----
        self._login_btn = ctk.CTkButton(
            self,
            text="Login",
            width=400,
            height=46,
            corner_radius=10,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._on_login,
        )
        self._login_btn.pack(padx=50, pady=(16, 0))

        # Hint
        ctk.CTkLabel(
            self,
            text="Default: admin / admin123",
            font=ctk.CTkFont(size=11),
            text_color="#475569",
        ).pack(pady=(10, 0))

    # --------------------------------------------------
    # TOGGLE PASSWORD
    # --------------------------------------------------

    def _toggle_password(self):
        self.password.configure(
            show="" if self.show_var.get() else "*"
        )

    # --------------------------------------------------
    # LOGIN
    # --------------------------------------------------

    def _on_login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()

        # Read password from settings if it was changed
        stored_pw = get_setting("admin_password", self.DEFAULT_PASS)

        if username == self.DEFAULT_USER and password == stored_pw:
            # Success — destroy window then fire callback
            self.destroy()
            if self.on_success:
                self.on_success()
        else:
            self._error_label.configure(
                text="❌  Invalid username or password. Please try again."
            )
            self.password.delete(0, "end")
            self.password.focus()

    # --------------------------------------------------
    # Keep old attribute name for backward compatibility
    # --------------------------------------------------

    @property
    def login(self):
        return self._on_login