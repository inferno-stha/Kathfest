"""
routes.py - All Flask route definitions for the attendance system.

This file maps URLs to view functions. It is the glue that connects:
    - The frontend (HTML templates / JavaScript)   ->  UI/templates/
    - The backend (face recognition / camera)      ->  backend/
    - The database (SQLite models)                 ->  database/

How this was created:
    This file replaces the placeholder-laden web_based/routes.py with
    real implementations that query the database, perform face recognition,
    and return actual data instead of dummy lists.

Architecture:
    Instead of using @app.route() decorators (which creates a circular
    import when routes.py imports app.py), this module exports a single
    function: init_routes(app). The app.py module calls init_routes(app)
    after creating the Flask app, passing the app object as a parameter.
    This completely avoids circular imports.

    - Page routes (GET)     ->  render Jinja2 templates with real data
    - API routes (POST)     ->  accept JSON, process, return JSON
    - Face recognition      ->  POST /api/mark-attendance uses OpenCV
    - CSV export            ->  POST /api/export-csv returns file download
"""

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    Response,
)
import datetime
import json
import base64

# =========================================================================
# Backend and database imports (the modules we integrated)
# =========================================================================
from database.db import (
    initialize_database,
    add_student,
    get_all_students,
    get_student_by_id,
    update_student,
    delete_student,
    search_students,
    update_face_encoding,
)
from database.models import Student, Attendance
from backend.attendance import (
    mark_attendance_from_frame,
    get_today_attendance_formatted,
    get_dashboard_stats,
    get_csv_data,
    reload_face_data,
)
from backend.camera import CameraStream, decode_base64_image
from backend.utils import login_required, login_required_api, format_time_12hr


# =========================================================================
# Initialize the database tables on module load.
# This ensures tables exist before any route handles a request.
# =========================================================================
initialize_database()


# =========================================================================
# Function: init_routes(app)
#
# Purpose:
#     Registers ALL routes on the given Flask app object.
#     Called by app.py after creating the Flask application.
#
# Why this pattern:
#     Using @app.route decorators in this file would require importing
#     'app' from app.py, while app.py imports this file — a circular
#     import that breaks Flask's debug reloader. By using a registration
#     function, the import is one-way: app.py -> routes.py.
#
# Args:
#     app: The Flask application instance from app.py
# =========================================================================
def init_routes(app):

    # =================================================================
    # LOGIN / LOGOUT
    #
    # Maps to Tkinter's login.py LoginWindow class.
    # =================================================================

    @app.route("/")
    def index():
        """Root URL redirect. If logged in, go to dashboard. Otherwise, login."""
        if "user" in session:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """
        Render login page and authenticate users.

        GET  -> Show login form
        POST -> Validate credentials and create session

        Authentication:
            Username: admin
            Password: admin

        How sessions work:
            1. On success, store session["user"] = "admin"
            2. Flask encrypts this into a session cookie
            3. Each request decrypts the cookie and checks "user" key
            4. session.clear() on logout
        """
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            if username == "admin" and password == "admin":
                session["user"] = username
                return redirect(url_for("dashboard"))

            return render_template("login.html", error="Invalid username or password.")

        return render_template("login.html", error=None)

    @app.route("/logout")
    def logout():
        """Log out by clearing the session and redirecting to login."""
        session.clear()
        return redirect(url_for("login"))

    # =================================================================
    # DASHBOARD
    #
    # Maps to Tkinter's show_dashboard() in UI/app.py line 146.
    # =================================================================

    @app.route("/dashboard")
    @login_required
    def dashboard():
        """
        Render the dashboard page with real attendance statistics.

        Data comes from get_dashboard_stats() which runs COUNT queries
        on the students and attendance tables in SQLite.

        Original Tkinter equivalent:
            show_dashboard() calculated stats from in-memory lists.
        """
        stats = get_dashboard_stats()

        return render_template(
            "dashboard.html",
            total_students=stats["total_students"],
            present_today=stats["present_today"],
            attendance_pct=stats["attendance_pct"],
        )

    # =================================================================
    # STUDENTS MODULE
    #
    # Maps to Tkinter's show_students() in UI/app.py line 182.
    # Now uses real SQLite queries instead of in-memory lists.
    # =================================================================

    @app.route("/students")
    @login_required
    def students():
        """
        Render the students page with data from the database.

        Queries get_all_students() and extracts unique departments
        and semesters for the filter dropdowns.
        """
        all_students = get_all_students()

        departments = sorted(set(s["department"] for s in all_students if s["department"]))
        semesters = sorted(set(s["semester"] for s in all_students if s["semester"]))

        return render_template(
            "students.html",
            students=all_students,
            departments=departments,
            semesters=semesters,
        )

    @app.route("/api/students/filter", methods=["POST"])
    @login_required_api
    def filter_students():
        """
        API: Filter students by department, semester, and text search.

        Called via JavaScript fetch() when dropdowns or search changes.
        Uses SQL WHERE with LIKE for case-insensitive search.
        """
        data = request.get_json()
        query = data.get("query", "").strip()
        dept = data.get("department", "all")
        sem = data.get("semester", "all")

        results = search_students(query, dept, sem)

        return jsonify(results)

    @app.route("/api/students/add", methods=["POST"])
    @login_required_api
    def add_student_route():
        """
        API: Add a new student to the database.

        Database: add_student() -> INSERT INTO students
        Handles duplicate roll_number via SQL UNIQUE constraint.
        """
        data = request.get_json()
        name = data.get("name", "").strip()
        roll = data.get("roll", "").strip()
        dept = data.get("department", "").strip()
        sem = data.get("semester", "").strip()

        if not all([name, roll, dept, sem]):
            return jsonify({"success": False, "error": "All fields are required."})

        student_id = add_student(name, roll, dept, sem)

        if student_id is None:
            return jsonify({
                "success": False,
                "error": f"Roll Number '{roll}' already exists!",
            })

        return jsonify({"success": True, "message": f"Student '{name}' added successfully."})

    @app.route("/api/students/delete", methods=["POST"])
    @login_required_api
    def delete_student_route():
        """
        API: Delete a student from the database.

        Database: delete_student() -> DELETE FROM students WHERE id = ?
        Cascade deletes attendance records via ON DELETE CASCADE.
        """
        data = request.get_json()
        student_id = data.get("student_id", "")

        if not student_id:
            return jsonify({"success": False, "error": "Student ID is required."})

        try:
            student_id = int(student_id)
        except ValueError:
            return jsonify({"success": False, "error": "Invalid student ID."})

        deleted = delete_student(student_id)

        if deleted:
            return jsonify({"success": True, "message": "Student deleted successfully."})
        else:
            return jsonify({"success": False, "error": "Student not found."})

    @app.route("/api/students/update", methods=["POST"])
    @login_required_api
    def update_student_route():
        """
        API: Update a student's information.

        Allows editing name, roll number, department, semester.
        """
        data = request.get_json()
        student_id = data.get("id")

        if not student_id:
            return jsonify({"success": False, "error": "Student ID is required."})

        try:
            student_id = int(student_id)
        except ValueError:
            return jsonify({"success": False, "error": "Invalid student ID."})

        updated = update_student(
            student_id,
            name=data.get("name"),
            roll_number=data.get("roll_number"),
            department=data.get("department"),
            semester=data.get("semester"),
        )

        if updated:
            return jsonify({"success": True, "message": "Student updated successfully."})
        else:
            return jsonify({
                "success": False,
                "error": "Update failed (duplicate roll number or student not found).",
            })

    # =================================================================
    # ATTENDANCE MODULE (with Face Recognition integration)
    #
    # Maps to Tkinter's show_attendance() in UI/app.py line 260.
    # Now fully integrated with face recognition:
    #   - Camera control      -> backend/camera.py
    #   - Face recognition    -> backend/face_recognizer.py
    #   - Attendance marking  -> backend/attendance.py
    #   - Database storage    -> database/db.py
    # =================================================================

    @app.route("/attendance")
    @login_required
    def attendance():
        """
        Render the attendance page with today's records and camera controls.

        Data: get_today_attendance_formatted() returns (name, time, status) tuples.
        """
        today_records = get_today_attendance_formatted()
        return render_template("attendance.html", attendance=today_records)

    @app.route("/api/attendance/data", methods=["GET"])
    @login_required_api
    def attendance_data():
        """
        API: Get today's attendance records as JSON.

        Called by JavaScript to refresh the attendance table
        without a full page reload.
        """
        records = get_today_attendance_formatted()
        result = [
            {"name": r[0], "time": r[1], "status": r[2]}
            for r in records
        ]
        return jsonify(result)

    @app.route("/api/attendance/mark", methods=["POST"])
    @login_required_api
    def mark_attendance_route():
        """
        API: Mark attendance for a student identified by face recognition.

        This is the KEY INTEGRATION ENDPOINT. It receives a camera frame
        (as base64 JPEG), runs face recognition on it, and marks attendance
        if a known student is identified.

        Flow:
            1. Decode the base64 image back to an OpenCV frame
            2. Call mark_attendance_from_frame(frame) which:
               a. Detects faces via face_recognition library
               b. Generates 128-d face encoding
               c. Compares against all stored encodings in database
               d. If match found, inserts attendance record
            3. Return result as JSON

        How this replaces the old system:
            OLD: Admin selected a student name from dropdown
            NEW: Camera captures frame -> AI recognizes face -> auto-mark
        """
        data = request.get_json()

        if "image" in data:
            image_base64 = data["image"]
            frame = decode_base64_image(image_base64)

            if frame is None:
                return jsonify({
                    "success": False,
                    "message": "Could not decode image from camera.",
                })
        else:
            return jsonify({
                "success": False,
                "message": "No image data received. Please use the camera.",
            })

        result = mark_attendance_from_frame(frame)
        return jsonify(result)

    @app.route("/api/attendance/mark-by-name", methods=["POST"])
    @login_required_api
    def mark_attendance_by_name():
        """
        API: Manually mark attendance by student name (fallback method).

        Fallback when the camera is unavailable. Looks up student by name
        in the database and marks them present.
        """
        data = request.get_json()
        student_name = data.get("name", "").strip()

        if not student_name:
            return jsonify({"success": False, "error": "Student name is required."})

        all_students = get_all_students()
        matched = [s for s in all_students if s["name"].lower() == student_name.lower()]

        if not matched:
            return jsonify({
                "success": False,
                "error": f"No student found with name '{student_name}'.",
            })

        student = matched[0]
        was_marked = Attendance.mark(student["id"])

        if was_marked:
            return jsonify({"success": True, "message": f"Attendance marked for '{student_name}'."})
        else:
            return jsonify({
                "success": False,
                "error": f"'{student_name}' is already marked present today!",
            })

    # =================================================================
    # FACE CAPTURE / REGISTRATION
    #
    # These endpoints handle the face registration flow:
    #   1. Admin adds student info via the Add Student modal
    #   2. Admin clicks "Capture Face" -> camera captures encoding
    #   3. Encoding is saved to the student's database record
    # =================================================================

    @app.route("/api/capture-face", methods=["POST"])
    @login_required_api
    def capture_face():
        """
        API: Capture a face from the camera and save its encoding.

        Called when the admin clicks "Capture Face" on the Students page.
        Receives student_id and base64 image, detects face, generates
        128-d encoding, and stores it in the database.
        """
        data = request.get_json()
        student_id = data.get("student_id")
        image_base64 = data.get("image")

        if not student_id or not image_base64:
            return jsonify({
                "success": False,
                "message": "Student ID and image are required.",
            })

        try:
            student_id = int(student_id)
        except ValueError:
            return jsonify({"success": False, "message": "Invalid student ID."})

        frame = decode_base64_image(image_base64)
        if frame is None:
            return jsonify({"success": False, "message": "Could not decode image."})

        try:
            from backend.face_recognizer import FaceRecognizer
            recognizer = FaceRecognizer()
        except ImportError as e:
            return jsonify({
                "success": False,
                "message": (
                    "Face recognition library not available. "
                    "Please install face_recognition and dlib. "
                    f"(Error: {e})"
                ),
            })

        face_locations = recognizer.detect_faces(frame)

        if len(face_locations) == 0:
            return jsonify({
                "success": False,
                "message": "No face detected. Please look at the camera.",
            })

        if len(face_locations) > 1:
            return jsonify({
                "success": False,
                "message": "Multiple faces detected. Only one person allowed.",
            })

        encodings = recognizer.get_encodings(frame, face_locations)

        if len(encodings) == 0:
            return jsonify({
                "success": False,
                "message": "Could not generate face encoding.",
            })

        success = update_face_encoding(student_id, encodings[0])

        if success:
            reload_face_data()
            return jsonify({
                "success": True,
                "message": "Face captured and encoding saved successfully.",
            })
        else:
            return jsonify({
                "success": False,
                "message": "Student not found in database.",
            })

    # =================================================================
    # REPORTS
    #
    # Maps to Tkinter's show_reports() in UI/app.py line 288.
    # =================================================================

    @app.route("/reports")
    @login_required
    def reports():
        """
        Render the reports page with attendance statistics.

        Data: total students, present today, absent (total - present).
        """
        stats = get_dashboard_stats()
        absent = stats["total_students"] - stats["present_today"]

        return render_template(
            "reports.html",
            total_students=stats["total_students"],
            present_students=stats["present_today"],
            absent_students=absent,
        )

    @app.route("/api/attendance/all", methods=["GET"])
    @login_required_api
    def get_all_attendance_api():
        """
        API: Get all attendance records (for reports or data tables).

        Supports optional date parameter: ?date=2026-07-30
        """
        target_date = request.args.get("date")

        if target_date:
            from database.db import get_attendance_by_date
            records = get_attendance_by_date(target_date)
        else:
            from database.db import get_all_attendance_records
            records = get_all_attendance_records()

        return jsonify(records)

    @app.route("/api/export-csv", methods=["GET"])
    @login_required_api
    def export_csv():
        """
        API: Export all attendance data as a downloadable CSV file.

        Generates CSV in memory and returns it as a file download
        response with correct MIME type and headers.
        """
        csv_data = get_csv_data()

        return Response(
            csv_data,
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=attendance_report.csv",
                "Content-Type": "text/csv; charset=utf-8",
            },
        )

    @app.route("/api/attendance/student/<int:student_id>", methods=["GET"])
    @login_required_api
    def get_student_attendance(student_id):
        """
        API: Get attendance records for a specific student.

        Used for the student-wise report feature.
        """
        from database.db import get_attendance_by_student
        records = get_attendance_by_student(student_id)
        return jsonify(records)

    # =================================================================
    # ABOUT
    #
    # Maps to Tkinter's show_about() in UI/app.py line 308.
    # =================================================================

    @app.route("/about")
    @login_required
    def about():
        """Render the About page with project information and team details."""
        return render_template("about.html")
