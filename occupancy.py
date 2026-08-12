"""
occupancy.py — Module 3: Classroom Occupancy Monitoring

Uses OpenCV HOG person detector to count people in frame.
Uses the shared camera module.
"""

import time
import threading
import random
import math
import os
from datetime import datetime

import cv2
import numpy as np

import database as db

_running = False
_callback = None

LOG_INTERVAL = 5
DEFAULT_CAPACITY = 60


def run_occupancy(room="main", capacity=DEFAULT_CAPACITY, callback=None):
    """Run occupancy monitoring using the shared camera."""
    global _running, _callback
    _running = True
    _callback = callback

    import camera

    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    print(f"[occupancy] Monitoring room '{room}' (capacity: {capacity})...")
    last_log = time.time()

    while _running:
        frame = camera.get_frame()
        if frame is None or frame.size == 0 or len(frame.shape) < 2:
            time.sleep(0.1)
            continue

        # Resize for faster detection
        small = cv2.resize(frame, (320, 240))
        boxes, _ = hog.detectMultiScale(small, winStride=(8, 8), padding=(4, 4), scale=1.05)
        count = len(boxes)

        now = time.time()
        if now - last_log >= LOG_INTERVAL:
            last_log = now
            db.log_occupancy(room, count, capacity)
            event = {
                "type": "occupancy",
                "room": room,
                "count": count,
                "capacity": capacity,
                "percentage": round(count / capacity * 100, 1) if capacity > 0 else 0,
                "timestamp": datetime.now().isoformat()
            }
            print(f"  [occupancy] {count}/{capacity} people ({event['percentage']}%)")
            if _callback:
                _callback(event)

        time.sleep(0.8)  # Check every 800ms


def simulate_occupancy(room="main", capacity=DEFAULT_CAPACITY, callback=None, interval=5):
    """Simulate occupancy data for demo/testing."""
    global _running
    _running = True
    print(f"[occupancy-sim] Simulating occupancy for room '{room}'...")
    count = random.randint(20, 40)
    t = 0
    while _running:
        delta = random.randint(-3, 3)
        wave = int(math.sin(t * 0.15) * 5)
        count = max(5, min(capacity, count + delta + wave))
        db.log_occupancy(room, count, capacity)
        event = {
            "type": "occupancy",
            "room": room,
            "count": count,
            "capacity": capacity,
            "percentage": round(count / capacity * 100, 1),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  [occupancy-sim] {count}/{capacity} people ({event['percentage']}%)")
        if callback:
            callback(event)
        t += 1
        time.sleep(interval + random.uniform(-1, 2))


def stop():
    global _running
    _running = False
