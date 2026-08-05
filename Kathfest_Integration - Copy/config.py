"""
config.py - Central configuration for the Smart Student Attendance System.

This file consolidates all configurable values from the original
backend/database/config.py, backend/database.py, and database/config.py
into one single source of truth. Every other module imports from here.

How this was merged:
    - CAMERA_INDEX, FACE_MATCH_THRESHOLD, FACE_SAMPLES were in
      database/config.py (lines 28, 42, 37)
    - DATABASE_NAME was in backend/database.py and database/database.py
    - SECRET_KEY was in web_based/app.py (line 40)
    - All Tkinter UI colors/styles were in UI/styles.py — those remain
      in the CSS for the web frontend, not here
"""

import os

# =========================================================================
# DATABASE CONFIGURATION
# =========================================================================

# Path to the SQLite database file.
# Stored in the database/ subdirectory so it's separate from application code.
DATABASE_NAME = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "database",
    "attendance.db"
)

# =========================================================================
# FLASK CONFIGURATION
# =========================================================================

# Secret key for encrypting Flask session cookies.
# In production, replace with os.urandom(24).hex() or an env variable.
SECRET_KEY = "smart-attendance-secret-key-change-in-production"

# Host and port for the development server.
HOST = "0.0.0.0"
PORT = 5000

# Debug mode (True during development, False in production).
DEBUG = True

# =========================================================================
# CAMERA CONFIGURATION
# =========================================================================

# Which camera device to use (0 = built-in, 1 = external USB, etc.)
CAMERA_INDEX = 0

# Desired camera resolution width and height.
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# =========================================================================
# FACE RECOGNITION SETTINGS
# =========================================================================

# Number of face samples to capture during student registration.
# More samples = better recognition accuracy but slower enrollment.
FACE_SAMPLES = 5

# Face matching tolerance (0.0 = strict, 1.0 = lenient).
# A LOWER distance means a STRONGER match. face_recognition treats a
# distance below this threshold as a match.
# Values used in the existing codebase: database/config.py used 0.50.
FACE_MATCH_THRESHOLD = 0.50

# -------------------------------------------------------------------------
# CONFIDENCE THRESHOLD
#
# When a face is matched we also compute a "similarity percentage":
#     confidence = (1 - face_distance) * 100
#
# If the computed confidence is BELOW CONFIDENCE_THRESHOLD the person is
# treated as "Unknown Person" and attendance is NOT marked.
#
# With FACE_MATCH_THRESHOLD = 0.50 the equivalent confidence cut-off is 50%.
# Set to e.g. 0.80 (80%) for stricter matching.
# -------------------------------------------------------------------------
CONFIDENCE_THRESHOLD = 0.55

# -------------------------------------------------------------------------
# DUPLICATE FACE REGISTRATION GUARD
#
# When registering a NEW face we compare it against every encoding already
# stored in the database. If the best face_distance is BELOW
# FACE_DUPLICATE_THRESHOLD, registration is rejected with the message:
#     "This face already exists in the database.
#      Registered as: <name> (Roll: <roll>)"
#
# face_distance of ~0.45-0.55 means "very similar face". 0.55-0.60 is the
# safe upper bound recommended in the task brief.
# -------------------------------------------------------------------------
FACE_DUPLICATE_THRESHOLD = 0.55

# =========================================================================
# ROI (REGION OF INTEREST) — RESTRICTED FACE DETECTION BOX
# =========================================================================

# Enable/disable the fixed central detection box.
ROI_ENABLED = True

# Size (width AND height, square) of the central detection box in pixels.
# For a 640x480 camera a 300x300 center box works well. The ROI is drawn
# as a green rectangle on the camera preview and only faces whose box
# CENTER falls inside the ROI are processed.
ROI_SIZE = 300

# Color of the ROI rectangle on the preview (BGR: green).
ROI_COLOR = (0, 255, 0)

# =========================================================================
# IMAGE / STORAGE
# =========================================================================

# Folder to save student registration photos (optional).
PHOTO_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "UI",
    "static",
    "images",
    "faces"
)

# =========================================================================
# DISPLAY SETTINGS (for OpenCV preview windows)
# =========================================================================

WINDOW_NAME = "Face Attendance System"

BOX_COLOR = (0, 255, 0)       # Green bounding box
BOX_THICKNESS = 2
TEXT_COLOR = (150, 255, 150)  # Light green text
FONT_SCALE = 0.7
