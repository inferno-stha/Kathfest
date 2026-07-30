"""
============================================================
Project : KathFest Face Attendance System
File    : recognize.py

Purpose:
Recognize a person by comparing the live face encoding
with stored face encodings in the SQLite database.
============================================================
"""

# ============================================================
# IMPORT LIBRARIES
# ============================================================

import cv2
import face_recognition

import config
import face_utils
import record_entry_and_insertion as database


# ============================================================
# LOAD REGISTERED STUDENTS
# ============================================================

people = database.get_all_people()

known_encodings = []
known_people = []

for person in people:

    known_encodings.append(person["encoding"])
    known_people.append(person)

print(f"{len(people)} students loaded.")
print(f"{len(known_encodings)} face encodings loaded.")


# ============================================================
# RECOGNITION FUNCTION
# ============================================================

def recognize_face():

    camera = face_utils.open_camera()

    while True:

        frame = face_utils.read_frame(camera)

        if frame is None:
            continue

        # Detect faces
        locations = face_utils.detect_faces(frame)

        # Generate encodings
        encodings = face_utils.generate_encodings(frame)

        # Compare every detected face
        for encoding, location in zip(encodings, locations):

            matches = face_recognition.compare_faces(
                known_encodings,
                encoding,
                tolerance=config.FACE_MATCH_THRESHOLD
            )

            name = "Unknown"
            person_id = None

            if True in matches:

                match_index = matches.index(True)

                matched_person = known_people[match_index]

                name = matched_person["name"]
                person_id = matched_person["person_id"]

                print(f"Matched : {name} (ID: {person_id})")

                # Mark attendance
                database.mark_attendance(person_id)

            else:

                print("Unknown Person")

            # Draw rectangle
            top, right, bottom, left = location

            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                config.BOX_COLOR,
                config.BOX_THICKNESS
            )

            cv2.putText(
                frame,
                name,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                config.FONT_SCALE,
                config.TEXT_COLOR,
                2
            )

        cv2.imshow(config.WINDOW_NAME, frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    face_utils.close_camera(camera)


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    recognize_face()