"""
Database connection and helper utilities for GRIT Interview Scheduler.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "grit_scheduler.db"
SCHEMA_FILE = BASE_DIR / "schema.sql"
SEED_FILE = BASE_DIR / "seed.sql"

SUCCESS_BANNER_MESSAGE = (
    "You’re booked! Your AI Engineering Track Interview is confirmed for "
    "Thursday, Nov 14 at 4:30 PM IST. A calendar invitation with your "
    "meeting link has been sent to your email. Please join 5 minutes early "
    "with your camera and workspace ready."
)

PASSED_EXACT_MESSAGE = (
    "Congratulations! You have passed your Track Badge Interview. "
    "Your GRIT AI Systems Track Badge has been unlocked and verified on your "
    "public profile. [View Your Badge & Certificate]"
)

RETAKE_EXACT_MESSAGE = (
    "Interview Outcome: Retake Required. Your interviewer has requested a retake on "
    "core architecture concepts. Your rebooking window will open on Nov 21, 2026 "
    "(7-day preparation window). Review your feedback notes here: [View Detailed Notes]."
)

NULLIFIED_EXACT_MESSAGE = (
    "Badge Nullified: Violation of academic integrity detected. "
    "All credentials have been revoked."
)

# Outcome mapping to Track_Eligibility status
OUTCOME_TO_ELIGIBILITY_STATUS = {
    "Pass": "Passed",
    "Fail": "Failed",
    "Retake": "Eligible"
}


def get_db_connection(db_path: Optional[Path | str] = None) -> sqlite3.Connection:
    """Returns a SQLite connection with row_factory enabled and foreign keys enforced."""
    target_path = str(db_path if db_path is not None else DB_FILE)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[Path | str] = None) -> None:
    """Initializes the database schema using schema.sql."""
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_db_connection(db_path)
    with conn:
        conn.executescript(schema_sql)
    conn.close()


def seed_db(db_path: Optional[Path | str] = None) -> None:
    """Populates the database with initial dummy seed data using seed.sql."""
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        seed_sql = f.read()

    conn = get_db_connection(db_path)
    with conn:
        conn.executescript(seed_sql)
    conn.close()


# User helpers
def get_all_users(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cursor = conn.execute("SELECT id, name, email, role, created_at FROM Users ORDER BY id ASC;")
    return [dict(row) for row in cursor.fetchall()]


def get_user_by_id(conn: sqlite3.Connection, user_id: int) -> Optional[Dict[str, Any]]:
    cursor = conn.execute("SELECT id, name, email, role, created_at FROM Users WHERE id = ?;", (user_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


# Eligibility helpers
def get_student_eligibility(conn: sqlite3.Connection, student_id: int) -> List[Dict[str, Any]]:
    query = """
    SELECT id, student_id, track_name, status, created_at, updated_at
    FROM Track_Eligibility
    WHERE student_id = ?
    ORDER BY id ASC;
    """
    cursor = conn.execute(query, (student_id,))
    return [dict(row) for row in cursor.fetchall()]


def get_all_eligibility(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    query = """
    SELECT 
        te.id,
        te.student_id,
        u.name AS student_name,
        u.email AS student_email,
        te.track_name,
        te.status,
        te.created_at,
        te.updated_at
    FROM Track_Eligibility te
    JOIN Users u ON te.student_id = u.id
    ORDER BY te.id ASC;
    """
    cursor = conn.execute(query)
    return [dict(row) for row in cursor.fetchall()]


# Slot helpers
def get_all_slots(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    query = """
    SELECT 
        s.id,
        s.interviewer_id,
        u.name AS interviewer_name,
        u.email AS interviewer_email,
        s.start_time,
        s.status,
        s.created_at
    FROM Interviewer_Slots s
    JOIN Users u ON s.interviewer_id = u.id
    ORDER BY s.start_time ASC;
    """
    cursor = conn.execute(query)
    return [dict(row) for row in cursor.fetchall()]


def get_available_slots(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    query = """
    SELECT 
        s.id,
        s.interviewer_id,
        u.name AS interviewer_name,
        u.email AS interviewer_email,
        s.start_time,
        s.status,
        s.created_at
    FROM Interviewer_Slots s
    JOIN Users u ON s.interviewer_id = u.id
    WHERE s.status = 'Available'
    ORDER BY s.start_time ASC;
    """
    cursor = conn.execute(query)
    return [dict(row) for row in cursor.fetchall()]


def get_interviewer_slots(conn: sqlite3.Connection, interviewer_id: int) -> List[Dict[str, Any]]:
    query = """
    SELECT 
        s.id,
        s.interviewer_id,
        s.start_time,
        s.status,
        s.created_at,
        b.id AS booking_id,
        u_stu.name AS student_name
    FROM Interviewer_Slots s
    LEFT JOIN Interview_Bookings b ON s.id = b.slot_id
    LEFT JOIN Users u_stu ON b.student_id = u_stu.id
    WHERE s.interviewer_id = ?
    ORDER BY s.start_time ASC;
    """
    cursor = conn.execute(query, (interviewer_id,))
    return [dict(row) for row in cursor.fetchall()]


def get_slot_by_id(conn: sqlite3.Connection, slot_id: int) -> Optional[Dict[str, Any]]:
    query = """
    SELECT 
        s.id,
        s.interviewer_id,
        u.name AS interviewer_name,
        u.email AS interviewer_email,
        s.start_time,
        s.status,
        s.created_at
    FROM Interviewer_Slots s
    JOIN Users u ON s.interviewer_id = u.id
    WHERE s.id = ?;
    """
    cursor = conn.execute(query, (slot_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def add_interviewer_slot(conn: sqlite3.Connection, interviewer_id: int, start_time: str) -> Tuple[bool, Dict[str, Any]]:
    """Adds a new Interviewer_Slots record, defaulting status to 'Available'."""
    with conn:
        user = conn.execute("SELECT id, role FROM Users WHERE id = ?;", (interviewer_id,)).fetchone()
        if not user:
            return False, {"error": "Interviewer user not found."}
        if user["role"] != "Interviewer":
            return False, {"error": "User does not have Interviewer role."}

        cursor = conn.execute(
            """
            INSERT INTO Interviewer_Slots (interviewer_id, start_time, status)
            VALUES (?, ?, 'Available');
            """,
            (interviewer_id, start_time)
        )
        slot_id = cursor.lastrowid
        slot = conn.execute("SELECT * FROM Interviewer_Slots WHERE id = ?;", (slot_id,)).fetchone()
        return True, dict(slot)


def delete_interviewer_slot(conn: sqlite3.Connection, slot_id: int, interviewer_id: int) -> Tuple[bool, str]:
    """Deletes an interviewer slot if it is Available (cannot delete Booked slots)."""
    with conn:
        slot = conn.execute("SELECT * FROM Interviewer_Slots WHERE id = ? AND interviewer_id = ?;", (slot_id, interviewer_id)).fetchone()
        if not slot:
            return False, "Slot not found or unauthorized."
        if slot["status"] == "Booked":
            return False, "Cannot delete a slot that is already booked."
        
        conn.execute("DELETE FROM Interviewer_Slots WHERE id = ?;", (slot_id,))
        return True, "Slot deleted successfully."


def lock_slot(conn: sqlite3.Connection, slot_id: int) -> Tuple[bool, str]:
    """Locks a slot to simulate a booking hold."""
    with conn:
        cursor = conn.execute("SELECT status FROM Interviewer_Slots WHERE id = ?;", (slot_id,))
        row = cursor.fetchone()
        if not row:
            return False, "Slot not found."
        if row["status"] != "Available":
            return False, f"Slot cannot be locked because it is currently '{row['status']}'."
        
        conn.execute("UPDATE Interviewer_Slots SET status = 'Locked' WHERE id = ?;", (slot_id,))
    return True, "Slot successfully locked for booking hold."


def unlock_slot(conn: sqlite3.Connection, slot_id: int) -> Tuple[bool, str]:
    """Releases a locked slot back to Available if hold is canceled or expires."""
    with conn:
        cursor = conn.execute("SELECT status FROM Interviewer_Slots WHERE id = ?;", (slot_id,))
        row = cursor.fetchone()
        if not row:
            return False, "Slot not found."
        if row["status"] != "Locked":
            return False, f"Slot is not currently Locked (status: {row['status']})."
        
        conn.execute("UPDATE Interviewer_Slots SET status = 'Available' WHERE id = ?;", (slot_id,))
    return True, "Slot hold released back to Available."


# Booking helpers
def create_booking(
    conn: sqlite3.Connection, 
    slot_id: int, 
    student_id: int, 
    track_name: str = "AI Engineering Track"
) -> Tuple[bool, Dict[str, Any]]:
    """
    Creates an Interview_Bookings record, sets slot status to 'Booked',
    and updates the Student's Track_Eligibility status to 'Scheduled' in one transaction.
    """
    with conn:
        # 1. Verify student exists and is eligible
        student = conn.execute("SELECT id, name, email, role FROM Users WHERE id = ?;", (student_id,)).fetchone()
        if not student:
            return False, {"error": "Student user not found."}
        if student["role"] != "Student":
            return False, {"error": "User is not a student."}

        # Check track eligibility (cannot book if Nullified)
        eligibility = conn.execute(
            """
            SELECT id, status FROM Track_Eligibility 
            WHERE student_id = ? AND (track_name = ? OR track_name LIKE 'AI%')
            ORDER BY id ASC LIMIT 1;
            """,
            (student_id, track_name)
        ).fetchone()

        if not eligibility:
            return False, {"error": f"Student has no eligibility record for track '{track_name}'."}

        if eligibility["status"] == "Nullified":
            return False, {"error": "Action blocked: Student badge credentials have been Nullified due to malpractice."}

        # 2. Verify slot
        slot = conn.execute("SELECT id, interviewer_id, start_time, status FROM Interviewer_Slots WHERE id = ?;", (slot_id,)).fetchone()
        if not slot:
            return False, {"error": "Slot not found."}
        if slot["status"] not in ("Available", "Locked"):
            return False, {"error": f"Slot is not available for booking (status: {slot['status']})."}

        # 3. Insert Interview_Bookings record
        cursor = conn.execute(
            """
            INSERT INTO Interview_Bookings (slot_id, student_id, outcome, feedback)
            VALUES (?, ?, 'Pending', 'Awaiting badge interview evaluation.');
            """,
            (slot_id, student_id)
        )
        booking_id = cursor.lastrowid

        # 4. Update Slot status to 'Booked'
        conn.execute("UPDATE Interviewer_Slots SET status = 'Booked' WHERE id = ?;", (slot_id,))

        # 5. Update Student's Track_Eligibility status to 'Scheduled'
        conn.execute(
            """
            UPDATE Track_Eligibility 
            SET status = 'Scheduled', updated_at = CURRENT_TIMESTAMP 
            WHERE student_id = ? AND (track_name = ? OR track_name LIKE 'AI%');
            """,
            (student_id, track_name)
        )

        return True, {
            "booking_id": booking_id,
            "slot_id": slot_id,
            "student_id": student_id,
            "student_name": student["name"],
            "start_time": slot["start_time"],
            "track_name": track_name,
            "outcome": "Pending",
            "message": SUCCESS_BANNER_MESSAGE
        }


def get_all_bookings(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    query = """
    SELECT 
        b.id,
        b.slot_id,
        s.start_time,
        b.student_id,
        u_stu.name AS student_name,
        u_stu.email AS student_email,
        s.interviewer_id,
        u_int.name AS interviewer_name,
        u_int.email AS interviewer_email,
        b.outcome,
        b.feedback,
        b.created_at,
        b.updated_at
    FROM Interview_Bookings b
    JOIN Interviewer_Slots s ON b.slot_id = s.id
    JOIN Users u_stu ON b.student_id = u_stu.id
    JOIN Users u_int ON s.interviewer_id = u_int.id
    ORDER BY s.start_time ASC;
    """
    cursor = conn.execute(query)
    return [dict(row) for row in cursor.fetchall()]


def get_student_booking(conn: sqlite3.Connection, student_id: int) -> Optional[Dict[str, Any]]:
    query = """
    SELECT 
        b.id,
        b.slot_id,
        s.start_time,
        b.student_id,
        u_stu.name AS student_name,
        u_stu.email AS student_email,
        s.interviewer_id,
        u_int.name AS interviewer_name,
        u_int.email AS interviewer_email,
        b.outcome,
        b.feedback,
        b.created_at,
        b.updated_at
    FROM Interview_Bookings b
    JOIN Interviewer_Slots s ON b.slot_id = s.id
    JOIN Users u_stu ON b.student_id = u_stu.id
    JOIN Users u_int ON s.interviewer_id = u_int.id
    WHERE b.student_id = ?
    ORDER BY b.id DESC LIMIT 1;
    """
    cursor = conn.execute(query, (student_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


# Section 2: Interviewer Daily Queue & Outcome Submission
def get_interviewer_queue(conn: sqlite3.Connection, interviewer_id: int) -> List[Dict[str, Any]]:
    """Fetches Daily Queue of booked interviews for a specific interviewer."""
    query = """
    SELECT 
        b.id AS booking_id,
        b.slot_id,
        s.start_time,
        s.status AS slot_status,
        b.student_id,
        u_stu.name AS student_name,
        u_stu.email AS student_email,
        b.outcome,
        b.feedback,
        b.created_at AS booked_at,
        b.updated_at AS evaluated_at,
        te.track_name,
        te.status AS eligibility_status
    FROM Interview_Bookings b
    JOIN Interviewer_Slots s ON b.slot_id = s.id
    JOIN Users u_stu ON b.student_id = u_stu.id
    LEFT JOIN Track_Eligibility te ON te.student_id = b.student_id AND (te.track_name = 'AI Engineering Track' OR te.track_name LIKE 'AI%')
    WHERE s.interviewer_id = ?
    ORDER BY s.start_time ASC;
    """
    cursor = conn.execute(query, (interviewer_id,))
    return [dict(row) for row in cursor.fetchall()]


def submit_evaluation(
    conn: sqlite3.Connection,
    booking_id: int,
    outcome: str,
    feedback: str
) -> Tuple[bool, Dict[str, Any]]:
    """
    Submits an evaluation outcome (Pass, Fail, Retake) and feedback for an interview booking.
    Crucially updates the student's Track_Eligibility status to match:
      - Pass   -> Passed
      - Fail   -> Failed
      - Retake -> Eligible
    """
    if outcome not in OUTCOME_TO_ELIGIBILITY_STATUS:
        valid_options = list(OUTCOME_TO_ELIGIBILITY_STATUS.keys())
        return False, {"error": f"Invalid outcome '{outcome}'. Must be one of {valid_options}."}

    new_eligibility_status = OUTCOME_TO_ELIGIBILITY_STATUS[outcome]

    with conn:
        booking = conn.execute(
            """
            SELECT b.id, b.student_id, b.slot_id, u.name AS student_name, u.email AS student_email
            FROM Interview_Bookings b
            JOIN Users u ON b.student_id = u.id
            WHERE b.id = ?;
            """,
            (booking_id,)
        ).fetchone()

        if not booking:
            return False, {"error": "Booking record not found."}

        student_id = booking["student_id"]

        # 1. Update Interview_Bookings outcome and feedback
        conn.execute(
            """
            UPDATE Interview_Bookings
            SET outcome = ?, feedback = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (outcome, feedback, booking_id)
        )

        # 2. Crucially update student's Track_Eligibility status
        conn.execute(
            """
            UPDATE Track_Eligibility
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE student_id = ? AND (track_name = 'AI Engineering Track' OR track_name LIKE 'AI%');
            """,
            (new_eligibility_status, student_id)
        )

        return True, {
            "booking_id": booking_id,
            "student_id": student_id,
            "student_name": booking["student_name"],
            "outcome": outcome,
            "feedback": feedback,
            "track_eligibility_status": new_eligibility_status,
            "message": f"Evaluation submitted successfully. Candidate marked as '{outcome}' and track badge status updated to '{new_eligibility_status}'."
        }


# ==============================================================
# PROMPT 4: ADMIN DASHBOARD & MALPRACTICE HANDLING
# ==============================================================
def get_admin_dashboard_metrics(conn: sqlite3.Connection) -> Dict[str, int]:
    """
    Calculates dashboard metrics for the Admin view:
    - Total Eligible (Unbooked)
    - Total Scheduled
    - Total Passed
    - Total Failed
    - Total Nullified
    - Total Students
    """
    cursor = conn.execute("""
        SELECT 
            COUNT(DISTINCT CASE WHEN te.status = 'Eligible' THEN u.id END) AS total_eligible,
            COUNT(DISTINCT CASE WHEN te.status = 'Scheduled' THEN u.id END) AS total_scheduled,
            COUNT(DISTINCT CASE WHEN te.status = 'Passed' THEN u.id END) AS total_passed,
            COUNT(DISTINCT CASE WHEN te.status = 'Failed' THEN u.id END) AS total_failed,
            COUNT(DISTINCT CASE WHEN te.status = 'Nullified' THEN u.id END) AS total_nullified,
            COUNT(DISTINCT u.id) AS total_students
        FROM Users u
        LEFT JOIN Track_Eligibility te ON u.id = te.student_id AND (te.track_name = 'AI Engineering Track' OR te.track_name = 'AI Systems Track')
        WHERE u.role = 'Student';
    """)
    row = cursor.fetchone()
    return {
        "total_eligible_unbooked": row["total_eligible"] or 0,
        "total_scheduled": row["total_scheduled"] or 0,
        "total_passed": row["total_passed"] or 0,
        "total_failed": row["total_failed"] or 0,
        "total_nullified": row["total_nullified"] or 0,
        "total_students": row["total_students"] or 0,
    }


def get_all_students_for_admin(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Returns a list of all students, their track eligibility, and their latest booking outcome."""
    query = """
    SELECT 
        u.id AS student_id,
        u.name,
        u.email,
        u.created_at AS joined_at,
        te.id AS eligibility_id,
        COALESCE(te.track_name, 'AI Engineering Track') AS track_name,
        COALESCE(te.status, 'Eligible') AS status,
        te.updated_at AS status_updated_at,
        b.id AS booking_id,
        b.outcome AS booking_outcome,
        b.feedback AS booking_feedback,
        s.start_time AS slot_time,
        u_int.name AS interviewer_name
    FROM Users u
    LEFT JOIN Track_Eligibility te ON u.id = te.student_id AND (te.track_name = 'AI Engineering Track' OR te.track_name LIKE 'AI%')
    LEFT JOIN Interview_Bookings b ON u.id = b.student_id
    LEFT JOIN Interviewer_Slots s ON b.slot_id = s.id
    LEFT JOIN Users u_int ON s.interviewer_id = u_int.id
    WHERE u.role = 'Student'
    GROUP BY u.id
    ORDER BY u.id ASC;
    """
    cursor = conn.execute(query)
    return [dict(row) for row in cursor.fetchall()]


def flag_malpractice(conn: sqlite3.Connection, student_id: int) -> Tuple[bool, Dict[str, Any]]:
    """
    Admin Action: Flags academic malpractice on a student.
    Crucially updates that student's Track_Eligibility status to 'Nullified'.
    """
    with conn:
        student = conn.execute("SELECT id, name, email, role FROM Users WHERE id = ?;", (student_id,)).fetchone()
        if not student:
            return False, {"error": "Student user not found."}
        if student["role"] != "Student":
            return False, {"error": "Malpractice flags can only be applied to Student users."}

        # Update all eligibility records for this student to 'Nullified'
        conn.execute(
            """
            UPDATE Track_Eligibility
            SET status = 'Nullified', updated_at = CURRENT_TIMESTAMP
            WHERE student_id = ?;
            """,
            (student_id,)
        )

        return True, {
            "student_id": student_id,
            "student_name": student["name"],
            "status": "Nullified",
            "message": f"Academic malpractice recorded. Credentials and Track Eligibility for {student['name']} set to 'Nullified'."
        }


def restore_student_eligibility(conn: sqlite3.Connection, student_id: int) -> Tuple[bool, Dict[str, Any]]:
    """Admin utility to restore a student back to 'Eligible' if needed."""
    with conn:
        conn.execute(
            """
            UPDATE Track_Eligibility
            SET status = 'Eligible', updated_at = CURRENT_TIMESTAMP
            WHERE student_id = ?;
            """,
            (student_id,)
        )
        return True, {
            "student_id": student_id,
            "status": "Eligible",
            "message": "Student eligibility restored to 'Eligible'."
        }
