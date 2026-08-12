"""
fire_smoke.py — Module 5: Fire & Smoke Detection

Uses color-based heuristic detection (or YOLOv8 if weights available).
Uses the shared camera module.
"""

import time
import threading
import random
import os
from datetime import datetime

import cv2
import numpy as np

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

import database as db

_running = False
_callback = None

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "fire_smoke.pt")
CONFIDENCE_THRESHOLD = 0.5


def _severity_from_confidence(confidence):
    if confidence > 0.85: return "critical"
    elif confidence > 0.65: return "high"
    elif confidence > 0.45: return "medium"
    return "low"


def run_fire_smoke(callback=None):
    """Run fire/smoke detection using the shared camera."""
    global _running, _callback
    _running = True
    _callback = callback

    import camera

    model = None
    if YOLO_AVAILABLE and os.path.exists(MODEL_PATH):
        try:
            model = YOLO(MODEL_PATH)
            print("[fire_smoke] Using YOLOv8 model.")
        except Exception as e:
            print(f"[fire_smoke] YOLO failed: {e}")

    if model is None:
        print("[fire_smoke] Using color-based fire detection fallback.")

    print("[fire_smoke] Monitoring for fire/smoke...")

    while _running:
        frame = camera.get_frame()
        if frame is None or frame.size == 0 or len(frame.shape) < 2:
            time.sleep(0.1)
            continue

        detected = False
        event_type = "fire"
        confidence = 0.0

        if model is None:
            # Color-based detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_fire = np.array([0, 120, 200])
            upper_fire = np.array([25, 255, 255])
            mask = cv2.inRange(hsv, lower_fire, upper_fire)
            fire_pct = np.sum(mask > 0) / mask.size * 100
            if fire_pct > 5.0:
                detected = True
                confidence = min(fire_pct / 20.0, 1.0)
        else:
            results = model(frame, verbose=False)
            for r in results:
                for box in r.boxes:
                    conf = float(box.conf[0])
                    cls_name = model.names.get(int(box.cls[0]), "fire")
                    if conf > CONFIDENCE_THRESHOLD:
                        detected = True
                        confidence = max(confidence, conf)
                        event_type = cls_name.lower()

        if detected:
            severity = _severity_from_confidence(confidence)
            db.log_fire(event_type, round(confidence, 3), severity)
            event = {
                "type": "fire_smoke",
                "event_type": event_type,
                "confidence": round(confidence, 3),
                "severity": severity,
                "timestamp": datetime.now().isoformat()
            }
            print(f"  [fire_smoke] 🔥 {event_type.upper()} — {confidence:.1%} ({severity})")
            if _callback:
                _callback(event)

        time.sleep(1.0)  # Check every second


def simulate_fire_smoke(callback=None, interval=30):
    """Simulate fire/smoke events."""
    global _running
    _running = True
    print("[fire_smoke-sim] Simulating fire/smoke detection...")
    while _running:
        if random.random() < 0.3:
            event_type = random.choice(["fire", "smoke"])
            confidence = round(random.uniform(0.45, 0.95), 3)
            severity = _severity_from_confidence(confidence)
            db.log_fire(event_type, confidence, severity)
            event = {
                "type": "fire_smoke", "event_type": event_type,
                "confidence": confidence, "severity": severity,
                "timestamp": datetime.now().isoformat()
            }
            print(f"  [fire_smoke-sim] 🔥 {event_type} ({severity})")
            if callback:
                callback(event)
        time.sleep(interval + random.uniform(-10, 15))


def stop():
    global _running
    _running = False
