"""
database.py — Shared SQLite layer used by every Campus Vision module.
Auto-creates the database and all required tables on first import.
"""

import sqlite3
import os
import json
import threading
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "campus.db")

_local = threading.local()


def _get_conn():
    """Return a thread-local SQLite connection."""
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.execute("PRAGMA foreign_keys=ON")
    return _local.conn


def init_db():
    """Create all tables if they don't exist."""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            encoding    TEXT NOT NULL,
            enrolled_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS attendance (
            rowid       INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT NOT NULL,
            student_name TEXT NOT NULL,
            timestamp   TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            confidence  REAL DEFAULT 0.0,
            FOREIGN KEY (student_id) REFERENCES students(id)
        );

        CREATE TABLE IF NOT EXISTS attention_logs (
            rowid         INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp     TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            total_faces   INTEGER DEFAULT 0,
            attentive     INTEGER DEFAULT 0,
            distracted    INTEGER DEFAULT 0,
            attention_pct REAL DEFAULT 0.0
        );

        CREATE TABLE IF NOT EXISTS occupancy_logs (
            rowid       INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            room        TEXT DEFAULT 'main',
            count       INTEGER DEFAULT 0,
            capacity    INTEGER DEFAULT 60
        );

        CREATE TABLE IF NOT EXISTS intruder_events (
            rowid       INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            snapshot    TEXT,
            resolved    INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS fire_events (
            rowid       INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            event_type  TEXT DEFAULT 'fire',
            confidence  REAL DEFAULT 0.0,
            severity    TEXT DEFAULT 'low',
            resolved    INTEGER DEFAULT 0
        );
    """)
    conn.commit()


# ─── Student helpers ─────────────────────────────────────────────────────────

def add_student(student_id: str, name: str, encoding: list):
    """Enroll a student with their face encoding."""
    conn = _get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO students (id, name, encoding) VALUES (?, ?, ?)",
        (student_id, name, json.dumps(encoding))
    )
    conn.commit()


def get_all_students():
    """Return list of dicts with id, name, encoding (as list)."""
    conn = _get_conn()
    rows = conn.execute("SELECT id, name, encoding FROM students").fetchall()
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "name": r["name"],
            "encoding": json.loads(r["encoding"])
        })
    return result


def get_student_count():
    conn = _get_conn()
    return conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]


# ─── Attendance helpers ──────────────────────────────────────────────────────

def log_attendance(student_id: str, student_name: str, confidence: float = 0.0):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO attendance (student_id, student_name, confidence) VALUES (?, ?, ?)",
        (student_id, student_name, confidence)
    )
    conn.commit()


def get_attendance_today():
    conn = _get_conn()
    today = date.today().isoformat()
    rows = conn.execute(
        "SELECT student_id, student_name, timestamp, confidence FROM attendance "
        "WHERE date(timestamp) = ? ORDER BY timestamp DESC",
        (today,)
    ).fetchall()
    return [dict(r) for r in rows]


def get_attendance_range(start_date: str, end_date: str):
    conn = _get_conn()
    rows = conn.execute(
        "SELECT student_id, student_name, timestamp, confidence FROM attendance "
        "WHERE date(timestamp) BETWEEN ? AND ? ORDER BY timestamp DESC",
        (start_date, end_date)
    ).fetchall()
    return [dict(r) for r in rows]


def get_attendance_count_today():
    conn = _get_conn()
    today = date.today().isoformat()
    return conn.execute(
        "SELECT COUNT(DISTINCT student_id) FROM attendance WHERE date(timestamp) = ?",
        (today,)
    ).fetchone()[0]


# ─── Attention helpers ───────────────────────────────────────────────────────

def log_attention(total_faces: int, attentive: int, distracted: int, attention_pct: float):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO attention_logs (total_faces, attentive, distracted, attention_pct) "
        "VALUES (?, ?, ?, ?)",
        (total_faces, attentive, distracted, attention_pct)
    )
    conn.commit()


def get_latest_attention():
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM attention_logs ORDER BY rowid DESC LIMIT 1"
    ).fetchone()
    return dict(row) if row else {
        "total_faces": 0, "attentive": 0, "distracted": 0, "attention_pct": 0.0
    }


def get_attention_history(limit=50):
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM attention_logs ORDER BY rowid DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(r) for r in rows]


# ─── Occupancy helpers ───────────────────────────────────────────────────────

def log_occupancy(room: str, count: int, capacity: int = 60):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO occupancy_logs (room, count, capacity) VALUES (?, ?, ?)",
        (room, count, capacity)
    )
    conn.commit()


def get_latest_occupancy(room: str = "main"):
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM occupancy_logs WHERE room = ? ORDER BY rowid DESC LIMIT 1",
        (room,)
    ).fetchone()
    return dict(row) if row else {"room": room, "count": 0, "capacity": 60}


def get_occupancy_history(room: str = "main", limit=50):
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM occupancy_logs WHERE room = ? ORDER BY rowid DESC LIMIT ?",
        (room, limit)
    ).fetchall()
    return [dict(r) for r in rows]


# ─── Intruder helpers ────────────────────────────────────────────────────────

def log_intruder(snapshot_path: str = None):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO intruder_events (snapshot) VALUES (?)",
        (snapshot_path,)
    )
    conn.commit()


def get_intruder_events(limit=20):
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM intruder_events ORDER BY rowid DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(r) for r in rows]


def get_intruder_count_today():
    conn = _get_conn()
    today = date.today().isoformat()
    return conn.execute(
        "SELECT COUNT(*) FROM intruder_events WHERE date(timestamp) = ?",
        (today,)
    ).fetchone()[0]


# ─── Fire/Smoke helpers ──────────────────────────────────────────────────────

def log_fire(event_type: str = "fire", confidence: float = 0.0, severity: str = "low"):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO fire_events (event_type, confidence, severity) VALUES (?, ?, ?)",
        (event_type, confidence, severity)
    )
    conn.commit()


def get_fire_events(limit=20):
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM fire_events ORDER BY rowid DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(r) for r in rows]


def get_fire_count_today():
    conn = _get_conn()
    today = date.today().isoformat()
    return conn.execute(
        "SELECT COUNT(*) FROM fire_events WHERE date(timestamp) = ?",
        (today,)
    ).fetchone()[0]


# Auto-initialize on import
init_db()
