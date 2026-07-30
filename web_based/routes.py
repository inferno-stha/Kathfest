"""routes.py - All route definitions for the Flask application.

This file maps URLs to view functions. Each view function renders
a Jinja2 template. Flask sessions are used to keep the user logged
in across multiple page requests.

How Flask sessions work:
    - When a user logs in successfully, we store their username in
      session['user'].
    - On every subsequent request, we check if session['user'] exists.
      If it does, the user is authenticated; otherwise we redirect
      them to the login page.
    - session.clear() removes all session data (logout).

How this maps to the original Tkinter project:
    Tkinter pages (show_dashboard, show_students, etc.) -> Flask routes
    Tkinter in-memory data (self.students_data)         -> Python lists (sample data)
    Tkinter button commands                             -> JavaScript fetch / form POST

Placeholder functions:
    Functions marked with "PLACEHOLDER" comments are stubs that the
    Backend Developer, Database Developer, or Integration Developer
    will implement later.
"""

from flask import render_template, request, redirect, url_for, session, jsonify
from app import app
import datetime

# ===================================================================
# SAMPLE DATA
# ===================================================================
# These lists replace the Tkinter MainApp's self.students_data and
# self.attendance_data. The Database Developer will replace these
# with SQLite queries later.
# ===================================================================

# Tuple format: (student_id, name, roll_number, department, semester)
students_data = [
    ("S001", "Aarav Sharma", "R101", "Computer Science", "2nd"),
    ("S002", "Priya Nair",    "R102", "Electronics",     "4th"),
    ("S003", "Rohan Gupta",   "R103", "Computer Science", "6th"),
    ("S004", "Sneha Iyer",    "R104", "Mechanical",      "8th"),
    ("S005", "Karan Verma",   "R105", "Civil",           "2nd"),
]

# Tuple format: (student_name, time, status)
attendance_data = [
    ("Aarav Sharma", "09:01 AM", "Present"),
    ("Priya Nair",   "09:02 AM", "Present"),
    ("Rohan Gupta",    "--",     "Absent"),
    ("Sneha Iyer",    "09:05 AM", "Present"),
    ("Karan Verma",    "--",     "Absent"),
]


# ===================================================================
# LOGIN / LOGOUT
# ===================================================================

@app.route("/")
def index():
    """Redirect root URL to login page (or dashboard if already logged in)."""
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Render the login page and handle login form submissions.

    Login credentials (for demo):
        Username: admin
        Password: admin

    The Database Developer can later replace the hardcoded check with
    a query against a users table in SQLite.

    How session works here:
        - On POST, we validate credentials.
        - If valid, we store session['user'] = 'admin'.
        - Flask automatically sends a session cookie to the browser.
        - On subsequent requests, Flask decrypts the cookie and
          restores session['user'].
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # --- Database Developer: replace with a real SELECT query ---
        if username == "admin" and password == "admin":
            session["user"] = username
            return redirect(url_for("dashboard"))
        # -----------------------------------------------------------

        return render_template("login.html", error="Invalid username or password.")

    return render_template("login.html", error=None)


@app.route("/logout")
def logout():
    """Clear the session and redirect to the login page.

    session.clear() removes all stored session data, effectively
    logging the user out.
    """
    session.clear()
    return redirect(url_for("login"))


# ===================================================================
# HELPER: Login required decorator logic
# ===================================================================
# To protect routes, we check session before rendering each page.
# This is done inside each route function rather than with a decorator
# so the code stays beginner-friendly.
# ===================================================================


# ===================================================================
# DASHBOARD
# ===================================================================

@app.route("/dashboard")
def dashboard():
    """Render the dashboard page with attendance statistics."""
    if "user" not in session:
        return redirect(url_for("login"))

    total = len(students_data)
    present = sum(1 for row in attendance_data if row[2] == "Present")
    pct = round((present / total) * 100, 1) if total else 0

    return render_template(
        "dashboard.html",
        total_students=total,
        present_today=present,
        attendance_pct=pct,
    )


# ===================================================================
# STUDENTS
# ===================================================================

@app.route("/students")
def students():
    """Render the students page with the student table and filter/search.

    The page includes department and semester dropdowns for filtering,
    plus a text search by name or roll number.

    Database Developer: replace students_data with a SELECT query.
    """
    if "user" not in session:
        return redirect(url_for("login"))

    # Extract unique departments and semesters from the data for dropdowns
    departments = sorted(set(s[3] for s in students_data))
    semesters = sorted(set(s[4] for s in students_data))

    return render_template(
        "students.html",
        students=students_data,
        departments=departments,
        semesters=semesters,
    )


@app.route("/api/students/filter", methods=["POST"])
def filter_students():
    """API endpoint to filter students by department, semester, and text.

    Called via JavaScript fetch() when the user changes a dropdown
    or types in the search box. Returns JSON so the table can be
    updated without a full page reload.

    Database Developer: replace this with a SQL WHERE query.
    """
    if "user" not in session:
        return jsonify([])

    data = request.get_json()
    dept = data.get("department", "all")
    sem = data.get("semester", "all")
    query = data.get("query", "").strip().lower()

    rows = students_data
    if dept != "all":
        rows = [r for r in rows if r[3] == dept]
    if sem != "all":
        rows = [r for r in rows if r[4] == sem]
    if query:
        rows = [r for r in rows if query in r[1].lower() or query in r[2].lower()]

    # Convert tuples to dicts for JSON serialization
    result = [
        {"id": r[0], "name": r[1], "roll": r[2], "department": r[3], "semester": r[4]}
        for r in rows
    ]
    return jsonify(result)


@app.route("/api/students/add", methods=["POST"])
def add_student():
    """API endpoint to add a new student (with duplicate checking).

    Checks for duplicate Student ID and Roll Number before adding.
    Returns JSON with success/error status.

    Database Developer: replace with an INSERT query.
    """
    if "user" not in session:
        return jsonify({"success": False, "error": "Not authenticated"})

    data = request.get_json()
    sid = data.get("student_id", "").strip()
    name = data.get("name", "").strip()
    roll = data.get("roll", "").strip()
    dept = data.get("department", "").strip()
    sem = data.get("semester", "").strip()

    if not all([sid, name, roll, dept, sem]):
        return jsonify({"success": False, "error": "All fields are required."})

    # Check for duplicate Student ID
    for s in students_data:
        if s[0].lower() == sid.lower():
            return jsonify({"success": False, "error": f"Student ID '{sid}' already exists!"})
        if s[2].lower() == roll.lower():
            return jsonify({"success": False, "error": f"Roll Number '{roll}' already exists!"})

    students_data.append((sid, name, roll, dept, sem))
    return jsonify({"success": True, "message": f"Student '{name}' added successfully."})


@app.route("/api/students/delete", methods=["POST"])
def delete_student():
    """API endpoint to delete a student by ID.

    Database Developer: replace with a DELETE query.
    """
    if "user" not in session:
        return jsonify({"success": False, "error": "Not authenticated"})

    data = request.get_json()
    sid = data.get("student_id", "")

    global students_data
    students_data = [s for s in students_data if s[0] != sid]
    return jsonify({"success": True})


# ===================================================================
# ATTENDANCE
# ===================================================================

@app.route("/attendance")
def attendance():
    """Render the attendance page with camera placeholder and table."""
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("attendance.html", attendance=attendance_data)


@app.route("/api/attendance/mark", methods=["POST"])
def mark_attendance():
    """API endpoint to mark a student as present.

    Checks for duplicate (already marked present) before adding.
    The student is identified by name (in production, face recognition
    would determine the identity).

    Integration Developer: connect this to face recognition output.
    """
    if "user" not in session:
        return jsonify({"success": False, "error": "Not authenticated"})

    data = request.get_json()
    student_name = data.get("name", "").strip()

    if not student_name:
        return jsonify({"success": False, "error": "Student name is required."})

    # Check if already marked present
    for a in attendance_data:
        if a[0] == student_name and a[2] == "Present":
            return jsonify({
                "success": False,
                "error": f"'{student_name}' is already marked present!",
            })

    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    attendance_data.append((student_name, time_str, "Present"))
    return jsonify({"success": True, "message": f"Attendance marked for '{student_name}'."})


# ===================================================================
# REPORTS
# ===================================================================

@app.route("/reports")
def reports():
    """Render the reports page with attendance statistics."""
    if "user" not in session:
        return redirect(url_for("login"))

    total = len(students_data)
    present = sum(1 for row in attendance_data if row[2] == "Present")
    absent = total - present

    return render_template(
        "reports.html",
        total_students=total,
        present_students=present,
        absent_students=absent,
    )


@app.route("/api/export-csv", methods=["POST"])
def export_csv():
    """PLACEHOLDER: Export attendance data as a CSV file.

    Backend Developer: implement CSV export using Python's csv module.
    Return the CSV file as a download response.
    """
    if "user" not in session:
        return jsonify({"success": False, "error": "Not authenticated"})

    # --- Backend Developer: implement CSV generation here ---
    return jsonify({"success": True, "message": "CSV export coming soon!"})


# ===================================================================
# ABOUT
# ===================================================================

@app.route("/about")
def about():
    """Render the about page with project details and team info."""
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("about.html")


# ===================================================================
# BACKEND PLACEHOLDER ROUTES
# ===================================================================

@app.route("/api/camera/start", methods=["POST"])
def start_camera():
    """PLACEHOLDER: Start the camera stream.

    Backend Developer: integrate OpenCV VideoCapture and stream
    frames to the browser via a video feed endpoint.
    """
    return jsonify({"success": True, "message": "Camera start coming soon!"})


@app.route("/api/camera/capture-face", methods=["POST"])
def capture_face():
    """PLACEHOLDER: Capture a face image and save its encoding.

    Backend Developer: capture frame from camera, detect face,
    compute encoding, and store it in the database.
    """
    return jsonify({"success": True, "message": "Face capture coming soon!"})


@app.route("/api/recognize-face", methods=["POST"])
def recognize_face():
    """PLACEHOLDER: Match a live face against stored encodings.

    Backend Developer: compare the current frame's face encoding
    against all stored encodings and return the best match.
    """
    return jsonify({"success": True, "message": "Face recognition coming soon!"})


@app.route("/api/students/load", methods=["GET"])
def load_students():
    """PLACEHOLDER: Reload students from the database.

    Database Developer: replace this with a SELECT query that
    refreshes the students_data list from SQLite.
    """
    return jsonify({"success": True, "message": "Load students coming soon!"})
