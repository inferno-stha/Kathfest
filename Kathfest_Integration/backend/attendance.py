"""
attendance.py - Attendance management and face recognition integration.

This module bridges the gap between the face recognition backend and
the attendance database. It provides the high-level operations that
the Flask routes call:

    - mark_attendance_from_frame(): Capture a frame, recognize the
      face, and mark attendance in one step.
    - get_attendance_summary(): Get formatted attendance data for
      the dashboard and reports.

How this was created:
    Attendance logic was scattered across:
        - backend/recordentryandinsertion.py (mark_attendance, export)
        - database/record_entry_and_insertion.py (improved versions)
        - routes.py (attendance endpoint stubs)

    This module consolidates those into a clean API.
"""

from datetime import datetime, date

from database.db import (
    get_today_attendance,
    get_attendance_stats,
    get_all_attendance_records,
    get_attendance_by_date,
    get_attendance_by_student,
    mark_attendance as db_mark_attendance,
    export_attendance_csv,
)
from backend.face_recognizer import FaceRecognizer


# Global face recognizer instance (lazy-initialized)
_recognizer = None


def get_recognizer():
    """
    Get or create the global FaceRecognizer instance.
    Using a singleton pattern avoids reloading face encodings on
    every request.
    """
    global _recognizer
    if _recognizer is None:
        _recognizer = FaceRecognizer()
    return _recognizer


# =========================================================================
# Function: mark_attendance_from_frame()
#
# Purpose:
#     The core attendance-marking pipeline. Takes an image frame,
#     runs face recognition on it, and if a known student is found,
#     marks them as present in the database.
#
# Args:
#     frame: A numpy array (BGR format) captured from the camera.
#            This can come from either the server-side camera or
#            from a base64-decoded image sent by the browser.
#
# Returns:
#     Dict with keys:
#         success (bool):       Whether attendance was marked
#         student_name (str):   Name of recognized student (or None)
#         message (str):        Human-readable result
#         already_marked (bool): True if already marked today
#
# Flow:
#     1. Get the FaceRecognizer singleton
#     2. Call recognizer.recognize(frame) to detect + compare
#     3. If recognized, call db.mark_attendance(student_id)
#     4. Return the result as a JSON-serializable dict
#
# How this integrates the original code:
#     - Face detection/encoding: database/face_utils.py
#     - Face comparison:        database/recognize.py
#     - Database insert:        database/record_entry_and_insertion.py
# =========================================================================
def mark_attendance_from_frame(frame):
    """
    Recognize a face in the given frame and mark attendance.

    This is the main integration point between computer vision
    and the database. It replaces the old manual attendance marking
    (where an admin would select a student name from a dropdown).

    Args:
        frame: OpenCV BGR image (numpy array)

    Returns:
        Dict with result information.
    """
    recognizer = get_recognizer()

    # Step 1: Run face recognition on the frame
    result = recognizer.recognize(frame)

    if not result["success"]:
        return {
            "success": False,
            "student_name": None,
            "message": result["message"],
            "already_marked": False,
        }

    # Step 2: Mark attendance in the database
    student = result["student"]
    student_id = student["id"]
    student_name = student["name"]

    was_marked = db_mark_attendance(student_id)

    if was_marked:
        return {
            "success": True,
            "student_name": student_name,
            "message": f"Attendance marked for '{student_name}'.",
            "already_marked": False,
        }
    else:
        return {
            "success": True,
            "student_name": student_name,
            "message": f"'{student_name}' was already marked present today.",
            "already_marked": True,
        }


# =========================================================================
# Function: get_today_attendance_formatted()
#
# Purpose:
#     Returns today's attendance records in the tuple format
#     expected by the Jinja2 templates (preserving backward
#     compatibility with the original template code).
#
# Returns:
#     List of (student_name, time, status) tuples
# =========================================================================
def get_today_attendance_formatted():
    """Get today's attendance in (name, time, status) tuple format."""
    return get_today_attendance()


# =========================================================================
# Function: get_dashboard_stats()
#
# Purpose:
#     Returns attendance statistics for the dashboard page.
#
# Returns:
#     Dict with total_students, present_today, attendance_pct
# =========================================================================
def get_dashboard_stats():
    """Get attendance statistics for the dashboard."""
    return get_attendance_stats()


# =========================================================================
# Function: get_all_attendance()
#
# Purpose:
#     Returns all attendance records for the reports page.
#
# Returns:
#     List of dicts with name, roll_number, department, date, time, status
# =========================================================================
def get_all_attendance():
    """Get all attendance records."""
    return get_all_attendance_records()


# =========================================================================
# Function: get_csv_data()
#
# Purpose:
#     Generates CSV string of all attendance data for download.
#
# Returns:
#     String with CSV-formatted data
# =========================================================================
def get_csv_data():
    """Export all attendance data as CSV string."""
    return export_attendance_csv()


def reload_face_data():
    """
    Reload face encodings from the database.
    Call this after registering a new student's face.
    """
    recognizer = get_recognizer()
    recognizer.reload_known_faces()
