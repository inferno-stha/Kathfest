# ============================================================
# IMPORT REQUIRED LIBRARIES
# ============================================================

import cv2
import face_recognition


# ============================================================
# OPEN THE WEBCAM
# ============================================================

camera = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not camera.isOpened():
    print("Error: Could not open webcam.")
    exit()


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    # --------------------------------------------------------
    # Capture one frame from the webcam
    # --------------------------------------------------------
    success, frame = camera.read()

    if not success:
        print("Error: Could not read frame.")
        break

    # --------------------------------------------------------
    # Convert image from BGR to RGB
    # OpenCV uses BGR but face_recognition requires RGB
    # --------------------------------------------------------
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # --------------------------------------------------------
    # Detect all faces in the frame
    # --------------------------------------------------------
    face_locations = face_recognition.face_locations(rgb_frame)

    # --------------------------------------------------------
    # Generate face encodings
    # Each detected face gets one 128-dimensional encoding
    # --------------------------------------------------------
    face_encodings = face_recognition.face_encodings(
        rgb_frame,
        face_locations
    )

    # --------------------------------------------------------
    # Draw a green rectangle around every detected face
    # --------------------------------------------------------
    for top, right, bottom, left in face_locations:

        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            (0, 255, 0),
            2
        )

    # --------------------------------------------------------
    # Display the number of detected faces
    # --------------------------------------------------------
    cv2.putText(
        frame,
        f"Faces Detected: {len(face_locations)}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 0, 0),
        2
    )

    # --------------------------------------------------------
    # Show the webcam window
    # --------------------------------------------------------
    cv2.imshow("Face Detection", frame)

    # --------------------------------------------------------
    # Read keyboard input
    # --------------------------------------------------------
    key = cv2.waitKey(1) & 0xFF

    # --------------------------------------------------------
    # Press 'S' to print the face encoding
    # --------------------------------------------------------
    if key == ord("s"):

        # Only continue if exactly one face is visible
        if len(face_encodings) == 1:

            encoding = face_encodings[0]

            print("\n" + "=" * 60)
            print("FACE ENCODING GENERATED")
            print("=" * 60)

            print("Encoding Length :", len(encoding))
            print("Data Type       :", type(encoding))
            print("Shape           :", encoding.shape)

            print("\nEncoding Values:\n")
            print(encoding)

        elif len(face_encodings) == 0:
            print("\nNo face detected.")

        else:
            print("\nMultiple faces detected. Please show only one face.")

    # --------------------------------------------------------
    # Press 'Q' to quit the program
    # --------------------------------------------------------
    elif key == ord("q"):
        print("\nProgram Closed.")
        break


# ============================================================
# RELEASE RESOURCES
# ============================================================

camera.release()
cv2.destroyAllWindows()