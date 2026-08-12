"""
intruder.py — Module 4: Intruder Detection

Detects unrecognized faces using OpenCV Haar Cascades
via the shared camera module.
"""

import time
import threading
import random
import os
from datetime import datetime

import cv2
import numpy as np

import database as db

_running = False
_callback = None

import time
import cv2
import database as db
CASCADE_PATH = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

CONSECUTIVE_THRESHOLD = 10
SNAPSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshots")
COOLDOWN = 60
MATCH_THRESHOLD = 0.55


def _extract_features(gray_face):
    resized = cv2.resize(gray_face, (100, 100))
    return (resized.astype(np.float32) / 255.0).flatten()


def _compare_faces(enc1, enc2):
    a = np.array(enc1, dtype=np.float32)
    b = np.array(enc2, dtype=np.float32)
    if len(a) != len(b) or len(a) == 0:
        return 0.0
    a_norm = a - np.mean(a)
    b_norm = b - np.mean(b)
    denom = np.linalg.norm(a_norm) * np.linalg.norm(b_norm)
    if denom == 0:
        return 0.0
    return float(np.dot(a_norm, b_norm) / denom)


def _save_snapshot(frame, face_rect):
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"intruder_{timestamp}.jpg"
    filepath = os.path.join(SNAPSHOT_DIR, filename)
    x, y, w, h = face_rect
    pad = 40
    fh, fw = frame.shape[:2]
    y1, x1 = max(0, y-pad), max(0, x-pad)
    y2, x2 = min(fh, y+h+pad), min(fw, x+w+pad)
    cv2.imwrite(filepath, frame[y1:y2, x1:x2])
    return filename


def run_intruder(callback=None):
    """Run intruder detection using the shared camera."""
    global _running, _callback
    _running = True
    _callback = callback

    import camera

    students = db.get_all_students()
    known_encodings = [np.array(s["encoding"], dtype=np.float32) for s in students]

    print(f"[intruder] Monitoring for unauthorized access ({len(students)} known)...")
    unknown_counter = 0
    last_alert_time = 0

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

            is_unknown = True
            if len(known_encodings) > 0:
                for known_enc in known_encodings:
                    if _compare_faces(face_encoding, known_enc) > MATCH_THRESHOLD:
                        is_unknown = False
                        break

            if is_unknown:
                unknown_counter += 1
                if unknown_counter >= CONSECUTIVE_THRESHOLD:
                    now = time.time()
                    if now - last_alert_time >= COOLDOWN:
                        last_alert_time = now
                        unknown_counter = 0
                        snapshot = _save_snapshot(frame, (x, y, w, h))
                        db.log_intruder(snapshot)
                        event = {
                            "type": "intruder",
                            "snapshot": snapshot,
                            "timestamp": datetime.now().isoformat()
                        }
                        print(f"  [intruder] ⚠ INTRUDER DETECTED! Snapshot: {snapshot}")
                        if _callback:
                            _callback(event)
            else:
                unknown_counter = max(0, unknown_counter - 1)

        time.sleep(0.5)


def simulate_intruder(callback=None, interval=25):
    """Simulate intruder detection events."""
    global _running
    _running = True
    print("[intruder-sim] Simulating intruder detection...")
    while _running:
        if random.random() < 0.4:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot = f"intruder_sim_{timestamp}.jpg"
            db.log_intruder(snapshot)
            event = {"type": "intruder", "snapshot": snapshot, "timestamp": datetime.now().isoformat()}
            print(f"  [intruder-sim] ⚠ Simulated intruder alert")
            if callback:
                callback(event)
        time.sleep(interval + random.uniform(-5, 10))


def stop():
    global _running
    _running = False
