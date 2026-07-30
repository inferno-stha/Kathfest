# 🎓 Smart Student Attendance System (Flask Web App)

A web-based attendance system that uses face recognition to identify students and record their attendance. This is a **Flask conversion** of the original Tkinter desktop application, preserving the same design, navigation, and functionality.

## Features

- **Login System** — Session-based authentication (demo: admin/admin)
- **Dashboard** — Overview with total students, present count, attendance percentage
- **Students Page** — Filter by department → semester → search by name/roll number
- **Attendance Page** — Camera preview placeholder with manual marking
- **Reports Page** — Statistics with CSV export placeholder
- **About Page** — Project info and team members
- **Responsive Design** — Works on desktop and tablet

## Technologies Used

| Layer          | Technology          |
|----------------|---------------------|
| Frontend       | HTML5, CSS3, JavaScript |
| Backend        | Python 3, Flask     |
| Templating     | Jinja2              |
| Styling        | CSS Variables       |
| Authentication | Flask Sessions      |

## Folder Structure

```
smart_attendance_web/
├── app.py                    # Flask entry point
├── routes.py                 # Route definitions
├── requirements.txt          # Dependencies
├── README.md
├── TODO.md
├── PROGRESS.md
├── ARCHITECTURE.md
├── templates/                # Jinja2 HTML templates
│   ├── base.html             # Layout template (sidebar + header)
│   ├── login.html            # Login page
│   ├── dashboard.html        # Dashboard page
│   ├── students.html         # Students page
│   ├── attendance.html       # Attendance page
│   ├── reports.html          # Reports page
│   └── about.html            # About page
├── static/
│   ├── css/
│   │   └── style.css         # Main stylesheet
│   ├── js/
│   │   └── script.js         # JavaScript placeholders
│   └── images/
├── backend/                  # Face recognition (future)
├── database/                 # SQLite (future)
└── assets/                   # Icons, images (future)
```

## Installation

1. **Clone or download** the project.

2. **Install Python 3.9+** if not already installed.

3. **Install Flask** (the only dependency):
   ```
   pip install flask
   ```
   Or using the requirements file:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Navigate to the project folder:
   ```
   cd smart_attendance_web
   ```

2. Run the Flask app:
   ```
   python app.py
   ```

3. Open your browser and go to:
   ```
   http://localhost:5000
   ```

4. **Login credentials:**
   - Username: `admin`
   - Password: `admin`

## Team Members

- **Frontend Developer** — Tkinter UI / Flask Web App
- **Backend Developer** — Camera & Face Recognition
- **Database Developer** — SQLite Integration
- **Integration Developer** — Connecting all modules

## Future Improvements

- Real face recognition with OpenCV
- SQLite database integration
- CSV export
- Live camera streaming to browser
- Real-time attendance updates
