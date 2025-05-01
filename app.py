import os
import cv2
import numpy as np
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
db_file = 'attendance.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT, reg_no TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY, student_id INTEGER, timestamp TEXT)''')
# Create default admin
cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
if not cursor.fetchone():
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin123'))
conn.commit()
conn.close()

# Ensure dataset folder
if not os.path.exists('dataset'):
    os.makedirs('dataset')

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user'] = username
            return redirect('/admin')
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')
    return render_template('admin.html')

@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        name = request.form['name']
        reg_no = request.form['reg_no']
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO students (name, reg_no) VALUES (?, ?)', (name, reg_no))
        conn.commit()
        student_id = cursor.lastrowid
        conn.close()

        save_path = f"dataset/{reg_no}"
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        cam = cv2.VideoCapture(0)
        count = 0
        while True:
            ret, frame = cam.read()
            if not ret:
                break
            cv2.imshow('Capturing Images - Press q to Quit', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            img_name = f"{save_path}/{count}.jpg"
            cv2.imwrite(img_name, frame)
            count += 1
            if count >= 50:
                break
        cam.release()
        cv2.destroyAllWindows()
        flash('Student registered and images captured!')
        return redirect('/admin')
    return render_template('register_student.html')

@app.route('/train_model')
def train_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    faces = []
    labels = []
    label_map = {}
    label_id = 0

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT id, reg_no FROM students')
    students = cursor.fetchall()
    conn.close()

    for student in students:
        student_id, reg_no = student
        label_map[label_id] = (student_id, reg_no)
        folder = f"dataset/{reg_no}"
        for img_name in os.listdir(folder):
            img_path = os.path.join(folder, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            faces_rect = detector.detectMultiScale(img)
            for (x, y, w, h) in faces_rect:
                faces.append(img[y:y + h, x:x + w])
                labels.append(label_id)
        label_id += 1

    np.save('label_map.npy', label_map)
    recognizer.train(faces, np.array(labels))
    recognizer.save('trainer.yml')
    flash('Model trained successfully!')
    return redirect('/admin')

@app.route('/take_attendance')
def take_attendance():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer.yml')
    label_map = np.load('label_map.npy', allow_pickle=True).item()
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cam = cv2.VideoCapture(0)
    while True:
        ret, frame = cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            face = gray[y:y + h, x:x + w]
            id_, conf = recognizer.predict(face)
            if conf < 70:
                student_id, reg_no = label_map[id_]
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute('SELECT name FROM students WHERE id = ?', (student_id,))
                name = cursor.fetchone()[0]
                cursor.execute('INSERT INTO attendance (student_id, timestamp) VALUES (?, ?)', (student_id, datetime.now()))
                conn.commit()
                conn.close()
                cv2.putText(frame, f"{name} ({reg_no})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.imshow('Taking Attendance - Press q to Quit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
    flash('Attendance recorded!')
    return redirect('/admin')

@app.route('/view_attendance')
def view_attendance():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''SELECT a.id, s.name, s.reg_no, a.timestamp FROM attendance a JOIN students s ON a.student_id = s.id ORDER BY a.timestamp DESC''')
    records = cursor.fetchall()
    conn.close()
    return render_template('view_attendance.html', attendance=records)

if __name__ == '__main__':
    app.run(debug=True)
