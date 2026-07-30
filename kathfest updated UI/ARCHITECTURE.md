# 🏗 ARCHITECTURE — Smart Student Attendance System

This document explains how the system is designed so any team member
(or new contributor) can understand how the pieces fit together.

---

## 1. System Overview

The application is a layered desktop system. Today, only the
**Frontend Layer** is implemented; the other layers are represented by
placeholder functions and empty folders (`backend/`, `database/`)
ready for the rest of the team.

```text
┌──────────────────────────────────────────────┐
│                    User                        │
└───────────────────────┬────────────────────────┘
                         │ interacts with
                         ▼
┌──────────────────────────────────────────────┐
│              Frontend Layer (Tkinter)           │
│   main.py / login.py / app.py / styles.py        │
└───────────────────────┬────────────────────────┘
                         │ calls placeholder methods
                         ▼
┌──────────────────────────────────────────────┐
│                Backend Layer                     │
│     Camera control, orchestration logic            │
│                (backend/)                            │
└───────────────────────┬────────────────────────┘
                         │ passes frames / requests
                         ▼
┌──────────────────────────────────────────────┐
│            Face Recognition Layer                 │
│   Face detection, encoding, matching                 │
│                (backend/)                              │
└───────────────────────┬────────────────────────┘
                         │ recognized student + timestamp
                         ▼
┌──────────────────────────────────────────────┐
│              Attendance Logic                      │
│   Decides Present/Absent, prevents duplicates          │
│                (backend/)                                │
└───────────────────────┬────────────────────────┘
                         │ read / write records
                         ▼
┌──────────────────────────────────────────────┐
│              Database Layer (SQLite)                 │
│         students, attendance, users tables               │
│                (database/)                                  │
└──────────────────────────────────────────────┘
```

---

## 2. Frontend Layer

**Location:** `main.py`, `login.py`, `app.py`, `styles.py`

- Built entirely with `tkinter` and `tkinter.ttk` — no external UI
  dependencies.
- Uses a **single `Tk()` instance** for the whole program. Screens are
  swapped by destroying and rebuilding widgets inside reusable Frame
  containers (`content_area` in `app.py`), instead of opening new
  windows. This is the standard, beginner-friendly pattern for
  multi-page Tkinter apps.
- `styles.py` centralizes all colors/fonts/icons so the UI has a
  single, consistent theme.
- All data the UI needs (student lists, attendance records) currently
  comes from hard-coded Python lists inside `app.py`, structured to
  match what the database layer will eventually return.

## 3. Backend Layer

**Location:** `backend/` (currently empty, placeholders live in
`app.py` until the module is built)

Responsible for:
- Opening/closing the camera (OpenCV `VideoCapture`)
- Streaming frames to the Attendance page preview
- Coordinating calls into the Face Recognition Layer
- Deciding when to mark attendance and calling the Database Layer

Hook points in the current code: `start_camera()`, `capture_face()`,
`mark_attendance()`, `export_csv()` in `app.py`.

## 4. Face Recognition Layer

**Location:** `backend/` (suggested: `backend/face_engine.py`)

Responsible for:
- Detecting faces in a camera frame
- Generating a face "encoding" (a numeric fingerprint of a face)
- Comparing a live encoding against stored student encodings to find
  the closest match

Hook point: `recognize_face()` in `app.py`.

## 5. Attendance Logic

Sits between the Face Recognition Layer and the Database Layer.
Responsible for:
- Preventing duplicate attendance entries for the same student on the
  same day
- Recording the exact timestamp and status ("Present")
- Handling edge cases (unknown face, low-confidence match)

## 6. Database Layer

**Location:** `database/` (suggested: `database/db_manager.py`,
`database/schema.sql`)

Suggested tables:

```text
students(id, student_id, name, roll_number, department, semester, face_encoding)
attendance(id, student_id, date, time, status)
users(id, username, password_hash)
```

Hook points: `load_students()`, `save_student()`, `delete_student()`,
`mark_attendance()` in `app.py`.

---

## 7. Application Flow (Sequence Diagram)

A simplified sequence for the "mark attendance" flow once the backend
is connected:

```text
User          Frontend         Backend        Face Recognition   Database
 │                │                │                  │              │
 │ Click "Start   │                │                  │              │
 │  Camera"       │                │                  │              │
 │───────────────►│                │                  │              │
 │                │ start_camera() │                  │              │
 │                │───────────────►│                  │              │
 │                │                │ open camera feed │              │
 │                │◄───────────────│                  │              │
 │  sees preview  │                │                  │              │
 │                │                │                  │              │
 │ Click "Mark    │                │                  │              │
 │  Attendance"   │                │                  │              │
 │───────────────►│                │                  │              │
 │                │ mark_attendance()                 │              │
 │                │───────────────►│                  │              │
 │                │                │ recognize_face() │              │
 │                │                │─────────────────►│              │
 │                │                │  student match    │              │
 │                │                │◄─────────────────│              │
 │                │                │  save record                     │
 │                │                │──────────────────────────────────►│
 │                │  refresh table │                                  │
 │                │◄───────────────│                                  │
 │  sees updated  │                │                                  │
 │  attendance    │                │                                  │
```

---

## 8. Folder Structure

```text
Smart_Attendance_System/
├── main.py            # Entry point, single Tk() instance
├── login.py            # Login screen
├── app.py                # Sidebar/header/pages + placeholders
├── styles.py               # Shared theme constants
├── README.md
├── TODO.md
├── PROGRESS.md
├── ARCHITECTURE.md
├── assets/
│   ├── icons/
│   └── images/
├── backend/               # Camera + face recognition (to be built)
├── database/                # SQLite schema + queries (to be built)
└── docs/                       # Diagrams, screenshots, notes
```

---

## 9. Team Responsibilities

| Layer               | Owner                    | Key Files                          |
|-----------------------|---------------------------|--------------------------------------|
| Frontend              | Frontend Developer          | `main.py`, `login.py`, `app.py`, `styles.py` |
| Backend / Camera        | Backend Developer              | `backend/`                              |
| Face Recognition           | Backend Developer                 | `backend/`                                 |
| Database                      | Database Developer                   | `database/`                                   |
| Integration                       | Integration Developer                   | Wiring across all files                          |

Each placeholder method in `app.py` includes a docstring naming which
role should implement it, so any team member can grep the codebase for
their responsibilities.
