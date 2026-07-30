"""
============================================================
Project : KathFest Face Attendance System
File    : face_utils.py

Purpose:
Contains all face detection and face encoding functions.

This file handles:
- Camera access
- Face detection
- Face encoding generation
- Drawing face boxes

============================================================
"""


# ============================================================
# IMPORT LIBRARIES
# ============================================================

import cv2
import face_recognition

import config



# ============================================================
# CAMERA FUNCTIONS
# ============================================================


def open_camera():

    camera = cv2.VideoCapture(config.CAMERA_INDEX)

    if not camera.isOpened():
        raise Exception("Camera could not be opened")

    # Set resolution
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Request higher FPS
    camera.set(cv2.CAP_PROP_FPS, 60)

    return camera



def read_frame(camera):
    """
    Captures one frame from webcam.

    Parameters:
        camera : OpenCV camera object

    Returns:
        frame
    """

    success, frame = camera.read()

    if not success:
        return None

    return frame



# ============================================================
# FACE DETECTION
# ============================================================


def detect_faces(frame):
    """
    Detects faces in an image.

    Parameters:
        frame : Image captured from camera

    Returns:
        face locations
    """


    # OpenCV uses BGR format
    # face_recognition requires RGB format

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


    face_locations = face_recognition.face_locations( rgb_frame )


    return face_locations



# ============================================================
# FACE ENCODING
# ============================================================


def generate_encodings(frame):
    """
    Generates 128-dimensional face encoding.

    Parameters:
        frame : Image captured from camera

    Returns:
        list of encodings
    """


    # Convert BGR to RGB

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # Find face positions

    face_locations = face_recognition.face_locations(
        rgb_frame
    )


    # Generate encoding

    encodings = face_recognition.face_encodings(
        rgb_frame,
        face_locations
    )


    return encodings



# ============================================================
# DRAW FACE RECTANGLE
# ============================================================


def draw_face_boxes(frame, face_locations):
    """
    Draws rectangle around detected faces.

    Parameters:
        frame
        face_locations

    Returns:
        frame with rectangles
    """


    for top, right, bottom, left in face_locations:


        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            config.BOX_COLOR,
            config.BOX_THICKNESS
        )


    return frame



# ============================================================
# RELEASE CAMERA
# ============================================================


def close_camera(camera):
    """
    Releases camera resources.
    """

    camera.release()
    cv2.destroyAllWindows()