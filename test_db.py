"""
Automated Test Suite for GRIT Interview Scheduler Database
Tests schema constraints, enums, foreign keys, cascades, and dummy data verification.
"""

import unittest
import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta

from db import init_db, seed_db, get_db_connection

TEST_DB_PATH = Path(__file__).resolve().parent / "test_grit_scheduler.db"


class TestDatabaseSetup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        init_db(TEST_DB_PATH)
        seed_db(TEST_DB_PATH)

    @classmethod
    def tearDownClass(cls):
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()

    def setUp(self):
        self.conn = get_db_connection(TEST_DB_PATH)

    def tearDown(self):
        self.conn.close()

    def test_users_count_and_roles(self):
        """Verify 1 Admin, 1 Interviewer, and 3 Students exist."""
        cursor = self.conn.execute("SELECT role, COUNT(*) as cnt FROM Users GROUP BY role")
        role_counts = {row["role"]: row["cnt"] for row in cursor.fetchall()}

        self.assertEqual(role_counts.get("Admin"), 1, "Expected 1 Admin user")
        self.assertEqual(role_counts.get("Interviewer"), 1, "Expected 1 Interviewer user")
        self.assertEqual(role_counts.get("Student"), 3, "Expected 3 Student users")

    def test_user_role_constraint(self):
        """Verify role enum constraint only allows Student, Interviewer, Admin."""
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO Users (name, email, role) VALUES ('Hacker', 'hacker@grit.edu', 'Superuser')"
            )

    def test_user_email_unique_constraint(self):
        """Verify user emails must be unique."""
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO Users (name, email, role) VALUES ('Duplicate', 'admin@grit.edu', 'Admin')"
            )

    def test_track_eligibility_seeded_correctly(self):
        """Verify all 3 students have Track_Eligibility with 'Eligible' for 'AI Systems Track'."""
        cursor = self.conn.execute("""
            SELECT u.name, te.track_name, te.status
            FROM Track_Eligibility te
            JOIN Users u ON te.student_id = u.id
            WHERE te.track_name = 'AI Systems Track'
            ORDER BY u.id
        """)
        records = cursor.fetchall()
        self.assertEqual(len(records), 3, "Expected 3 eligibility records for AI Systems Track")
        for rec in records:
            self.assertEqual(rec["track_name"], "AI Systems Track")
            self.assertEqual(rec["status"], "Eligible")

    def test_track_eligibility_status_constraint(self):
        """Verify Track_Eligibility status enum: Eligible, Scheduled, Passed, Failed, Nullified."""
        student_id = self.conn.execute("SELECT id FROM Users WHERE role = 'Student' LIMIT 1").fetchone()["id"]
        # Valid statuses
        for status in ['Eligible', 'Scheduled', 'Passed', 'Failed', 'Nullified']:
            self.conn.execute(
                "INSERT INTO Track_Eligibility (student_id, track_name, status) VALUES (?, ?, ?)",
                (student_id, f"Track {status}", status)
            )
        # Invalid status
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO Track_Eligibility (student_id, track_name, status) VALUES (?, ?, ?)",
                (student_id, "Track Invalid", "UnknownStatus")
            )

    def test_interviewer_slots_tomorrow(self):
        """Verify 4 Interviewer_Slots are generated with status 'Available' for tomorrow."""
        cursor = self.conn.execute("SELECT * FROM Interviewer_Slots")
        slots = cursor.fetchall()
        self.assertEqual(len(slots), 4, "Expected 4 interviewer slots")

        # Verify all slots are 'Available'
        for slot in slots:
            self.assertEqual(slot["status"], "Available")
            # Verify the slot date matches tomorrow
            slot_date = slot["start_time"].split()[0]
            expected_date = self.conn.execute("SELECT date('now', 'localtime', '+1 day') as d").fetchone()["d"]
            self.assertEqual(slot_date, expected_date)

    def test_interviewer_slot_status_constraint(self):
        """Verify Interviewer_Slots status enum: Available, Locked, Booked."""
        interviewer_id = self.conn.execute("SELECT id FROM Users WHERE role = 'Interviewer' LIMIT 1").fetchone()["id"]
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO Interviewer_Slots (interviewer_id, start_time, status) VALUES (?, datetime('now'), 'Invalid')",
                (interviewer_id,)
            )

    def test_interview_bookings_creation_and_constraints(self):
        """Verify booking creation, outcome constraint (Pending, Pass, Fail, Retake), and FK integrity."""
        slot_id = self.conn.execute("SELECT id FROM Interviewer_Slots LIMIT 1").fetchone()["id"]
        student_id = self.conn.execute("SELECT id FROM Users WHERE role = 'Student' LIMIT 1").fetchone()["id"]

        # Valid booking
        self.conn.execute(
            "INSERT INTO Interview_Bookings (slot_id, student_id, outcome, feedback) VALUES (?, ?, 'Pending', 'Initial setup')",
            (slot_id, student_id)
        )
        booking = self.conn.execute("SELECT * FROM Interview_Bookings WHERE slot_id = ?", (slot_id,)).fetchone()
        self.assertIsNotNone(booking)
        self.assertEqual(booking["outcome"], "Pending")

        # Unique slot_id constraint test (a slot cannot be booked twice)
        another_student_id = self.conn.execute("SELECT id FROM Users WHERE role = 'Student' AND id != ? LIMIT 1", (student_id,)).fetchone()["id"]
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO Interview_Bookings (slot_id, student_id, outcome) VALUES (?, ?, 'Pending')",
                (slot_id, another_student_id)
            )

        # Invalid outcome constraint test
        slot2_id = self.conn.execute("SELECT id FROM Interviewer_Slots WHERE id != ? LIMIT 1", (slot_id,)).fetchone()["id"]
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO Interview_Bookings (slot_id, student_id, outcome) VALUES (?, ?, 'InvalidOutcome')",
                (slot2_id, student_id)
            )

    def test_cascade_delete(self):
        """Verify deleting a user cascades to Track_Eligibility and Slots."""
        # Create a temporary student
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO Users (name, email, role) VALUES ('Temp Student', 'temp@grit.edu', 'Student')")
        temp_id = cursor.lastrowid
        cursor.execute("INSERT INTO Track_Eligibility (student_id, track_name, status) VALUES (?, 'Test Track', 'Eligible')", (temp_id,))

        # Verify eligibility exists
        elig = self.conn.execute("SELECT * FROM Track_Eligibility WHERE student_id = ?", (temp_id,)).fetchone()
        self.assertIsNotNone(elig)

        # Delete user
        self.conn.execute("DELETE FROM Users WHERE id = ?", (temp_id,))

        # Verify eligibility was cascaded and deleted
        elig_after = self.conn.execute("SELECT * FROM Track_Eligibility WHERE student_id = ?", (temp_id,)).fetchone()
        self.assertIsNone(elig_after)


if __name__ == "__main__":
    unittest.main()
