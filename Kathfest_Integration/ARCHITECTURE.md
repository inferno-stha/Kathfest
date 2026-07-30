# ARCHITECTURE.md — System Architecture

## Smart Student Attendance System Using Face Recognition

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Layer Architecture](#2-layer-architecture)
3. [Request Flow](#3-request-flow)
4. [Attendance Flow](#4-attendance-flow)
5. [Database Schema](#5-database-schema)
6. [Face Recognition Pipeline](#6-face-recognition-pipeline)
7. [Module Map (Original → Integrated)](#7-module-map-original--integrated)
8. [Team Responsibilities](#8-team-responsibilities)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                             │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Login    │  │Dashboard │  │ Students │  │   Attendance     │   │
│  │ Page     │  │ Page     │  │ Page     │  │   Page (Camera)  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───────┬──────────┘   │
│       │             │             │               │              │
│       └─────────────┴─────────────┴───────────────┘              │
│                              │   HTML/CSS/JS                     │
│                              │   Fetch API (JSON)                │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│                    FLASK WEB SERVER                              │
│                               │                                  │
│  ┌───────────────────────────┴──────────────────────────────┐   │
│  │                       routes.py                           │   │
│  │  ┌────────┐ ┌────────┐ ┌──────────┐ ┌────────┐ ┌─────┐  │   │
│  │  │ Login  │ │Dashbd. │ │ Students │ │Attend. │ │Rprts│  │   │
│  │  │ Routes │ │ Routes │ │  Routes  │ │ Routes │ │Rts  │  │   │
│  │  └───┬────┘ └───┬────┘ └────┬─────┘ └───┬─────┘ └──┬──┘  │   │
│  └──────┼──────────┼───────────┼───────────┼───────────┼─────┘   │
│         │          │           │           │           │         │
│         ▼          ▼           ▼           ▼           ▼         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                     BACKEND MODULES                         │  │
│  │                                                            │  │
│  │  ┌─────────────────────┐  ┌───────────────────────────┐   │  │
│  │  │ backend/attendance.py│  │ backend/face_recognizer.py│   │  │
│  │  │ Mark attendance via  │  │ Face detection, encoding, │   │  │
│  │  │ face recognition     │  │ comparison (OpenCV + fr)  │   │  │
│  │  └────────┬────────────┘  └───────────┬───────────────┘   │  │
│  │           │                           │                    │  │
│  │  ┌────────┴────────────┐  ┌───────────┴───────────────┐   │  │
│  │  │ backend/camera.py   │  │ backend/utils.py           │   │  │
│  │  │ Camera stream mgmt  │  │ Decorators, helpers        │   │  │
│  │  └────────┬────────────┘  └───────────────────────────┘   │  │
│  └───────────┼────────────────────────────────────────────────┘  │
│              │                                                    │
│              ▼                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    DATABASE LAYER                           │  │
│  │                                                            │  │
│  │  ┌────────────────────────┐  ┌────────────────────────┐   │  │
│  │  │   database/db.py       │  │   database/models.py   │   │  │
│  │  │   SQLite CRUD          │  │   OOP Student &        │   │  │
│  │  │   (functional style)   │  │   Attendance classes   │   │  │
│  │  └───────────┬────────────┘  └────────────────────────┘   │  │
│  │              │                                             │  │
│  │              ▼                                             │  │
│  │  ┌──────────────────────────────────────────────────┐     │  │
│  │  │              attendance.db (SQLite)               │     │  │
│  │  │  ┌──────────────┐       ┌──────────────────┐    │     │  │
│  │  │  │  students    │       │   attendance     │    │     │  │
│  │  │  │  id (PK)     │◄──────│   student_id(FK) │    │     │  │
│  │  │  │  name        │       │   date           │    │     │  │
│  │  │  │  roll_number │       │   time           │    │     │  │
│  │  │  │  department  │       │   status         │    │     │  │
│  │  │  │  semester    │       └──────────────────┘    │     │  │
│  │  │  │  face_enc.   │                               │     │  │
│  │  │  └──────────────┘                               │     │  │
│  │  └──────────────────────────────────────────────────┘     │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Layer Architecture

### Frontend Layer (UI/)

```
UI/templates/           UI/static/
    │                       │
    │   Jinja2 Rendering    │   Static Serving
    ▼                       ▼
┌───────────────────────────────────────────────────────────────┐
│  Template Inheritance Chain:                                  │
│                                                               │
│  base.html (layout with sidebar + header)                     │
│    ├── login.html      (standalone, no sidebar)               │
│    ├── dashboard.html  (extend base)                          │
│    ├── students.html   (extend base + inline <script>)        │
│    ├── attendance.html (extend base + inline <script>)        │
│    ├── reports.html    (extend base + inline <script>)        │
│    └── about.html      (extend base)                          │
└───────────────────────────────────────────────────────────────┘
```

**Key Design Decisions:**
- All pages extend `base.html` for consistent sidebar/header (except login)
- Each page has inline `<script>` blocks for page-specific JavaScript
- Global utilities are in `static/js/script.js`
- Communication with backend is via `fetch()` API (no page reloads for CRUD)
- The blue theme and all colors are defined as CSS variables in `style.css`

### Flask Backend (app.py + routes.py)

```
app.py                       routes.py
    │                            │
    │  Creates Flask app         │  @app.route() decorators
    │  Sets template/static dirs │  Each function = one endpoint
    │  Imports routes.py         │  Returns render_template() or jsonify()
    │  Calls app.run()           │
```

**Route Categories:**
1. **Page Routes** (GET) — Render HTML templates with data
2. **API Routes** (POST/GET) — Accept/return JSON, handle AJAX calls
3. **File Routes** (GET) — Return file downloads (CSV)

### OpenCV Face Recognition (backend/)

```
┌─────────────────────────────────────────────────────────────────┐
│                  Face Recognition Pipeline                       │
│                                                                  │
│  1. Frame Capture (camera.py)                                    │
│     ├── From server-side: CameraStream.read()                    │
│     └── From browser: decode_base64_image(image_data)            │
│         │                                                       │
│         ▼                                                       │
│  2. Face Detection (face_recognizer.py)                          │
│     ├── Convert BGR → RGB                                        │
│     ├── face_recognition.face_locations() (HOG)                  │
│     └── Returns list of (top, right, bottom, left) tuples       │
│         │                                                       │
│         ▼                                                       │
│  3. Face Encoding (face_recognizer.py)                           │
│     ├── face_recognition.face_encodings() (ResNet CNN)          │
│     └── Returns 128-dimensional numpy array                     │
│         │                                                       │
│         ▼                                                       │
│  4. Face Comparison (face_recognizer.py)                         │
│     ├── Load known encodings from database (get_all_face_encodings)
│     ├── face_recognition.compare_faces() (Euclidean distance)   │
│     ├── Matched if distance < FACE_MATCH_THRESHOLD (0.50)       │
│     └── Returns matched student dict or None                    │
│         │                                                       │
│         ▼                                                       │
│  5. Attendance Marking (attendance.py)                           │
│     ├── mark_attendance(student_id) → INSERT INTO attendance    │
│     └── Checks for duplicate (already marked today)             │
└─────────────────────────────────────────────────────────────────┘
```

### Database Layer (database/)

```
┌─────────────────────────────────────────────────────────────────┐
│                   Database Architecture                          │
│                                                                  │
│  database/db.py (functional)          database/models.py (OOP)   │
│  ┌─────────────────────────┐          ┌────────────────────┐    │
│  │ get_connection()        │          │ Student             │    │
│  │ initialize_database()   │          │   .get(id)          │    │
│  │ add_student()           │          │   .get_all()        │    │
│  │ get_all_students()      │          │   .save()           │    │
│  │ get_student_by_id()     │          │   .delete()         │    │
│  │ update_student()        │          │   .save_face_enc()  │    │
│  │ delete_student()        │          │   .get_attendance() │    │
│  │ search_students()       │          └────────────────────┘    │
│  │ get_all_face_encodings()│          ┌────────────────────┐    │
│  │ update_face_encoding()  │          │ Attendance          │    │
│  │ mark_attendance()       │          │   .mark(id)         │    │
│  │ get_today_attendance()  │          │   .get_today()      │    │
│  │ get_all_attendance()    │          │   .get_all()        │    │
│  │ get_attendance_by_date()│          │   .get_stats()      │    │
│  │ get_attendance_stats()  │          │   .export_csv()     │    │
│  │ export_attendance_csv() │          └────────────────────┘    │
│  └─────────────────────────┘                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Request Flow

### Page Load (e.g., Dashboard)

```
Browser                          Flask Server
   │                                 │
   │  GET /dashboard                 │
   │────────────────────────────────>│
   │                                 │
   │                         ┌───────┴────────┐
   │                         │  Check session  │
   │                         │  "user" in sess?│
   │                         └───────┬────────┘
   │                                 │
   │                    No ┌──────────┴──────────┐
   │                    ┌──┤ Redirect to /login  │
   │                    │  └─────────────────────┘
   │               ┌────┴────┐
   │               │  Yes    │
   │               └────┬────┘
   │                     ▼
   │             ┌───────────────────┐
   │             │ get_dashboard_    │
   │             │ stats()           │
   │             │ ─ COUNT students  │
   │             │ ─ COUNT present   │
   │             │ ─ Calculate %     │
   │             └───────┬───────────┘
   │                     ▼
   │             ┌───────────────────┐
   │             │ render_template(  │
   │             │   "dashboard.html",│
   │             │   total_students,  │
   │             │   present_today,   │
   │             │   attendance_pct   │
   │             │ )                 │
   │             └───────┬───────────┘
   │                     │
   │  HTML Page          │
   │<────────────────────│
   ▼                     ▼
```

### AJAX Request (e.g., Add Student via Modal)

```
Browser                          Flask Server
   │                                 │
   │  User clicks "Save" in modal    │
   │  JavaScript gather form data    │
   │                                 │
   │  POST /api/students/add         │
   │  Content-Type: application/json │
   │  Body: {name, roll, dept, sem}  │
   │────────────────────────────────>│
   │                                 │
   │                         ┌───────┴────────┐
   │                         │  Validate input │
   │                         └───────┬────────┘
   │                                 │
   │                         ┌───────┴────────┐
   │                         │  add_student()  │
   │                         │  INSERT INTO    │
   │                         │  students       │
   │                         └───────┬────────┘
   │                                 │
   │  Response: JSON                 │
   │  {success: true,                │
   │   message: "added"}             │
   │<────────────────────────────────│
   │                                 │
   │  JavaScript:                    │
   │  - Show success alert           │
   │  - Close modal                  │
   │  - Refresh table via            │
   │    filterStudents()             │
   ▼                                 ▼
```

---

## 4. Attendance Flow (Face Recognition)

This is the most critical flow in the system. It integrates the browser camera, the Flask backend, the face recognition module, and the database.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ATTENDANCE MARKING FLOW                           │
│                                                                     │
│  BROWSER (attendance.html JavaScript)                               │
│                                                                     │
│  1. User clicks "Start Camera"                                      │
│     → navigator.mediaDevices.getUserMedia({video: true})            │
│     → Video stream appears in <video> element                       │
│                                                                     │
│  2. User clicks "Mark Attendance"                                   │
│     → JavaScript captures current frame:                            │
│       canvas.drawImage(video, 0, 0)                                 │
│       image_data = canvas.toDataURL('image/jpeg')                   │
│                                                                     │
│  3. JavaScript sends POST request:                                  │
│     → POST /api/attendance/mark                                     │
│     → Body: {"image": "data:image/jpeg;base64,/9j..."}             │
│         │                                                           │
│         ▼                                                           │
│  FLASK SERVER (routes.py)                                           │
│                                                                     │
│  4. decode_base64_image(image_base64)                               │
│     → Strips "data:image/jpeg;base64," prefix                      │
│     → base64.b64decode() → bytes                                    │
│     → np.frombuffer() → numpy array                                 │
│     → cv2.imdecode() → OpenCV BGR frame                             │
│         │                                                           │
│         ▼                                                           │
│  BACKEND (attendance.py → face_recognizer.py)                       │
│                                                                     │
│  5. mark_attendance_from_frame(frame)                               │
│       │                                                             │
│       ▼                                                             │
│  6. FaceRecognizer.recognize(frame)                                 │
│       │                                                             │
│       ├── 6a. detect_faces(frame)                                   │
│       │    → Convert BGR → RGB                                      │
│       │    → face_recognition.face_locations(rgb)                   │
│       │    → Returns [(top, right, bottom, left), ...]              │
│       │    → If 0 faces: return "No face detected"                  │
│       │    → If >1 faces: return "Multiple faces"                   │
│       │                                                             │
│       ├── 6b. get_encodings(frame, face_locations)                  │
│       │    → face_recognition.face_encodings(rgb, locations)        │
│       │    → Returns [128-d numpy array, ...]                       │
│       │                                                             │
│       └── 6c. compare_faces(face_encoding)                          │
│            → Load known encodings from DB (on init)                 │
│            → face_recognition.compare_faces(                        │
│                known_encodings, encoding, tolerance=0.50)            │
│            → If match found: return matched student                 │
│            → If no match: return None ("Unknown face")              │
│                                                                     │
│  7. If recognized: db_mark_attendance(student_id)                   │
│     → Check if already marked today                                 │
│     → If not: INSERT INTO attendance                                │
│     → Return success                                                │
│         │                                                           │
│         ▼                                                           │
│  RESPONSE                                                            │
│                                                                     │
│  8. Flask returns JSON:                                             │
│     {                                                               │
│       success: true/false,                                          │
│       student_name: "Aarav Sharma" or null,                         │
│       message: "Attendance marked for 'Aarav Sharma'.",             │
│       already_marked: false                                         │
│     }                                                               │
│         │                                                           │
│         ▼                                                           │
│  BROWSER                                                            │
│                                                                     │
│  9. JavaScript receives response:                                   │
│     → Show success/error message in status div                      │
│     → If success: refresh attendance table via /api/attendance/data │
│     → Enable "Mark Attendance" button again                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Database Schema

```
┌─────────────────────────────────────────────────────────────────┐
│  Table: students                                                │
├─────────────────────────────────────────────────────────────────┤
│  Column           Type          Constraints         Original    │
│  ─────────────────────────────────────────────────────────────   │
│  id               INTEGER       PK AUTOINCREMENT    person_id   │
│  name             TEXT          NOT NULL             name        │
│  roll_number      TEXT          UNIQUE NOT NULL      roll_no     │
│  department       TEXT                               department  │
│  semester         TEXT           [NEW - was missing]  —          │
│  face_encoding    BLOB                               face_enc.   │
│  registered_date  TIMESTAMP     DEFAULT CURRENT_TS    reg_date   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Table: attendance                                              │
├─────────────────────────────────────────────────────────────────┤
│  Column           Type          Constraints         Original    │
│  ─────────────────────────────────────────────────────────────   │
│  id               INTEGER       PK AUTOINCREMENT    att_id      │
│  student_id       INTEGER       FK → students.id    person_id   │
│  date             DATE          NOT NULL             att_date   │
│  time             TIME          NOT NULL             att_time   │
│  status           TEXT          DEFAULT 'Present'    status      │
└─────────────────────────────────────────────────────────────────┘

Foreign Key: attendance.student_id → students.id ON DELETE CASCADE
```

**Key Differences from Original Schema:**
- Renamed `person` → `students`, `person_id` → `id`
- Renamed `roll_no` → `roll_number`
- Added `semester` column (required by UI but missing in original)
- Renamed `attendance_id` → `id`, `attendance_date` → `date`, `attendance_time` → `time`
- Added `ON DELETE CASCADE` for referential integrity

---

## 6. Face Recognition Pipeline

### How Face Recognition Works

The system uses the `face_recognition` library, which wraps `dlib`'s state-of-the-art face recognition model.

```
┌─────────────────────────────────────────────────────────────────┐
│                    FACE RECOGNITION PIPELINE                     │
│                                                                  │
│  Input: Image (640×480 BGR from webcam)                         │
│                                                                  │
│  Step 1: Preprocessing                                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)                  │    │
│  │ Converts OpenCV's BGR format to RGB (required by        │    │
│  │ face_recognition library)                                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                         │                                       │
│                         ▼                                       │
│  Step 2: Face Detection (HOG + Linear SVM)                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ face_recognition.face_locations(rgb_image)              │    │
│  │                                                         │    │
│  │ Uses Histogram of Oriented Gradients (HOG) to find     │    │
│  │ face-like patterns in the image, then a linear SVM     │    │
│  │ to classify each region as face / not-face.            │    │
│  │                                                         │    │
│  │ Output: [(top, right, bottom, left), ...]              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                         │                                       │
│                         ▼                                       │
│  Step 3: Face Encoding (ResNet-34 CNN)                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ face_recognition.face_encodings(rgb, face_locations)    │    │
│  │                                                         │    │
│  │ Uses a deep residual network (ResNet-34) trained on    │    │
│  │ millions of face images. The network outputs a         │    │
│  │ 128-dimensional vector that uniquely identifies a      │    │
│  │ person's face (similar to a "face fingerprint").       │    │
│  │                                                         │    │
│  │ Output: [array([0.12, -0.05, ..., 0.33]), ...]        │    │
│  │         Each array has 128 float64 values               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                         │                                       │
│                         ▼                                       │
│  Step 4: Face Comparison (Euclidean Distance)                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ face_recognition.compare_faces(                         │    │
│  │     known_encodings,     # List of 128-d arrays         │    │
│  │     face_encoding,       # Query 128-d array            │    │
│  │     tolerance=0.50       # Matching threshold           │    │
│  │ )                                                        │    │
│  │                                                         │    │
│  │ Computes Euclidean distance between the query encoding  │    │
│  │ and each known encoding. If distance < tolerance, it's  │    │
│  │ a match (smaller distance = more similar).              │    │
│  │                                                         │    │
│  │ Output: [True, False, False, True, ...]                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                         │                                       │
│                         ▼                                       │
│  Step 5: Database Storage                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Encoding serialization for SQLite storage:              │    │
│  │                                                         │    │
│  │ Store:   encoding.astype(np.float64).tobytes() → BLOB   │    │
│  │ Retrieve: np.frombuffer(blob, dtype=np.float64) → arr   │    │
│  │                                                         │    │
│  │ This converts the 128-d numpy array to raw bytes for    │    │
│  │ storage in a BLOB column, and back to array for use.    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Output: Matched student dict or None                           │
└─────────────────────────────────────────────────────────────────┘
```

### Face Registration Flow

```
Admin adds student via form
         │
         ▼
Student record created in database
(no face encoding yet)
         │
         ▼
Admin selects student, clicks "Capture Face"
         │
         ▼
Camera opens in modal (MediaDevices API)
         │
         ▼
Admin clicks "Capture Face"
         │
         ▼
Frame sent to POST /api/capture-face
         │
         ▼
Backend detects face → generates encoding
         │
         ▼
Encoding saved to students.face_encoding (BLOB)
         │
         ▼
FaceRecognizer singleton reloads known faces
```

---

## 7. Module Map (Original → Integrated)

This table shows how the scattered original files were combined into the final structure.

| Original File | Lines | Integrated Into |
|---|---|---|
| `backend/database.py` | 40 | `database/db.py` (table creation) |
| `backend/recordentryandinsertion.py` | 123 | `database/db.py` (CRUD functions) |
| `database/config.py` | 76 | `config.py` (settings) |
| `database/database.py` | 47 | `database/db.py` (connection) |
| `database/face_utils.py` | 192 | `backend/face_recognizer.py`, `backend/camera.py` |
| `database/main.py` | 132 | `backend/face_recognizer.py` (reference) |
| `database/recognize.py` | 128 | `backend/face_recognizer.py` (comparison logic) |
| `database/register.py` | 343 | `backend/face_recognizer.py` (capture logic) |
| `database/record_entry_and_insertion.py` | 229 | `database/db.py` (numpy serialization) |
| `UI/app.py` | 450 | `UI/templates/*` (UI converted to HTML) |
| `UI/login.py` | 329 | `UI/templates/login.html`, `routes.py` |
| `UI/styles.py` | 135 | `UI/static/css/style.css` |
| `UI/main.py` | 85 | `app.py` (entry point concept) |
| `web_based/app.py` | 58 | `app.py` (rewritten) |
| `web_based/routes.py` | 391 | `routes.py` (rewritten with real logic) |
| `web_based/templates/*` | 945 | `UI/templates/*` (updated) |
| `web_based/static/*` | 829 | `UI/static/*` (updated) |

**Duplicates Removed:**
- Two `export_attendance_to_csv()` functions → one in `db.py`
- Two `insert_person()` functions → one `add_student()` in `db.py`
- Two `mark_attendance()` functions → one in `db.py`
- Two `get_all_people()` functions → one `get_all_face_encodings()` in `db.py`
- Three database schema definitions → one `initialize_database()` in `db.py`
- Three camera management implementations → `CameraStream` class in `camera.py`

---

## 8. Team Responsibilities

### Frontend Developer
| Responsibility | Files |
|---|---|
| HTML templates with Jinja2 | `UI/templates/*.html` |
| CSS styling (blue theme) | `UI/static/css/style.css` |
| JavaScript interactions | `UI/static/js/script.js` |
| Camera access via MediaDevices | `attendance.html` inline scripts |
| Modal dialogs (add student, capture face) | `students.html` |
| Table rendering and filtering | `students.html`, reports pages |
| API communication via fetch() | All inline `<script>` blocks |

### Backend Developer
| Responsibility | Files |
|---|---|
| Face detection pipeline | `backend/face_recognizer.py` |
| Face encoding generation | `backend/face_recognizer.py` |
| Face comparison & matching | `backend/face_recognizer.py` |
| Camera stream management | `backend/camera.py` |
| Attendance + recognition integration | `backend/attendance.py` |
| Image encoding/decoding | `backend/camera.py`, `backend/utils.py` |
| Base64 ↔ OpenCV frame conversion | `backend/camera.py` |

### Database Developer
| Responsibility | Files |
|---|---|
| SQLite schema design | `database/db.py` |
| Student CRUD operations | `database/db.py` |
| Attendance CRUD operations | `database/db.py` |
| Face encoding serialization (numpy ↔ BLOB) | `database/db.py` |
| Search/filter queries | `database/db.py` |
| Statistics queries (dashboard) | `database/db.py` |
| CSV export | `database/db.py` |
| OOP wrappers | `database/models.py` |

### Integration Developer
| Responsibility | Files |
|---|---|
| Merged all modules into single app | `app.py`, `routes.py` |
| Created route definitions | `routes.py` |
| Connected frontend to backend APIs | `routes.py` |
| Wired attendance marking to face recognition | `routes.py`, `attendance.py` |
| Replaced dummy data with real DB queries | `routes.py` |
| Session management (login/logout) | `routes.py` |
| Configuration consolidation | `config.py` |
| Package structure (`__init__.py` files) | `backend/__init__.py`, `database/__init__.py` |

---

## ASCII Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   ┌───────────┐     ┌────────────────┐     ┌──────────────────────┐    │
│   │  Browser   │────▶│   Flask App    │────▶│   Face Recognition  │    │
│   │  (HTML/JS) │     │   (routes.py)  │     │   (face_recognizer) │    │
│   └─────┬─────┘     └───────┬────────┘     └──────────┬───────────┘    │
│         │                   │                          │                │
│         │     Templates     │     API calls            │                │
│         │     (Jinja2)      │     (fetch JSON)         │                │
│         │                   │                          │                │
│         ▼                   ▼                          ▼                │
│   ┌───────────┐     ┌────────────────┐     ┌──────────────────────┐    │
│   │  UI/      │     │  Database      │     │  OpenCV + face_rec.  │    │
│   │ templates │     │  (SQLite)      │     │  (Camera, Detection) │    │
│   └───────────┘     └────────────────┘     └──────────────────────┘    │
│                                                                         │
│   DATA FLOW:                                                            │
│   Browser ──fetch──▶ Flask ──SQL──▶ Database                            │
│   Browser ──fetch──▶ Flask ──cv2──▶ Camera                              │
│   Camera ──frame──▶ FaceRec ──fr──▶ Compare ──match──▶ Mark Attendance  │
│   Mark Attendance ──INSERT──▶ Database ──SELECT──▶ Browser table        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```
