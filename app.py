from flask import Flask, render_template, request, redirect, url_for, flash
from camera import detect_faces_and_capture  # Assuming your face detection function is in camera.py
from db import connect_sqlite, init_databases  # Assuming your SQLite connection and init functions are in db.py
import os
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Initialize the database
init_databases()

@app.route('/')
def index():
    return render_template('index.html')


# ---------- Register Student ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']

        # Capture face and store it
        detect_faces_and_capture(name)

        # Save student to DB
        try:
            conn = connect_sqlite()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (name) VALUES (?)", (name,))
            conn.commit()
            conn.close()

            flash(f'{name} registered successfully!')
        except Exception as e:
            flash(f'Error: {str(e)}')
        return redirect(url_for('register'))

    return render_template('register.html')


# ---------- Take Attendance ----------
@app.route('/take_attendance', methods=['GET', 'POST'])
def take_attendance():
    if request.method == 'POST':
        name = request.form['name']

        # Capture face and store it
        detect_faces_and_capture(name)

        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        try:
            conn = connect_sqlite()
            cursor = conn.cursor()

            # Get student ID or insert if new
            cursor.execute("SELECT id FROM students WHERE name = ?", (name,))
            result = cursor.fetchone()

            if result:
                student_id = result[0]
            else:
                cursor.execute("INSERT INTO students (name) VALUES (?)", (name,))
                student_id = cursor.lastrowid

            # Insert attendance
            cursor.execute("INSERT INTO attendance (student_id, name, timestamp) VALUES (?, ?, ?)",
                           (student_id, name, timestamp))

            conn.commit()
            conn.close()

            flash(f'Attendance marked for {name} at {timestamp}')
        except Exception as e:
            flash(f'Error: {str(e)}')

        return redirect(url_for('take_attendance'))

    return render_template('attendance.html')


# ---------- View Attendance Records ----------
@app.route('/view_attendance')
def view_attendance():
    try:
        conn = connect_sqlite()
        cursor = conn.cursor()
        cursor.execute("SELECT students.name, attendance.timestamp FROM attendance JOIN students ON students.id = attendance.student_id ORDER BY attendance.timestamp DESC")
        data_sqlite = cursor.fetchall()
        conn.close()
        return render_template('view.html', data_sqlite=data_sqlite)
    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect(url_for('index'))
from flask import Flask, render_template, request, redirect, url_for, flash
from camera import detect_faces_and_capture  # Assuming your face detection function is in camera.py
from db import connect_sqlite, init_databases  # Assuming your SQLite connection and init functions are in db.py
import os
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Initialize the database
init_databases()

@app.route('/')
def index():
    return render_template('index.html')


# ---------- Register Student ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']

        # Capture face and store it
        detect_faces_and_capture(name)

        # Save student to DB
        try:
            conn = connect_sqlite()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (name) VALUES (?)", (name,))
            conn.commit()
            conn.close()

            flash(f'{name} registered successfully!')
        except Exception as e:
            flash(f'Error: {str(e)}')
        return redirect(url_for('register'))

    return render_template('register.html')


# ---------- Take Attendance ----------
@app.route('/take_attendance', methods=['GET', 'POST'])
def take_attendance():
    if request.method == 'POST':
        name = request.form['name']

        # Capture face and store it
        detect_faces_and_capture(name)

        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        try:
            conn = connect_sqlite()
            cursor = conn.cursor()

            # Get student ID or insert if new
            cursor.execute("SELECT id FROM students WHERE name = ?", (name,))
            result = cursor.fetchone()

            if result:
                student_id = result[0]
            else:
                cursor.execute("INSERT INTO students (name) VALUES (?)", (name,))
                student_id = cursor.lastrowid

            # Insert attendance
            cursor.execute("INSERT INTO attendance (student_id, name, timestamp) VALUES (?, ?, ?)",
                           (student_id, name, timestamp))

            conn.commit()
            conn.close()

            flash(f'Attendance marked for {name} at {timestamp}')
        except Exception as e:
            flash(f'Error: {str(e)}')

        return redirect(url_for('take_attendance'))

    return render_template('attendance.html')


# ---------- View Attendance Records ----------
@app.route('/view_attendance')
def view_attendance():
    try:
        conn = connect_sqlite()
        cursor = conn.cursor()
        cursor.execute("SELECT students.name, attendance.timestamp FROM attendance JOIN students ON students.id = attendance.student_id ORDER BY attendance.timestamp DESC")
        data_sqlite = cursor.fetchall()
        conn.close()
        return render_template('view.html', data_sqlite=data_sqlite)
    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True)
