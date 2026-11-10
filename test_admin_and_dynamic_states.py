"""
Automated Test Suite for Prompt 4 (Admin Dashboard & Malpractice)
and Prompt 5 (Student After Result Dynamic States).
"""

import unittest
from app import app
from db import (
    init_db,
    seed_db,
    get_db_connection,
    PASSED_EXACT_MESSAGE,
    RETAKE_EXACT_MESSAGE,
    NULLIFIED_EXACT_MESSAGE
)


class TestAdminAndDynamicStates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_db()

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    # ================= PROMPT 4 TESTS =================
    def test_01_admin_metrics_and_student_table(self):
        """Prompt 4: Test metrics ('Total Eligible (Unbooked)' vs 'Total Scheduled') and student table."""
        res = self.client.get('/api/admin/dashboard')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        # Check metrics structure
        metrics = data["metrics"]
        self.assertIn("total_eligible_unbooked", metrics)
        self.assertIn("total_scheduled", metrics)
        self.assertEqual(metrics["total_eligible_unbooked"], 3)
        self.assertEqual(metrics["total_scheduled"], 0)

        # Check students list
        students = data["students"]
        self.assertEqual(len(students), 3)
        names = [s["name"] for s in students]
        self.assertIn("Alex Rivera", names)
        self.assertIn("Bianca Chen", names)
        self.assertIn("Devon Brooks", names)

    def test_02_flag_malpractice_updates_eligibility_to_nullified(self):
        """Prompt 4: Highly visible 'Flag Malpractice' button updates Track_Eligibility to 'Nullified'."""
        target_student_id = 4  # Bianca Chen

        # Flag malpractice
        res = self.client.post('/api/admin/flag-malpractice', json={"student_id": target_student_id})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "Nullified")

        # Verify directly in SQLite DB
        conn = get_db_connection()
        records = conn.execute(
            "SELECT status FROM Track_Eligibility WHERE student_id = ?",
            (target_student_id,)
        ).fetchall()
        self.assertGreater(len(records), 0)
        for r in records:
            self.assertEqual(r["status"], "Nullified")
        conn.close()

        # Verify updated metrics in admin dashboard
        dash_res = self.client.get('/api/admin/dashboard')
        metrics = dash_res.get_json()["metrics"]
        self.assertEqual(metrics["total_nullified"], 1)

    # ================= PROMPT 5 TESTS =================
    def test_03_prompt_5_passed_exact_message(self):
        """
        Prompt 5 Condition 1: If Status == 'Passed':
        Exact message:
        'Congratulations! You have passed your Track Badge Interview. Your GRIT AI Systems Track Badge has been unlocked and verified on your public profile. [View Your Badge & Certificate]'
        """
        student_id = 3  # Alex Rivera
        # Set status to Passed
        conn = get_db_connection()
        conn.execute("UPDATE Track_Eligibility SET status = 'Passed' WHERE student_id = ?", (student_id,))
        conn.commit()
        conn.close()

        res = self.client.get(f'/api/student/{student_id}/dashboard')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data["primary_track"]["status"], "Passed")
        self.assertEqual(
            data["exact_messages"]["passed"],
            "Congratulations! You have passed your Track Badge Interview. Your GRIT AI Systems Track Badge has been unlocked and verified on your public profile. [View Your Badge & Certificate]"
        )

    def test_04_prompt_5_retake_exact_message(self):
        """
        Prompt 5 Condition 2: If Status == 'Eligible' (after a Retake outcome):
        Exact message:
        'Interview Outcome: Retake Required. Your interviewer has requested a retake on core architecture concepts. Your rebooking window will open on Nov 21, 2026 (7-day preparation window). Review your feedback notes here: [View Detailed Notes].'
        """
        student_id = 5  # Devon Brooks

        # Book slot, submit evaluation as 'Retake'
        slots_res = self.client.get('/api/slots?status=Available')
        slot_id = slots_res.get_json()["slots"][0]["id"]
        book_res = self.client.post('/api/bookings', json={
            "slot_id": slot_id,
            "student_id": student_id,
            "track_name": "AI Engineering Track"
        })
        booking_id = book_res.get_json()["booking"]["booking_id"]

        eval_res = self.client.post(f'/api/bookings/{booking_id}/evaluation', json={
            "outcome": "Retake",
            "feedback": "Needs revision on core architecture concepts."
        })
        self.assertEqual(eval_res.status_code, 200)

        # Check student dashboard
        dash_res = self.client.get(f'/api/student/{student_id}/dashboard')
        data = dash_res.get_json()

        self.assertEqual(data["primary_track"]["status"], "Eligible")
        self.assertTrue(data["has_retake"])
        self.assertEqual(
            data["exact_messages"]["retake"],
            "Interview Outcome: Retake Required. Your interviewer has requested a retake on core architecture concepts. Your rebooking window will open on Nov 21, 2026 (7-day preparation window). Review your feedback notes here: [View Detailed Notes]."
        )

    def test_05_prompt_5_nullified_exact_message(self):
        """
        Prompt 5 Condition 3: If Status == 'Nullified':
        Exact message:
        'Badge Nullified: Violation of academic integrity detected. All credentials have been revoked.'
        """
        student_id = 4  # Bianca Chen (Nullified in test_02)
        res = self.client.get(f'/api/student/{student_id}/dashboard')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data["primary_track"]["status"], "Nullified")
        self.assertEqual(
            data["exact_messages"]["nullified"],
            "Badge Nullified: Violation of academic integrity detected. All credentials have been revoked."
        )


if __name__ == "__main__":
    unittest.main()
