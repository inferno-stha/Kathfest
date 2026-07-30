import sqlite3

DATABASE_NAME = "attendance.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER NOT NULL,
        attendance_date DATE NOT NULL,
        attendance_time TIME NOT NULL,
        status TEXT DEFAULT 'Present',

        FOREIGN KEY(person_id)
        REFERENCES person(person_id)
    )
    """)

    conn.commit()
    conn.close()

    print("Database initialized successfully.")


if __name__ == "__main__":

    initialize_database()