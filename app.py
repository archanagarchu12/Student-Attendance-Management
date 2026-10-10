
import sqlite3

# Connect to the database
conn = sqlite3.connect("attendance.db")

# Create a cursor to execute SQL commands
cursor = conn.cursor()

# Create the students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL
)
""")

# Save changes and close the connection
conn.commit()
conn.close()

print("Database and students table created successfully!")

# Add a student to the database
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

cursor.execute(
    "INSERT INTO students (name, department) VALUES (?, ?)",
    ("Arun", "IT")
)

conn.commit()
conn.close()

print("Student added successfully!")

# Retrieve student details from the database
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM students")
students = cursor.fetchall()

print("Student Records:")

for student in students:
    print(student)

conn.close()

# Update a student's name
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

cursor.execute(
    "UPDATE students SET name = ? WHERE id = ?",
    ("Rahul", 2)
)

conn.commit()
conn.close()

print("Student updated successfully!")
# Verify the updated student record
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM students")
print("Updated Student Records:")

for student in cursor.fetchall():
    print(student)

conn.close()

# Delete a student record
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

cursor.execute(
    "DELETE FROM students WHERE id = ?",
    (2,)
)

if cursor.rowcount > 0:
    print("Student deleted successfully!")
else:
    print("Student ID not found!")

conn.commit()
conn.close()

# Verify the deleted student record
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM students")
print("Student Records After Deletion:")

for student in cursor.fetchall():
    print(student)
conn.close()

# STEP 5: ATTENDANCE MANAGEMENT

import sqlite3
from datetime import date

# Connect to the database
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Create the attendance table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    attendance_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Present', 'Absent')),
    UNIQUE(student_id, attendance_date),
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

conn.commit()
conn.close()

print("\nAttendance table created successfully!")


# Mark attendance for all students
def mark_attendance():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    today = date.today().isoformat()

    cursor.execute("SELECT id, name FROM students ORDER BY id")
    students = cursor.fetchall()

    if not students:
        print("No students found!")
        conn.close()
        return

    print("\n--- MARK ATTENDANCE ---")
    print("Date:", today)

    for student in students:
        student_id, name = student

        while True:
            status = input(
                "Enter P for Present or A for Absent "
                + "for " + name + " (ID " + str(student_id) + "): "
            ).strip().upper()

            if status in ("P", "A"):
                break

            print("Invalid input! Enter P or A.")

        if status == "P":
            status = "Present"
        else:
            status = "Absent"

        # Update today's record if it already exists.
        # Otherwise, insert a new attendance record.
        cursor.execute("""
            SELECT id FROM attendance
            WHERE student_id = ? AND attendance_date = ?
        """, (student_id, today))

        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE attendance
                SET status = ?
                WHERE student_id = ? AND attendance_date = ?
            """, (status, student_id, today))
        else:
            cursor.execute("""
                INSERT INTO attendance
                (student_id, attendance_date, status)
                VALUES (?, ?, ?)
            """, (student_id, today, status))

    conn.commit()
    conn.close()

    print("\nAttendance saved successfully!")


# Display present and absent counts for today
def show_attendance_counts():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    today = date.today().isoformat()

    cursor.execute("""
        SELECT
            COUNT(CASE WHEN status = 'Present' THEN 1 END),
            COUNT(CASE WHEN status = 'Absent' THEN 1 END)
        FROM attendance
        WHERE attendance_date = ?
    """, (today,))

    present, absent = cursor.fetchone()

    print("\n--- TODAY'S ATTENDANCE SUMMARY ---")
    print("Present:", present)
    print("Absent:", absent)
    print("Total marked:", present + absent)

    conn.close()
# Run attendance operations
mark_attendance()
show_attendance_counts()
