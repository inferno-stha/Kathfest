"""
migrate_db.py - Database migration script for the v2 upgrade.

The v1 database schema (from the original KathFest integration) only had:
    students:  id, name, roll_number, department, semester, face_encoding
    attendance: id, student_id, date, time, status

The v2 upgrade adds:
    students.face_image        - JPEG photo of the registered face
    attendance.department      - department snapshot at mark time
    attendance.semester        - semester snapshot at mark time
    attendance.confidence      - similarity % of the face match
    attendance.session_id      - camera session that recorded the row
    camera_sessions            - new table tracking attendance sessions
    indexes on roll_number / department / semester / attendance.date

IMPORTANT:
    The Flask app runs this migration AUTOMATICALLY every time it starts
    (see database/db.py -> initialize_database()). Running this script is
    OPTIONAL and only needed if you want to verify / force the upgrade
    without starting the web server.

Usage:
    python migrate_db.py            # run the migration
    python migrate_db.py --check    # only report what would change
"""

import sqlite3
import sys
import os

# Make sure the project root is importable (for config.DATABASE_NAME)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DATABASE_NAME


def _get_columns(conn, table):
    """Return the list of column names for a table."""
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [row[1] for row in rows]


def migrate(check_only=False):
    """
    Apply (or report) the v2 schema changes.

    Args:
        check_only: If True, only print the required changes, don't apply.

    Returns:
        True if any changes were applied (or would be applied).
    """
    print("=" * 60)
    print(" Smart Student Attendance - DB Migration (v1 -> v2)")
    print(f" Database : {DATABASE_NAME}")
    print("=" * 60)

    if not os.path.exists(DATABASE_NAME):
        print("\n[!] Database file not found.")
        print("    It will be created automatically when the app starts.\n")
        return False

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    changed = False

    # ------------------------------------------------------------------
    # 1. students.face_image / students.face_registered columns
    # ------------------------------------------------------------------
    student_cols = _get_columns(conn, "students")
    if "face_image" not in student_cols:
        print("\n[students] ADD COLUMN face_image BLOB")
        changed = True
        if not check_only:
            cursor.execute("ALTER TABLE students ADD COLUMN face_image BLOB")
    else:
        print("\n[students] face_image column already exists (OK)")

    if "face_registered" not in student_cols:
        print("\n[students] ADD COLUMN face_registered INTEGER DEFAULT 0")
        changed = True
        if not check_only:
            cursor.execute(
                "ALTER TABLE students ADD COLUMN face_registered INTEGER DEFAULT 0"
            )
    else:
        print("\n[students] face_registered column already exists (OK)")

    # ------------------------------------------------------------------
    # 2. attendance new columns
    # ------------------------------------------------------------------
    attendance_cols = _get_columns(conn, "attendance")
    new_attendance_columns = {
        "department": "TEXT",
        "semester": "TEXT",
        "confidence": "REAL",
        "session_id": "INTEGER",
    }
    for col, col_type in new_attendance_columns.items():
        if col not in attendance_cols:
            print(f"[attendance] ADD COLUMN {col} {col_type}")
            changed = True
            if not check_only:
                cursor.execute(f"ALTER TABLE attendance ADD COLUMN {col} {col_type}")
        else:
            print(f"[attendance] {col} column already exists (OK)")

    # ------------------------------------------------------------------
    # 3. camera_sessions table
    # ------------------------------------------------------------------
    existing = [r[0] for r in cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    if "camera_sessions" not in existing:
        print("\n[camera_sessions] CREATE TABLE")
        changed = True
        if not check_only:
            cursor.execute("""
                CREATE TABLE camera_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP,
                    total_recognized INTEGER DEFAULT 0,
                    unknown_faces INTEGER DEFAULT 0
                )
            """)
    else:
        print("\n[camera_sessions] table already exists (OK)")

    # ------------------------------------------------------------------
    # 4. Indexes for the filter queries
    # ------------------------------------------------------------------
    indexes = {
        "idx_students_roll": ("students", "roll_number"),
        "idx_students_dept": ("students", "department"),
        "idx_students_sem": ("students", "semester"),
        "idx_attendance_date": ("attendance", "date"),
        "idx_attendance_student": ("attendance", "student_id"),
    }
    existing_indexes = [r[1] for r in cursor.execute(
        "PRAGMA index_list(attendance)").fetchall()] + [r[1] for r in cursor.execute(
        "PRAGMA index_list(students)").fetchall()]
    for name, (table, col) in indexes.items():
        if name not in existing_indexes:
            print(f"[index] CREATE INDEX {name} ON {table}({col})")
            changed = True
            if not check_only:
                cursor.execute(
                    f"CREATE INDEX {name} ON {table}({col})")
        else:
            print(f"[index] {name} already exists (OK)")

    if not check_only and changed:
        conn.commit()

    conn.close()

    print("\n" + "=" * 60)
    if check_only:
        print(" Check complete.", "Changes needed." if changed else "Schema is up to date.")
    else:
        print(" Migration complete." if changed else " Nothing to migrate (already v2).")
    print("=" * 60)
    return changed


if __name__ == "__main__":
    check_only = "--check" in sys.argv
    migrate(check_only=check_only)
