"""
enroll.py — Register a student's face into the Campus Vision system.

Uses OpenCV's LBPH face recognizer (no dlib dependency).

Usage:
    python enroll.py --name "John Doe" --id S001 --image photo.jpg
    python enroll.py --name "Jane Doe" --id S002 --webcam
    python enroll.py --demo
"""

import argparse
import sys
import os
import numpy as np
import cv2
import database as db

# OpenCV Haar cascade for face detection
CASCADE_PATH = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)


def _extract_face_features(gray_face):
    """Extract a simple histogram-based feature vector from a grayscale face crop."""
    resized = cv2.resize(gray_face, (100, 100))
    # Use a flattened normalized image as the 'encoding'
    return (resized.astype(np.float32) / 255.0).flatten().tolist()


def enroll_from_image(student_id: str, name: str, image_path: str):
    """Enroll a student from an image file."""
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        return False

    img = cv2.imread(image_path)
    if img is None:
        print(f"[ERROR] Cannot read image: {image_path}")
        return False

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(60, 60))

    if len(faces) == 0:
        print("[ERROR] No face detected in the image.")
        return False

    if len(faces) > 1:
        print(f"[WARNING] {len(faces)} faces detected. Using the largest one.")
        faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)

    x, y, w, h = faces[0]
    face_crop = gray[y:y+h, x:x+w]
    encoding = _extract_face_features(face_crop)

    db.add_student(student_id, name, encoding)
    print(f"[OK] Enrolled '{name}' (ID: {student_id}) successfully.")
    return True


def enroll_from_webcam(student_id: str, name: str):
    """Enroll a student by capturing from the system webcam."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        return False

    print("[INFO] Webcam opened. Press SPACE to capture, ESC to cancel.")

    captured = False
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 3, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(display, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.putText(display, f"Enrolling: {name} ({student_id})",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display, "SPACE=Capture  ESC=Cancel",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.imshow("Enroll Face", display)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            if len(faces) > 0:
                x, y, w, h = faces[0]
                face_crop = gray[y:y+h, x:x+w]
                encoding = _extract_face_features(face_crop)
                db.add_student(student_id, name, encoding)
                print(f"[OK] Enrolled '{name}' (ID: {student_id}) successfully.")
                captured = True
            else:
                print("[WARNING] No face detected in capture. Try again.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return captured


def enroll_demo_students():
    """Enroll some demo students with random encodings for simulation mode."""
    demo_students = [
        ("S001", "Arjun Sharma"),
        ("S002", "Priya Patel"),
        ("S003", "Rahul Kumar"),
        ("S004", "Ananya Singh"),
        ("S005", "Vikram Reddy"),
        ("S006", "Sneha Gupta"),
        ("S007", "Aditya Nair"),
        ("S008", "Kavya Menon"),
        ("S009", "Rohan Das"),
        ("S010", "Ishita Joshi"),
    ]

    count = db.get_student_count()
    if count >= len(demo_students):
        print(f"[INFO] {count} students already enrolled. Skipping demo enrollment.")
        return

    for sid, name in demo_students:
        fake_encoding = np.random.randn(10000).tolist()
        db.add_student(sid, name, fake_encoding)
        print(f"  Enrolled demo: {name} ({sid})")

    print(f"[OK] {len(demo_students)} demo students enrolled.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enroll a student face")
    parser.add_argument("--name", type=str, help="Student name")
    parser.add_argument("--id", type=str, help="Student ID")
    parser.add_argument("--image", type=str, help="Path to face image")
    parser.add_argument("--webcam", action="store_true", help="Capture from webcam")
    parser.add_argument("--demo", action="store_true", help="Enroll demo students for simulation")

    args = parser.parse_args()

    if args.demo:
        enroll_demo_students()
    elif not args.name or not args.id:
        print("[ERROR] --name and --id are required.")
        parser.print_help()
        sys.exit(1)
    elif args.webcam:
        enroll_from_webcam(args.id, args.name)
    elif args.image:
        enroll_from_image(args.id, args.name, args.image)
    else:
        print("[ERROR] Provide --image or --webcam")
        parser.print_help()
        sys.exit(1)
