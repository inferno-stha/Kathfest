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
from datetime import datetime, date, timedelta
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
#         department    - Snapshot of the student's department at mark time
#         semester      - Snapshot of the student's semester at mark time
#         confidence    - Similarity percentage (0-100) of the face match
#         session_id    - Camera session id that recorded the attendance
#
#     camera_sessions:
#         id            - Auto-incrementing primary key
#         started_at    - Timestamp when the session started
#         ended_at      - Timestamp when the session ended
#         total_recognized - Number of distinct students recognized
#         unknown_faces    - Number of unknown faces seen
#
# Indexes (created in _create_indexes()):
#     - students.roll_number
#     - students.department
#     - students.semester
#     - attendance.date
#     - attendance.student_id
#
# How this differs from original:
#     - Original 'person' table renamed to 'students' with added 'semester'
#     - Original 'roll_no' renamed to 'roll_number'
#     - Original 'attendance_date' / 'attendance_time' renamed to 'date' / 'time'
#     - Added FOREIGN KEY constraint for referential integrity
#     - attendance gained department / semester / confidence / session_id
#     - New camera_sessions table tracks each attendance session
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
            face_image BLOB,
            face_registered INTEGER DEFAULT 0,
            registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -- Attendance table (with extra columns added in v2) --
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date DATE NOT NULL,
            time TIME NOT NULL,
            status TEXT DEFAULT 'Present',
            department TEXT,
            semester TEXT,
            confidence REAL,
            session_id INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    # -- Camera sessions table (added in v2) --
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS camera_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            total_recognized INTEGER DEFAULT 0,
            unknown_faces INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

    # Migrate older databases and create indexes.
    _create_indexes()
    _migrate_attendance_schema()


def _create_indexes():
    """
    Create indexes that speed up the most common filter queries.
    Indexes use IF NOT EXISTS so this is safe to run on every start.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_roll ON students(roll_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_dept ON students(department)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_sem ON students(semester)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id)")
    conn.commit()
    conn.close()


def _migrate_attendance_schema():
    """
    In-place migration for databases created by the ORIGINAL v1 schema.
    If the attendance table is missing the new v2 columns, ALTER TABLE
    statements add them (SQLite supports ADD COLUMN). Existing rows get
    NULL defaults which the app treats as 0% / no-session.
    """
    conn = get_connection()
    cursor = conn.cursor()

    columns = [row[1] for row in cursor.execute("PRAGMA table_info(attendance)").fetchall()]

    new_columns = {
        "department": "TEXT",
        "semester": "TEXT",
        "confidence": "REAL",
        "session_id": "INTEGER",
    }

    for col, col_type in new_columns.items():
        if col not in columns:
            cursor.execute(f"ALTER TABLE attendance ADD COLUMN {col} {col_type}")

    # Add face_image column to students if missing (v2 feature).
    student_cols = [row[1] for row in cursor.execute("PRAGMA table_info(students)").fetchall()]
    if "face_image" not in student_cols:
        cursor.execute("ALTER TABLE students ADD COLUMN face_image BLOB")
    if "face_registered" not in student_cols:
        cursor.execute(
            "ALTER TABLE students ADD COLUMN face_registered INTEGER DEFAULT 0"
        )

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
        SELECT id, name, roll_number, department, semester, face_encoding, face_image, face_registered
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
        SELECT id, name, roll_number, department, semester, face_encoding, face_image, face_registered
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

    sql = "SELECT id, name, roll_number, department, semester, face_encoding, face_registered FROM students WHERE 1=1"
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
        SELECT id, name, roll_number, department, semester, face_encoding, face_image
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


def update_face_encoding(student_id, face_encoding, face_image=None):
    """
    Store or update a student's face encoding.

    Args:
        student_id: The student's database id
        face_encoding: Numpy array of the face encoding
        face_image: Optional JPEG bytes of the registered face photo

    Returns:
        True if successful.
    """
    conn = get_connection()
    cursor = conn.cursor()

    encoding_blob = face_encoding.astype(np.float64).tobytes()

    if face_image is not None:
        cursor.execute("""
            UPDATE students
            SET face_encoding = ?, face_image = ?, face_registered = 1
            WHERE id = ?
        """, (encoding_blob, face_image, student_id))
    else:
        cursor.execute("""
            UPDATE students
            SET face_encoding = ?, face_registered = 1
            WHERE id = ?
        """, (encoding_blob, student_id))

    conn.commit()
    success = cursor.rowcount > 0
    conn.close()

    return success


# =========================================================================
# ATTENDANCE OPERATIONS
# =========================================================================

def mark_attendance(student_id, confidence=None, session_id=None, department=None, semester=None):
    """
    Mark a student as present for today.

    Only marks attendance if the student has NOT already been marked
    present today (prevents duplicates).

    Args:
        student_id: The student's database id
        confidence: Similarity percentage (0-100) of the face match (v2)
        session_id: Camera session id that recorded the attendance (v2)
        department: Snapshot of the student's department (v2)
        semester:   Snapshot of the student's semester (v2)

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
        INSERT INTO attendance (student_id, date, time, status, department, semester, confidence, session_id)
        VALUES (?, ?, ?, 'Present', ?, ?, ?, ?)
    """, (student_id, today_date, current_time, department, semester, confidence, session_id))

    conn.commit()
    conn.close()
    return True


def get_today_attendance():
    """
    Get all attendance records for today, joined with student names.

    Returns:
        List of tuples: (student_name, time, status, confidence)
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
        SELECT s.name, a.time, a.status, a.confidence
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date = ?
        ORDER BY a.time ASC
    """, (today_date,))

    rows = cursor.fetchall()
    conn.close()

    return [(row["name"], row["time"], row["status"], row["confidence"]) for row in rows]


def get_all_attendance_records(department=None, semester=None, status=None, date_from=None, date_to=None):
    """
    Get all attendance records with student information.

    Args:
        department: Filter by department, or None for all
        semester:   Filter by semester, or None for all
        status:     Filter by status ('Present'/'Absent'), or None for all
        date_from:  Start date (YYYY-MM-DD) inclusive, or None
        date_to:    End date (YYYY-MM-DD) inclusive, or None

    Returns:
        List of dicts: {id, name, roll_number, department, date, time,
                        status, confidence, semester}

    Used for reports, CSV export and the dashboard.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT a.id, s.name, s.roll_number, s.department,
               a.date, a.time, a.status, a.confidence, a.semester
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE 1=1
    """
    params = []

    if department and department != "all":
        sql += " AND a.department = ?"
        params.append(department)
    if semester and semester != "all":
        sql += " AND a.semester = ?"
        params.append(semester)
    if status and status != "all":
        sql += " AND a.status = ?"
        params.append(status)
    if date_from:
        sql += " AND a.date >= ?"
        params.append(date_from)
    if date_to:
        sql += " AND a.date <= ?"
        params.append(date_to)

    sql += " ORDER BY a.date DESC, a.time DESC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_attendance_by_date(target_date=None, department=None, semester=None):
    """
    Get attendance records filtered by a specific date.

    Args:
        target_date: Date string (YYYY-MM-DD), or None for today
        department:  Filter by department, or None for all
        semester:    Filter by semester, or None for all

    Returns:
        List of dicts: {name, roll_number, department, date, time, status, confidence}
    """
    if target_date is None:
        target_date = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT s.name, s.roll_number, s.department,
               a.date, a.time, a.status, a.confidence
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date = ?
    """
    params = [target_date]

    if department and department != "all":
        sql += " AND a.department = ?"
        params.append(department)
    if semester and semester != "all":
        sql += " AND a.semester = ?"
        params.append(semester)

    sql += " ORDER BY a.time ASC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_attendance_by_student(student_id):
    """
    Get attendance records for a specific student.

    Args:
        student_id: The student's database id

    Returns:
        List of dicts: {date, time, status, confidence, semester}
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, time, status, confidence, semester
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

    # Students with a registered face
    cursor.execute("SELECT COUNT(*) FROM students WHERE face_encoding IS NOT NULL")
    face_registered = cursor.fetchone()[0]

    conn.close()

    attendance_pct = round((present_today / total_students) * 100, 1) if total_students else 0

    return {
        "total_students": total_students,
        "present_today": present_today,
        "attendance_pct": attendance_pct,
        "face_registered": face_registered,
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
        SELECT s.name, s.roll_number, s.department, s.semester,
               a.date, a.time, a.status, a.confidence
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.date DESC, a.time DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(["Name", "Roll Number", "Department", "Semester",
                     "Date", "Time", "Status", "Confidence (%)"])

    # Data rows
    for row in rows:
        writer.writerow([row["name"], row["roll_number"], row["department"],
                         row["semester"], row["date"], row["time"],
                         row["status"], row["confidence"] if row["confidence"] is not None else ""])

    return output.getvalue()


# =========================================================================
# V2 ADDITIONS
# -------------------------------------------------------------------------
# The functions below power the new hackathon-ready features:
#     - Duplicate face registration guard
#     - Individual graphical reports
#     - Dashboard charts (department / semester / daily / monthly)
#     - Camera sessions
#     - Face search
# =========================================================================

# -------------------------------------------------------------------------
# DUPLICATE FACE REGISTRATION GUARD
# -------------------------------------------------------------------------

def get_all_face_encodings_for_duplicate_check():
    """
    Retrieve every student that has a face encoding, INCLUDING students
    that were just added but whose encoding may be the same face.

    Returns:
        List of dicts: {id, name, roll_number, encoding (numpy array)}
    """
    return get_all_face_encodings()


def find_duplicate_face(face_encoding, threshold, recognizer):
    """
    Check whether the given face encoding already belongs to another
    student in the database.

    Args:
        face_encoding: 128-d numpy array of the new face
        threshold: face_distance below which we treat it as a duplicate
        recognizer: FaceRecognizer instance (to reuse loaded encodings)

    Returns:
        Dict {is_duplicate, student, distance, confidence} or
        {is_duplicate: False} if no match.
    """
    if face_encoding is None:
        return {"is_duplicate": False}

    return recognizer.find_best_match(face_encoding, threshold=threshold)


# -------------------------------------------------------------------------
# INDIVIDUAL STUDENT REPORT (for Chart.js on the Reports page)
# -------------------------------------------------------------------------

def get_student_stats(student_id):
    """
    Build a full statistical report for one student.

    Returns:
        Dict with:
            total_classes (int)   - number of distinct dates with a record
            present (int)         - 'Present' records
            absent (int)          - 'Absent' records
            attendance_pct (float)- present / total * 100
            last_attendance (str) - most recent attendance date
            monthly_labels (list) - month names, e.g. ['Jan', 'Feb', ...]
            monthly_present (list)- present count per month
            monthly_total (list)  - total records per month
            weekly_labels (list)  - week labels (Mon..Sun based on weeks used)
            weekly_present (list) - present count per week
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, time, status, confidence
        FROM attendance
        WHERE student_id = ?
        ORDER BY date ASC
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()

    records = [dict(r) for r in rows]

    total_classes = len(records)
    present = sum(1 for r in records if r["status"] == "Present")
    absent = total_classes - present
    attendance_pct = round((present / total_classes) * 100, 1) if total_classes else 0.0

    last_attendance = records[-1]["date"] if records else None

    # --- Monthly aggregation (present / total per calendar month) ---
    monthly = {}
    for r in records:
        month_key = r["date"][:7]  # YYYY-MM
        monthly.setdefault(month_key, {"present": 0, "total": 0})
        monthly[month_key]["total"] += 1
        if r["status"] == "Present":
            monthly[month_key]["present"] += 1

    monthly_labels = []
    monthly_present = []
    monthly_total = []
    for key in sorted(monthly.keys()):
        try:
            month_label = datetime.strptime(key, "%Y-%m").strftime("%b %Y")
        except ValueError:
            month_label = key
        monthly_labels.append(month_label)
        monthly_present.append(monthly[key]["present"])
        monthly_total.append(monthly[key]["total"])

    # --- Weekly aggregation (last 8 weeks: present / total) ---
    weekly = {}
    today = date.today()
    for offset in range(0, 8):
        # Week label: Monday of the week
        d = today - timedelta(days=today.weekday() + offset * 7)
        weekly[d.isoformat()] = {"present": 0, "total": 0}
    for r in records:
        try:
            r_date = datetime.strptime(r["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        week_start = r_date - timedelta(days=r_date.weekday())
        week_start = week_start.isoformat()
        if week_start in weekly:
            weekly[week_start]["total"] += 1
            if r["status"] == "Present":
                weekly[week_start]["present"] += 1

    weekly_labels = []
    weekly_present = []
    weekly_total = []
    for key in sorted(weekly.keys()):
        try:
            label = datetime.strptime(key, "%Y-%m-%d").strftime("%d %b")
        except ValueError:
            label = key
        weekly_labels.append(label)
        weekly_present.append(weekly[key]["present"])
        weekly_total.append(weekly[key]["total"])

    return {
        "total_classes": total_classes,
        "present": present,
        "absent": absent,
        "attendance_pct": attendance_pct,
        "last_attendance": last_attendance,
        "monthly_labels": monthly_labels,
        "monthly_present": monthly_present,
        "monthly_total": monthly_total,
        "weekly_labels": weekly_labels,
        "weekly_present": weekly_present,
        "weekly_total": weekly_total,
    }


# -------------------------------------------------------------------------
# DASHBOARD CHART DATA
# -------------------------------------------------------------------------

def get_attendance_by_department():
    """
    Count of students marked present today grouped by department.

    Returns:
        List of dicts: {department, present, total}
    """
    conn = get_connection()
    cursor = conn.cursor()
    today_date = date.today().isoformat()

    cursor.execute("""
        SELECT s.department AS department,
               COUNT(DISTINCT a.student_id) AS present,
               (SELECT COUNT(*) FROM students s2
                WHERE s2.department = s.department) AS total
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date = ? AND s.department IS NOT NULL
        GROUP BY s.department
        ORDER BY s.department ASC
    """, (today_date,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_attendance_by_semester():
    """
    Count of students marked present today grouped by semester.

    Returns:
        List of dicts: {semester, present, total}
    """
    conn = get_connection()
    cursor = conn.cursor()
    today_date = date.today().isoformat()

    cursor.execute("""
        SELECT s.semester AS semester,
               COUNT(DISTINCT a.student_id) AS present,
               (SELECT COUNT(*) FROM students s2
                WHERE s2.semester = s.semester) AS total
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date = ? AND s.semester IS NOT NULL
        GROUP BY s.semester
        ORDER BY s.semester ASC
    """, (today_date,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_daily_attendance(days=14):
    """
    Present count per day for the last N days (for the today's / daily graph).

    Returns:
        List of dicts: {date, present} for each of the last N days.
    """
    conn = get_connection()
    cursor = conn.cursor()

    result = []
    today = date.today()
    for offset in range(days - 1, -1, -1):
        d = (today - timedelta(days=offset)).isoformat()
        cursor.execute("""
            SELECT COUNT(DISTINCT student_id) AS present
            FROM attendance
            WHERE date = ?
        """, (d,))
        present = cursor.fetchone()["present"]
        result.append({"date": d, "present": present})

    conn.close()
    return result


def get_monthly_attendance(months=6):
    """
    Attendance records aggregated by month for the last N months.

    Returns:
        List of dicts: {month, total, present, pct}
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT substr(date, 1, 7) AS month,
               COUNT(*) AS total,
               SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present
        FROM attendance
        WHERE date >= ?
        GROUP BY substr(date, 1, 7)
        ORDER BY month ASC
    """, ((date.today() - timedelta(days=months * 31)).isoformat(),))

    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        month_key = r["month"]
        try:
            label = datetime.strptime(month_key, "%Y-%m").strftime("%b %Y")
        except ValueError:
            label = month_key
        present = r["present"] or 0
        total = r["total"]
        result.append({
            "month": label,
            "total": total,
            "present": present,
            "pct": round((present / total) * 100, 1) if total else 0,
        })
    return result


def get_top_absent_students(limit=5):
    """
    Students with the lowest attendance percentage (top absent).

    Returns:
        List of dicts: {id, name, roll_number, department, total, present, pct}
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, s.name, s.roll_number, s.department,
               COUNT(a.id) AS total,
               SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present
        FROM students s
        LEFT JOIN attendance a ON a.student_id = s.id
        GROUP BY s.id
        HAVING total > 0
        ORDER BY present * 1.0 / total ASC, total DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        present = r["present"] or 0
        total = r["total"] or 0
        result.append({
            "id": r["id"],
            "name": r["name"],
            "roll_number": r["roll_number"],
            "department": r["department"],
            "total": total,
            "present": present,
            "pct": round((present / total) * 100, 1) if total else 0,
        })
    return result


# -------------------------------------------------------------------------
# CAMERA SESSIONS
# -------------------------------------------------------------------------

def create_camera_session():
    """
    Create a new camera session row.

    Returns:
        The new session id (int).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO camera_sessions (started_at) VALUES (?)", (datetime.now().isoformat(),))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def end_camera_session(session_id, total_recognized, unknown_faces):
    """
    Mark a camera session as finished with its summary numbers.

    Args:
        session_id: Session id from create_camera_session()
        total_recognized: Number of distinct students recognized
        unknown_faces: Number of unknown faces encountered
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE camera_sessions
        SET ended_at = ?, total_recognized = ?, unknown_faces = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), total_recognized, unknown_faces, session_id))
    conn.commit()
    conn.close()


def get_session_summary(session_id):
    """
    Retrieve the summary for a finished camera session.

    Returns:
        Dict with session details, or None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM camera_sessions WHERE id = ?
    """, (session_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# -------------------------------------------------------------------------
# FACE SEARCH
# -------------------------------------------------------------------------

def get_last_attendance_date(student_id):
    """
    Get the most recent date this student was marked present.

    Returns:
        Date string (YYYY-MM-DD) or None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MAX(date) AS last_date FROM attendance WHERE student_id = ?
    """, (student_id,))
    row = cursor.fetchone()
    conn.close()
    return row["last_date"] if row else None
