"""
report.py — CSV export of attendance records.

Generates filterable CSV reports of attendance data.
Used by the dashboard API's /api/report/csv endpoint.
"""

import csv
import io
from datetime import date, datetime, timedelta

import database as db


def generate_attendance_csv(start_date=None, end_date=None, student_id=None):
    """
    Generate a CSV string of attendance records.

    Args:
        start_date: Start date filter (YYYY-MM-DD string)
        end_date: End date filter (YYYY-MM-DD string)
        student_id: Optional student ID filter

    Returns:
        CSV string
    """
    if not start_date:
        start_date = date.today().isoformat()
    if not end_date:
        end_date = date.today().isoformat()

    records = db.get_attendance_range(start_date, end_date)

    if student_id:
        records = [r for r in records if r["student_id"] == student_id]

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["Student ID", "Student Name", "Timestamp", "Confidence"])

    # Data rows
    for record in records:
        writer.writerow([
            record["student_id"],
            record["student_name"],
            record["timestamp"],
            record["confidence"]
        ])

    return output.getvalue()


def get_attendance_summary(target_date=None):
    """
    Get a summary of attendance for a given date.

    Returns:
        dict with total_enrolled, present_today, absent_today, attendance_rate
    """
    if not target_date:
        target_date = date.today().isoformat()

    total_enrolled = db.get_student_count()
    present_today = db.get_attendance_count_today()
    absent_today = max(0, total_enrolled - present_today)
    rate = (present_today / total_enrolled * 100) if total_enrolled > 0 else 0

    return {
        "date": target_date,
        "total_enrolled": total_enrolled,
        "present_today": present_today,
        "absent_today": absent_today,
        "attendance_rate": round(rate, 1)
    }


if __name__ == "__main__":
    # Quick test
    csv_data = generate_attendance_csv()
    print(csv_data)
    print(get_attendance_summary())
