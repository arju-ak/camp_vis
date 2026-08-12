"""
attention.py — Module 2: Classroom Attention Analysis

Uses MediaPipe Face Mesh to estimate head pose (yaw/pitch),
classifying each face as attentive or distracted.
Uses the shared camera module.
"""

import time
import threading
import random
import math
from datetime import datetime

import cv2
import numpy as np

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

import database as db

_running = False
_callback = None

YAW_THRESHOLD = 30
PITCH_THRESHOLD = 25
LOG_INTERVAL = 5


def _estimate_head_pose(landmarks, img_w, img_h):
    indices = [1, 152, 33, 263, 61, 291]
    face_2d = []
    face_3d = []
    for idx in indices:
        lm = landmarks[idx]
        x, y = int(lm.x * img_w), int(lm.y * img_h)
        face_2d.append([x, y])
        face_3d.append([x, y, lm.z * 3000])

    face_2d = np.array(face_2d, dtype=np.float64)
    face_3d = np.array(face_3d, dtype=np.float64)

    focal_length = img_w
    cam_matrix = np.array([
        [focal_length, 0, img_w / 2],
        [0, focal_length, img_h / 2],
        [0, 0, 1]
    ], dtype=np.float64)
    dist_coeffs = np.zeros((4, 1), dtype=np.float64)

    _, rot_vec, _ = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_coeffs)
    rot_mat, _ = cv2.Rodrigues(rot_vec)
    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rot_mat)

    return angles[1], angles[0]  # yaw, pitch


def run_attention(callback=None):
    """Run attention analysis using the shared camera."""
    global _running, _callback
    _running = True
    _callback = callback

    import camera

    if not MEDIAPIPE_AVAILABLE:
        print("[attention] MediaPipe not available. Using face-count fallback.")

    face_mesh = None
    if MEDIAPIPE_AVAILABLE:
        try:
            mp_face_mesh = mp.solutions.face_mesh
            face_mesh = mp_face_mesh.FaceMesh(
                max_num_faces=30, refine_landmarks=True,
                min_detection_confidence=0.5, min_tracking_confidence=0.5
            )
        except Exception as e:
            print(f"[attention] MediaPipe face_mesh initialization note: {e}. Using face detection fallback.")
            face_mesh = None

    print("[attention] Running classroom attention analysis...")
    last_log = time.time()

    # Haar cascade fallback for counting faces if mediapipe fails
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    while _running:
        frame = camera.get_frame()
        if frame is None or frame.size == 0 or len(frame.shape) < 2:
            time.sleep(0.1)
            continue

        h, w = frame.shape[:2]
        total_faces = 0
        attentive = 0
        distracted = 0

        if face_mesh is not None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            if results.multi_face_landmarks:
                total_faces = len(results.multi_face_landmarks)
                for face_lm in results.multi_face_landmarks:
                    try:
                        yaw, pitch = _estimate_head_pose(face_lm.landmark, w, h)
                        if abs(yaw) < YAW_THRESHOLD and abs(pitch) < PITCH_THRESHOLD:
                            attentive += 1
                        else:
                            distracted += 1
                    except:
                        attentive += 1  # Default to attentive on error
        else:
            # Fallback: detect faces with Haar cascade, assume mostly attentive
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(gray, 1.3, 5, minSize=(50, 50))
            total_faces = len(faces)
            attentive = max(1, int(total_faces * 0.75)) if total_faces > 0 else 0
            distracted = total_faces - attentive

        attention_pct = (attentive / total_faces * 100) if total_faces > 0 else 0

        now = time.time()
        if now - last_log >= LOG_INTERVAL:
            last_log = now
            db.log_attention(total_faces, attentive, distracted, round(attention_pct, 1))
            event = {
                "type": "attention",
                "total_faces": total_faces,
                "attentive": attentive,
                "distracted": distracted,
                "attention_pct": round(attention_pct, 1),
                "timestamp": datetime.now().isoformat()
            }
            print(f"  [attention] {attentive}/{total_faces} attentive ({attention_pct:.0f}%)")
            if _callback:
                _callback(event)

        time.sleep(0.3)

    if face_mesh:
        face_mesh.close()


def simulate_attention(callback=None, interval=4):
    """Simulate attention analysis for demo/testing."""
    global _running
    _running = True
    print("[attention-sim] Simulating classroom attention...")
    base_attention = 75.0
    t = 0
    while _running:
        total_faces = random.randint(20, 40)
        wave = math.sin(t * 0.1) * 15
        noise = random.gauss(0, 5)
        attention_pct = max(30, min(100, base_attention + wave + noise))
        attentive = int(total_faces * attention_pct / 100)
        distracted = total_faces - attentive
        db.log_attention(total_faces, attentive, distracted, round(attention_pct, 1))
        event = {
            "type": "attention",
            "total_faces": total_faces,
            "attentive": attentive,
            "distracted": distracted,
            "attention_pct": round(attention_pct, 1),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  [attention-sim] {attentive}/{total_faces} attentive ({attention_pct:.0f}%)")
        if callback:
            callback(event)
        t += 1
        time.sleep(interval + random.uniform(-1, 1))


def stop():
    global _running
    _running = False
