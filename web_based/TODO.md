# TODO List — Smart Student Attendance System

## Frontend (Flask Web App)

- [x] Base template with sidebar and header
- [x] Login page with session authentication
- [x] Dashboard page with stats cards
- [x] Students page with filter (department → semester → text search)
- [x] Attendance page with camera placeholder
- [x] Reports page with statistics and CSV export placeholder
- [x] About page with project info

## Backend (Face Recognition)

- [ ] Implement `start_camera()` — OpenCV VideoCapture streaming
- [ ] Implement `capture_face()` — Face detection and encoding
- [ ] Implement `recognize_face()` — Compare live face with stored encodings

## Database (SQLite)

- [ ] Replace `students_data` with real SQLite SELECT query
- [ ] Implement `save_student()` — INSERT new student
- [ ] Implement `delete_student()` — DELETE student by ID
- [ ] Create users table for login

## Integration

- [ ] Connect face recognition output to `mark_attendance()`
- [ ] Connect camera stream to attendance marking flow
- [ ] Implement CSV export
- [ ] Real-time attendance update without page reload

## Testing

- [ ] Test all filter combinations on Students page
- [ ] Test duplicate student ID / roll number detection
- [ ] Test duplicate attendance marking prevention
- [ ] Test login/logout flow
