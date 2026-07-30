# Architecture — Smart Student Attendance System

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    BROWSER (Client)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Dashboard │  │ Students │  │Attendance│  │ Reports  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │              │              │              │        │
│  ┌────┴──────────────┴──────────────┴──────────────┴────┐  │
│  │              Jinja2 Templates (HTML)                  │  │
│  └─────────────────────────┬────────────────────────────┘  │
│                            │                                │
│  ┌─────────────────────────┴────────────────────────────┐  │
│  │              CSS + JavaScript                         │  │
│  └─────────────────────────┬────────────────────────────┘  │
└─────────────────────────────┼──────────────────────────────┘
                              │ HTTP (GET/POST)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FLASK BACKEND (Server)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                     routes.py                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │   │
│  │  │  /login  │  │/dashboard│  │  /api/students/  │   │   │
│  │  │  /logout │  │/students │  │  /api/attendance │   │   │
│  │  │          │  │/reports  │  │  /api/camera/*   │   │   │
│  │  │          │  │/about    │  │  /api/export-csv │   │   │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                │
│  ┌─────────────────────────┴────────────────────────────┐  │
│  │              Session Management                       │  │
│  │         (Flask sessions - cookie-based)               │  │
│  └─────────────────────────┬────────────────────────────┘  │
│                            │                                │
│  ┌─────────────────────────┴────────────────────────────┐  │
│  │              Sample Data (in-memory lists)            │  │
│  │    ↓ (Database Developer replaces with SQLite)        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ (Future Integration)
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER (Future)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                     SQLite                            │   │
│  │  students(id, student_id, name, roll, dept, sem,     │   │
│  │           face_encoding)                              │   │
│  │  attendance(id, student_id, date, time, status)      │   │
│  │  users(id, username, password_hash)                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              FACE RECOGNITION LAYER (Future)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  OpenCV + face_recognition library                    │   │
│  │  1. Capture frame from camera                         │   │
│  │  2. Detect face(s) in frame                           │   │
│  │  3. Compute 128-d face encoding                        │   │
│  │  4. Compare against stored encodings                  │   │
│  │  5. Return best match (or "unknown")                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Layer Description

### 1. Frontend (Browser)

- **Jinja2 Templates** — HTML files in `templates/` that render dynamic content using Flask's template engine. `base.html` provides the common layout (sidebar + header), and child pages override the `{% block content %}` section.
- **CSS** — `static/css/style.css` contains all styling using CSS variables that mirror the Tkinter `styles.py` color theme.
- **JavaScript** — `static/js/script.js` handles interactivity: filtering students via AJAX, showing modals, and placeholder functions for camera/face recognition.

### 2. Flask Backend (Server)

- **app.py** — Creates the Flask application, sets the secret key, imports routes.
- **routes.py** — Contains all route definitions:
  - **Page routes** (`/login`, `/dashboard`, `/students`, etc.) render Jinja2 templates.
  - **API routes** (`/api/students/filter`, `/api/students/add`, `/api/attendance/mark`, etc.) return JSON for AJAX calls.
- **Sessions** — Flask stores `session['user']` after login. Every page route checks this before rendering. Logout calls `session.clear()`.

### 3. Database Layer (Future — Database Developer)

- Currently using in-memory Python lists (`students_data`, `attendance_data`).
- The **Database Developer** will:
  - Create SQLite schema with `students`, `attendance`, and `users` tables.
  - Replace all sample data with real `SELECT`, `INSERT`, `DELETE` queries.
  - Hash passwords for login.

### 4. Face Recognition Layer (Future — Backend Developer)

- Currently all face recognition functions are placeholders.
- The **Backend Developer** will:
  - Integrate OpenCV for camera access.
  - Use `face_recognition` library for face detection and encoding.
  - Implement the `start_camera()`, `capture_face()`, and `recognize_face()` endpoints.
  - Stream video frames to the browser.

## Application Flow

```
User opens browser → /login (GET) → Login page
  ↓
Enters credentials → /login (POST) → Validate (admin/admin)
  ↓
Success → Store session['user'] → Redirect to /dashboard
  ↓
Navigate to /students → Filter by Department → Semester → Text
  ↓
Add Student → Modal form → POST /api/students/add
  ↓
Navigate to /attendance → Start Camera → Mark Attendance
  ↓
Navigate to /reports → View stats → Export CSV (placeholder)
  ↓
Click Logout → session.clear() → Redirect to /login
```

## Team Responsibilities

| Team Member | Focus Area | Files to Modify |
|-------------|-----------|-----------------|
| **Frontend Developer** | HTML/CSS/JS templates | `templates/*.html`, `static/css/*.css`, `static/js/*.js` |
| **Backend Developer** | Camera, face recognition, CSV | `routes.py` (camera/face endpoints), `static/js/script.js` |
| **Database Developer** | SQLite, queries, user auth | `routes.py` (data endpoints), `database/` folder |
| **Integration Developer** | Connect all modules, attendance flow | `routes.py` (mark_attendance), `templates/attendance.html` |

## Folder Structure

```
smart_attendance_web/
├── app.py                    # Flask configuration & entry point
├── routes.py                 # All route definitions (pages + API)
├── requirements.txt          # Python dependencies
├── README.md                 # Project overview & setup
├── TODO.md                   # Task checklist
├── PROGRESS.md               # Progress tracking
├── ARCHITECTURE.md           # This file
├── templates/                # Jinja2 HTML templates
│   ├── base.html             # Layout (sidebar + header + content block)
│   ├── login.html            # Login form
│   ├── dashboard.html        # Dashboard stats
│   ├── students.html         # Student table + filter + modal
│   ├── attendance.html       # Camera preview + attendance table
│   ├── reports.html          # Stats + CSV export
│   └── about.html            # Project info
├── static/
│   ├── css/style.css         # Stylesheet (matches Tkinter theme)
│   ├── js/script.js          # JavaScript (placeholders)
│   └── images/               # Image assets (empty)
├── backend/                  # Face recognition module (future)
├── database/                 # SQLite schema & queries (future)
└── assets/                   # Icons, fonts (future)
```
