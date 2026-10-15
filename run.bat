@echo off
title Vision Attendance Launcher
cd /d "%~dp0"
echo Starting Vision Attendance...
".\.venv\Scripts\python.exe" app_gui.py
pause
