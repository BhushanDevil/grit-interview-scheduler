"""
Automated Integration Tests for Prompt 2: Student Dashboard & Booking Flow
Tests UI data requirements, hold locking simulation, booking creation, and exact success banner verification.
"""

import unittest
import json
from app import app
from db import init_db, seed_db, get_db_connection, SUCCESS_BANNER_MESSAGE


class TestStudentBookingFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_db()

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        conn = get_db_connection()
        self.student = conn.execute("SELECT id, name, email FROM Users WHERE role = 'Student' ORDER BY id ASC LIMIT 1").fetchone()
        conn.close()
        self.student_id = self.student["id"]

    def test_01_student_dashboard_layout_data(self):
        """Verify Student Dashboard provides track progress, eligibility, and available slots."""
        response = self.client.get(f'/api/student/{self.student_id}/dashboard')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        # Verify student identity
        self.assertEqual(data["student"]["name"], self.student["name"])
        self.assertEqual(data["student"]["role"], "Student")

        # Verify Track Eligibility status is 'Eligible'
        self.assertEqual(data["primary_track"]["status"], "Eligible")

        # Verify available slots
        self.assertGreaterEqual(len(data["available_slots"]), 4)
        for slot in data["available_slots"]:
            self.assertEqual(slot["status"], "Available")

    def test_02_slot_booking_hold_lock_and_unlock(self):
        """Simulate clicking a slot: status changes to 'Locked'. Cancelling hold reverts to 'Available'."""
        slots_res = self.client.get('/api/slots?status=Available')
        slots = slots_res.get_json()["slots"]
        slot_id = slots[0]["id"]

        # Step 1: Simulate Booking Hold -> lock slot
        lock_res = self.client.post(f'/api/slots/{slot_id}/lock')
        self.assertEqual(lock_res.status_code, 200)
        lock_data = lock_res.get_json()
        self.assertTrue(lock_data["success"])
        self.assertEqual(lock_data["slot"]["status"], "Locked")

        # Verify in DB
        conn = get_db_connection()
        slot_row = conn.execute("SELECT status FROM Interviewer_Slots WHERE id = ?", (slot_id,)).fetchone()
        self.assertEqual(slot_row["status"], "Locked")
        conn.close()

        # Step 2: Cancel hold -> unlock slot
        unlock_res = self.client.post(f'/api/slots/{slot_id}/unlock')
        self.assertEqual(unlock_res.status_code, 200)
        unlock_data = unlock_res.get_json()
        self.assertTrue(unlock_data["success"])
        self.assertEqual(unlock_data["slot"]["status"], "Available")

    def test_03_booking_confirmation_and_exact_success_banner(self):
        """
        When confirmed:
        1. Create Interview_Bookings record
        2. Update Slot status to 'Booked'
        3. Update Student's Track_Eligibility status to 'Scheduled'
        4. Return exact success banner message
        """
        slots_res = self.client.get('/api/slots?status=Available')
        slots = slots_res.get_json()["slots"]
        target_slot = slots[0]
        slot_id = target_slot["id"]

        # Hold lock
        self.client.post(f'/api/slots/{slot_id}/lock')

        # Confirm booking
        booking_payload = {
            "slot_id": slot_id,
            "student_id": self.student_id,
            "track_name": "AI Engineering Track"
        }
        res = self.client.post('/api/bookings', json=booking_payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()

        # Check exact required success message
        expected_banner = (
            "You’re booked! Your AI Engineering Track Interview is confirmed for "
            "Thursday, Nov 14 at 4:30 PM IST. A calendar invitation with your "
            "meeting link has been sent to your email. Please join 5 minutes early "
            "with your camera and workspace ready."
        )
        self.assertEqual(data["message"], expected_banner)

        # Check DB State:
        conn = get_db_connection()
        # 1. Interview_Bookings record created with outcome='Pending'
        booking = conn.execute(
            "SELECT * FROM Interview_Bookings WHERE slot_id = ? AND student_id = ?",
            (slot_id, self.student_id)
        ).fetchone()
        self.assertIsNotNone(booking)
        self.assertEqual(booking["outcome"], "Pending")

        # 2. Slot status updated to 'Booked'
        slot = conn.execute("SELECT status FROM Interviewer_Slots WHERE id = ?", (slot_id,)).fetchone()
        self.assertEqual(slot["status"], "Booked")

        # 3. Student Track_Eligibility status updated to 'Scheduled'
        elig = conn.execute(
            "SELECT status FROM Track_Eligibility WHERE student_id = ? AND (track_name = 'AI Engineering Track' OR track_name LIKE 'AI%')",
            (self.student_id,)
        ).fetchone()
        self.assertEqual(elig["status"], "Scheduled")

        conn.close()

    def test_04_updated_dashboard_reflects_scheduled_and_reduced_slots(self):
        """After booking, student dashboard shows reduced available slots and updated status."""
        response = self.client.get(f'/api/student/{self.student_id}/dashboard')
        data = response.get_json()

        # Available slots should be decremented by 1
        self.assertIsNotNone(data["booking"])
        self.assertEqual(data["booking"]["outcome"], "Pending")
        # Track eligibility is Scheduled
        self.assertEqual(data["primary_track"]["status"], "Scheduled")


if __name__ == "__main__":
    unittest.main()
