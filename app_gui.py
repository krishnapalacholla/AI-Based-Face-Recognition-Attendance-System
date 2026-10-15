"""
app_gui.py

GUI entry point for Vision Attendance.

Flow:  SplashScreen  →  LoginWindow  →  AttendanceDashboard
"""

from gui.splash import SplashScreen
from gui.login import LoginWindow
from gui.dashboard import AttendanceDashboard


# ==================================================
# OPEN DASHBOARD
# ==================================================

def open_dashboard():
    dashboard = AttendanceDashboard()
    dashboard.mainloop()


# ==================================================
# OPEN LOGIN
# ==================================================

def open_login():
    """
    Show the login window.
    Pass open_dashboard as the on_success callback
    so it launches automatically after a correct login.
    """
    login = LoginWindow(on_success=open_dashboard)
    login.mainloop()


# ==================================================
# MAIN
# ==================================================

def main():
    splash = SplashScreen(on_complete=open_login)
    splash.mainloop()


if __name__ == "__main__":
    main()