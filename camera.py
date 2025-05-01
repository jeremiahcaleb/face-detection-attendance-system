import cv2
import os

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Ensure capture directory exists
CAPTURE_DIR = "static/captures"
os.makedirs(CAPTURE_DIR, exist_ok=True)

def detect_faces_and_capture(name):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Cannot access camera.")
        return

    captured = False
    face_counter = 0  # To prevent overwriting and ensure face capture

    while not captured:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from camera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        # If faces are detected, capture the first face or a better one
        if len(faces) > 0:
            # Pick the largest face if multiple are detected
            largest_face = max(faces, key=lambda x: x[2] * x[3])  # Largest face by area (width * height)
            (x, y, w, h) = largest_face
            img = frame[y:y+h, x:x+w]

            # Save the image with a unique filename based on the student's name
            filename = os.path.join(CAPTURE_DIR, f"{name}_{face_counter}.jpg")
            cv2.imwrite(filename, img)
            print(f"[INFO] Face image saved to {filename}")
            
            captured = True  # Mark face as captured
            face_counter += 1  # Increment counter for multiple captures

        # Show live feed (optional, can be removed for production)
        cv2.imshow('Capturing Face - Press Q to exit', frame)

        # Press 'q' to quit if needed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if not captured:
        print("[INFO] No face captured successfully.")
    else:
        print("[INFO] Face capture successful.")
