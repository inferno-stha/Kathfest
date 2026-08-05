# 🎓 Smart Student Attendance System Using Face Recognition

> **A fully integrated, runnable Flask web application** that combines a Tkinter-inspired UI, OpenCV face recognition, and SQLite database into a single, coherent attendance management system.
>
> **Version 2.0** — now with automatic attendance, region-of-interest (ROI) detection, duplicate-face prevention, confidence scoring, graphical reports, and a face-search feature.

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

### 📊 Dashboard
- **Total Students** count (from database)
- **Present Today** count (from attendance table)
- **Attendance Percentage** (auto-calculated)
- **Face Registered** count — students with a stored face encoding
- Quick action buttons to navigate to Students, Attendance, Face Search, Reports
- **Graphical analytics** (Chart.js): attendance by department, attendance by semester, last 14 days trend, monthly totals
- **Top Absent Students** table — the most frequently absent students
- All numbers and charts refresh automatically on page load

### 👨‍🎓 Students Module
- **Add Student** — Insert new student records into SQLite with **server-side + client-side validation** (name, roll number, department, semester)
- **Edit Student** — Update name, roll number, department, semester
- **Delete Student** — Remove student (cascades to attendance records)
- **Search/Filter** — Filter by department, semester, or text search (name/roll) — real-time without a page reload
- **Face Registration** — Capture face encoding via webcam and store in database
- **Duplicate Face Guard** — A face that already matches another registered student is rejected, preventing duplicate registrations
- **Toast notifications** and inline field hints for every action

### 📷 Attendance Module (Face Recognition)
- **Start Attendance** — One button starts the camera, opens a camera session, and begins **fully automatic recognition**
- **Automatic Recognition** — Detects a face, generates a 128-d encoding, and compares it against stored encodings continuously
- **Auto-Marking** — Matched students are marked Present automatically in the database with their **confidence score**
- **Region of Interest (ROI) Detection** — Recognition only runs inside the on-screen green ROI box, so you can aim the camera and ignore background faces
- **Confidence Scoring** — Every recognition result shows `confidence = (1 − face_distance) × 100`; results below the confidence threshold are ignored
- **Session Summary** — Each attendance run records a `camera_sessions` entry with total recognized and unknown faces
- **Duplicate Prevention** — Students already marked present in the current session are not re-marked
- **Live recognition table** — every recognized student appears in the table in real time with confidence
- **Warning Messages** — No face, face outside ROI, multiple faces, unknown face — all shown to user

### 🔍 Face Search Module (NEW)
- **Search a person by face** — point the camera at any person and find their student record
- Matches against the registered face database and shows name, roll, department, semester, match confidence, and attendance status for today

### 📄 Reports
- **Individual graphical report** — pick a student and see total/present/absent/percentage plus a Pie chart, Monthly bar chart, and Weekly line chart
- **Daily Report** — Attendance records filtered by date, department, semester, and status
- **Export to PNG / PDF** — download any chart as an image or a combined PDF report
- **Export CSV** — Download all records or today-only as CSV files

### 🔐 Login
- Session-based authentication with Flask sessions
- Demo credentials: `admin / admin`
- Redirects to Dashboard on success

### ℹ About
- Project description, version, team info (updated to Version 2.0)

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
├── migrate_db.py              # Standalone database migration script (--check)
├── change.txt                 # Change log vs. the original program
├── README.md                  # This file
├── TODO.md                    # Task checklist
├── PROGRESS.md                # Progress tracking
├── ARCHITECTURE.md            # System architecture documentation
│
├── backend/                   # Face recognition & camera modules
│   ├── __init__.py
│   ├── face_recognizer.py     # Face detection, ROI, encoding, comparison, duplicate check
│   ├── camera.py              # Camera stream management
│   ├── attendance.py          # Attendance + face recognition integration + camera sessions
│   ├── validation.py          # Input validation (name, roll, department, semester)
│   └── utils.py               # Utility functions
│
├── database/                  # Database layer
│   ├── __init__.py
│   ├── db.py                  # SQLite CRUD operations (merged) + stats & filter queries
│   ├── models.py              # OOP wrappers (Student, Attendance classes)
│   └── attendance.db          # SQLite database (auto-created/migrated)
│
├── UI/                        # Frontend assets
│   ├── templates/             # Jinja2 HTML templates
│   │   ├── base.html          # Main layout (sidebar, header, toast container)
│   │   ├── login.html         # Login page
│   │   ├── dashboard.html     # Dashboard with stats + charts
│   │   ├── students.html      # Student management with validation + face capture
│   │   ├── attendance.html    # Automatic attendance with ROI overlay + session summary
│   │   ├── face_search.html   # NEW: search a person by face
│   │   ├── reports.html       # Individual graphical reports + PNG/PDF export
│   │   └── about.html         # Project info
│   │
│   └── static/                # Static assets
│       ├── css/style.css      # Full stylesheet (blue theme + v2 components)
│       ├── js/script.js       # Global JavaScript helpers (toasts, validation, spinner)
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
- Click **"Add Student"** and fill in the details (fields are validated as you type)
- After adding, select a student and click **📷** (Camera icon) to capture their face
- Click **"Start Camera"**, then **"Capture Face"** to register their face encoding
- If a face is already registered for another student, the system rejects it

### 3. Take Attendance (automatic)
- Go to **Attendance** page
- Click **"Start Attendance"** to activate your webcam — recognition runs automatically
- Position the person inside the green **ROI box** on the camera preview
- The system continuously detects the face, computes the match confidence, and marks the student present
- The live recognition table and session summary update in real time
- Click **"Stop Attendance"** to end the session and save the summary

### 4. Face Search
- Go to **Face Search** page
- Click **"Start Camera"**, position the person in the ROI box
- Click **"Search Face"** to find their student record and today's attendance status

### 5. View Reports
- Go to **Reports** page
- Pick a student to see their graphical report (Pie, Monthly, Weekly)
- Click **"Export PNG / PDF"** to download charts, or **"Export CSV"** for attendance records

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Root — redirects to login or dashboard |
| GET/POST | `/login` | Login page and authentication |
| GET | `/logout` | Log out and clear session |
| GET | `/dashboard` | Dashboard with attendance stats + charts |
| GET | `/students` | Student management page |
| POST | `/api/students/filter` | Filter/search students by name, roll, department, semester (JSON) |
| POST | `/api/students/add` | Add a new student (validated) |
| POST | `/api/students/update` | Update student info (validated) |
| POST | `/api/students/delete` | Delete a student |
| GET | `/api/students/stats/<id>` | Per-student attendance stats (total/present/absent/percentage) |
| POST | `/api/capture-face` | Capture face encoding for a student (with duplicate-face guard) |
| GET | `/attendance` | Attendance page with camera + ROI |
| GET | `/api/attendance/data` | Get today's attendance (JSON) |
| POST | `/api/attendance/mark` | Mark attendance via face recognition (image) |
| POST | `/api/attendance/mark-by-name` | Manual attendance by name |
| GET | `/api/attendance/all` | All attendance records (JSON) |
| GET | `/api/attendance/student/<id>` | Student-wise attendance |
| POST | `/api/attendance/session/start` | Start a camera session (returns session_id) |
| POST | `/api/attendance/session/end` | End a camera session and store the summary |
| GET | `/face-search` | Face Search page |
| POST | `/api/face-search` | Search a student by face image |
| GET | `/api/dashboard/attendance-by-department` | Present/absent counts grouped by department |
| GET | `/api/dashboard/attendance-by-semester` | Present/absent counts grouped by semester |
| GET | `/api/dashboard/daily?days=N` | Daily present/absent counts for the last N days |
| GET | `/api/dashboard/monthly?months=N` | Monthly present/absent counts for the last N months |
| GET | `/api/dashboard/top-absent` | Most frequently absent students |
| GET | `/reports` | Reports page (individual graphical report) |
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

- [x] **Analytics dashboard** — Charts showing attendance trends over time (department, semester, daily, monthly)
- [x] **Export to PDF** — Generate formatted PDF reports (per-student)
- [ ] **Password hashing** — Replace plain-text password with bcrypt/argon2
- [ ] **Multiple face encodings** — Store multiple samples per student for better accuracy
- [ ] **Live video streaming** — Stream the OpenCV feed to the browser in real time
- [ ] **Student self-registration** — Let students register their face at a kiosk
- [ ] **Email/SMS notifications** — Notify parents of absent students
- [ ] **Authentication with database** — Replace dummy login with users table
- [ ] **Docker deployment** — Containerized setup for easy deployment
