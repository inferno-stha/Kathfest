"""
============================================================
Project : KathFest Face Attendance System
File    : config.py

Purpose:
This file stores all configurable values used throughout
the project.

Instead of hardcoding values in multiple files,
we define them here so they can be changed easily.
============================================================
"""

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

# SQLite database file
DATABASE_NAME = "database/student_faces.db"


# ============================================================
# CAMERA CONFIGURATION
# ============================================================

# Default webcam
CAMERA_INDEX = 1


# ============================================================
# FACE RECOGNITION SETTINGS
# ============================================================

# Number of face samples to capture during registration
# More samples = Better recognition (but larger database)
FACE_SAMPLES = 5

# Face matching threshold
# Lower = More strict
# Higher = More lenient
FACE_MATCH_THRESHOLD = 0.50


# ============================================================
# IMAGE STORAGE
# ============================================================

# Folder to save student's registration photo
PHOTO_FOLDER = "photos"


# ============================================================
# DISPLAY SETTINGS
# ============================================================

WINDOW_NAME = "Face Attendance System - KathFest"

BOX_COLOR = (0, 255, 0)      # Green

BOX_THICKNESS = 2

TEXT_COLOR = (150, 255, 150)

FONT_SCALE = 0.7

""" 
# Text
TEXT_COLOR = (180, 220, 255)

# Rectangle
BOX_COLOR = (100, 200, 100)

# Text size
FONT_SCALE = 0.7
"""