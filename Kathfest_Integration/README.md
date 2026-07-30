# 🎓 Smart Student Attendance System Using Face Recognition

> **A fully integrated, runnable Flask web application** that combines a Tkinter-inspired UI, OpenCV face recognition, and SQLite database into a single, coherent attendance management system.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Folder Structure](#folder-structure)
- [Usage Guide](#usage-guide)
- [API Endpoints](#api-endpoints)
- [Team Members](#team-members)
- [Future Improvements](#future-improvements)

---

## Overview

This project was built for the **KathFest Hackathon** by integrating code from three separate modules:

| Original Module | Content | What was done |
|---|---|---|
| `backend/` | OpenCV camera, face detection, attendance CRUD | Refactored into `backend/face_recognizer.py`, `backend/camera.py`, `backend/attendance.py` |
| `UI/` | Tkinter desktop application with sidebar navigation, login, dashboard, etc. | Converted to Flask+Jinja2 templates (preserving the original blue theme and layout) |
| `database/` | SQLite schema, face encoding serialization, data access | Consolidated into `database/db.py` and `database/models.py` |
| `web_based/` | In-progress Flask app with dummy data stubs | Replaced with real implementation — all stubs are now connected to the database and OpenCV |

Instead of rewriting from scratch, we analyzed, merged, and extended the existing code. The final result runs from a single command: `python app.py`.

---

## Features

### 🔐 Login
- Session-based authentication with Flask sessions
- Demo credentials: `admin / admin`
- Redirects to Dashboard on success

### 📊 Dashboard
- **Total Students** count (from database)
- **Present Today** count (from attendance table)
- **Attendance Percentage** (auto-calculated)
- Quick action buttons to navigate to Students, Attendance, Reports

### 👨‍🎓 Students Module
- **Add Student** — Insert new student records into SQLite
- **Edit Student** — Update name, roll number, department, semester
- **Delete Student** — Remove student (cascades to attendance records)
- **Search/Filter** — Filter by department, semester, or text search (name/roll)
- **Face Registration** — Capture face encoding via webcam and store in database

### 📷 Attendance Module (Face Recognition)
- **Start Camera** — Activates browser's webcam via MediaDevices API
- **Mark Attendance** — Captures a video frame, sends to backend, runs OpenCV face recognition
- **Automatic Recognition** — Detects face, generates 128-d encoding, compares against stored encodings
- **Auto-Marking** — If matched, attendance is marked as Present in the database
- **Duplicate Prevention** — Already-present students are not re-marked
- **Warning Messages** — No face, multiple faces, unknown face — all shown to user

### 📄 Reports
- **Daily Report** — Attendance records filtered by date
- **Student-wise Report** — Per-student attendance history
- **Export CSV** — Download all records or today-only as CSV files

### ℹ About
- Project description, version, team info

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | Flask 3.0 (Python) |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Templating** | Jinja2 |
| **Database** | SQLite 3 |
| **Computer Vision** | OpenCV (`cv2`) |
| **Face Recognition** | `face_recognition` library (dlib + ResNet) |
| **Face Encoding** | 128-dimensional numpy arrays serialized as BLOBs |

---

## Installation

### Prerequisites

1. **Python 3.9+** (tested with Python 3.14)
2. **Webcam** (built-in or USB)
3. **Visual C++ Build Tools** (Windows) or **CMake** (for dlib)

### Step 1: Clone the repository

```bash
git clone <repository-url>
cd Kathfest_Integration
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

> **Note on face_recognition / dlib installation:**
> The `face_recognition` library requires `dlib`, which needs C++ compilation tools.
> - **Windows:** Install CMake (`pip install cmake`) and Visual C++ Build Tools
> - **macOS/Linux:** Usually works with `pip install dlib` directly
>
> If you encounter issues, you can still run the app for all non-camera features.
> The face recognition endpoints will return appropriate error messages.

### Step 3: Initialize the database

The database is automatically initialized when you first run the app.
No manual setup is required.

---

## Running the Project

### Development Server

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

### Login Credentials

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin` |

---

### Running Without a Webcam

The app works without a webcam! You can:

1. **Add students** manually via the Students page
2. **Mark attendance manually** using the attendance page's API
3. **View reports** and export CSV

The face recognition features will show appropriate warnings when no camera is available.

---

## Folder Structure

```
Kathfest_Integration/
│
├── app.py                     # Flask entry point — run this!
├── routes.py                  # All Flask route definitions
├── config.py                  # Central configuration (merged from all sources)
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── TODO.md                    # Task checklist
├── PROGRESS.md                # Progress tracking
├── ARCHITECTURE.md            # System architecture documentation
│
├── backend/                   # Face recognition & camera modules
│   ├── __init__.py
│   ├── face_recognizer.py     # Face detection, encoding, comparison
│   ├── camera.py              # Camera stream management
│   ├── attendance.py          # Attendance + face recognition integration
│   └── utils.py               # Utility functions
│
├── database/                  # Database layer
│   ├── __init__.py
│   ├── db.py                  # SQLite CRUD operations (merged)
│   ├── models.py              # OOP wrappers (Student, Attendance classes)
│   └── attendance.db          # SQLite database (auto-created)
│
├── UI/                        # Frontend assets
│   ├── templates/             # Jinja2 HTML templates
│   │   ├── base.html          # Main layout (sidebar, header)
│   │   ├── login.html         # Login page
│   │   ├── dashboard.html     # Dashboard with stats
│   │   ├── students.html      # Student management
│   │   ├── attendance.html    # Camera + face recognition
│   │   ├── reports.html       # Reports and CSV export
│   │   └── about.html         # Project info
│   │
│   └── static/                # Static assets
│       ├── css/style.css      # Full stylesheet (blue theme)
│       ├── js/script.js       # Global JavaScript
│       └── images/            # Images directory
│
├── web_based/                 # Original Flask app (reference only)
│
└── deployment/                # Deployment configuration
```

---

## Usage Guide

### 1. Login
Open `http://localhost:5000` in your browser. Enter `admin` / `admin`.

### 2. Add Students
- Go to **Students** page
- Click **"Add Student"** and fill in the details
- After adding, select a student and click **📷** (Camera icon) to capture their face
- Click **"Start Camera"**, then **"Capture Face"** to register their face encoding

### 3. Take Attendance
- Go to **Attendance** page
- Click **"Start Camera"** to activate your webcam
- When a student is in front of the camera, click **"Mark Attendance"**
- The system will automatically recognize the student and mark them present
- The table below updates in real time

### 4. View Reports
- Go to **Reports** page to see statistics
- Click **"Export CSV"** to download attendance records

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Root — redirects to login or dashboard |
| GET/POST | `/login` | Login page and authentication |
| GET | `/logout` | Log out and clear session |
| GET | `/dashboard` | Dashboard with attendance stats |
| GET | `/students` | Student management page |
| POST | `/api/students/filter` | Filter/search students (JSON) |
| POST | `/api/students/add` | Add a new student |
| POST | `/api/students/update` | Update student info |
| POST | `/api/students/delete` | Delete a student |
| POST | `/api/capture-face` | Capture face encoding for a student |
| GET | `/attendance` | Attendance page with camera |
| GET | `/api/attendance/data` | Get today's attendance (JSON) |
| POST | `/api/attendance/mark` | Mark attendance via face recognition (image) |
| POST | `/api/attendance/mark-by-name` | Manual attendance by name |
| GET | `/api/attendance/all` | All attendance records (JSON) |
| GET | `/api/attendance/student/<id>` | Student-wise attendance |
| GET | `/reports` | Reports page |
| GET | `/api/export-csv` | Download CSV attendance report |
| GET | `/about` | About page |

---

## Team Members

| Role | Responsibility |
|---|---|
| **Frontend Developer** | HTML templates, CSS styling, JavaScript interactions |
| **Backend Developer** | OpenCV face recognition, camera integration, Flask routes |
| **Database Developer** | SQLite schema, CRUD operations, data integrity |
| **Integration Developer** | Merged all modules into one working application |

---

## Future Improvements

- [ ] **Password hashing** — Replace plain-text password with bcrypt/argon2
- [ ] **Multiple face encodings** — Store multiple samples per student for better accuracy
- [ ] **Live video streaming** — Stream the OpenCV feed to the browser in real time
- [ ] **Student self-registration** — Let students register their face at a kiosk
- [ ] **Email/SMS notifications** — Notify parents of absent students
- [ ] **Analytics dashboard** — Charts showing attendance trends over time
- [ ] **Export to PDF** — Generate formatted PDF reports
- [ ] **Authentication with database** — Replace dummy login with users table
- [ ] **Docker deployment** — Containerized setup for easy deployment
