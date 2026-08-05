"""
validation.py - Reusable input validation utilities.

This module centralises every validation rule used during student
registration so the frontend (JavaScript) and the backend (Python)
follow EXACTLY the same rules.

Validation rules (from the task brief):
    Roll Number:
        - Accept positive integers            -> "42"
        - Accept valid college formats        -> "BCT001", "KIC081BCT026"
        - Reject negatives, empties, special characters, invalid formats

    Name:
        - Accept alphabets, spaces, hyphen, apostrophe
        - Reject numbers, symbols, special characters

Usage:
    from backend.validation import validate_student_input

    errors = validate_student_input(name, roll, department, semester)
    if errors:
        return jsonify({"success": False, "errors": errors})
"""

import re

# =========================================================================
# Regular expressions
# =========================================================================

# Name: letters (unicode), spaces, hyphen, apostrophe. 2+ characters.
NAME_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ' -]{2,60}$")

# Roll number: either pure digits (1+), or a college-style code made of
# uppercase letters + digits (e.g. BCT001, KIC081BCT026).
ROLL_NUMBER_PATTERN = re.compile(r"^(?:\d+|[A-Z]{2,6}\d{3,}|[A-Z]{2,6}\d+[A-Z]{2,6}\d+)$")

# Department: letters, spaces, hyphen, apostrophe, ampersand, period.
DEPARTMENT_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ &.'-]{2,60}$")

# Semester: "1st" .. "12th" style labels.
VALID_SEMESTERS = [
    "1st", "2nd", "3rd", "4th", "5th", "6th",
    "7th", "8th", "9th", "10th", "11th", "12th",
]


def validate_name(name):
    """
    Validate a student name.

    Accepts alphabets, spaces, hyphen and apostrophe.
    Rejects numbers, symbols and special characters.

    Args:
        name: Raw name string.

    Returns:
        Error message string, or None if valid.
    """
    name = (name or "").strip()
    if not name:
        return "Name is required."
    if not NAME_PATTERN.match(name):
        return (
            "Invalid name. Use letters, spaces, hyphen (-) or "
            "apostrophe (') only (2-60 characters)."
        )
    return None


def validate_roll_number(roll):
    """
    Validate a roll number.

    Accepts positive integers ("42") or valid college formats
    ("BCT001", "KIC081BCT026"). Rejects negatives, empty values,
    special characters and invalid formats.

    Args:
        roll: Raw roll number string.

    Returns:
        Error message string, or None if valid.
    """
    roll = (roll or "").strip()
    if not roll:
        return "Roll Number is required."
    if not ROLL_NUMBER_PATTERN.match(roll):
        return (
            "Invalid roll number. Use a positive integer (e.g. 42) or a "
            "college format (e.g. BCT001, KIC081BCT026)."
        )
    return None


def validate_department(department):
    """
    Validate a department name.

    Args:
        department: Raw department string.

    Returns:
        Error message string, or None if valid.
    """
    department = (department or "").strip()
    if not department:
        return "Department is required."
    if not DEPARTMENT_PATTERN.match(department):
        return "Invalid department. Use letters, spaces, hyphens or ampersand."
    return None


def validate_semester(semester):
    """
    Validate a semester label.

    Args:
        semester: Raw semester string.

    Returns:
        Error message string, or None if valid.
    """
    semester = (semester or "").strip()
    if not semester:
        return "Semester is required."
    if semester not in VALID_SEMESTERS:
        return f"Invalid semester. Choose one of: {', '.join(VALID_SEMESTERS)}."
    return None


def validate_student_input(name, roll, department, semester):
    """
    Validate all student registration fields at once.

    Args:
        name: Raw name string
        roll: Raw roll number string
        department: Raw department string
        semester: Raw semester string

    Returns:
        Dict mapping field name -> error message for every invalid field.
        Empty dict means the input is valid.
    """
    errors = {}

    name_error = validate_name(name)
    if name_error:
        errors["name"] = name_error

    roll_error = validate_roll_number(roll)
    if roll_error:
        errors["roll"] = roll_error

    dept_error = validate_department(department)
    if dept_error:
        errors["department"] = dept_error

    sem_error = validate_semester(semester)
    if sem_error:
        errors["semester"] = sem_error

    return errors
