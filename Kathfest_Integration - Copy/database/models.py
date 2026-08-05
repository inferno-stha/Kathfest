"""
models.py - Object-Oriented wrappers for database operations.

This module provides Student and Attendance classes that encapsulate
database CRUD operations. While the db.py module provides functional
interfaces, this module provides an OOP layer for code that prefers
working with objects.

Why have both?
    - db.py functions are simple and stateless (good for route handlers)
    - models.py classes provide encapsulation and state (good for
      complex business logic in backend modules)
    - Both ultimately use the same database functions from db.py

Usage example:
    student = Student.get(1)
    student.name = "New Name"
    student.save()
"""

from database import db


# =========================================================================
# Class: Student
#
# Purpose:
#     Represents a single student record with OOP-style CRUD operations.
#
# Attributes:
#     id, name, roll_number, department, semester, face_encoding
#
# Usage:
#     # Create a new student
#     s = Student(name="Aarav", roll_number="R101", department="CS", semester="2nd")
#     s.save()  # Inserts into database
#
#     # Get existing student
#     s = Student.get(1)
#     print(s.name)
#
#     # Update
#     s.semester = "4th"
#     s.save()  # Updates in database
#
#     # Delete
#     s.delete()
# =========================================================================
class Student:
    def __init__(self, id=None, name="", roll_number="", department="", semester="",
                 face_encoding=None):
        """Initialize a Student object (does NOT save to database)."""
        self.id = id
        self.name = name
        self.roll_number = roll_number
        self.department = department
        self.semester = semester
        self.face_encoding = face_encoding

    @classmethod
    def get(cls, student_id):
        """Retrieve a student by ID from the database."""
        data = db.get_student_by_id(student_id)
        if data is None:
            return None
        return cls(
            id=data["id"],
            name=data["name"],
            roll_number=data["roll_number"],
            department=data["department"],
            semester=data["semester"],
            face_encoding=data.get("face_encoding"),
        )

    @classmethod
    def get_all(cls):
        """Retrieve all students from the database."""
        return db.get_all_students()

    def save(self):
        """
        Save (insert or update) this student in the database.
        If self.id is None, INSERT a new record.
        If self.id exists, UPDATE the existing record.
        """
        if self.id is None:
            # Insert new student
            new_id = db.add_student(
                self.name,
                self.roll_number,
                self.department,
                self.semester,
                self.face_encoding,
            )
            if new_id:
                self.id = new_id
                return True
            return False
        else:
            # Update existing student
            return db.update_student(
                self.id,
                name=self.name,
                roll_number=self.roll_number,
                department=self.department,
                semester=self.semester,
            )

    def delete(self):
        """Delete this student from the database."""
        if self.id is not None:
            return db.delete_student(self.id)
        return False

    def save_face_encoding(self, encoding):
        """Store the face encoding for this student."""
        if self.id is not None:
            self.face_encoding = encoding
            return db.update_face_encoding(self.id, encoding)
        return False

    def get_attendance_records(self):
        """Get all attendance records for this student."""
        if self.id is None:
            return []
        return db.get_attendance_by_student(self.id)

    def to_dict(self):
        """Serialize to dict (for JSON responses)."""
        return {
            "id": self.id,
            "name": self.name,
            "roll_number": self.roll_number,
            "department": self.department,
            "semester": self.semester,
        }


# =========================================================================
# Class: Attendance
#
# Purpose:
#     Represents attendance operations in OOP style.
#
# Usage:
#     stats = Attendance.get_stats()
#     today = Attendance.get_today()
#     csv_data = Attendance.export_csv()
# =========================================================================
class Attendance:
    @staticmethod
    def mark(student_id):
        """Mark a student as present for today."""
        return db.mark_attendance(student_id)

    @staticmethod
    def get_today():
        """Get today's attendance records."""
        return db.get_today_attendance()

    @staticmethod
    def get_all():
        """Get all attendance records."""
        return db.get_all_attendance_records()

    @staticmethod
    def get_by_date(date_str):
        """Get attendance records for a specific date."""
        return db.get_attendance_by_date(date_str)

    @staticmethod
    def get_by_student(student_id):
        """Get attendance records for a specific student."""
        return db.get_attendance_by_student(student_id)

    @staticmethod
    def get_stats():
        """Get attendance statistics for the dashboard."""
        return db.get_attendance_stats()

    @staticmethod
    def export_csv():
        """Export all attendance data as CSV string."""
        return db.export_attendance_csv()
