# TODO.md — Project Task Checklist

## Smart Student Attendance System Using Face Recognition

### Legend
- [x] Completed
- [ ] Pending / Not Started

---

## Phase 1: Project Analysis

- [x] Read all existing files in `backend/`, `UI/`, `database/`, `web_based/`
- [x] Identify dependencies between modules
- [x] Find duplicate code across modules
- [x] Determine integration strategy

## Phase 2: Configuration

- [x] Create `config.py` consolidating settings from:
  - [x] `database/config.py` (CAMERA_INDEX, FACE_MATCH_THRESHOLD, etc.)
  - [x] `web_based/app.py` (SECRET_KEY)
  - [x] `backend/database.py` (database path)
  - [x] `database/database.py` (database path)

## Phase 3: Database Layer

- [x] Create `database/__init__.py`
- [x] Create `database/db.py` merging:
  - [x] `backend/database.py` (table creation)
  - [x] `database/database.py` (connection initialization)
  - [x] `backend/recordentryandinsertion.py` (CRUD operations)
  - [x] `database/record_entry_and_insertion.py` (improved CRUD + numpy)
  - [x] Add missing `semester` field to students table
  - [x] Rename `roll_no` → `roll_number` for consistency
- [x] Create `database/models.py` (OOP wrappers)
- [x] Test database initialization

## Phase 4: Backend Layer

- [x] Create `backend/__init__.py`
- [x] Create `backend/face_recognizer.py` merging:
  - [x] `database/face_utils.py` (camera, detection, encoding)
  - [x] `database/recognize.py` (face comparison)
  - [x] `database/main.py` (basic detection loop)
  - [x] `database/register.py` (capture during registration)
- [x] Create `backend/camera.py` (CameraStream class)
- [x] Create `backend/attendance.py` (attendance + recognition integration)
- [x] Create `backend/utils.py` (helpers, decorators)

## Phase 5: Flask Web Layer

- [x] Create `app.py` (Flask entry point)
- [x] Create `routes.py` with all endpoints:
  - [x] Login/Logout (session-based)
  - [x] Dashboard (real database stats)
  - [x] Students CRUD (SQLite queries)
  - [x] Face capture/registration
  - [x] Attendance marking via face recognition
  - [x] Reports with CSV export
  - [x] About page

## Phase 6: Frontend Integration

- [x] Move templates from `web_based/templates/` to `UI/templates/`
- [x] Move static files from `web_based/static/` to `UI/static/`
- [x] Update `students.html`:
  - [x] Use dict keys instead of tuple indices
  - [x] Add face registration modal with camera
  - [x] Add edit/delete buttons per row
- [x] Update `attendance.html`:
  - [x] Real camera preview via MediaDevices API
  - [x] Frame capture and send to `/api/attendance/mark`
  - [x] Real-time table refresh after marking
  - [x] Status messages (success/error/warning)
- [x] Update `reports.html`:
  - [x] Real CSV download
  - [x] All attendance records table
- [x] Update `script.js` with API communication helpers
- [x] Update `style.css` with additional styles (btn-sm, alerts)

## Phase 7: Documentation

- [x] Create `README.md`
- [ ] Create `TODO.md` (this file)
- [ ] Create `PROGRESS.md`
- [ ] Create `ARCHITECTURE.md`
- [x] Add extensive comments to all Python files
- [x] Add code comments explaining every route, function, and integration point

## Phase 8: Testing & Verification

- [ ] Test that `python app.py` starts without import errors
- [ ] Test login page renders correctly
- [ ] Test dashboard stats with real database
- [ ] Test adding a student
- [ ] Test deleting a student
- [ ] Test search/filter students
- [ ] Test face capture modal
- [ ] Test attendance page camera
- [ ] Test face recognition marking
- [ ] Test CSV export
- [ ] Test reports page
- [ ] Test logout

## Phase 9: Polish

- [ ] Remove old `__pycache__` directories
- [ ] Remove duplicate/unused files from original modules
- [ ] Verify all imports work correctly
- [ ] Ensure error handling works for camera-unavailable scenarios
