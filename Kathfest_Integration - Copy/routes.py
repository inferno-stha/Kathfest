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
    get_attendance_by_date,
    get_all_attendance_records,
    get_attendance_by_student,
    get_attendance_by_department,
    get_attendance_by_semester,
    get_daily_attendance,
    get_monthly_attendance,
    get_top_absent_students,
    get_student_stats,
    get_session_summary,
)
from database.models import Student, Attendance
from backend.attendance import (
    mark_attendance_from_frame,
    get_today_attendance_formatted,
    get_dashboard_stats,
    get_csv_data,
    reload_face_data,
    search_student_by_face,
    start_camera_session,
    finish_camera_session,
)
from backend.camera import CameraStream, decode_base64_image
from backend.utils import login_required, login_required_api, format_time_12hr
from backend.validation import (
    validate_student_input,
    validate_name,
    validate_roll_number,
    validate_department,
    validate_semester,
)


# =========================================================================
# Initialize the database tables on module load.
# This ensures tables exist before any route handles a request.
# =========================================================================
initialize_database()


# =========================================================================
# Helper: _sanitize_students()
#
# SQLite BLOB columns (face_encoding / face_image) are returned as raw
# bytes, which Flask's JSON encoder cannot serialize. For JSON responses
# we convert:
#     face_encoding -> has_face (bool)    - just a flag for the table icon
#     face_image    -> base64 string      - used by the Face Search card
# =========================================================================
def _sanitize_students(students):
    sanitized = []
    for s in students:
        item = dict(s)
        item["has_face"] = s.get("face_encoding") is not None
        item["face_registered"] = bool(s.get("face_registered", 0)) or s.get("face_encoding") is not None
        item.pop("face_encoding", None)
        if s.get("face_image") is not None:
            item["face_image"] = base64.b64encode(s["face_image"]).decode("utf-8")
        else:
            item.pop("face_image", None)
        sanitized.append(item)
    return sanitized


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
            face_registered=stats.get("face_registered", 0),
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

        return jsonify(_sanitize_students(results))

    @app.route("/api/students/add", methods=["POST"])
    @app.route("/students/add", methods=["POST"])
    @login_required_api
    def add_student_route():
        """
        API: Add a new student to the database.

        Registered at BOTH:
            POST /api/students/add     (legacy)
            POST /students/add         (RESTful, used by the Students page)

        Database: add_student() -> INSERT INTO students
        Handles duplicate roll_number via SQL UNIQUE constraint.

        Validation (v2): name, roll_number, department and semester are
        validated with the same regex rules the frontend uses.
        """
        data = request.get_json() or {}
        name = data.get("name", "").strip()
        roll = (data.get("roll") or data.get("roll_number") or "").strip()
        dept = data.get("department", "").strip()
        sem = data.get("semester", "").strip()

        # Input validation (backend regex rules)
        errors = validate_student_input(name, roll, dept, sem)
        if errors:
            return jsonify({
                "success": False,
                "error": "; ".join(errors.values()),
                "errors": errors,
            })

        student_id = add_student(name, roll, dept, sem)

        if student_id is None:
            return jsonify({
                "success": False,
                "error": f"Roll Number '{roll}' already exists!",
            })

        return jsonify({
            "success": True,
            "message": f"Student '{name}' added successfully.",
            "student_id": student_id,
        })

    @app.route("/api/students/delete", methods=["POST"])
    @app.route("/students/<int:student_id>/delete", methods=["POST"])
    @login_required_api
    def delete_student_route(student_id=None):
        """
        API: Delete a student from the database.

        Registered at BOTH:
            POST /api/students/delete              (student_id in JSON body)
            POST /students/<id>/delete             (student_id in URL)

        Database: delete_student() -> DELETE FROM students WHERE id = ?
        Cascade deletes attendance records via ON DELETE CASCADE. The
        row removal also deletes the stored face_encoding / face_image.
        """
        data = request.get_json() or {}

        if student_id is None:
            student_id = data.get("student_id", "")

        if not student_id:
            return jsonify({"success": False, "error": "Student ID is required."})

        try:
            student_id = int(student_id)
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "Invalid student ID."})

        deleted = delete_student(student_id)

        if deleted:
            return jsonify({"success": True, "message": "Student deleted successfully."})
        else:
            return jsonify({"success": False, "error": "Student not found."}), 404

    @app.route("/students/<int:student_id>", methods=["GET"])
    @login_required_api
    def get_student_route(student_id):
        """
        API: Get ONE student's data for the Edit modal.

        Registered at:
            GET /students/<id>

        Returns JSON (no BLOBs) so the modal can pre-fill its fields.
        """
        student = get_student_by_id(student_id)

        if student is None:
            return jsonify({"success": False, "error": "Student not found."}), 404

        return jsonify({
            "success": True,
            "student": {
                "id": student["id"],
                "name": student["name"],
                "roll_number": student["roll_number"],
                "department": student["department"],
                "semester": student["semester"],
                "face_registered": student.get("face_encoding") is not None
                                   or bool(student.get("face_registered", 0)),
            },
        })

    @app.route("/api/students/update", methods=["POST"])
    @app.route("/students/<int:student_id>/edit", methods=["POST"])
    @login_required_api
    def update_student_route(student_id=None):
        """
        API: Update a student's information.

        Registered at BOTH:
            POST /api/students/update          (id in JSON body)
            POST /students/<id>/edit           (id in URL)

        Allows editing name, roll number, department, semester.
        Only fields actually provided in the request are changed.
        Validated with the same rules as registration (v2).
        """
        data = request.get_json() or {}

        if student_id is None:
            student_id = data.get("id")

        if not student_id:
            return jsonify({"success": False, "error": "Student ID is required."})

        try:
            student_id = int(student_id)
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "Invalid student ID."})

        name = data.get("name")
        roll_number = data.get("roll_number")
        department = data.get("department")
        semester = data.get("semester")

        # Validate ONLY the fields being changed (partial update)
        errors = {}
        if name is not None:
            err = validate_name(name)
            if err:
                errors["name"] = err
        if roll_number is not None:
            err = validate_roll_number(roll_number)
            if err:
                errors["roll"] = err
        if department is not None:
            err = validate_department(department)
            if err:
                errors["department"] = err
        if semester is not None:
            err = validate_semester(semester)
            if err:
                errors["semester"] = err

        if errors:
            return jsonify({
                "success": False,
                "error": "; ".join(errors.values()),
                "errors": errors,
            })

        updated = update_student(
            student_id,
            name=name,
            roll_number=roll_number,
            department=department,
            semester=semester,
        )

        if updated:
            return jsonify({"success": True, "message": "Student updated successfully."})
        else:
            return jsonify({
                "success": False,
                "error": "Update failed (duplicate roll number or student not found).",
            }), 404

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

        Data: get_today_attendance_formatted() returns (name, time, status,
        confidence) tuples. Department/semester dropdowns are populated
        from the students table.
        """
        today_records = get_today_attendance_formatted()
        all_students = get_all_students()

        departments = sorted(set(s["department"] for s in all_students if s["department"]))
        semesters = sorted(set(s["semester"] for s in all_students if s["semester"]))

        return render_template(
            "attendance.html",
            attendance=today_records,
            departments=departments,
            semesters=semesters,
        )

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
            {
                "name": r[0],
                "time": r[1],
                "status": r[2],
                "confidence": r[3],
            }
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
               a. Detects faces via face_recognition library (ROI-restricted)
               b. Generates 128-d face encoding
               c. Compares against all stored encodings in database
               d. If match found, inserts attendance record with confidence
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

        # Optional v2 metadata passed from the automatic-attendance loop
        session_id = data.get("session_id")
        department = data.get("department")
        semester = data.get("semester")

        result = mark_attendance_from_frame(
            frame,
            session_id=session_id,
            department=department,
            semester=semester,
        )
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
    # CAMERA SESSIONS + FULLY AUTOMATIC ATTENDANCE
    #
    # New v2 workflow:
    #   1. Frontend calls POST /api/attendance/session/start  -> gets session_id
    #   2. Frontend streams frames to POST /api/attendance/mark
    #      (which now accepts session_id + department/semester snapshots)
    #   3. Frontend calls POST /api/attendance/session/end with a summary
    # =================================================================

    @app.route("/api/attendance/session/start", methods=["POST"])
    @login_required_api
    def attendance_session_start():
        """
        API: Start a new camera attendance session.

        Returns:
            {session_id: N} which the browser loop attaches to every
            attendance request so the whole run is traceable.
        """
        session_id = start_camera_session()
        return jsonify({"success": True, "session_id": session_id})

    @app.route("/api/attendance/session/end", methods=["POST"])
    @login_required_api
    def attendance_session_end():
        """
        API: End a camera attendance session and store its summary.

        Body:
            {session_id, total_recognized, unknown_faces}
        """
        data = request.get_json() or {}
        session_id = data.get("session_id")
        total_recognized = data.get("total_recognized", 0)
        unknown_faces = data.get("unknown_faces", 0)

        if not session_id:
            return jsonify({"success": False, "error": "session_id is required."})

        try:
            session_id = int(session_id)
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "Invalid session_id."})

        summary = finish_camera_session(
            session_id,
            int(total_recognized or 0),
            int(unknown_faces or 0),
        )
        return jsonify({"success": True, "summary": summary})

    # =================================================================
    # FACE CAPTURE / REGISTRATION
    #
    # These endpoints handle the face registration flow:
    #   1. Admin adds student info via the Add Student modal
    #   2. Admin clicks "Capture Face" -> camera captures encoding
    #   3. Encoding is saved to the student's database record
    # =================================================================

    @app.route("/api/capture-face", methods=["POST"])
    @app.route("/students/<int:student_id>/capture", methods=["POST"])
    @login_required_api
    def capture_face(student_id=None):
        """
        API: Capture a face from the camera and save its encoding.

        Registered at BOTH:
            POST /api/capture-face             (student_id in JSON body)
            POST /students/<id>/capture        (student_id in URL)

        Called when the admin clicks "Capture Face" on the Students page.
        Receives a base64 image, detects face, generates 128-d encoding,
        and stores it in the database.

        v2 improvements:
            - Duplicate face guard: before saving, the new encoding is
              compared with every stored encoding. If the best match is
              too close (face_distance < FACE_DUPLICATE_THRESHOLD) the
              registration is REJECTED with:
                  "This face already exists in the database.
                   Registered as: <name> (Roll: <roll>)"
            - Stores a JPEG photo of the registered face for the Face
              Search result card.
        """
        data = request.get_json() or {}

        if student_id is None:
            student_id = data.get("student_id")
        image_base64 = data.get("image")

        if not student_id or not image_base64:
            return jsonify({
                "success": False,
                "message": "Student ID and image are required.",
            })

        try:
            student_id = int(student_id)
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "Invalid student ID."})

        # Check the student actually exists before processing the image.
        student = get_student_by_id(student_id)
        if student is None:
            return jsonify({"success": False, "message": "Student not found."}), 404

        frame = decode_base64_image(image_base64)
        if frame is None:
            return jsonify({"success": False, "message": "Could not decode image."})

        try:
            from backend.face_recognizer import FaceRecognizer
            from config import FACE_DUPLICATE_THRESHOLD
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

        # -----------------------------------------------------------------
        # DUPLICATE FACE GUARD
        # -----------------------------------------------------------------
        duplicate = recognizer.check_duplicate_face(
            encodings[0],
            threshold=FACE_DUPLICATE_THRESHOLD,
        )
        if duplicate["is_duplicate"]:
            dup_student = duplicate["student"]
            return jsonify({
                "success": False,
                "is_duplicate": True,
                "message": (
                    "This face already exists in the database. "
                    f"Registered as: {dup_student['name']} "
                    f"(Roll: {dup_student['roll_number']})"
                ),
                "duplicate_student": dup_student,
                "distance": duplicate.get("distance"),
            })

        # -----------------------------------------------------------------
        # Encode the raw JPEG for the face_image column.
        # -----------------------------------------------------------------
        import cv2
        ok, buffer = cv2.imencode(".jpg", frame)
        face_image_bytes = buffer.tobytes() if ok else None

        success = update_face_encoding(student_id, encodings[0], face_image=face_image_bytes)

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

        Data: total students, present today, absent (total - present),
        plus the student list for the individual graphical report dropdown.
        """
        stats = get_dashboard_stats()
        absent = stats["total_students"] - stats["present_today"]
        all_students = get_all_students()

        departments = sorted(set(s["department"] for s in all_students if s["department"]))
        semesters = sorted(set(s["semester"] for s in all_students if s["semester"]))

        return render_template(
            "reports.html",
            total_students=stats["total_students"],
            present_students=stats["present_today"],
            absent_students=absent,
            students=all_students,
            departments=departments,
            semesters=semesters,
        )

    @app.route("/api/students/stats/<int:student_id>", methods=["GET"])
    @login_required_api
    def student_stats(student_id):
        """
        API: Get full statistical report for ONE student.

        Returns total classes, present, absent, attendance %, monthly and
        weekly series — everything the Reports page charts need.
        """
        student = get_student_by_id(student_id)
        if student is None:
            return jsonify({"success": False, "error": "Student not found."})

        stats = get_student_stats(student_id)

        return jsonify({
            "success": True,
            "student": {
                "id": student["id"],
                "name": student["name"],
                "roll_number": student["roll_number"],
                "department": student["department"],
                "semester": student["semester"],
            },
            "stats": stats,
        })

    @app.route("/api/attendance/all", methods=["GET"])
    @login_required_api
    def get_all_attendance_api():
        """
        API: Get all attendance records (for reports or data tables).

        Supports optional filters:
            ?date=2026-07-30
            &department=Computer
            &semester=5th
            &status=Present
            &date_from=...&date_to=...
        """
        target_date = request.args.get("date")

        filters = {
            "department": request.args.get("department"),
            "semester": request.args.get("semester"),
            "status": request.args.get("status"),
            "date_from": request.args.get("date_from"),
            "date_to": request.args.get("date_to"),
        }

        if target_date:
            records = get_attendance_by_date(
                target_date,
                department=filters["department"],
                semester=filters["semester"],
            )
        else:
            records = get_all_attendance_records(**filters)

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
        records = get_attendance_by_student(student_id)
        return jsonify(records)

    # =================================================================
    # FACE SEARCH
    #
    # NEW v2 page. Open the camera, capture a face, and search the
    # database for the matching student. Displays a result card with
    # student details and attendance statistics.
    # =================================================================

    @app.route("/face-search")
    @login_required
    def face_search():
        """Render the Face Search page (camera preview + result card)."""
        return render_template("face_search.html")

    @app.route("/api/face-search", methods=["POST"])
    @login_required_api
    def face_search_api():
        """
        API: Search the database for a student using their face.

        Receives a base64 camera frame, runs face recognition, and
        returns the matching student's details + attendance stats.
        Never writes to the attendance table.
        """
        data = request.get_json()

        if not data or "image" not in data:
            return jsonify({"success": False, "message": "No image received."})

        frame = decode_base64_image(data["image"])
        if frame is None:
            return jsonify({"success": False, "message": "Could not decode image."})

        result = search_student_by_face(frame)

        if not result["success"]:
            return jsonify(result)

        # Convert the registered face photo (bytes) to base64 for display
        if result.get("result") and result["result"].get("face_image"):
            result["result"]["face_image"] = base64.b64encode(
                result["result"]["face_image"]
            ).decode("utf-8")

        return jsonify(result)

    # =================================================================
    # DASHBOARD CHART DATA
    #
    # v2 endpoints that feed the Chart.js graphs on the dashboard.
    # =================================================================

    @app.route("/api/dashboard/attendance-by-department", methods=["GET"])
    @login_required_api
    def dashboard_by_department():
        """API: Attendance grouped by department (today)."""
        return jsonify(get_attendance_by_department())

    @app.route("/api/dashboard/attendance-by-semester", methods=["GET"])
    @login_required_api
    def dashboard_by_semester():
        """API: Attendance grouped by semester (today)."""
        return jsonify(get_attendance_by_semester())

    @app.route("/api/dashboard/daily", methods=["GET"])
    @login_required_api
    def dashboard_daily():
        """API: Present count per day for the last N days."""
        try:
            days = int(request.args.get("days", 14))
        except ValueError:
            days = 14
        return jsonify(get_daily_attendance(days))

    @app.route("/api/dashboard/monthly", methods=["GET"])
    @login_required_api
    def dashboard_monthly():
        """API: Attendance aggregated by month."""
        try:
            months = int(request.args.get("months", 6))
        except ValueError:
            months = 6
        return jsonify(get_monthly_attendance(months))

    @app.route("/api/dashboard/top-absent", methods=["GET"])
    @login_required_api
    def dashboard_top_absent():
        """API: Students with the lowest attendance percentage."""
        try:
            limit = int(request.args.get("limit", 5))
        except ValueError:
            limit = 5
        return jsonify(get_top_absent_students(limit))

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
