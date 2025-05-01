import sqlite3
import os

# Connect to SQLite database
def connect_sqlite():
    return sqlite3.connect('attendance.db')

# Initialize tables in SQLite
def init_sqlite():
    conn = connect_sqlite()
    cursor = conn.cursor()

    # Create students table with photo_path
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            photo_path TEXT
        )
    ''')

    # Create attendance table with status column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Present',
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ SQLite tables initialized.")

# Call this from app.py
def init_databases():
    init_sqlite()

# Function to get all students
def get_all_students():
    conn = connect_sqlite()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM students")
    students = cursor.fetchall()
    conn.close()
    return students

# Function to get attendance for a student
def get_attendance(student_id):
    conn = connect_sqlite()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, status FROM attendance WHERE student_id = ?", (student_id,))
    attendance = cursor.fetchall()
    conn.close()
    return attendance

# Function to mark attendance for a student
def mark_attendance(student_id, name, status='Present'):
    conn = connect_sqlite()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (student_id, name, status) VALUES (?, ?, ?)",
                   (student_id, name, status))
    conn.commit()
    conn.close()

# Function to get student by name (for registration or attendance check)
def get_student_by_name(name):
    conn = connect_sqlite()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM students WHERE name = ?", (name,))
    student = cursor.fetchone()
    conn.close()
    return student
