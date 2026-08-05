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
    CONFIDENCE_THRESHOLD,
    FACE_DUPLICATE_THRESHOLD,
    ROI_ENABLED,
    ROI_SIZE,
    ROI_COLOR,
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

    # =====================================================================
    # ROI (REGION OF INTEREST) — restricted face detection
    #
    # Only faces whose CENTER falls inside the fixed central rectangle are
    # returned. Faces outside the box are ignored, which prevents false
    # detections from background objects / passers-by.
    # =====================================================================
    def get_roi_rect(self, frame):
        """
        Compute the central ROI rectangle for the given frame.

        Args:
            frame: Image from OpenCV (BGR format)

        Returns:
            Tuple (left, top, right, bottom) for the ROI box.
        """
        height, width = frame.shape[:2]
        roi_size = min(ROI_SIZE, width, height)
        left = (width - roi_size) // 2
        top = (height - roi_size) // 2
        return (left, top, left + roi_size, top + roi_size)

    def detect_faces_in_roi(self, frame):
        """
        Detect faces but keep ONLY the ones whose box centre is inside ROI.

        Args:
            frame: Image from OpenCV (BGR format)

        Returns:
            (face_locations, roi_rect) where face_locations is the filtered
            list of (top, right, bottom, left) tuples.
        """
        face_locations = self.detect_faces(frame)

        if not ROI_ENABLED:
            return face_locations, None

        left, top, right, bottom = self.get_roi_rect(frame)

        filtered = []
        for (t, r, b, l) in face_locations:
            face_cx = (l + r) // 2
            face_cy = (t + b) // 2
            if left <= face_cx <= right and top <= face_cy <= bottom:
                filtered.append((t, r, b, l))

        return filtered, (left, top, right, bottom)

    def draw_roi(self, frame):
        """
        Draw the green ROI rectangle on the frame (client-side preview uses
        CSS overlay, this is for server-side OpenCV windows).

        Args:
            frame: Image to draw on

        Returns:
            Frame with the ROI rectangle drawn.
        """
        if not ROI_ENABLED:
            return frame
        left, top, right, bottom = self.get_roi_rect(frame)
        self.cv2.rectangle(frame, (left, top), (right, bottom), ROI_COLOR, 2)
        return frame

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

    # =====================================================================
    # BEST-MATCH with distance + confidence
    #
    # confidence = (1 - face_distance) * 100
    # =====================================================================
    def find_best_match(self, face_encoding, threshold=FACE_MATCH_THRESHOLD):
        """
        Find the closest stored encoding and return distance/confidence.

        Args:
            face_encoding: 128-d numpy array to match
            threshold: face_distance below which we consider a match

        Returns:
            Dict:
                matched (bool)
                student (dict or None)  - id, name, roll_number, face_image
                distance (float)        - best face_distance
                confidence (float)      - (1 - distance) * 100
        """
        if not self.known_encodings or face_encoding is None:
            return {
                "matched": False,
                "student": None,
                "distance": None,
                "confidence": 0.0,
            }

        # Compute distance to every stored encoding
        distances = self.face_recognition.face_distance(self.known_encodings, face_encoding)
        best_index = int(self.np.argmin(distances))
        best_distance = float(distances[best_index])
        confidence = round((1 - best_distance) * 100, 1)

        if best_distance <= threshold:
            matched_student = self.known_students[best_index]
            return {
                "matched": True,
                "student": {
                    "id": int(matched_student["id"]),
                    "name": matched_student["name"],
                    "roll_number": matched_student["roll_number"],
                    "department": matched_student.get("department"),
                    "semester": matched_student.get("semester"),
                    "face_image": matched_student.get("face_image"),
                },
                "distance": round(best_distance, 4),
                "confidence": confidence,
            }

        return {
            "matched": False,
            "student": None,
            "distance": round(best_distance, 4),
            "confidence": confidence,
        }

    def check_duplicate_face(self, face_encoding, threshold=FACE_DUPLICATE_THRESHOLD):
        """
        Guard used during face REGISTRATION. If the new face is too similar
        to an existing student's face, registration is rejected.

        Args:
            face_encoding: 128-d numpy array of the newly captured face
            threshold: face_distance below which it is considered a duplicate

        Returns:
            Dict:
                is_duplicate (bool)
                student (dict or None) - the existing student it matches
                distance (float)
                confidence (float)
        """
        result = self.find_best_match(face_encoding, threshold=threshold)

        if result["matched"]:
            return {
                "is_duplicate": True,
                "student": result["student"],
                "distance": result["distance"],
                "confidence": result["confidence"],
            }
        return {
            "is_duplicate": False,
            "student": None,
            "distance": result["distance"],
            "confidence": result["confidence"],
        }

    def recognize(self, frame):
        """
        Run full face recognition pipeline on a single frame.

        Detection is restricted to the ROI box (when enabled) and the
        returned student includes the confidence percentage.

        Args:
            frame: Image from OpenCV (BGR format)

        Returns:
            Dict with keys: success, student, locations, message,
                            confidence, distance, roi
        """
        face_locations, roi = self.detect_faces_in_roi(frame)

        if len(face_locations) == 0:
            return {
                "success": False,
                "student": None,
                "locations": [],
                "message": "No face detected. Please look at the camera.",
                "confidence": 0.0,
                "distance": None,
                "roi": roi,
            }

        if len(face_locations) > 1:
            return {
                "success": False,
                "student": None,
                "locations": face_locations,
                "message": "Multiple faces detected. Only one person allowed.",
                "confidence": 0.0,
                "distance": None,
                "roi": roi,
            }

        encodings = self.get_encodings(frame, face_locations)

        if len(encodings) == 0:
            return {
                "success": False,
                "student": None,
                "locations": face_locations,
                "message": "Could not generate face encoding. Try adjusting lighting.",
                "confidence": 0.0,
                "distance": None,
                "roi": roi,
            }

        matched = self.find_best_match(encodings[0], threshold=FACE_MATCH_THRESHOLD)

        if not matched["matched"]:
            return {
                "success": False,
                "student": None,
                "locations": face_locations,
                "message": "Unknown Person",
                "confidence": matched["confidence"],
                "distance": matched["distance"],
                "roi": roi,
            }

        # Confidence guard: reject if below the configurable threshold.
        if matched["confidence"] < CONFIDENCE_THRESHOLD * 100:
            return {
                "success": False,
                "student": None,
                "locations": face_locations,
                "message": "Unknown Person (low confidence)",
                "confidence": matched["confidence"],
                "distance": matched["distance"],
                "roi": roi,
            }

        return {
            "success": True,
            "student": matched["student"],
            "locations": face_locations,
            "message": f"Detected: {matched['student']['name']}",
            "confidence": matched["confidence"],
            "distance": matched["distance"],
            "roi": roi,
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
