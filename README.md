# Vision Attendance — AI Face Recognition System

A professional desktop attendance management system powered by **InsightFace** AI, built with Python and a modern dark-mode GUI.

---

## Features

| Category | Feature |
|---|---|
| **AI Core** | InsightFace / ArcFace real-time recognition |
| **Registration** | Guided webcam face capture (5 images) |
| **Recognition** | Multi-user, multi-face, confirmation-based |
| **Attendance** | Auto-mark, duplicate prevention, daily tracking |
| **Records** | Search, filter by date/name, delete individual records |
| **Export** | Styled Excel (.xlsx) + PDF reports |
| **Analytics** | Daily trend chart, per-user bar chart, stat cards |
| **Settings** | Threshold slider, confirmation frames, camera index, DB backup/restore |
| **GUI** | CustomTkinter dark-mode, sidebar navigation, 5 pages |
| **Database** | SQLite (local, no server needed) |

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch GUI application
```bash
python app_gui.py
```
Login: **admin** / **admin123**

### 3. Launch CLI application
```bash
python app.py
```

---

## Project Structure

```
FaceRecognitionAttendance/
├── app.py                      # CLI entry point
├── app_gui.py                  # GUI entry point
├── requirements.txt
│
├── gui/
│   ├── splash.py               # Splash screen
│   ├── login.py                # Login window
│   ├── dashboard.py            # Main dashboard (all pages)
│   ├── analytics.py            # Analytics charts window
│   ├── settings.py             # Settings window
│   └── about.py                # About window
│
├── registration/
│   ├── register_user.py        # Main registration flow
│   ├── image_capture.py        # Webcam capture helper
│   └── user_manager.py         # List / delete users
│
├── recognition/
│   ├── face_detector.py        # InsightFace wrapper
│   ├── face_encoder.py         # Embedding generation
│   └── face_recognizer.py      # Recognition + attendance
│
├── attendance/
│   ├── attendance_manager.py   # Mark / view attendance (SQLite)
│   ├── excel_manager.py        # Excel export (styled)
│   └── pdf_manager.py          # PDF export (ReportLab)
│
├── database/
│   ├── database.py             # Connection helper, settings
│   └── models.py               # AttendanceRecord, AdminUser
│
├── camera/
│   └── camera.py               # OpenCV webcam wrapper
│
├── dataset/                    # Captured face images (auto-created)
├── embeddings/                 # embeddings.pkl (auto-created)
├── attendance_exports/         # Excel / PDF exports (auto-created)
└── database/attendance.db      # SQLite database (auto-created)
```

---

## How It Works

### 1. Register a User
- Click **Register User** in the sidebar
- Enter a name and click **Open Camera & Register**
- A webcam window opens — press **SPACE** to capture 5 face images
- Face embeddings are auto-generated and saved

### 2. Mark Attendance
- Click **Live Recognition** in the sidebar
- Click **Start Recognition**
- The AI scans faces continuously
- After 5 confirmed frames, attendance is marked automatically
- Each person is only marked once per day

### 3. View & Export Records
- Click **Attendance Records** in the sidebar
- Search by name or filter by date
- Export to Excel or PDF with one click

### 4. Analytics
- Click **Analytics** for daily/user trend charts

### 5. Settings
- Adjust recognition threshold (higher = stricter)
- Set confirmation frames (higher = slower but more accurate)
- Backup / restore the database

---

## Tech Stack

| Library | Purpose |
|---|---|
| `insightface` | ArcFace face detection & embedding |
| `customtkinter` | Modern dark-mode GUI |
| `opencv-python` | Camera capture & frame rendering |
| `matplotlib` | Analytics charts |
| `openpyxl` | Excel export |
| `reportlab` | PDF export |
| `sqlite3` | Local database (built-in) |
| `Pillow` | Image processing |
| `bcrypt` | Password hashing |

---

## Default Credentials

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin123` |

Change the password in **Settings → Security**.
