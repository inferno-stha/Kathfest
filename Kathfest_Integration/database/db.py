"""
db.py - Database connection and initialization for the attendance system.

This module was created by merging the functionality from:
    1. backend/database.py  (table creation logic)
    2. database/database.py (get_connection + initialize_database)
    3. backend/recordentryandinsertion.py (CRUD operations)
    4. database/record_entry_and_insertion.py (improved CRUD with numpy)

Why merged:
    - Three separate files all connected to the same database with
      overlapping table definitions. Keeping them separate would cause
      maintenance confusion and duplicate code.
    - The database/record_entry_and_insertion.py version has better
      numpy integration for face encoding serialization, so we adopt
      that approach here.
    - Added a semester field to the students table (required by the UI
      but missing from the original person table).

Design decisions:
    - Face encodings are stored as BLOBs (binary large objects) using
      numpy .tobytes() and np.frombuffer() for serialization.
    - The students table uses 'roll_number' (not 'roll_no') for
      consistency with the requested schema.
    - All functions accept and return dicts for clarity.
"""

import sqlite3
import numpy as np
from datetime import datetime, date
import csv
import io
import os

from config import DATABASE_NAME


# =========================================================================
# Helper: ensure database directory exists
# =========================================================================
def _ensure_db_dir():
    """Create the database directory if it doesn't exist."""
    db_dir = os.path.dirname(DATABASE_NAME)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)


# =========================================================================
# Function: get_connection()
#
# Purpose:
#     Returns a new SQLite connection to the attendance database.
#     Every function that needs to query the database calls this
#     instead of creating connections directly — this way we only
#     specify the database path in ONE place (config.py).
#
#     SQLite row_factory is set to sqlite3.Row so that query results
#     can be accessed both by index (row[0]) and by column name
#     (row["name"]).
#
# Called When:
#     Any time a database read or write is needed.
# =========================================================================
def get_connection():
    """Create and return a connection to the SQLite database."""
    _ensure_db_dir()
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# =========================================================================
# Function: initialize_database()
#
# Purpose:
#     Creates the students and attendance tables if they don't already
#     exist. Called once when the Flask application starts.
#
# Tables created:
#     students:
#         id            - Auto-incrementing primary key
#         name          - Student's full name (required)
#         roll_number   - Unique roll number (required)
#         department    - Department name
#         semester      - Current semester (e.g. "2nd", "4th")
#         face_encoding - Numpy face encoding stored as BLOB
#         registered_date - Timestamp of when the student was added
#
#     attendance:
#         id            - Auto-incrementing primary key
#         student_id    - Foreign key referencing students.id
#         date          - Attendance date (ISO format: YYYY-MM-DD)
#         time          - Attendance time (HH:MM:SS format)
#         status        - 'Present' or 'Absent' (default 'Present')
#
# How this differs from original:
#     - Original 'person' table renamed to 'students' with added 'semester'
#     - Original 'roll_no' renamed to 'roll_number'
#     - Original 'attendance_date' / 'attendance_time' renamed to 'date' / 'time'
#     - Added FOREIGN KEY constraint for referential integrity
# =========================================================================
def initialize_database():
    """Create the required tables if they do not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # -- Students table --
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT UNIQUE NOT NULL,
            department TEXT,
            semester TEXT,
            face_encoding BLOB,
            registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -- Attendance table --
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date DATE NOT NULL,
            time TIME NOT NULL,
            status TEXT DEFAULT 'Present',
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# =========================================================================
# STUDENT CRUD OPERATIONS
# =========================================================================

def add_student(name, roll_number, department, semester, face_encoding=None):
    """
    Insert a new student record into the database.

    Args:
        name: Student's full name (string)
        roll_number: Unique roll number (string)
        department: Department name (string)
        semester: Current semester (string, e.g. "2nd")
        face_encoding: Numpy array of face encoding, or None

    Returns:
        The new student's id (int) if successful, or None if duplicate.

    How it works:
        1. Serialize the face_encoding numpy array to bytes using
           astype(np.float64).tobytes().
        2. Execute an INSERT SQL statement with parameterized ? placeholders
           to prevent SQL injection.
        3. If a UNIQUE constraint fails (duplicate roll_number), catch the
           exception and return None.

    Original source:
        Merged from database/record_entry_and_insertion.py insert_person()
        and backend/recordentryandinsertion.py insert_person().
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Serialize face encoding to binary blob
    encoding_blob = None
    if face_encoding is not None:
        encoding_blob = face_encoding.astype(np.float64).tobytes()

    try:
        cursor.execute("""
            INSERT INTO students (name, roll_number, department, semester, face_encoding)
            VALUES (?, ?, ?, ?, ?)
        """, (name, roll_number, department, semester, encoding_blob))
        conn.commit()
        student_id = cursor.lastrowid
        conn.close()
        return student_id
    except sqlite3.IntegrityError:
        # Duplicate roll_number
        conn.close()
        return None


def get_all_students():
    """
    Retrieve all students from the database.

    Returns:
        List of dicts, each with keys: id, name, roll_number, department, semester.

    How it works:
        1. SELECT all columns (except face_encoding which is large) from students.
        2. Fetch all rows as sqlite3.Row objects (dict-like).
        3. Convert each Row to a regular dict for JSON serialization.

    Original source:
        database/record_entry_and_insertion.py get_all_people()
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, roll_number, department, semester
        FROM students
        ORDER BY name ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_student_by_id(student_id):
    """
    Retrieve a single student by their primary key id.

    Returns:
        Dict with student data, or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, roll_number, department, semester, face_encoding
        FROM students
        WHERE id = ?
    """, (student_id,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    student = dict(row)

    # Deserialize face encoding from BLOB to numpy array
    if student["face_encoding"] is not None:
        student["face_encoding"] = np.frombuffer(
            student["face_encoding"],
            dtype=np.float64
        )

    return student


def update_student(student_id, name=None, roll_number=None, department=None, semester=None):
    """
    Update a student's information. Only non-None fields are updated.

    Returns:
        True if successful, False if roll_number conflicts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Build dynamic SET clause for non-None fields
    updates = []
    params = []
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if roll_number is not None:
        updates.append("roll_number = ?")
        params.append(roll_number)
    if department is not None:
        updates.append("department = ?")
        params.append(department)
    if semester is not None:
        updates.append("semester = ?")
        params.append(semester)

    if not updates:
        conn.close()
        return False

    params.append(student_id)

    try:
        cursor.execute(f"""
            UPDATE students
            SET {", ".join(updates)}
            WHERE id = ?
        """, params)
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        conn.close()
        return False


def delete_student(student_id):
    """
    Delete a student and all their attendance records.

    Returns:
        True if a row was deleted, False if not found.

    Note:
        The ON DELETE CASCADE foreign key constraint ensures that
        attendance records for this student are also deleted.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()

    return deleted


def search_students(query, department=None, semester=None):
    """
    Search and filter students by name/roll_number, department, and semester.

    Args:
        query: Text to search in name or roll_number (case-insensitive)
        department: Filter by department, or None for all
        semester: Filter by semester, or None for all

    Returns:
        List of matching student dicts.

    This replaces the old in-memory filtering in routes.py with
    a proper SQL WHERE query, making it more efficient for large datasets.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT id, name, roll_number, department, semester FROM students WHERE 1=1"
    params = []

    if query:
        sql += " AND (LOWER(name) LIKE ? OR LOWER(roll_number) LIKE ?)"
        params.extend([f"%{query.lower()}%", f"%{query.lower()}%"])

    if department and department != "all":
        sql += " AND department = ?"
        params.append(department)

    if semester and semester != "all":
        sql += " AND semester = ?"
        params.append(semester)

    sql += " ORDER BY name ASC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_all_face_encodings():
    """
    Retrieve all students who have face encodings stored.

    Returns:
        List of dicts: {id, name, roll_number, encoding (numpy array)}

    This is used by the face recognition module to build the
    known_encodings list for comparison.

    Original source:
        database/record_entry_and_insertion.py get_all_people()
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, roll_number, face_encoding
        FROM students
        WHERE face_encoding IS NOT NULL
    """)

    rows = cursor.fetchall()
    conn.close()

    people = []
    for row in rows:
        row_dict = dict(row)
        if row_dict["face_encoding"] is not None:
            row_dict["encoding"] = np.frombuffer(
                row_dict["face_encoding"],
                dtype=np.float64
            )
        people.append(row_dict)

    return people


def update_face_encoding(student_id, face_encoding):
    """
    Store or update a student's face encoding.

    Args:
        student_id: The student's database id
        face_encoding: Numpy array of the face encoding

    Returns:
        True if successful.
    """
    conn = get_connection()
    cursor = conn.cursor()

    encoding_blob = face_encoding.astype(np.float64).tobytes()

    cursor.execute("""
        UPDATE students
        SET face_encoding = ?
        WHERE id = ?
    """, (encoding_blob, student_id))

    conn.commit()
    success = cursor.rowcount > 0
    conn.close()

    return success


# =========================================================================
# ATTENDANCE OPERATIONS
# =========================================================================

def mark_attendance(student_id):
    """
    Mark a student as present for today.

    Only marks attendance if the student has NOT already been marked
    present today (prevents duplicates).

    Args:
        student_id: The student's database id

    Returns:
        True if attendance was newly marked, False if already marked.

    How it works:
        1. Get today's date and current time.
        2. Check if an attendance record already exists for this
           student today.
        3. If not, INSERT a new record with status 'Present'.
        4. If yes, do nothing (already present).

    Original source:
        Merged from database/record_entry_and_insertion.py mark_attendance()
        and backend/recordentryandinsertion.py mark_attendance().
    """
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now()
    today_date = now.date().isoformat()       # "2026-07-30"
    current_time = now.strftime("%H:%M:%S")   # "14:30:00"

    # Check if already marked present today
    cursor.execute("""
        SELECT id FROM attendance
        WHERE student_id = ? AND date = ?
    """, (student_id, today_date))

    if cursor.fetchone() is not None:
        conn.close()
        return False  # Already marked

    # Insert new attendance record
    cursor.execute("""
        INSERT INTO attendance (student_id, date, time, status)
        VALUES (?, ?, ?, 'Present')
    """, (student_id, today_date, current_time))

    conn.commit()
    conn.close()
    return True


def get_today_attendance():
    """
    Get all attendance records for today, joined with student names.

    Returns:
        List of tuples: (student_name, time, status)
        This format matches what the existing Jinja2 templates expect.

    How it works:
        1. JOIN attendance with students on student_id.
        2. Filter by today's date.
        3. Return as a list of (name, time, status) tuples.

    Original source:
        This consolidates ad-hoc queries from routes.py and
        database/record_entry_and_insertion.py.
    """
    conn = get_connection()
    cursor = conn.cursor()

    today_date = date.today().isoformat()

    cursor.execute("""
        SELECT s.name, a.time, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date = ?
        ORDER BY a.time ASC
    """, (today_date,))

    rows = cursor.fetchall()
    conn.close()

    return [(row["name"], row["time"], row["status"]) for row in rows]


def get_all_attendance_records():
    """
    Get all attendance records with student information.

    Returns:
        List of dicts: {name, roll_number, department, date, time, status}

    Used for reports and CSV export.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.name, s.roll_number, s.department,
               a.date, a.time, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.date DESC, a.time DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_attendance_by_date(target_date=None):
    """
    Get attendance records filtered by a specific date.

    Args:
        target_date: Date string (YYYY-MM-DD), or None for today

    Returns:
        List of dicts: {name, roll_number, department, date, time, status}
    """
    if target_date is None:
        target_date = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.name, s.roll_number, s.department,
               a.date, a.time, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date = ?
        ORDER BY a.time ASC
    """, (target_date,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_attendance_by_student(student_id):
    """
    Get attendance records for a specific student.

    Args:
        student_id: The student's database id

    Returns:
        List of dicts: {date, time, status}
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, time, status
        FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC
    """, (student_id,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_attendance_stats():
    """
    Calculate attendance statistics for the dashboard.

    Returns:
        Dict with keys:
            total_students (int): Total number of students in the database
            present_today (int): Number of students marked present today
            attendance_pct (float): Percentage of students present today

    How this maps to the original:
        Tkinter's show_dashboard() calculated these from in-memory lists.
        Now they come from real database queries.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Total students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Present today
    today_date = date.today().isoformat()
    cursor.execute("""
        SELECT COUNT(DISTINCT student_id)
        FROM attendance
        WHERE date = ?
    """, (today_date,))
    present_today = cursor.fetchone()[0]

    conn.close()

    attendance_pct = round((present_today / total_students) * 100, 1) if total_students else 0

    return {
        "total_students": total_students,
        "present_today": present_today,
        "attendance_pct": attendance_pct,
    }


def export_attendance_csv():
    """
    Generate a CSV string of all attendance records.

    Returns:
        String containing CSV-formatted attendance data.

    How it works:
        1. Query all attendance records joined with student info.
        2. Write to an in-memory StringIO buffer.
        3. Return the buffer contents as a string.

    Original source:
        backend/recordentryandinsertion.py export_attendance_to_csv()
        and database/record_entry_and_insertion.py export_attendance_to_csv().
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.name, s.roll_number, s.department,
               a.date, a.time, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.date DESC, a.time DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(["Name", "Roll Number", "Department", "Date", "Time", "Status"])

    # Data rows
    for row in rows:
        writer.writerow([row["name"], row["roll_number"], row["department"],
                         row["date"], row["time"], row["status"]])

    return output.getvalue()
