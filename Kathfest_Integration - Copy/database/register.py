"""
============================================================
Project : KathFest Face Attendance System
File    : register.py

Purpose:
Register a new student by capturing multiple face samples.

Author : KathFest Team
============================================================
"""

# ============================================================
# IMPORT LIBRARIES
# ============================================================

import cv2
import time

import config
import face_utils
import record_entry_and_insertion as database


# ============================================================
# REGISTRATION INSTRUCTIONS
# ============================================================

INSTRUCTIONS = [

    "Look Straight",

    "Turn Slightly Left",

    "Turn Slightly Right",

    "Look Slightly Up",

    "Look Slightly Down"

]


# ============================================================
# REGISTER FUNCTION
# ============================================================

def register_student():

    print("\n========== Student Registration ==========\n")

    roll_no = input("Roll Number : ")
    name = input("Student Name : ")
    department = input("Department  : ")

    print("\nOpening Camera...\n")

    camera = face_utils.open_camera()

    encodings = []

    sample_number = 0

    countdown = 3

    countdown_start = None

    capturing = False

    print("\nPress Q anytime to cancel.\n")

    while True:

        frame = face_utils.read_frame(camera)

        if frame is None:
            continue

        locations = face_utils.detect_faces(frame)

        frame = face_utils.draw_face_boxes(
            frame,
            locations
        )

        # --------------------------------------------------
        # Draw Sample Number
        # --------------------------------------------------

        cv2.putText(

            frame,

            f"Sample : {sample_number+1}/{config.FACE_SAMPLES}",

            (20,40),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (255,255,255),

            2

        )

        # --------------------------------------------------
        # Draw Instruction
        # --------------------------------------------------

        if sample_number < len(INSTRUCTIONS):

            instruction = INSTRUCTIONS[sample_number]

        else:

            instruction = "Hold Still"

        cv2.putText(

            frame,

            instruction,

            (20,80),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (0,255,255),

            2

        )

        # --------------------------------------------------
        # Status
        # --------------------------------------------------

        cv2.putText(

            frame,

            "Press Q to Cancel",

            (20,120),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (100,255,100),

            2

        )
        # --------------------------------------------------
        # Face Detection Status
        # --------------------------------------------------

        if len(locations) == 0:

            capturing = False
            countdown_start = None

            cv2.putText(
                frame,
                "No Face Detected",
                (20, 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        elif len(locations) > 1:

            capturing = False
            countdown_start = None

            cv2.putText(
                frame,
                "Only One Person Allowed",
                (20, 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        else:

            current_encodings = face_utils.generate_encodings(frame)

            if len(current_encodings) == 1:

                if not capturing:

                    capturing = True
                    countdown_start = time.time()

                elapsed = time.time() - countdown_start

                remaining = max(0, countdown - int(elapsed))

                cv2.putText(
                    frame,
                    f"Capturing in {remaining}",
                    (20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 0),
                    2
                )

                if elapsed >= countdown:

                    encodings.append(current_encodings[0])

                    sample_number += 1

                    print(
                        f"Sample {sample_number}/{config.FACE_SAMPLES} captured"
                    )

                    capturing = False
                    countdown_start = None

                    cv2.putText(
                        frame,
                        "Sample Captured!",
                        (20, 200),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2
                    )

                    cv2.imshow(config.WINDOW_NAME, frame)
                    cv2.waitKey(600)

        # --------------------------------------------------
        # Show Window
        # --------------------------------------------------

        cv2.imshow(
            config.WINDOW_NAME,
            frame
        )

        # Exit

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            print("\nRegistration Cancelled.")

            break

        if sample_number >= config.FACE_SAMPLES:

            break
    # ========================================================
    # CLOSE CAMERA
    # ========================================================

    face_utils.close_camera(camera)

    # ========================================================
    # CHECK REGISTRATION
    # ========================================================

    if sample_number == config.FACE_SAMPLES:

        print("\n====================================")
        print(" Registration Successful ")
        print("====================================")

        # ----------------------------------------------------
        # Choose encoding to store
        # ----------------------------------------------------

        # For now, save the first encoding.
        # Later we can improve the database to save all samples.
        face_encoding = encodings[0]

        try:

            database.insert_person(
                name=name,
                roll_no=roll_no,
                department=department,
                face_encoding=face_encoding
            )

            print("Student saved successfully.")
            print(f"Name       : {name}")
            print(f"Roll No    : {roll_no}")
            print(f"Department : {department}")

            return {
                "person_id": None,
                "name": name,
                "roll_no": roll_no,
                "department": department
            }

        except Exception as e:

            print("\nDatabase Error")
            print(e)

            return None

    else:

        print("\nRegistration Incomplete.")
        print(
            f"Captured {sample_number}/{config.FACE_SAMPLES} samples."
        )

        return None


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    student = register_student()

    if student:

        print("\nReturned Data:")
        print(student)

    else:

        print("\nNo student registered.")