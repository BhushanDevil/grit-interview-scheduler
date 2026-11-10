#!/usr/bin/env python3
"""
Flask Web Application for GRIT Interview Scheduler
Implements:
- Student View (including Prompt 5 "After Result" Dynamic States: Passed, Retake, Nullified)
- Interviewer View (Prompt 3: Manage Availability, Daily Queue, Outcomes)
- Admin View (Prompt 4: Dashboard Metrics, Student Cohort Table, Flag Malpractice)
"""

import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session

from db import (
    get_db_connection,
    init_db,
    seed_db,
    get_all_users,
    get_user_by_id,
    get_all_slots,
    get_available_slots,
    get_interviewer_slots,
    get_slot_by_id,
    add_interviewer_slot,
    delete_interviewer_slot,
    lock_slot,
    unlock_slot,
    create_booking,
    get_all_bookings,
    get_student_eligibility,
    get_student_booking,
    get_interviewer_queue,
    submit_evaluation,
    get_admin_dashboard_metrics,
    get_all_students_for_admin,
    flag_malpractice,
    restore_student_eligibility,
    SUCCESS_BANNER_MESSAGE,
    PASSED_EXACT_MESSAGE,
    RETAKE_EXACT_MESSAGE,
    NULLIFIED_EXACT_MESSAGE
)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "grit-scheduler-secret-key-linear-notion"

# Ensure database exists
DB_FILE = Path(__file__).resolve().parent / "grit_scheduler.db"
if not DB_FILE.exists():
    init_db()
    seed_db()


@app.route("/")
def index():
    return render_template("index.html")


# ================= USER & AUTH ROUTES =================
@app.route("/api/users", methods=["GET"])
def api_users():
    conn = get_db_connection()
    try:
        users = get_all_users(conn)
        return jsonify({"users": users})
    finally:
        conn.close()


@app.route("/api/current-user", methods=["GET", "POST"])
def api_current_user():
    conn = get_db_connection()
    try:
        if request.method == "POST":
            data = request.get_json() or {}
            user_id = data.get("user_id")
            user = get_user_by_id(conn, user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            return jsonify({"user": user})

        # GET current user
        user_id = session.get("user_id")
        user = None
        if user_id:
            user = get_user_by_id(conn, user_id)
        
        # Default to first Student (Alex Rivera, ID: 5)
        if not user:
            student = conn.execute("SELECT * FROM Users WHERE role = 'Student' ORDER BY id ASC LIMIT 1").fetchone()
            if student:
                user = dict(student)
                session["user_id"] = user["id"]
                session["role"] = user["role"]

        return jsonify({"user": user})
    finally:
        conn.close()


# ================= STUDENT VIEW ROUTES (PROMPT 2 & 5) =================
@app.route("/api/student/<int:student_id>/dashboard", methods=["GET"])
def api_student_dashboard(student_id):
    conn = get_db_connection()
    try:
        student = get_user_by_id(conn, student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404

        eligibilities = get_student_eligibility(conn, student_id)
        booking = get_student_booking(conn, student_id)
        available_slots = get_available_slots(conn)

        # Primary track for badge interview
        primary_track = next((e for e in eligibilities if e["track_name"] == "AI Engineering Track"), None)
        if not primary_track and eligibilities:
            primary_track = eligibilities[0]

        has_retake = False
        if booking and booking.get("outcome") == "Retake":
            has_retake = True

        return jsonify({
            "student": student,
            "primary_track": primary_track,
            "eligibilities": eligibilities,
            "booking": booking,
            "has_retake": has_retake,
            "available_slots": available_slots,
            "exact_messages": {
                "success_banner": SUCCESS_BANNER_MESSAGE,
                "passed": PASSED_EXACT_MESSAGE,
                "retake": RETAKE_EXACT_MESSAGE,
                "nullified": NULLIFIED_EXACT_MESSAGE
            }
        })
    finally:
        conn.close()


# ================= INTERVIEWER VIEW ROUTES (PROMPT 3 & ITEM #5) =================
@app.route("/api/interviewer/<int:interviewer_id>/dashboard", methods=["GET"])
def api_interviewer_dashboard(interviewer_id):
    conn = get_db_connection()
    try:
        interviewer = get_user_by_id(conn, interviewer_id)
        if not interviewer:
            return jsonify({"error": "Interviewer not found"}), 404

        slots = get_interviewer_slots(conn, interviewer_id)
        queue = get_interviewer_queue(conn, interviewer_id)
        cohort = get_all_students_for_admin(conn)

        unbooked_count = len([s for s in cohort if s["status"] == "Eligible"])
        booked_count = len([s for s in cohort if s["status"] == "Scheduled"])

        return jsonify({
            "interviewer": interviewer,
            "slots": slots,
            "queue": queue,
            "cohort": cohort,
            "stats": {
                "total_slots": len(slots),
                "available_slots": len([s for s in slots if s["status"] == "Available"]),
                "locked_slots": len([s for s in slots if s["status"] == "Locked"]),
                "booked_slots": len([s for s in slots if s["status"] == "Booked"]),
                "pending_evaluations": len([q for q in queue if q["outcome"] == "Pending"]),
                "completed_evaluations": len([q for q in queue if q["outcome"] != "Pending"]),
                "unbooked_students": unbooked_count,
                "booked_students": booked_count,
                "total_students": len(cohort)
            }
        })
    finally:
        conn.close()


@app.route("/api/interviewer/<int:interviewer_id>/queue", methods=["GET"])
def api_interviewer_queue(interviewer_id):
    conn = get_db_connection()
    try:
        queue = get_interviewer_queue(conn, interviewer_id)
        return jsonify({"queue": queue})
    finally:
        conn.close()


@app.route("/api/interviewer/cohort", methods=["GET"])
def api_interviewer_cohort():
    """Item #5: Interview team view of which eligible students have booked and which haven't."""
    conn = get_db_connection()
    try:
        cohort = get_all_students_for_admin(conn)
        return jsonify({"cohort": cohort})
    finally:
        conn.close()


# ================= ADMIN VIEW ROUTES (PROMPT 4) =================
@app.route("/api/admin/dashboard", methods=["GET"])
def api_admin_dashboard():
    conn = get_db_connection()
    try:
        metrics = get_admin_dashboard_metrics(conn)
        students = get_all_students_for_admin(conn)
        return jsonify({
            "metrics": metrics,
            "students": students
        })
    finally:
        conn.close()


@app.route("/api/admin/flag-malpractice", methods=["POST"])
def api_flag_malpractice():
    """
    Prompt 4: Highly visible Flag Malpractice action.
    Updates the student's Track_Eligibility status to 'Nullified'.
    """
    data = request.get_json() or {}
    student_id = data.get("student_id")

    if not student_id:
        return jsonify({"error": "student_id is required"}), 400

    conn = get_db_connection()
    try:
        success, result = flag_malpractice(conn, student_id)
        if not success:
            return jsonify(result), 400

        return jsonify({
            "success": True,
            "data": result,
            "message": result["message"]
        }), 200
    finally:
        conn.close()


@app.route("/api/admin/restore-student", methods=["POST"])
def api_restore_student():
    """Admin utility to unflag/restore student eligibility back to 'Eligible'."""
    data = request.get_json() or {}
    student_id = data.get("student_id")

    if not student_id:
        return jsonify({"error": "student_id is required"}), 400

    conn = get_db_connection()
    try:
        success, result = restore_student_eligibility(conn, student_id)
        return jsonify({"success": True, "data": result}), 200
    finally:
        conn.close()


# ================= SLOTS ROUTES (MANAGE AVAILABILITY) =================
@app.route("/api/slots", methods=["GET", "POST"])
def api_slots():
    conn = get_db_connection()
    try:
        if request.method == "POST":
            data = request.get_json() or {}
            interviewer_id = data.get("interviewer_id")
            start_time = data.get("start_time")

            if not interviewer_id or not start_time:
                return jsonify({"error": "interviewer_id and start_time are required"}), 400

            success, result = add_interviewer_slot(conn, interviewer_id, start_time)
            if not success:
                return jsonify(result), 400

            return jsonify({"success": True, "slot": result}), 201

        status = request.args.get("status")
        interviewer_id = request.args.get("interviewer_id")
        if status == "Available":
            slots = get_available_slots(conn)
        elif interviewer_id:
            slots = get_interviewer_slots(conn, int(interviewer_id))
        else:
            slots = get_all_slots(conn)
        return jsonify({"slots": slots})
    finally:
        conn.close()


@app.route("/api/slots/<int:slot_id>", methods=["DELETE"])
def api_delete_slot(slot_id):
    interviewer_id = request.args.get("interviewer_id", type=int)
    if not interviewer_id:
        return jsonify({"error": "interviewer_id required"}), 400

    conn = get_db_connection()
    try:
        success, message = delete_interviewer_slot(conn, slot_id, interviewer_id)
        if not success:
            return jsonify({"error": message}), 400
        return jsonify({"success": True, "message": message})
    finally:
        conn.close()


@app.route("/api/slots/<int:slot_id>/lock", methods=["POST"])
def api_lock_slot(slot_id):
    conn = get_db_connection()
    try:
        success, message = lock_slot(conn, slot_id)
        if not success:
            return jsonify({"error": message}), 400
        slot = get_slot_by_id(conn, slot_id)
        return jsonify({
            "success": True, 
            "message": message,
            "slot": slot
        })
    finally:
        conn.close()


@app.route("/api/slots/<int:slot_id>/unlock", methods=["POST"])
def api_unlock_slot(slot_id):
    conn = get_db_connection()
    try:
        success, message = unlock_slot(conn, slot_id)
        if not success:
            return jsonify({"error": message}), 400
        slot = get_slot_by_id(conn, slot_id)
        return jsonify({
            "success": True, 
            "message": message,
            "slot": slot
        })
    finally:
        conn.close()


# ================= BOOKINGS & OUTCOMES EVALUATION =================
@app.route("/api/bookings", methods=["GET", "POST"])
def api_bookings():
    conn = get_db_connection()
    try:
        if request.method == "POST":
            data = request.get_json() or {}
            slot_id = data.get("slot_id")
            student_id = data.get("student_id")
            track_name = data.get("track_name", "AI Engineering Track")

            if not slot_id or not student_id:
                return jsonify({"error": "slot_id and student_id are required"}), 400

            success, result = create_booking(conn, slot_id, student_id, track_name)
            if not success:
                return jsonify(result), 400

            return jsonify({
                "success": True,
                "booking": result,
                "message": result["message"]
            }), 201

        bookings = get_all_bookings(conn)
        return jsonify({"bookings": bookings})
    finally:
        conn.close()


@app.route("/api/bookings/<int:booking_id>/evaluation", methods=["POST"])
def api_submit_evaluation(booking_id):
    """
    Submits evaluation outcome (Pass, Fail, Retake) and feedback.
    Crucially updates Track_Eligibility status to:
      - Pass   -> Passed
      - Fail   -> Failed
      - Retake -> Eligible
    """
    data = request.get_json() or {}
    outcome = data.get("outcome")
    feedback = data.get("feedback", "")

    if not outcome:
        return jsonify({"error": "Outcome is required (Pass, Fail, Retake)"}), 400

    conn = get_db_connection()
    try:
        success, result = submit_evaluation(conn, booking_id, outcome, feedback)
        if not success:
            return jsonify(result), 400

        return jsonify({
            "success": True,
            "evaluation": result,
            "message": result["message"]
        }), 200
    finally:
        conn.close()


@app.route("/api/reset-data", methods=["POST"])
def api_reset_data():
    """Utility endpoint to re-seed initial dummy data for testing."""
    init_db()
    seed_db()
    return jsonify({"success": True, "message": "Database reset to initial test data."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
