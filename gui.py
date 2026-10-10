
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

# Database file stays in the same folder as this Python file
DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "attendance.db"
)

selected_student_id = None


def connect_db():
    return sqlite3.connect(DB_PATH)


def setup_database():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL
                CHECK(status IN ('Present', 'Absent')),
            UNIQUE(student_id, attendance_date),
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    conn.commit()
    conn.close()


def refresh_students():
    for item in student_table.get_children():
        student_table.delete(item)

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, department FROM students ORDER BY id"
    )
    rows = cur.fetchall()
    conn.close()

    for number, row in enumerate(rows, start=1):
        db_id, name, department = row
        student_table.insert(
            "",
            "end",
            iid=str(db_id),
            values=(number, name, department)
        )

    update_counts()



def clear_fields():
    global selected_student_id
    selected_student_id = None

    name_entry.delete(0, tk.END)
    department_entry.delete(0, tk.END)

    student_table.selection_remove(
        student_table.selection()
    )

    name_entry.focus_set()


def select_student(event=None):
    global selected_student_id

    selection = student_table.selection()
    if not selection:
        return

    selected_student_id = int(selection[0])
    values = student_table.item(selection[0], "values")

    name_entry.delete(0, tk.END)
    name_entry.insert(0, values[1])

    department_entry.delete(0, tk.END)
    department_entry.insert(0, values[2])


def add_student():
    name = name_entry.get().strip()
    department = department_entry.get().strip()

    if not name or not department:
        messagebox.showwarning(
            "Missing details",
            "Enter both student name and department."
        )
        return

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (name, department) VALUES (?, ?)",
        (name, department)
    )
    conn.commit()
    conn.close()

    refresh_students()
    clear_fields()
    messagebox.showinfo("Success", "Student added successfully.")


def update_student():
    if selected_student_id is None:
        messagebox.showwarning(
            "Select student",
            "Select a student row first."
        )
        return

    name = name_entry.get().strip()
    department = department_entry.get().strip()

    if not name or not department:
        messagebox.showwarning(
            "Missing details",
            "Enter both name and department."
        )
        return

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE students SET name=?, department=? WHERE id=?",
        (name, department, selected_student_id)
    )
    changed = cur.rowcount
    conn.commit()
    conn.close()

    refresh_students()
    clear_fields()

    if changed:
        messagebox.showinfo(
            "Success", "Student updated successfully."
        )
    else:
        messagebox.showerror(
            "Error", "Student record not found."
        )


def delete_student():
    if selected_student_id is None:
        messagebox.showwarning(
            "Select student",
            "Select a student row first."
        )
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Delete this student and their attendance records?"
    )

    if not confirm:
        return

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM attendance WHERE student_id=?",
        (selected_student_id,)
    )
    cur.execute(
        "DELETE FROM students WHERE id=?",
        (selected_student_id,)
    )

    changed = cur.rowcount
    conn.commit()
    conn.close()

    refresh_students()
    refresh_attendance()
    clear_fields()

    if changed:
        messagebox.showinfo(
            "Success",
            "Student and attendance records deleted."
        )
    else:
        messagebox.showerror(
            "Error", "Student record not found."
        )


def mark_attendance():
    selection = student_table.selection()

    if not selection:
        messagebox.showwarning(
            "Select student",
            "Select a student from Student Records first."
        )
        return

    student_id = int(selection[0])
    status = attendance_status.get()
    today = date.today().isoformat()

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        """SELECT id FROM attendance
           WHERE student_id=? AND attendance_date=?""",
        (student_id, today)
    )

    existing = cur.fetchone()

    if existing:
        cur.execute(
            """UPDATE attendance SET status=?
               WHERE student_id=? AND attendance_date=?""",
            (status, student_id, today)
        )
    else:
        cur.execute(
            """INSERT INTO attendance
               (student_id, attendance_date, status)
               VALUES (?, ?, ?)""",
            (student_id, today, status)
        )

    conn.commit()
    conn.close()

    refresh_attendance()
    update_counts()

    messagebox.showinfo(
        "Attendance Saved",
        "Attendance marked as " + status + "."
    )


def refresh_attendance():
    for item in attendance_table.get_children():
        attendance_table.delete(item)

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT students.id,
               students.name,
               students.department,
               attendance.attendance_date,
               attendance.status
        FROM attendance
        JOIN students
        ON students.id = attendance.student_id
        ORDER BY attendance.attendance_date DESC,
                 students.name
    """)

    rows = cur.fetchall()
    conn.close()

    for row in rows:
        attendance_table.insert("", "end", values=row)


def update_counts():
    conn = connect_db()
    cur = conn.cursor()
    today = date.today().isoformat()

    cur.execute("SELECT COUNT(*) FROM students")
    total = cur.fetchone()[0]

    cur.execute(
        """SELECT COUNT(*) FROM attendance
           WHERE attendance_date=? AND status='Present'""",
        (today,)
    )
    present = cur.fetchone()[0]

    cur.execute(
        """SELECT COUNT(*) FROM attendance
           WHERE attendance_date=? AND status='Absent'""",
        (today,)
    )
    absent = cur.fetchone()[0]

    conn.close()

    total_value.config(text=str(total))
    present_value.config(text=str(present))
    absent_value.config(text=str(absent))


def refresh_all():
    refresh_students()
    refresh_attendance()


# Create database and tables
setup_database()

# Main window
root = tk.Tk()
root.title("Student Attendance Management System")
root.geometry("1050x760")
root.minsize(900, 650)
root.configure(bg="#f4efff")

# Table design
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="white",
    foreground="#302044",
    rowheight=27,
    fieldbackground="white",
    font=("Arial", 10)
)

style.configure(
    "Treeview.Heading",
    background="#6c3fc5",
    foreground="white",
    font=("Arial", 10, "bold")
)

style.map(
    "Treeview",
    background=[("selected", "#d9c8ff")],
    foreground=[("selected", "#302044")]
)

# Header
header = tk.Frame(root, bg="#6c3fc5", height=76)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="STUDENT ATTENDANCE MANAGEMENT",
    bg="#6c3fc5",
    fg="white",
    font=("Arial", 19, "bold")
).pack(pady=(12, 2))

tk.Label(
    header,
    text="Manage student records and daily attendance",
    bg="#6c3fc5",
    fg="#eee5ff",
    font=("Arial", 10)
).pack()

# Summary cards
cards = tk.Frame(root, bg="#f4efff")
cards.pack(fill="x", padx=16, pady=10)


def create_card(title, color):
    card = tk.Frame(
        cards, bg="white", bd=1, relief="solid"
    )
    card.pack(
        side="left", expand=True, fill="x", padx=5
    )

    tk.Label(
        card,
        text=title,
        bg="white",
        fg=color,
        font=("Arial", 10, "bold")
    ).pack(pady=(8, 2))

    value = tk.Label(
        card,
        text="0",
        bg="white",
        fg="#302044",
        font=("Arial", 20, "bold")
    )
    value.pack(pady=(0, 8))

    return value


total_value = create_card("TOTAL STUDENTS", "#6c3fc5")
present_value = create_card("PRESENT TODAY", "#168653")
absent_value = create_card("ABSENT TODAY", "#d54b76")

# Student details form
form = tk.LabelFrame(
    root,
    text=" Student Details ",
    bg="white",
    fg="#6c3fc5",
    font=("Arial", 10, "bold"),
    padx=10,
    pady=8
)
form.pack(fill="x", padx=20, pady=5)

tk.Label(
    form, text="Student Name",
    bg="white", fg="#302044"
).grid(row=0, column=0, sticky="w", padx=5)

name_entry = tk.Entry(
    form, font=("Arial", 11), width=23
)
name_entry.grid(
    row=1, column=0, padx=5, pady=5, sticky="ew"
)

tk.Label(
    form, text="Department",
    bg="white", fg="#302044"
).grid(row=0, column=1, sticky="w", padx=5)

department_entry = tk.Entry(
    form, font=("Arial", 11), width=18
)
department_entry.grid(
    row=1, column=1, padx=5, pady=5, sticky="ew"
)

form.columnconfigure(0, weight=1)
form.columnconfigure(1, weight=1)


def make_button(parent, text, command, color):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg="white",
        activebackground=color,
        activeforeground="white",
        relief="flat",
        font=("Arial", 9, "bold"),
        padx=8,
        pady=7,
        cursor="hand2"
    )


button_frame = tk.Frame(form, bg="white")
button_frame.grid(row=1, column=2, padx=5)

make_button(
    button_frame, "Add Student",
    add_student, "#6c3fc5"
).pack(side="left", padx=2)

make_button(
    button_frame, "Update",
    update_student, "#8b60d9"
).pack(side="left", padx=2)

make_button(
    button_frame, "Delete",
    delete_student, "#d54b76"
).pack(side="left", padx=2)

make_button(
    button_frame, "Clear",
    clear_fields, "#718096"
).pack(side="left", padx=2)

# Student records table
student_frame = tk.LabelFrame(
    root,
    text=" Student Records — Select a row to edit or mark attendance ",
    bg="white",
    fg="#6c3fc5",
    font=("Arial", 10, "bold"),
    padx=8,
    pady=8
)
student_frame.pack(
    fill="both", expand=True, padx=20, pady=5
)

student_table = ttk.Treeview(
    student_frame,
    columns=("regno", "name", "department"),
    show="headings",
    height=6,
    selectmode="browse"
)

student_table.heading("regno", text="Reg. No.")
student_table.heading("name", text="Student Name")
student_table.heading("department", text="Department")

student_table.column("regno", width=90, anchor="center")
student_table.column("name", width=300)
student_table.column("department", width=180)

student_scroll = ttk.Scrollbar(
    student_frame,
    orient="vertical",
    command=student_table.yview
)
student_table.configure(
    yscrollcommand=student_scroll.set
)

student_table.pack(side="left", fill="both", expand=True)
student_scroll.pack(side="right", fill="y")

student_table.bind(
    "<<TreeviewSelect>>", select_student
)

# Mark attendance section
attendance_frame = tk.LabelFrame(
    root,
    text=" Mark Today's Attendance ",
    bg="white",
    fg="#6c3fc5",
    font=("Arial", 10, "bold"),
    padx=10,
    pady=6
)
attendance_frame.pack(fill="x", padx=20, pady=5)

attendance_status = tk.StringVar(value="Present")

tk.Radiobutton(
    attendance_frame,
    text="Present",
    variable=attendance_status,
    value="Present",
    bg="white",
    fg="#168653",
    font=("Arial", 10, "bold"),
    activebackground="white"
).pack(side="left", padx=10)

tk.Radiobutton(
    attendance_frame,
    text="Absent",
    variable=attendance_status,
    value="Absent",
    bg="white",
    fg="#d54b76",
    font=("Arial", 10, "bold"),
    activebackground="white"
).pack(side="left", padx=10)

make_button(
    attendance_frame,
    "Save Attendance",
    mark_attendance,
    "#6c3fc5"
).pack(side="left", padx=15)

make_button(
    attendance_frame,
    "Refresh Records",
    refresh_all,
    "#80aee8"
).pack(side="right", padx=5)

# Attendance history table
history_frame = tk.LabelFrame(
    root,
    text=" Attendance Records ",
    bg="white",
    fg="#6c3fc5",
    font=("Arial", 10, "bold"),
    padx=8,
    pady=8
)
history_frame.pack(
    fill="both", expand=True, padx=20, pady=(5, 12)
)

attendance_table = ttk.Treeview(
    history_frame,
    columns=("id", "name", "department", "date", "status"),
    show="headings",
    height=5
)

columns = [
    ("id", "Student ID"),
    ("name", "Student Name"),
    ("department", "Department"),
    ("date", "Date"),
    ("status", "Status")
]

for col, heading in columns:
    attendance_table.heading(col, text=heading)

attendance_table.column("id", width=85, anchor="center")
attendance_table.column("name", width=200)
attendance_table.column("department", width=130)
attendance_table.column("date", width=120, anchor="center")
attendance_table.column("status", width=100, anchor="center")

history_scroll = ttk.Scrollbar(
    history_frame,
    orient="vertical",
    command=attendance_table.yview
)
attendance_table.configure(
    yscrollcommand=history_scroll.set
)

attendance_table.pack(side="left", fill="both", expand=True)
history_scroll.pack(side="right", fill="y")

# Load saved records and start the GUI
refresh_students()
refresh_attendance()
root.mainloop()
