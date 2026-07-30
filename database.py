import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("attendance.db")

# Create cursor
cursor = conn.cursor()

# Create Person table
cursor.execute("""
CREATE TABLE IF NOT EXISTS person (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_no TEXT UNIQUE NOT NULL,
    department TEXT,
    face_encoding BLOB NOT NULL,
    registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Create Attendance table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    attendance_date DATE NOT NULL,
    attendance_time TIME NOT NULL,
    status TEXT DEFAULT 'Present',

    FOREIGN KEY(person_id) REFERENCES person(person_id)
)
""")

# Save changes
conn.commit()

# Close connection
conn.close()


