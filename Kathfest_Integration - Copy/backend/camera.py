"""
camera.py - Camera stream management module.

This module handles webcam access and frame capture for the face
recognition system. OpenCV (cv2) is imported lazily to allow the
module to be imported without the library installed — camera functions
will simply raise an ImportError at runtime with a clear message.
"""

import base64
from io import BytesIO

from config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT


# =========================================================================
# Class: CameraStream
#
# Purpose:
#     Manages the webcam lifecycle — open, read frames, release.
#
# Dependencies:
#     - OpenCV (cv2): Loaded lazily in open() method
# =========================================================================
class CameraStream:
    """
    A wrapper around OpenCV VideoCapture for safe camera management.
    """

    def __init__(self, index=CAMERA_INDEX):
        """Initialize with the camera device index."""
        self.index = index
        self.camera = None
        self.is_active = False

    def open(self):
        """
        Open the webcam for video capture.

        Returns:
            True if camera opened successfully, False otherwise.

        Raises:
            ImportError: If OpenCV (cv2) is not installed.
        """
        if self.is_active:
            return True

        import cv2  # Lazy import — fails here if cv2 not installed
        self.cv2 = cv2

        self.camera = cv2.VideoCapture(self.index)

        if not self.camera.isOpened():
            self.camera = None
            self.is_active = False
            return False

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

        self.is_active = True
        return True

    def read(self):
        """
        Capture a single frame from the camera.

        Returns:
            The frame (numpy array in BGR format) if successful, else None.
        """
        if not self.is_active or self.camera is None:
            return None

        success, frame = self.camera.read()

        if not success:
            return None

        return frame

    def capture_frame(self):
        """
        Convenience method: read a frame and encode it to JPEG base64.

        Returns:
            Dict with keys: success, image (base64 str), message
        """
        frame = self.read()

        if frame is None:
            return {"success": False, "image": None, "message": "Could not capture frame."}

        _, buffer = self.cv2.imencode(".jpg", frame)
        image_base64 = base64.b64encode(buffer).decode("utf-8")

        return {
            "success": True,
            "image": image_base64,
            "message": "Frame captured successfully.",
        }

    def capture_frame_bytes(self):
        """
        Capture a frame and return it as JPEG bytes.

        Returns:
            JPEG bytes, or None on failure.
        """
        frame = self.read()

        if frame is None:
            return None

        _, buffer = self.cv2.imencode(".jpg", frame)
        return buffer.tobytes()

    def release(self):
        """Release the camera and clean up resources."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None

        self.is_active = False

    def __del__(self):
        """Destructor: ensure camera is released on object destruction."""
        self.release()


# =========================================================================
# Function: decode_base64_image()
#
# Purpose:
#     Decode a base64-encoded JPEG string back to a numpy array (BGR).
#
# This is used in routes.py when receiving images from the browser's
# canvas.toDataURL() for face recognition.
#
# Returns:
#     Numpy array in BGR format, or None on failure.
# =========================================================================
def decode_base64_image(image_base64):
    """
    Decode a base64 JPEG string to an OpenCV BGR image.

    Args:
        image_base64: Base64-encoded JPEG string (with or without data:image prefix)

    Returns:
        OpenCV BGR frame (numpy array), or None on failure.
    """
    try:
        import cv2
        import numpy as np

        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]

        image_bytes = base64.b64decode(image_base64)
        np_array = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        return frame
    except ImportError:
        return None
    except Exception:
        return None
