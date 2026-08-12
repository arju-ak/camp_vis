"""
attendance.py — Module 1: Face Recognition Attendance

Detects faces via shared webcam using OpenCV Haar Cascades,
matches against enrolled students using histogram comparison,
and logs attendance.
"""

import time
import threading
import random
import os
from datetime import datetime

import numpy as np
import cv2
import database as db

# Load Haar cascade
CASCADE_PATH = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

DUPLICATE_WINDOW = 300
MATCH_THRESHOLD = 0.65

_recent_checkins = {}
_running = False
_callback = None


def _extract_features(gray_face):
    resized = cv2.resize(gray_face, (100, 100))
    return (resized.astype(np.float32) / 255.0).flatten()


def _compare_faces(encoding1, encoding2):
    a = np.array(encoding1, dtype=np.float32)
    b = np.array(encoding2, dtype=np.float32)
    if len(a) != len(b) or len(a) == 0:
        return 0.0
    a_norm = a - np.mean(a)
    b_norm = b - np.mean(b)
    denom = np.linalg.norm(a_norm) * np.linalg.norm(b_norm)
    if denom == 0:
        return 0.0
    return float(np.dot(a_norm, b_norm) / denom)


def _can_checkin(student_id: str) -> bool:
    if student_id not in _recent_checkins:
        return True
    return (time.time() - _recent_checkins[student_id]) > DUPLICATE_WINDOW


def run_attendance(callback=None):
    """Run attendance detection using the shared camera."""
    global _running, _callback
    _running = True
    _callback = callback

    import camera

    students = db.get_all_students()
    if not students:
        print("[attendance] No students enrolled. Use --simulate or enroll first.")
        _running = False
        return

    known_encodings = [np.array(s["encoding"], dtype=np.float32) for s in students]
    known_ids = [s["id"] for s in students]
    known_names = [s["name"] for s in students]

    print(f"[attendance] Running face recognition ({len(students)} enrolled)...")

    while _running:
        frame = camera.get_frame()
        if frame is None or frame.size == 0 or len(frame.shape) < 2:
            time.sleep(0.1)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(60, 60))

        for (x, y, w, h) in faces:
            face_crop = gray[y:y+h, x:x+w]
            face_encoding = _extract_features(face_crop)

            best_match = -1
            best_idx = -1
            for i, known_enc in enumerate(known_encodings):
                similarity = _compare_faces(face_encoding, known_enc)
                if similarity > best_match:
                    best_match = similarity
                    best_idx = i

            if best_match > MATCH_THRESHOLD and best_idx >= 0:
                sid = known_ids[best_idx]
                sname = known_names[best_idx]
                if _can_checkin(sid):
                    _recent_checkins[sid] = time.time()
                    confidence = round(best_match, 3)
                    db.log_attendance(sid, sname, confidence)
                    event = {
                        "type": "attendance",
                        "student_id": sid,
                        "student_name": sname,
                        "confidence": confidence,
                        "timestamp": datetime.now().isoformat()
                    }
                    print(f"  [attendance] ✓ {sname} ({sid}) — {confidence:.1%}")
                    if _callback:
                        _callback(event)

        time.sleep(0.5)  # Check every 500ms


def simulate_attendance(callback=None, interval=8):
    """Simulate attendance events for demo/testing."""
    global _running
    _running = True

    from enroll import enroll_demo_students
    enroll_demo_students()

    students = db.get_all_students()
    if not students:
        print("[attendance-sim] No students to simulate.")
        return

    print(f"[attendance-sim] Simulating attendance for {len(students)} students...")

    while _running:
        student = random.choice(students)
        sid, sname = student["id"], student["name"]
        if _can_checkin(sid):
            confidence = round(random.uniform(0.72, 0.98), 3)
            _recent_checkins[sid] = time.time()
            db.log_attendance(sid, sname, confidence)
            event = {
                "type": "attendance",
                "student_id": sid,
                "student_name": sname,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat()
            }
            print(f"  [attendance-sim] ✓ {sname} ({sid}) — {confidence:.1%}")
            if callback:
                callback(event)
        time.sleep(interval + random.uniform(-2, 4))


def stop():
    global _running
    _running = False
