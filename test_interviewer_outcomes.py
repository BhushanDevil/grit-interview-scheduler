"""
Automated Test Suite for Prompt 3: Interviewer Dashboard & Outcomes
Tests:
- Section 1: Adding Interviewer_Slots (defaults to 'Available')
- Section 2: Daily Queue retrieval for interviewer
- Submitting Evaluations:
  * Pass   -> updates booking outcome to 'Pass' and Track_Eligibility to 'Passed'
  * Fail   -> updates booking outcome to 'Fail' and Track_Eligibility to 'Failed'
  * Retake -> updates booking outcome to 'Retake' and Track_Eligibility back to 'Eligible'
"""

import unittest
from datetime import datetime, timedelta
from app import app
from db import init_db, seed_db, get_db_connection


class TestInterviewerDashboardAndOutcomes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_db()

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        self.interviewer_id = 2  # Dr. Marcus Rivera
        self.student_id = 3      # Alex Rivera

    def test_01_add_interviewer_slot_defaults_to_available(self):
        """Section 1: Test form submission to add new Interviewer_Slot, defaulting to Available."""
        tomorrow_str = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d 10:00:00")
        payload = {
            "interviewer_id": self.interviewer_id,
            "start_time": tomorrow_str
        }
        res = self.client.post('/api/slots', json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()

        self.assertTrue(data["success"])
        self.assertEqual(data["slot"]["status"], "Available")
        self.assertEqual(data["slot"]["interviewer_id"], self.interviewer_id)
        self.assertEqual(data["slot"]["start_time"], tomorrow_str)

        # Verify in database
        conn = get_db_connection()
        slot_db = conn.execute("SELECT * FROM Interviewer_Slots WHERE id = ?", (data["slot"]["id"],)).fetchone()
        self.assertIsNotNone(slot_db)
        self.assertEqual(slot_db["status"], "Available")
        conn.close()

    def test_02_daily_queue_listing(self):
        """Section 2: Test daily queue retrieval showing student name, time, and booking info."""
        # 1. First ensure a booking exists for this interviewer
        # Get an available slot
        slots_res = self.client.get('/api/slots?status=Available')
        slots = slots_res.get_json()["slots"]
        self.assertGreater(len(slots), 0)
        target_slot_id = slots[0]["id"]

        # Book it for Alex Rivera
        book_res = self.client.post('/api/bookings', json={
            "slot_id": target_slot_id,
            "student_id": self.student_id,
            "track_name": "AI Engineering Track"
        })
        self.assertEqual(book_res.status_code, 201)

        # 2. Query interviewer queue
        queue_res = self.client.get(f'/api/interviewer/{self.interviewer_id}/queue')
        self.assertEqual(queue_res.status_code, 200)
        queue_data = queue_res.get_json()

        self.assertIn("queue", queue_data)
        self.assertGreater(len(queue_data["queue"]), 0)

        # Check candidate details in queue
        first_item = queue_data["queue"][0]
        self.assertEqual(first_item["student_name"], "Alex Rivera")
        self.assertEqual(first_item["outcome"], "Pending")
        self.assertIsNotNone(first_item["start_time"])

    def test_03_submit_evaluation_pass_updates_eligibility_to_passed(self):
        """
        Logic: On submit 'Pass':
        - Updates Interview_Bookings outcome to 'Pass'
        - Updates student's Track_Eligibility status to 'Passed'
        """
        # Find the active booking
        conn = get_db_connection()
        booking = conn.execute(
            "SELECT id, student_id FROM Interview_Bookings WHERE student_id = ? ORDER BY id DESC LIMIT 1",
            (self.student_id,)
        ).fetchone()
        conn.close()

        booking_id = booking["id"]

        eval_payload = {
            "outcome": "Pass",
            "feedback": "Outstanding architectural reasoning, clean code structure, and deep knowledge of distributed systems."
        }
        res = self.client.post(f'/api/bookings/{booking_id}/evaluation', json=eval_payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertTrue(data["success"])
        self.assertEqual(data["evaluation"]["outcome"], "Pass")
        self.assertEqual(data["evaluation"]["track_eligibility_status"], "Passed")

        # Verify DB directly
        conn = get_db_connection()
        b_row = conn.execute("SELECT outcome, feedback FROM Interview_Bookings WHERE id = ?", (booking_id,)).fetchone()
        self.assertEqual(b_row["outcome"], "Pass")
        self.assertIn("Outstanding architectural", b_row["feedback"])

        te_row = conn.execute(
            "SELECT status FROM Track_Eligibility WHERE student_id = ? AND track_name = 'AI Engineering Track'",
            (self.student_id,)
        ).fetchone()
        self.assertEqual(te_row["status"], "Passed")
        conn.close()

    def test_04_submit_evaluation_fail_updates_eligibility_to_failed(self):
        """
        Logic: On submit 'Fail':
        - Updates Interview_Bookings outcome to 'Fail'
        - Updates student's Track_Eligibility status to 'Failed'
        """
        # Create a second booking with Bianca Chen (student ID 4)
        student_2_id = 4
        slots_res = self.client.get('/api/slots?status=Available')
        target_slot_id = slots_res.get_json()["slots"][0]["id"]

        self.client.post('/api/bookings', json={
            "slot_id": target_slot_id,
            "student_id": student_2_id,
            "track_name": "AI Engineering Track"
        })

        conn = get_db_connection()
        booking = conn.execute(
            "SELECT id FROM Interview_Bookings WHERE student_id = ? ORDER BY id DESC LIMIT 1",
            (student_2_id,)
        ).fetchone()
        conn.close()

        booking_id = booking["id"]

        eval_payload = {
            "outcome": "Fail",
            "feedback": "Candidate struggled with basic concurrency control and system failure handling."
        }
        res = self.client.post(f'/api/bookings/{booking_id}/evaluation', json=eval_payload)
        self.assertEqual(res.status_code, 200)

        # Verify DB directly
        conn = get_db_connection()
        b_row = conn.execute("SELECT outcome FROM Interview_Bookings WHERE id = ?", (booking_id,)).fetchone()
        self.assertEqual(b_row["outcome"], "Fail")

        te_row = conn.execute(
            "SELECT status FROM Track_Eligibility WHERE student_id = ? AND track_name = 'AI Engineering Track'",
            (student_2_id,)
        ).fetchone()
        self.assertEqual(te_row["status"], "Failed")
        conn.close()

    def test_05_submit_evaluation_retake_crucially_updates_eligibility_to_eligible(self):
        """
        Logic: On submit 'Retake':
        - Updates Interview_Bookings outcome to 'Retake'
        - CRUCIALLY updates student's Track_Eligibility status back to 'Eligible'
        """
        # Create a third booking with Devon Brooks (student ID 5)
        student_3_id = 5
        slots_res = self.client.get('/api/slots?status=Available')
        target_slot_id = slots_res.get_json()["slots"][0]["id"]

        self.client.post('/api/bookings', json={
            "slot_id": target_slot_id,
            "student_id": student_3_id,
            "track_name": "AI Engineering Track"
        })

        # Check before evaluation, status is 'Scheduled'
        conn = get_db_connection()
        te_before = conn.execute(
            "SELECT status FROM Track_Eligibility WHERE student_id = ? AND track_name = 'AI Engineering Track'",
            (student_3_id,)
        ).fetchone()
        self.assertEqual(te_before["status"], "Scheduled")

        booking = conn.execute(
            "SELECT id FROM Interview_Bookings WHERE student_id = ? ORDER BY id DESC LIMIT 1",
            (student_3_id,)
        ).fetchone()
        conn.close()

        booking_id = booking["id"]

        eval_payload = {
            "outcome": "Retake",
            "feedback": "Strong foundational knowledge, but needs minor revision on API rate limiting. Eligible for immediate retake."
        }
        res = self.client.post(f'/api/bookings/{booking_id}/evaluation', json=eval_payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["evaluation"]["outcome"], "Retake")
        self.assertEqual(data["evaluation"]["track_eligibility_status"], "Eligible")

        # Verify DB directly
        conn = get_db_connection()
        b_row = conn.execute("SELECT outcome FROM Interview_Bookings WHERE id = ?", (booking_id,)).fetchone()
        self.assertEqual(b_row["outcome"], "Retake")

        te_row = conn.execute(
            "SELECT status FROM Track_Eligibility WHERE student_id = ? AND track_name = 'AI Engineering Track'",
            (student_3_id,)
        ).fetchone()
        self.assertEqual(te_row["status"], "Eligible", "Crucial test: Retake must set status back to 'Eligible'")
        conn.close()


if __name__ == "__main__":
    unittest.main()
