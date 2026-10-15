import customtkinter as ctk


class SplashScreen(ctk.CTk):

    def __init__(self, on_complete=None):
        super().__init__()

        self.on_complete = on_complete

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Vision Attendance")
        self.geometry("700x420")
        self.resizable(False, False)

        self.configure(fg_color="#081221")

        # Bring window to front
        self.lift()
        self.attributes("-topmost", True)
        self.after_idle(self.attributes, "-topmost", False)
        self.focus_force()

        # ----------------------------
        # Title
        # ----------------------------

        ctk.CTkLabel(
            self,
            text="VISION ATTENDANCE",
            font=ctk.CTkFont(
                size=34,
                weight="bold"
            )
        ).pack(pady=(80, 10))

        ctk.CTkLabel(
            self,
            text="AI Face Recognition Attendance System",
            text_color="#9CA3AF",
            font=ctk.CTkFont(size=18)
        ).pack()

        self.status = ctk.CTkLabel(
            self,
            text="Initializing...",
            font=ctk.CTkFont(size=16)
        )

        self.status.pack(pady=(70, 20))

        self.progress = ctk.CTkProgressBar(
            self,
            width=420,
            height=18
        )

        self.progress.pack()

        self.progress.set(0)

        self.messages = [
            "Loading AI Engine...",
            "Loading InsightFace...",
            "Connecting Database...",
            "Preparing Camera...",
            "Starting Application..."
        ]

        self.step = 0

        self._timer_id = self.after(
            400,
            self.update_progress
        )

    # --------------------------------------------------

    def update_progress(self):
        if not self.winfo_exists():
            return

        if self.step < len(self.messages):
            self.status.configure(
                text=self.messages[self.step]
            )
            self.progress.set(
                (self.step + 1) / len(self.messages)
            )
            self.step += 1
            self._timer_id = self.after(
                700,
                self.update_progress
            )
        else:
            self._timer_id = self.after(
                300,
                self.finish
            )

    # --------------------------------------------------

    def finish(self):
        if not self.winfo_exists():
            return

        if hasattr(self, "_timer_id") and self._timer_id:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass

        cb = self.on_complete
        self.destroy()

        if cb:
            cb()