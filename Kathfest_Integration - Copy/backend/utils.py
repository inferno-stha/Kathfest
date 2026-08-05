"""
utils.py - Utility functions for the attendance system.

This module provides helper functions used across the application.
It centralizes common tasks like:
    - Image base64 encoding/decoding (requires cv2 + numpy)
    - Date/time formatting
    - Session validation helpers

Dependencies like cv2 and numpy are imported lazily (inside the
functions that use them) so that this module can be imported even
if those heavy libraries are not installed. This allows the Flask
app to start and serve pages even without OpenCV.
"""

import base64
from io import BytesIO
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, jsonify


# =========================================================================
# Function: encode_frame_to_base64()
#
# Purpose:
#     Encode an OpenCV frame (numpy array) to a base64 JPEG string
#     that can be sent to the browser in a JSON response.
#
# Args:
#     frame: OpenCV BGR image (numpy array)
#
# Returns:
#     Base64-encoded JPEG string (without data:image prefix)
#
# Note:
#     cv2 is imported here (lazy) to avoid requiring OpenCV at
#     module import time.
# =========================================================================
def encode_frame_to_base64(frame):
    import cv2
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")


# =========================================================================
# Function: decode_base64_to_frame()
#
# Purpose:
#     Decode a base64 JPEG string back to an OpenCV frame.
#     This is the inverse of encode_frame_to_base64().
#
# Args:
#     image_base64: Base64-encoded JPEG string (may include data:image prefix)
#
# Returns:
#     OpenCV BGR frame (numpy array), or None on failure
#
# Note:
#     cv2 and numpy are imported here (lazy) to avoid requiring them
#     at module import time.
# =========================================================================
def decode_base64_to_frame(image_base64):
    import cv2
    import numpy as np
    try:
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        image_bytes = base64.b64decode(image_base64)
        np_array = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        return frame
    except Exception:
        return None


# =========================================================================
# Function: format_time_12hr()
#
# Purpose:
#     Convert a 24-hour time string (HH:MM:SS) to 12-hour format (HH:MM AM/PM).
#
# Args:
#     time_str: Time in "14:30:00" format
#
# Returns:
#     Time in "02:30 PM" format
# =========================================================================
def format_time_12hr(time_str):
    try:
        dt = datetime.strptime(time_str, "%H:%M:%S")
        return dt.strftime("%I:%M %p").lstrip("0")
    except ValueError:
        return time_str


# =========================================================================
# Function: login_required()
#
# Purpose:
#     A decorator that protects Flask routes by checking if the user
#     is logged in (i.e., has an active session).
#
# Usage:
#     @app.route("/dashboard")
#     @login_required
#     def dashboard():
#         ...
#
# If the user is not logged in, they are redirected to the login page.
# =========================================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# =========================================================================
# Function: login_required_api()
#
# Purpose:
#     A decorator for API routes that returns a JSON error
#     instead of redirecting (since API calls expect JSON).
# =========================================================================
def login_required_api(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return jsonify({"success": False, "error": "Not authenticated"})
        return f(*args, **kwargs)
    return decorated_function
