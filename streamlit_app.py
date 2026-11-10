"""
GRIT Interview Scheduler - Streamlit Cloud Application
Deployable for FREE in 1-click on Streamlit Community Cloud (share.streamlit.io).
Supports Student, Interviewer, and Admin roles with relational SQLite data.
"""

import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path

from db import (
    get_db_connection,
    init_db,
    seed_db,
    get_all_users,
    get_user_by_id,
    get_available_slots,
    get_interviewer_slots,
    add_interviewer_slot,
    delete_interviewer_slot,
    lock_slot,
    unlock_slot,
    create_booking,
    get_student_booking,
    get_student_eligibility,
    get_interviewer_queue,
    submit_evaluation,
    get_admin_dashboard_metrics,
    get_all_students_for_admin,
    flag_malpractice,
    restore_student_eligibility,
    SUCCESS_BANNER_MESSAGE,
    PASSED_EXACT_MESSAGE,
    RETAKE_EXACT_MESSAGE,
    NULLIFIED_EXACT_MESSAGE,
    DB_FILE
)

# Page configuration
st.set_page_config(
    page_title="GRIT Interview Scheduler",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure database exists
if not DB_FILE.exists():
    init_db()
    seed_db()

# Custom CSS for Notion/Linear aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 1.25rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-eligible { background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }
    .badge-scheduled { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
    .badge-passed { background: #f0fdf4; color: #15803d; border: 1px solid #86efac; }
    .badge-failed { background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; }
    .badge-nullified { background: #ffe4e6; color: #9f1239; border: 1px solid #fda4af; }
    .nullified-container {
        background: linear-gradient(180deg, #4c0519 0%, #881337 100%);
        color: #ffffff;
        padding: 3rem;
        border-radius: 1rem;
        border: 2px solid #e11d48;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ================= SIDEBAR: ROLE SWITCHER & USER CONTEXT =================
st.sidebar.markdown("### 🎓 GRIT Scheduler")
st.sidebar.caption("Track Badge Interview Management")

conn = get_db_connection()
users = get_all_users(conn)
conn.close()

# Role Switcher
role = st.sidebar.radio(
    "Select View / Role:",
    ["Student", "Interviewer", "Admin"],
    index=0
)

st.sidebar.markdown("---")

# Active user selection
if role == "Student":
    students = [u for u in users if u["role"] == "Student"]
    student_opts = {f"{s['name']} ({s['email']})": s["id"] for s in students}
    selected_label = st.sidebar.selectbox("Active Student:", list(student_opts.keys()), index=0)
    current_student_id = student_opts[selected_label]
elif role == "Interviewer":
    interviewers = [u for u in users if u["role"] == "Interviewer"]
    int_opts = {f"{i['name']} ({i['email']})": i["id"] for i in interviewers}
    selected_label = st.sidebar.selectbox("Active Interviewer:", list(int_opts.keys()), index=0)
    current_interviewer_id = int_opts[selected_label]
else:
    admins = [u for u in users if u["role"] == "Admin"]
    admin_opts = {f"{a['name']} ({a['email']})": a["id"] for a in admins}
    selected_label = st.sidebar.selectbox("Active Admin:", list(admin_opts.keys()), index=0)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Initial Test Data"):
    init_db()
    seed_db()
    st.sidebar.success("Database reset to initial test data!")
    st.rerun()


# ==============================================================
# 1. STUDENT VIEW (PROMPTS 2 & 5)
# ==============================================================
if role == "Student":
    conn = get_db_connection()
    student = get_user_by_id(conn, current_student_id)
    eligibilities = get_student_eligibility(conn, current_student_id)
    booking = get_student_booking(conn, current_student_id)
    available_slots = get_available_slots(conn)
    conn.close()

    primary_track = eligibilities[0] if eligibilities else {"status": "Eligible", "track_name": "AI Engineering Track"}
    track_status = primary_track["status"]
    has_retake = (booking and booking.get("outcome") == "Retake")

    # ================= PROMPT 5 STATE 3: NULLIFIED OVERWRITE =================
    if track_status == "Nullified":
        st.markdown(f"""
        <div class="nullified-container">
            <h1 style="color:#ffffff; font-size: 2.2rem; margin-bottom: 1rem;">🛡️ Academic Integrity Lockout</h1>
            <h2 style="color:#fecdd3; font-size: 1.3rem; font-weight: 700; line-height: 1.5;">
                {NULLIFIED_EXACT_MESSAGE}
            </h2>
            <p style="color:#ffe4e6; margin-top: 1.5rem; font-size: 0.95rem; max-width: 600px; margin-left: auto; margin-right: auto;">
                Account for <strong>{student['name']}</strong> has been flagged for violation of technical badge interview standards. All credentials, bookings, and eligibility have been revoked.
            </p>
            <div style="margin-top: 2rem; font-size: 0.85rem; color: #f43f5e;">
                Disciplinary Reference: #MAL-2026-094 • Contact: integrity@grit.edu
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # ================= PROMPT 5 STATE 1: PASSED CELEBRATORY CARD =================
        if track_status == "Passed":
            st.balloons()
            st.success(f"🏆 {PASSED_EXACT_MESSAGE}")
            with st.expander("🎖️ [View Your Badge & Certificate]"):
                st.markdown(f"""
                ### Verified Badge Credential
                - **Recipient:** {student['name']}
                - **Badge Title:** GRIT AI Systems Track Badge
                - **Verification Ledger ID:** `GRIT-AI-{student['id']}982`
                - **Status:** **Passed & Verified**
                - **Evaluator:** Dr. Marcus Rivera
                """)

        # ================= PROMPT 5 STATE 2: RETAKE WARNING CARD =================
        elif track_status == "Eligible" and has_retake:
            st.warning(f"⚠️ {RETAKE_EXACT_MESSAGE}")
            with st.expander("📝 [View Detailed Notes]"):
                fb = booking.get("feedback") if booking else "Focus on core architectural trade-offs."
                st.markdown(f"**Evaluator Feedback:** *\"{fb}\"*")

        # ================= PROMPT 2 SUCCESS BANNER (WHEN SCHEDULED) =================
        elif track_status == "Scheduled":
            st.info(f"📅 {SUCCESS_BANNER_MESSAGE}")

        # Header Progress Card
        st.markdown(f"### AI Engineering Track: 100% Complete. You are eligible for your interview.")
        st.caption(f"Candidate: **{student['name']}** • Status: **{track_status}** • Prerequisites: **4 of 4 Badges Met (100%)**")

        st.progress(1.0)

        # Scheduled Booking Card
        if booking:
            with st.container(border=True):
                st.markdown("#### 📅 Your Scheduled Interview")
                c1, c2, c3 = st.columns(3)
                c1.metric("Date & Time", booking["start_time"].split()[0] + " " + booking["start_time"].split()[1][:5])
                c2.metric("Interviewer", booking["interviewer_name"])
                c3.metric("Outcome", booking["outcome"])
                if booking.get("feedback"):
                    st.caption(f"Feedback notes: *{booking['feedback']}*")

        # Available Slots Grid
        if track_status in ("Eligible", "Scheduled"):
            st.markdown("---")
            st.markdown("### 🕒 Available Interview Slots")

            if not available_slots:
                st.info("No open slots currently available. Switch to Interviewer view to add more slots.")
            else:
                cols = st.columns(min(len(available_slots), 4))
                for idx, slot in enumerate(available_slots):
                    col = cols[idx % 4]
                    with col:
                        with st.container(border=True):
                            st.markdown(f"**{slot['start_time']}**")
                            st.caption(f"Interviewer: {slot['interviewer_name']}")
                            st.caption("Duration: 45 min • Google Meet")

                            if st.button("Book Slot", key=f"book_slot_{slot['id']}"):
                                conn = get_db_connection()
                                lock_slot(conn, slot["id"])
                                ok, result = create_booking(conn, slot["id"], current_student_id)
                                conn.close()
                                if ok:
                                    st.success(result["message"])
                                    st.rerun()
                                else:
                                    st.error(result.get("error", "Failed to book slot"))


# ==============================================================
# 2. INTERVIEWER VIEW (PROMPT 3)
# ==============================================================
elif role == "Interviewer":
    conn = get_db_connection()
    interviewer = get_user_by_id(conn, current_interviewer_id)
    my_slots = get_interviewer_slots(conn, current_interviewer_id)
    queue = get_interviewer_queue(conn, current_interviewer_id)
    conn.close()

    st.markdown(f"## Interviewer Portal: {interviewer['name']}")
    st.caption("Manage availability slots and submit technical evaluations.")

    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("Open Slots", len([s for s in my_slots if s["status"] == "Available"]))
    col_s2.metric("Pending Queue", len([q for q in queue if q["outcome"] == "Pending"]))
    col_s3.metric("Evaluations Logged", len([q for q in queue if q["outcome"] != "Pending"]))

    st.markdown("---")

    # Section 1: Manage Availability
    st.markdown("### Section 1: Manage Availability")
    st.caption("Add new Interviewer_Slots (defaults to 'Available').")

    with st.form("add_slot_form", clear_on_submit=True):
        f1, f2 = st.columns(2)
        slot_date = f1.date_input("Slot Date", min_value=datetime.now().date() + timedelta(days=1))
        slot_time = f2.time_input("Slot Time", value=datetime.strptime("10:00", "%H:%M").time())
        add_submitted = st.form_submit_button("➕ Publish Slot")

        if add_submitted:
            dt_str = f"{slot_date.strftime('%Y-%m-%d')} {slot_time.strftime('%H:%M:00')}"
            conn = get_db_connection()
            ok, res = add_interviewer_slot(conn, current_interviewer_id, dt_str)
            conn.close()
            if ok:
                st.success(f"Slot added for {dt_str} (status: Available)")
                st.rerun()

    if my_slots:
        st.markdown("##### Your Published Slots")
        for s in my_slots:
            with st.container(border=True):
                sc1, sc2, sc3 = st.columns([3, 2, 1])
                sc1.markdown(f"🕒 **{s['start_time']}**")
                sc2.markdown(f"Status: `{s['status']}`" + (f" ({s['student_name']})" if s.get('student_name') else ""))
                if s["status"] == "Available":
                    if sc3.button("🗑️ Delete", key=f"del_slot_{s['id']}"):
                        conn = get_db_connection()
                        delete_interviewer_slot(conn, s["id"], current_interviewer_id)
                        conn.close()
                        st.rerun()

    st.markdown("---")

    # Section 2: Daily Queue
    st.markdown("### Section 2: Daily Queue")
    st.caption("Candidate evaluations tied to your slots.")

    if not queue:
        st.info("No candidates currently booked in your queue.")
    else:
        for item in queue:
            with st.container(border=True):
                qc1, qc2 = st.columns([3, 2])
                qc1.markdown(f"#### 👤 {item['student_name']} (`{item['student_email']}`)")
                qc1.caption(f"Track: **{item['track_name']}** • Slot: **{item['start_time']}**")

                with qc2:
                    st.markdown(f"Current Outcome: **{item['outcome']}**")
                    with st.expander("📝 Submit Evaluation"):
                        with st.form(f"eval_form_{item['booking_id']}"):
                            outcome = st.selectbox(
                                "Outcome Decision",
                                ["Pass", "Fail", "Retake"],
                                index=0
                            )
                            feedback = st.text_area("Evaluation Feedback", value=item.get("feedback") or "")
                            sub_eval = st.form_submit_button("Submit Evaluation")

                            if sub_eval:
                                conn = get_db_connection()
                                ok, res = submit_evaluation(conn, item["booking_id"], outcome, feedback)
                                conn.close()
                                if ok:
                                    st.success(res["message"])
                                    st.rerun()


# ==============================================================
# 3. ADMIN VIEW (PROMPT 4)
# ==============================================================
elif role == "Admin":
    conn = get_db_connection()
    metrics = get_admin_dashboard_metrics(conn)
    students = get_all_students_for_admin(conn)
    conn.close()

    st.markdown("## Admin & Operations Dashboard")
    st.caption("Cohort progression, eligibility status, and academic integrity management.")

    # Prompt 4 Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Eligible (Unbooked)", metrics["total_eligible_unbooked"])
    m2.metric("Total Scheduled", metrics["total_scheduled"])
    m3.metric("Badges Issued (Passed)", metrics["total_passed"])
    m4.metric("Malpractice Flags", metrics["total_nullified"])

    st.markdown("---")

    # Prompt 4 Student Data Table
    st.markdown("### Student Cohort & Malpractice Oversight")
    st.caption("Table: Users ⋈ Track_Eligibility")

    for s in students:
        with st.container(border=True):
            tc1, tc2, tc3, tc4 = st.columns([3, 2, 2, 2])
            tc1.markdown(f"**{s['name']}**")
            tc1.caption(f"`{s['email']}`")

            tc2.markdown(f"Track: **{s['track_name']}**")
            tc3.markdown(f"Status: **{s['status']}**")
            if s.get("booking_outcome"):
                tc3.caption(f"Outcome: {s['booking_outcome']}")

            with tc4:
                if s["status"] == "Nullified":
                    st.error("🚨 Nullified")
                    if st.button("Restore", key=f"restore_{s['student_id']}"):
                        conn = get_db_connection()
                        restore_student_eligibility(conn, s["student_id"])
                        conn.close()
                        st.rerun()
                else:
                    if st.button("🚨 Flag Malpractice", key=f"flag_{s['student_id']}", help="Sets Track_Eligibility to 'Nullified'"):
                        conn = get_db_connection()
                        flag_malpractice(conn, s["student_id"])
                        conn.close()
                        st.warning(f"Malpractice flagged for {s['name']}!")
                        st.rerun()
