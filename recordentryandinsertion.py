import sqlite3

def insert_person(name, roll_no, department, face_encoding):#function to register student

    conn = sqlite3.connect("attendance.db")#to establish a relation between python and database
    cursor = conn.cursor()#to communicate or exchange data or information between file and database

    cursor.execute("""
        INSERT INTO person(name, roll_no, department, face_encoding)
        VALUES (?, ?, ?, ?)
    """, (name, roll_no, department, face_encoding))#values equals ? garera pachi argument pass garda variable le argument ko value lincha

    conn.commit()#to save a change made on the database
    conn.close()

def get_all_people():

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT person_id, name, face_encoding
        FROM person
    ''')

    people = cursor.fetchall()

    conn.close()

    # Formatted printing
    print('\n{:<10} {:<20} {:<30}'.format('ID', 'NAME', 'ENCODING'))
    print('-' * 65)

    for person in people:
        person_id, name, encoding = person
        print('{:<10} {:<20} {:<30}'.format(
            person_id,
            name,
            str(encoding)[:30] + '...'
        ))

    return people
from datetime import datetime

def mark_attendance(person_id):

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    # Get current date and time
    now = datetime.now()
    attendance_date = now.date().isoformat()          # Example: 2026-07-17
    attendance_time = now.time().strftime("%H:%M:%S") # Example: 09:15:32

    # Check if attendance is already marked today
    cursor.execute("""
        SELECT *
        FROM attendance
        WHERE person_id = ? AND attendance_date = ?
    """, (person_id, attendance_date))

    record = cursor.fetchone()

    # If not already marked, insert attendance
    if record is None:
        cursor.execute("""
            INSERT INTO attendance
            (person_id, attendance_date, attendance_time)
            VALUES (?, ?, ?)
        """, (person_id, attendance_date, attendance_time))

        conn.commit()
        print("Attendance marked successfully.")

    else:
        print("Attendance already marked for today.")

    conn.close()
import csv

def export_attendance_to_csv(filename="attendance_report.csv"):

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    # Get attendance data with student information
    cursor.execute("""
        SELECT 
            p.name,
            p.roll_no,
            p.department,
            a.attendance_date,
            a.attendance_time,
            a.status
        FROM attendance a
        JOIN person p ON a.person_id = p.person_id
        ORDER BY a.attendance_date, a.attendance_time
    """)

    rows = cursor.fetchall()

    # Create CSV file
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Header row
        writer.writerow([
            "Name",
            "Roll No",
            "Department",
            "Attendance Date",
            "Attendance Time",
            "Status"
        ])

        # Data rows
        writer.writerows(rows)

    conn.close()

    print(f"Attendance exported successfully to '{filename}'")
if __name__ == "__main__":
    export_attendance_to_csv()