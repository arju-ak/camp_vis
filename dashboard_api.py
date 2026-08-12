"""
dashboard_api.py — Module 6: Flask API for the Campus Vision Dashboard

Serves as the single entry point. Launches all vision modules in background
threads and provides REST + WebSocket APIs for the frontend.

Usage:
    python dashboard_api.py              # Live mode (uses system webcam via camera.py)
    python dashboard_api.py --simulate   # Simulation mode (synthetic data)
"""

import os
import sys
import json
import argparse
import threading
from datetime import datetime, date

from flask import Flask, jsonify, request, send_from_directory, Response
from flask_cors import CORS
from flask_socketio import SocketIO

import cv2
import time
import database as db
import report
import attendance
import attention
import occupancy
import intruder
import fire_smoke
import camera

# ─── App setup ───────────────────────────────────────────────────────────────

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

SIMULATE = False


# ─── WebSocket event broadcaster ─────────────────────────────────────────────

def broadcast_event(event: dict):
    """Push a real-time event to all connected dashboard clients."""
    socketio.emit("vision_event", event)


# ─── REST API endpoints ──────────────────────────────────────────────────────

@app.route("/")
def serve_dashboard():
    """Serve the main dashboard HTML."""
    return send_from_directory("frontend", "index.html")


@app.route("/stats")
@app.route("/api/stats")
def api_stats():
    """Aggregate dashboard statistics."""
    att = db.get_latest_attention()
    occ = db.get_latest_occupancy()
    summary = report.get_attendance_summary()

    return jsonify({
        "attendance": {
            "total_enrolled": summary["total_enrolled"],
            "present_today": summary["present_today"],
            "absent_today": summary["absent_today"],
            "attendance_rate": summary["attendance_rate"]
        },
        "attention": {
            "total_faces": att["total_faces"],
            "attentive": att["attentive"],
            "distracted": att["distracted"],
            "attention_pct": att["attention_pct"]
        },
        "occupancy": {
            "room": occ["room"],
            "count": occ["count"],
            "capacity": occ["capacity"],
            "percentage": round(occ["count"] / occ["capacity"] * 100, 1) if occ["capacity"] > 0 else 0
        },
        "intruders": {
            "today": db.get_intruder_count_today()
        },
        "fire": {
            "today": db.get_fire_count_today()
        },
        "timestamp": datetime.now().isoformat(),
        "mode": "simulation" if SIMULATE else "live"
    })


@app.route("/api/attendance")
def api_attendance():
    """Today's attendance records."""
    records = db.get_attendance_today()
    return jsonify({
        "records": records,
        "count": len(records),
        "summary": report.get_attendance_summary()
    })


@app.route("/api/attention")
def api_attention():
    """Current and historical attention data."""
    latest = db.get_latest_attention()
    history = db.get_attention_history(30)
    return jsonify({
        "current": latest,
        "history": history
    })


@app.route("/api/occupancy")
def api_occupancy():
    """Current and historical occupancy data."""
    room = request.args.get("room", "main")
    latest = db.get_latest_occupancy(room)
    history = db.get_occupancy_history(room, 30)
    return jsonify({
        "current": latest,
        "history": history
    })


@app.route("/api/intruders")
def api_intruders():
    """Recent intruder events."""
    events = db.get_intruder_events(20)
    return jsonify({
        "events": events,
        "total_today": db.get_intruder_count_today()
    })


@app.route("/api/fire-events")
def api_fire_events():
    """Recent fire/smoke events."""
    events = db.get_fire_events(20)
    return jsonify({
        "events": events,
        "total_today": db.get_fire_count_today()
    })


@app.route("/api/report/csv")
def api_report_csv():
    """Download attendance as CSV."""
    start = request.args.get("start", date.today().isoformat())
    end = request.args.get("end", date.today().isoformat())
    sid = request.args.get("student_id", None)

    csv_data = report.generate_attendance_csv(start, end, sid)

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=attendance_{start}_{end}.csv"}
    )


@app.route("/api/students")
def api_students():
    """List enrolled students (without encodings)."""
    students = db.get_all_students()
    return jsonify({
        "students": [{"id": s["id"], "name": s["name"]} for s in students],
        "count": len(students)
    })

# ─── Video Stream ─────────────────────────────────────────────────────────────

def gen_frames():
    """Generate MJPEG video stream from shared camera."""
    while True:
        if SIMULATE:
            # Send a blank placeholder in simulation
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + b'\r\n')
            time.sleep(0.1)
            continue
            
        frame = camera.get_frame()
        if frame is not None:
            # Resize a bit for bandwidth
            small = cv2.resize(frame, (640, 480))
            ret, buffer = cv2.imencode('.jpg', small, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.01)

@app.route('/api/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# ─── Snapshot serving ─────────────────────────────────────────────────────────

@app.route("/snapshots/<filename>")
def serve_snapshot(filename):
    """Serve intruder snapshot images."""
    snap_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshots")
    return send_from_directory(snap_dir, filename)


# ─── Module launchers ─────────────────────────────────────────────────────────

def start_modules_live():
    """Start all vision modules with live shared webcam feed."""
    print("\n" + "=" * 60)
    print("  CAMPUS VISION AI — LIVE MODE")
    print("  Initializing shared webcam capture...")
    print("=" * 60 + "\n")

    if not camera.start(camera_index=0):
        print("[ERROR] Failed to start shared camera. Exiting live modules.")
        return []

    threads = [
        threading.Thread(target=attendance.run_attendance,
                        kwargs={"callback": broadcast_event},
                        daemon=True, name="attendance"),
        threading.Thread(target=attention.run_attention,
                        kwargs={"callback": broadcast_event},
                        daemon=True, name="attention"),
        threading.Thread(target=occupancy.run_occupancy,
                        kwargs={"callback": broadcast_event},
                        daemon=True, name="occupancy"),
        threading.Thread(target=intruder.run_intruder,
                        kwargs={"callback": broadcast_event},
                        daemon=True, name="intruder"),
        threading.Thread(target=fire_smoke.run_fire_smoke,
                        kwargs={"callback": broadcast_event},
                        daemon=True, name="fire_smoke"),
    ]

    for t in threads:
        t.start()
        print(f"  ✓ Started {t.name}")

    return threads


def start_modules_simulate():
    """Start all vision modules in simulation mode."""
    print("\n" + "=" * 60)
    print("  CAMPUS VISION AI — SIMULATION MODE")
    print("  Generating synthetic events for dashboard demo")
    print("=" * 60 + "\n")

    threads = [
        threading.Thread(target=attendance.simulate_attendance,
                        kwargs={"callback": broadcast_event, "interval": 8},
                        daemon=True, name="attendance-sim"),
        threading.Thread(target=attention.simulate_attention,
                        kwargs={"callback": broadcast_event, "interval": 4},
                        daemon=True, name="attention-sim"),
        threading.Thread(target=occupancy.simulate_occupancy,
                        kwargs={"callback": broadcast_event, "interval": 5},
                        daemon=True, name="occupancy-sim"),
        threading.Thread(target=intruder.simulate_intruder,
                        kwargs={"callback": broadcast_event, "interval": 25},
                        daemon=True, name="intruder-sim"),
        threading.Thread(target=fire_smoke.simulate_fire_smoke,
                        kwargs={"callback": broadcast_event, "interval": 30},
                        daemon=True, name="fire_smoke-sim"),
    ]

    for t in threads:
        t.start()
        print(f"  ✓ Started {t.name}")

    return threads


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Campus Vision AI Dashboard Server")
    parser.add_argument("--simulate", action="store_true",
                        help="Run in simulation mode (no webcam needed)")
    parser.add_argument("--port", type=int, default=5000, help="Server port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host")

    args = parser.parse_args()
    SIMULATE = args.simulate

    # Initialize database
    db.init_db()

    # Start vision modules
    if SIMULATE:
        start_modules_simulate()
    else:
        start_modules_live()

    print(f"\n  🌐 Dashboard: http://localhost:{args.port}")
    print(f"  📡 API:       http://localhost:{args.port}/api/stats")
    print(f"  📊 Mode:      {'Simulation' if SIMULATE else 'Live'}\n")

    try:
        # Run Flask with SocketIO
        socketio.run(app, host=args.host, port=args.port,
                     debug=False, allow_unsafe_werkzeug=True)
    finally:
        if not SIMULATE:
            camera.stop()
