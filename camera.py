"""
camera.py — Shared camera capture for all Campus Vision modules.

Opens the webcam ONCE and distributes frames to all registered consumers.
Solves the Windows limitation of only one process/thread holding the camera.
"""

import threading
import time
import cv2
import numpy as np

_lock = threading.Lock()
_frame = None
_cap = None
_running = False
_thread = None
_camera_index = 0


def start(camera_index=0):
    """Start the shared camera capture thread."""
    global _cap, _running, _thread, _camera_index
    _camera_index = camera_index

    if _running:
        return True

    _cap = cv2.VideoCapture(camera_index)
    if not _cap.isOpened():
        print(f"[camera] ERROR: Cannot open webcam (index {camera_index})")
        return False

    # Set reasonable resolution
    _cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    _cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    _running = True
    _thread = threading.Thread(target=_capture_loop, daemon=True, name="shared-camera")
    _thread.start()

    w = int(_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(_cap.get(cv2.CAP_PROP_FPS))
    print(f"[camera] Webcam opened: {w}x{h} @ {fps}fps (index {camera_index})")
    return True


def _capture_loop():
    """Continuously capture frames from the webcam."""
    global _frame, _running
    while _running:
        ret, frame = _cap.read()
        if ret:
            with _lock:
                _frame = frame.copy()
        else:
            time.sleep(0.01)
        time.sleep(0.016)  # ~60fps max capture rate


def get_frame():
    """Get the latest frame. Returns None if no frame available."""
    with _lock:
        if _frame is not None:
            return _frame.copy()
    return None


def is_running():
    """Check if the camera is active."""
    return _running


def stop():
    """Stop the shared camera."""
    global _running, _cap
    _running = False
    if _cap is not None:
        _cap.release()
        _cap = None
    print("[camera] Webcam released.")
