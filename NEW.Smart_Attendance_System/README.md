# 🎓 Smart Student Attendance System Using Face Recognition

A desktop application that automates classroom attendance using face
recognition, built with a clean, modular Python/Tkinter frontend so a
hackathon team can build the backend, database, and face recognition
layers in parallel.

> **Status:** Frontend/UI complete. Backend, database, and face
> recognition are placeholders ready for integration.

---

## 📋 Project Overview

Manual attendance taking is slow and error-prone. This project replaces
the roll-call with a camera that recognizes each student's face and
automatically logs their attendance. This repository currently contains
the **complete graphical user interface**, built entirely with Python's
built-in `tkinter` library, with clearly marked placeholder functions
for the team members responsible for the camera, face recognition, and
database layers.

---

## ✨ Features

- 🔐 **Login screen** with show/hide password and dummy authentication
- 📊 **Dashboard** with live-style stat cards (Total Students, Present
  Today, Attendance %) and quick-action shortcuts
- 👨‍🎓 **Student Management** with a searchable table (`ttk.Treeview`),
  Add/Delete/Capture Face actions
- 📷 **Attendance** page with a camera preview placeholder, Start
  Camera / Mark Attendance controls, and a live attendance table
- 📄 **Reports** page summarizing total/present/absent students with
  a CSV export placeholder
- ℹ **About** page with project and team information
- 🚪 **Logout** with a confirmation dialog
- 🎨 Consistent, professional dark-blue/light-grey theme defined in a
  single `styles.py` file
- 🧭 Single-window page switching (no popup windows) using Tkinter
  Frames — a beginner-friendly pattern for multi-page desktop apps

---

## 🗂 Folder Structure

```text
Smart_Attendance_System/
├── main.py               # Entry point — creates the ONE Tk() window
├── login.py               # Login screen UI + dummy authentication
├── app.py                  # Sidebar, header, and all pages
├── styles.py                # Shared colors, fonts, icons, sizing
│
├── README.md                 # This file
├── TODO.md                     # Hackathon task checklist
├── PROGRESS.md                  # Progress tracker
├── ARCHITECTURE.md                # System design & diagrams
│
├── assets/
│   ├── icons/                       # App icons (future use)
│   └── images/                       # Screenshots, logos (future use)
│
├── backend/                            # Face recognition & camera logic (TODO)
├── database/                            # SQLite schema & queries (TODO)
└── docs/                                 # Extra documentation, diagrams
```

---

## 🛠 Technologies Used

| Layer            | Technology                        |
|-------------------|-----------------------------------|
| UI Framework      | Python `tkinter` / `ttk`          |
| Language          | Python 3.9+                        |
| Face Recognition  | OpenCV + `face_recognition` (planned) |
| Database          | SQLite (planned)                    |
| Version Control   | Git & GitHub                         |

The frontend has **zero external dependencies** — it runs with a
standard Python installation.

---

## 💻 Installation

1. Make sure **Python 3.9 or newer** is installed:
   ```bash
   python3 --version
   ```
2. Clone or download this repository.
3. No `pip install` is required for the current UI-only version,
   since `tkinter` ships with standard Python. (On some Linux
   distributions you may need `sudo apt-get install python3-tk`.)

---

## ▶ Running the Project

From the project's root folder, run:

```bash
python3 main.py
```

Log in with the demo credentials:

- **Username:** `admin`
- **Password:** `admin`

---

## 👥 Team Members

| Role                          | Responsibility                                   |
|--------------------------------|---------------------------------------------------|
| Frontend Developer             | Tkinter UI (this codebase)                        |
| Backend Developer               | Camera integration & face recognition             |
| Database Developer               | SQLite schema, queries, authentication            |
| Integration Developer             | Wiring backend + database into the UI placeholders |

---

## 🚀 Future Improvements

- Replace dummy login with real SQLite-backed authentication
- Connect OpenCV camera feed to the Attendance page preview
- Implement face capture, encoding storage, and recognition
- Persist students and attendance records in SQLite
- Real CSV/PDF export for Reports
- Add charts (e.g. attendance trends) to the Dashboard
- Package the app into a standalone executable (PyInstaller)

---

## 🖼 Screenshots

_Add screenshots here once the UI has been run locally, e.g.:_

```text
docs/screenshots/login.png
docs/screenshots/dashboard.png
docs/screenshots/students.png
docs/screenshots/attendance.png
```

---

## 📄 License

This project is released under the MIT License — free to use, modify,
and distribute for educational and hackathon purposes.
