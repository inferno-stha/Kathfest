import sqlite3
import numpy as np
import csv
from datetime import datetime

DATABASE_NAME = "attendance.db"


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection():

    return sqlite3.connect(DATABASE_NAME)


# =====================================================
# INSERT STUDENT
# =====================================================

def insert_person(name, roll_no, department, face_encoding):

    conn = get_connection()
    cursor = conn.cursor()

    encoding_blob = face_encoding.astype(np.float64).tobytes()

    cursor.execute("""
        INSERT INTO person
        (name, roll_no, department, face_encoding)

        VALUES (?, ?, ?, ?)
    """, (
        name,
        roll_no,
        department,
        encoding_blob
    ))

    conn.commit()
    conn.close()

    print("Student registered successfully.")


# =====================================================
# LOAD ALL PEOPLE
# =====================================================

def get_all_people():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            person_id,
            name,
            roll_no,
            department,
            face_encoding

        FROM person
    """)

    rows = cursor.fetchall()

    conn.close()

    people = []

    for row in rows:

        person_id, name, roll_no, department, encoding_blob = row

        encoding = np.frombuffer(
            encoding_blob,
            dtype=np.float64
        )

        people.append({

            "person_id": person_id,

            "name": name,

            "roll_no": roll_no,

            "department": department,

            "encoding": encoding

        })

    return people


# =====================================================
# MARK ATTENDANCE
# =====================================================

def mark_attendance(person_id):

    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now()

    attendance_date = now.date().isoformat()
    attendance_time = now.strftime("%H:%M:%S")

    cursor.execute("""
        SELECT attendance_id

        FROM attendance

        WHERE person_id=?
        AND attendance_date=?
    """, (
        person_id,
        attendance_date
    ))

    record = cursor.fetchone()

    if record is None:

        cursor.execute("""
            INSERT INTO attendance
            (
                person_id,
                attendance_date,
                attendance_time
            )

            VALUES (?, ?, ?)
        """, (
            person_id,
            attendance_date,
            attendance_time
        ))

        conn.commit()

        print("Attendance marked successfully.")

    else:

        print("Attendance already marked today.")

    conn.close()


# =====================================================
# EXPORT CSV
# =====================================================

def export_attendance_to_csv(filename="attendance_report.csv"):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT

            p.name,
            p.roll_no,
            p.department,

            a.attendance_date,
            a.attendance_time,
            a.status

        FROM attendance a

        JOIN person p

        ON a.person_id=p.person_id

        ORDER BY
        a.attendance_date,
        a.attendance_time
    """)

    rows = cursor.fetchall()

    conn.close()

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Name",
            "Roll No",
            "Department",
            "Date",
            "Time",
            "Status"
        ])

        writer.writerows(rows)

    print("Attendance exported successfully.")


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    people = get_all_people()

    print(f"{len(people)} students found.")

    for person in people:

        print(
            person["person_id"],
            person["name"],
            person["roll_no"]
        )