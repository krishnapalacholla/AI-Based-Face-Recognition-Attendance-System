"""
analytics.py

Analytics window for the Face Recognition
Attendance System.

Displays:
  - Daily attendance chart (last 14 days)
  - Per-user attendance bar chart
  - Monthly summary
  - Stat cards: total records, active users, avg daily
"""

import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import customtkinter as ctk
import matplotlib
matplotlib.use("Agg")                       # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


DATABASE_PATH = Path("database") / "attendance.db"


# ==================================================
# COLOURS (shared with dashboard)
# ==================================================

APP_BG   = "#07111F"
CARD_BG  = "#101E33"
BORDER   = "#22324A"
TEXT     = "#F8FAFC"
MUTED    = "#94A3B8"
PRIMARY  = "#2563EB"
ACCENT   = "#0EA5E9"
SUCCESS  = "#16A34A"


class AnalyticsWindow(ctk.CTkToplevel):
    """
    Analytics dashboard displaying attendance charts
    and summary statistics.
    """

    def __init__(self, parent):
        super().__init__(parent)

        # --------------------------------------------------
        # WINDOW
        # --------------------------------------------------

        self.title("Analytics — Attendance Insights")
        self.geometry("1000x720")
        self.minsize(860, 600)
        self.configure(fg_color=APP_BG)
        self.grab_set()
        self.focus_force()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------

        header = ctk.CTkFrame(
            self,
            fg_color=CARD_BG,
            corner_radius=0,
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="📊  Attendance Analytics",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT,
        ).grid(row=0, column=0, padx=28, pady=20, sticky="w")

        # Refresh button
        ctk.CTkButton(
            header,
            text="↺  Refresh",
            width=120,
            height=36,
            fg_color=PRIMARY,
            hover_color="#1D4ED8",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._load_data,
        ).grid(row=0, column=1, padx=24, pady=16, sticky="e")

        # --------------------------------------------------
        # SCROLLABLE BODY
        # --------------------------------------------------

        self.body = ctk.CTkScrollableFrame(
            self,
            fg_color=APP_BG,
            corner_radius=0,
        )
        self.body.grid(
            row=1, column=0,
            sticky="nsew",
            padx=0, pady=0,
        )
        self.body.grid_columnconfigure(0, weight=1)

        self._body_row = 0

        # --------------------------------------------------
        # LOAD & RENDER
        # --------------------------------------------------

        self._load_data()

    # ==================================================
    # DATA LOADING
    # ==================================================

    def _load_data(self):
        """Fetch records from SQLite and re-render charts."""

        # Clear body
        for widget in self.body.winfo_children():
            widget.destroy()
        self._body_row = 0

        records = self._fetch_records()

        if not records:
            ctk.CTkLabel(
                self.body,
                text=(
                    "No attendance records found.\n\n"
                    "Start face recognition to mark attendance."
                ),
                text_color=MUTED,
                font=ctk.CTkFont(size=16),
                justify="center",
            ).grid(row=0, column=0, pady=100)
            return

        self._render_stat_cards(records)
        self._render_daily_chart(records)
        self._render_user_chart(records)

    # --------------------------------------------------
    # FETCH
    # --------------------------------------------------

    def _fetch_records(self):
        if not DATABASE_PATH.exists():
            return []
        try:
            conn = sqlite3.connect(str(DATABASE_PATH))
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, date, time "
                "FROM attendance ORDER BY date DESC, time DESC"
            )
            rows = cursor.fetchall()
            conn.close()
            return rows
        except sqlite3.Error:
            return []

    # ==================================================
    # STAT CARDS
    # ==================================================

    def _render_stat_cards(self, records):
        cards_frame = ctk.CTkFrame(
            self.body,
            fg_color="transparent",
        )
        cards_frame.grid(
            row=self._body_row, column=0,
            padx=24, pady=(20, 0), sticky="ew"
        )
        self._body_row += 1

        for col in range(4):
            cards_frame.grid_columnconfigure(col, weight=1, uniform="sc")

        # Stats
        total       = len(records)
        users       = len({r[1] for r in records})
        today_str   = datetime.now().strftime("%Y-%m-%d")
        today_count = sum(1 for r in records if r[2] == today_str)

        dates = sorted({r[2] for r in records})
        avg_daily = round(total / max(len(dates), 1), 1)

        stats = [
            ("📋 Total Records",   str(total),        PRIMARY),
            ("👤 Unique Users",    str(users),         ACCENT),
            ("📅 Present Today",   str(today_count),   SUCCESS),
            ("📈 Daily Average",   str(avg_daily),     "#F59E0B"),
        ]

        for col, (label, value, color) in enumerate(stats):
            card = ctk.CTkFrame(
                cards_frame,
                fg_color=CARD_BG,
                corner_radius=12,
                border_width=1,
                border_color=BORDER,
                height=100,
            )
            card.grid(
                row=0, column=col,
                padx=(0 if col == 0 else 8,
                      0 if col == 3 else 8),
                sticky="nsew"
            )
            card.grid_propagate(False)

            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=MUTED,
            ).pack(pady=(16, 2))

            ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color=color,
            ).pack()

    # ==================================================
    # DAILY CHART — last 14 days
    # ==================================================

    def _render_daily_chart(self, records):
        # Aggregate
        daily: dict = defaultdict(int)
        for _, _, date, _ in records:
            daily[date] += 1

        # Last 14 days
        today = datetime.now().date()
        days  = [
            (today - timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(13, -1, -1)
        ]
        counts = [daily.get(d, 0) for d in days]
        dates_dt = [datetime.strptime(d, "%Y-%m-%d") for d in days]

        frame = self._chart_card("📅  Daily Attendance — Last 14 Days")

        fig = Figure(figsize=(8, 2.8), dpi=100, facecolor=CARD_BG)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(CARD_BG)

        ax.bar(
            dates_dt, counts,
            color=PRIMARY,
            width=0.6,
            zorder=3,
        )
        ax.plot(
            dates_dt, counts,
            color=ACCENT,
            linewidth=1.8,
            marker="o",
            markersize=4,
            zorder=4,
        )

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        fig.autofmt_xdate(rotation=30, ha="right")

        ax.set_ylim(bottom=0)
        ax.yaxis.set_major_locator(
            plt.MaxNLocator(integer=True)
        )

        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER)

        ax.tick_params(colors=MUTED, labelsize=9)
        ax.set_ylabel("Attendance", color=MUTED, fontsize=10)
        ax.grid(
            axis="y",
            color=BORDER,
            linewidth=0.5,
            zorder=0,
        )
        fig.tight_layout(pad=1.2)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(
            fill="both", expand=True, padx=16, pady=(0, 16)
        )

    # ==================================================
    # USER CHART — top 10 users by attendance
    # ==================================================

    def _render_user_chart(self, records):
        user_counts: dict = defaultdict(int)
        for _, name, _, _ in records:
            user_counts[name] += 1

        sorted_users = sorted(
            user_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        if not sorted_users:
            return

        names  = [u[0] for u in sorted_users]
        counts = [u[1] for u in sorted_users]

        frame = self._chart_card("👥  Attendance by User (Top 10)")

        fig = Figure(figsize=(8, 2.8), dpi=100, facecolor=CARD_BG)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(CARD_BG)

        colors = [PRIMARY] + [ACCENT] * (len(names) - 1)
        bars = ax.barh(names[::-1], counts[::-1], color=colors[::-1], height=0.55)

        for bar, val in zip(bars, counts[::-1]):
            ax.text(
                bar.get_width() + 0.1,
                bar.get_y() + bar.get_height() / 2,
                str(val),
                va="center",
                color=TEXT,
                fontsize=9,
            )

        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER)

        ax.tick_params(colors=MUTED, labelsize=9)
        ax.set_xlabel("Days Present", color=MUTED, fontsize=10)
        ax.grid(
            axis="x",
            color=BORDER,
            linewidth=0.5,
            zorder=0,
        )
        ax.set_xlim(right=max(counts) * 1.15)
        fig.tight_layout(pad=1.2)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(
            fill="both", expand=True, padx=16, pady=(0, 16)
        )

    # ==================================================
    # CHART CARD HELPER
    # ==================================================

    def _chart_card(self, title: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            self.body,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=BORDER,
        )
        card.grid(
            row=self._body_row, column=0,
            padx=24, pady=(16, 0), sticky="ew"
        )
        self._body_row += 1

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=18, pady=(14, 6))

        sep = ctk.CTkFrame(card, height=1, fg_color=BORDER)
        sep.pack(fill="x", padx=18, pady=(0, 8))

        return card
