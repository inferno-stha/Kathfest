"""
face_recognizer.py - Face detection and recognition module.

This module is the heart of the Smart Student Attendance System's
computer vision capability. It provides all face-related operations.

Dependencies like cv2 and face_recognition are imported lazily
(inside __init__) so this module can be imported even without those
libraries installed. The FaceRecognizer class checks at construction
time and raises a clear error if dependencies are missing.
"""

from config import (
    FACE_MATCH_THRESHOLD,
    BOX_COLOR,
    BOX_THICKNESS,
    TEXT_COLOR,
    FONT_SCALE,
)

from database.db import get_all_face_encodings


# =========================================================================
# Class: FaceRecognizer
#
# Purpose:
#     Provides all face detection, encoding, and recognition operations
#     used by the camera and attendance modules.
#
# Dependencies:
#     - OpenCV (cv2): Camera and image manipulation
#     - face_recognition: Face detection, encoding, comparison
#     - numpy: Array operations
#
# These are imported inside __init__() so the module-level imports
# don't fail if libraries are missing.
# =========================================================================
class FaceRecognizer:
    """
    Unified interface for face detection, encoding, and recognition.
    """

    def __init__(self):
        """
        Initialize the recognizer by loading dependencies and known faces.

        Raises:
            ImportError: If cv2 or face_recognition are not installed.
        """
        # Lazy imports — allows module to be imported without these libs
        import cv2
        import face_recognition
        import numpy as np

        self.cv2 = cv2
        self.face_recognition = face_recognition
        self.np = np

        self._load_known_faces()

    def _load_known_faces(self):
        """Load all registered face encodings from the database into memory."""
        self.known_students = get_all_face_encodings()
        self.known_encodings = [
            s["encoding"] for s in self.known_students
            if s.get("encoding") is not None
        ]

    def reload_known_faces(self):
        """Reload face encodings from the database."""
        self._load_known_faces()

    def detect_faces(self, frame):
        """
        Detect all face locations in an image frame.

        Args:
            frame: Image from OpenCV (BGR format)

        Returns:
            List of face location tuples (top, right, bottom, left)
        """
        rgb_frame = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
        face_locations = self.face_recognition.face_locations(rgb_frame)
        return face_locations

    def get_encodings(self, frame, face_locations=None):
        """
        Generate 128-dimensional face encodings for detected faces.

        Args:
            frame: Image from OpenCV (BGR format)
            face_locations: Pre-computed face locations, or None to detect

        Returns:
            List of 128-d numpy arrays (one per detected face)
        """
        rgb_frame = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)

        if face_locations is None:
            face_locations = self.detect_faces(frame)

        encodings = self.face_recognition.face_encodings(rgb_frame, face_locations)
        return encodings

    def compare_faces(self, face_encoding):
        """
        Compare a single face encoding against all known encodings.

        Args:
            face_encoding: A 128-d numpy array to match

        Returns:
            The matching student dict from known_students, or None if no match.
        """
        if not self.known_encodings:
            return None

        matches = self.face_recognition.compare_faces(
            self.known_encodings,
            face_encoding,
            tolerance=FACE_MATCH_THRESHOLD
        )

        if True in matches:
            match_index = matches.index(True)
            return self.known_students[match_index]

        return None

    def recognize(self, frame):
        """
        Run full face recognition pipeline on a single frame.

        Args:
            frame: Image from OpenCV (BGR format)

        Returns:
            Dict with keys: success, student, locations, message
        """
        face_locations = self.detect_faces(frame)

        if len(face_locations) == 0:
            return {
                "success": False,
                "student": None,
                "locations": [],
                "message": "No face detected. Please look at the camera.",
            }

        if len(face_locations) > 1:
            return {
                "success": False,
                "student": None,
                "locations": face_locations,
                "message": "Multiple faces detected. Only one person allowed.",
            }

        encodings = self.get_encodings(frame, face_locations)

        if len(encodings) == 0:
            return {
                "success": False,
                "student": None,
                "locations": face_locations,
                "message": "Could not generate face encoding. Try adjusting lighting.",
            }

        matched_student = self.compare_faces(encodings[0])

        if matched_student is None:
            return {
                "success": False,
                "student": None,
                "locations": face_locations,
                "message": "Unknown face. Student not recognized.",
            }

        return {
            "success": True,
            "student": {
                "id": int(matched_student["id"]),
                "name": matched_student["name"],
                "roll_number": matched_student["roll_number"],
            },
            "locations": face_locations,
            "message": f"Recognized: {matched_student['name']}",
        }

    def draw_face_boxes(self, frame, face_locations, names=None):
        """
        Draw bounding boxes and labels around detected faces.

        Args:
            frame: Image to draw on
            face_locations: List of (top, right, bottom, left) tuples
            names: List of names to display, or None

        Returns:
            Frame with rectangles drawn on it
        """
        for i, (top, right, bottom, left) in enumerate(face_locations):
            self.cv2.rectangle(
                frame, (left, top), (right, bottom),
                BOX_COLOR, BOX_THICKNESS
            )
            if names and i < len(names):
                self.cv2.putText(
                    frame, names[i], (left, top - 10),
                    self.cv2.FONT_HERSHEY_SIMPLEX,
                    FONT_SCALE, TEXT_COLOR, 2
                )
        return frame
