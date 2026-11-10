#!/usr/bin/env python3
"""
CLI Seed Script for GRIT Interview Scheduler
Populates the SQLite database with required dummy data.
"""

import sys
from db import init_db, seed_db, get_db_connection, get_all_users, get_all_eligibility, get_all_slots


def run():
    print("Initializing database schema...")
    init_db()
    print("✓ Schema initialized successfully.")

    print("\nSeeding dummy data...")
    seed_db()
    print("✓ Dummy data seeded successfully.")

    conn = get_db_connection()
    try:
        users = get_all_users(conn)
        eligibility = get_all_eligibility(conn)
        slots = get_all_slots(conn)

        print("\n" + "=" * 60)
        print("DATABASE SUMMARY REPORT")
        print("=" * 60)

        print(f"\n[Users] Total: {len(users)}")
        print(f"{'ID':<4} | {'Name':<20} | {'Email':<26} | {'Role':<12}")
        print("-" * 68)
        for u in users:
            print(f"{u['id']:<4} | {u['name']:<20} | {u['email']:<26} | {u['role']:<12}")

        print(f"\n[Track Eligibility] Total: {len(eligibility)}")
        print(f"{'ID':<4} | {'Student Name':<20} | {'Track Name':<22} | {'Status':<12}")
        print("-" * 68)
        for e in eligibility:
            print(f"{e['id']:<4} | {e['student_name']:<20} | {e['track_name']:<22} | {e['status']:<12}")

        print(f"\n[Interviewer Slots] Total: {len(slots)}")
        print(f"{'ID':<4} | {'Interviewer':<20} | {'Start Time':<22} | {'Status':<12}")
        print("-" * 68)
        for s in slots:
            print(f"{s['id']:<4} | {s['interviewer_name']:<20} | {s['start_time']:<22} | {s['status']:<12}")

        print("=" * 60 + "\n")

    finally:
        conn.close()


if __name__ == "__main__":
    run()
