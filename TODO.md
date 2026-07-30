# ✅ TODO — Smart Student Attendance System

A shared checklist for the hackathon team. Check items off as they are
completed so everyone can see progress at a glance.

## Frontend (UI)

- [x] Build Login UI
- [x] Build Dashboard page
- [x] Build Student Management page
- [x] Build Attendance page
- [x] Build Reports page
- [x] Build About page
- [x] Sidebar navigation + page switching
- [x] Apply consistent theme (`styles.py`)
- [ ] Add form dialog for "Add Student"
- [ ] Add confirmation dialog for "Delete Student"

## Backend

- [ ] Set up OpenCV camera capture (`start_camera`)
- [ ] Stream live camera frames into the Attendance preview
- [ ] Implement face capture & encoding (`capture_face`)
- [ ] Implement face recognition matching (`recognize_face`)
- [ ] Implement CSV export (`export_csv`)

## Database

- [ ] Design SQLite schema (students, attendance, users tables)
- [ ] Implement `load_students()` with real queries
- [ ] Implement `save_student()` (INSERT)
- [ ] Implement `delete_student()` (DELETE)
- [ ] Implement `mark_attendance()` (INSERT attendance record)
- [ ] Replace dummy login with real authentication

## Integration

- [ ] Connect face recognition results to `mark_attendance()`
- [ ] Refresh Dashboard stats from live database counts
- [ ] Wire Reports page to real attendance totals
- [ ] Handle camera/database errors gracefully in the UI

## Testing & Polish

- [ ] Test login with invalid credentials
- [ ] Test navigation between all pages
- [ ] Test Treeview search/filter with edge cases (empty query, no matches)
- [ ] Test on Windows, macOS, and Linux
- [ ] Cross-check UI at different window sizes

## Packaging & Presentation

- [ ] Add screenshots to `docs/screenshots/`
- [ ] Package with PyInstaller (optional, for demo laptop)
- [ ] Prepare final presentation slides
- [ ] Rehearse live demo flow (login → dashboard → attendance → reports)
