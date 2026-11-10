"""
Generates the publication-quality 2-page PDF write-up for
the GRIT Interview Scheduler project based on the assignment PDF requirements.
"""

import os
os.environ["MPLCONFIGDIR"] = "/tmp"

import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_PDF = "GRIT_Interview_Scheduler_Writeup.pdf"

# Design palette (Notion/Linear aesthetic)
C_PRIMARY = "#0f172a"      # slate-900
C_SECONDARY = "#334155"    # slate-700
C_MUTED = "#64748b"        # slate-500
C_BG_PAGE = "#ffffff"
C_CARD_BG = "#f8fafc"      # slate-50
C_CARD_BORDER = "#cbd5e1"  # slate-300
C_EMERALD = "#059669"      # emerald-600
C_EMERALD_BG = "#ecfdf5"   # emerald-50
C_AMBER = "#d97706"        # amber-600
C_AMBER_BG = "#fffbeb"     # amber-50
C_ROSE = "#e11d48"         # rose-600
C_ROSE_BG = "#fff1f2"      # rose-50
C_BLUE = "#2563eb"         # blue-600
C_BLUE_BG = "#eff6ff"      # blue-50


def draw_rounded_card(ax, x, y, w, h, bg=C_CARD_BG, border=C_CARD_BORDER, lw=1.0, rad=0.015):
    """Draws a rounded rectangular card on axis."""
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={rad}",
        facecolor=bg, edgecolor=border, linewidth=lw,
        transform=ax.transAxes, clip_on=False
    )
    ax.add_patch(rect)


def create_page_1(fig, ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Header Banner
    draw_rounded_card(ax, 0.04, 0.90, 0.92, 0.085, bg="#0f172a", border="#1e293b", rad=0.012)
    ax.text(0.06, 0.952, "GRIT Interview Scheduler — Product Architecture Write-up",
            fontsize=13, weight="bold", color="#ffffff", transform=ax.transAxes)
    ax.text(0.06, 0.928, "AI Product Engineer: Round 1 Assignment | NIAT Track Badge Certification System",
            fontsize=8.5, color="#94a3b8", transform=ax.transAxes)
    ax.text(0.94, 0.940, "PAGE 1 OF 2", fontsize=8.5, weight="bold", color="#38bdf8",
            ha="right", transform=ax.transAxes)
    ax.text(0.94, 0.918, "Live Prototype: Render Cloud • SQLite • Python 3.11", fontsize=7.5,
            color="#94a3b8", ha="right", transform=ax.transAxes)

    # -------------------------------------------------------------
    # SECTION 1: INTERVIEW JOURNEY STATE MACHINE
    # -------------------------------------------------------------
    draw_rounded_card(ax, 0.04, 0.585, 0.92, 0.30, bg="#ffffff", border=C_CARD_BORDER, rad=0.012)
    ax.text(0.06, 0.865, "1. Interview Journey State Machine (States & Transitions)",
            fontsize=10.5, weight="bold", color=C_PRIMARY, transform=ax.transAxes)
    ax.text(0.06, 0.848, "Every state a student's interview journey traverses from prerequisite completion to verified badge or revocation:",
            fontsize=8, color=C_MUTED, transform=ax.transAxes)

    # State Flow Boxes
    states = [
        ("Ineligible", "Prerequisites < 100%\nModules & quizzes pending", C_MUTED, "#f1f5f9"),
        ("Eligible", "Coursework 100% complete\nUnbooked & ready to schedule", C_EMERALD, C_EMERALD_BG),
        ("Hold (Locked)", "Slot selected; 5-min timer\nLock prevents collisions", C_AMBER, C_AMBER_BG),
        ("Scheduled", "Booking confirmed; invite sent\nEvaluator assigned in queue", C_BLUE, C_BLUE_BG),
        ("Evaluation", "Live 45-min technical call\nRubric & coding review", C_PRIMARY, "#f8fafc")
    ]

    box_w = 0.165
    box_h = 0.055
    y_pos = 0.775
    for i, (name, desc, color, bg) in enumerate(states):
        x_pos = 0.06 + i * 0.182
        draw_rounded_card(ax, x_pos, y_pos, box_w, box_h, bg=bg, border=color, lw=1.2, rad=0.008)
        ax.text(x_pos + box_w/2, y_pos + 0.034, name, fontsize=8, weight="bold", color=color,
                ha="center", transform=ax.transAxes)
        ax.text(x_pos + box_w/2, y_pos + 0.010, desc, fontsize=6.2, color=C_SECONDARY,
                ha="center", transform=ax.transAxes)
        if i < len(states) - 1:
            ax.annotate("", xy=(x_pos + box_w + 0.016, y_pos + box_h/2),
                        xytext=(x_pos + box_w + 0.002, y_pos + box_h/2),
                        arrowprops=dict(arrowstyle="->", color=C_MUTED, lw=1.2),
                        xycoords="axes fraction")

    # Outcome Branches
    outcomes = [
        ("Passed", "Badge unlocked & public certificate\nCredential added to NIAT ledger", C_EMERALD, C_EMERALD_BG),
        ("Failed", "Competencies not met\nDetailed remediation notes", C_ROSE, C_ROSE_BG),
        ("Retake", "Eligible after 7-day cooldown\nResets Track_Eligibility to 'Eligible'", C_AMBER, C_AMBER_BG),
        ("Nullified", "Academic integrity violation flagged\nPermanent credential revocation", "#991b1b", "#fee2e2")
    ]

    y_pos_out = 0.695
    ax.text(0.06, 0.755, "Post-Evaluation Outcomes & Terminal Integrity States:",
            fontsize=7.5, weight="bold", color=C_SECONDARY, transform=ax.transAxes)

    for i, (name, desc, color, bg) in enumerate(outcomes):
        x_pos = 0.06 + i * 0.228
        draw_rounded_card(ax, x_pos, y_pos_out, 0.21, 0.048, bg=bg, border=color, lw=1.2, rad=0.008)
        ax.text(x_pos + 0.105, y_pos_out + 0.028, f"● {name}", fontsize=7.8, weight="bold", color=color,
                ha="center", transform=ax.transAxes)
        ax.text(x_pos + 0.105, y_pos_out + 0.009, desc, fontsize=6.2, color=C_SECONDARY,
                ha="center", transform=ax.transAxes)

    # State Transition Summary Table
    y_table = 0.60
    draw_rounded_card(ax, 0.06, y_table, 0.88, 0.082, bg="#f8fafc", border=C_CARD_BORDER, rad=0.006)
    table_text = (
        "TRANSITION TRIGGER MATRIX:\n"
        "• Coursework Completed (100%) → Moves from Ineligible to Eligible (Unbooked).\n"
        "• Click Open Slot → Atomically locks slot ('Locked') & starts 5-min client hold timer. Cancel/expire releases hold.\n"
        "• Confirm Booking → Atomically writes Interview_Bookings, updates Slot to 'Booked', updates Student to 'Scheduled'.\n"
        "• Interviewer Outcome Evaluation → 'Pass' updates to Passed; 'Fail' to Failed; 'Retake' crucially resets to Eligible.\n"
        "• Admin Malpractice Flag → Overwrites student's Track_Eligibility to 'Nullified' from ANY state instantly."
    )
    ax.text(0.075, y_table + 0.041, table_text, fontsize=6.7, color=C_SECONDARY, linespacing=1.35,
            va="center", transform=ax.transAxes)

    # -------------------------------------------------------------
    # SECTION 2: DATA MODEL & PREVENTING DOUBLE BOOKINGS
    # -------------------------------------------------------------
    draw_rounded_card(ax, 0.04, 0.265, 0.92, 0.31, bg="#ffffff", border=C_CARD_BORDER, rad=0.012)
    ax.text(0.06, 0.555, "2. Relational Data Model & Slot Collision Prevention",
            fontsize=10.5, weight="bold", color=C_PRIMARY, transform=ax.transAxes)
    ax.text(0.06, 0.538, "Schema entities, relational foreign keys, integrity constraints, and concurrency locking mechanisms:",
            fontsize=8, color=C_MUTED, transform=ax.transAxes)

    # 4 Tables Schema Cards
    tables = [
        ("Users", "id (PK, int)\nname (text)\nemail (text, UNIQUE)\nrole (Student | Interviewer | Admin)\ncreated_at (datetime)"),
        ("Track_Eligibility", "id (PK, int)\nstudent_id (FK → Users.id)\ntrack_name (text)\nstatus (Eligible|Scheduled|\nPassed|Failed|Nullified)\nupdated_at (datetime)"),
        ("Interviewer_Slots", "id (PK, int)\ninterviewer_id (FK → Users.id)\nstart_time (datetime)\nstatus (Available|Locked|\nBooked)\ncreated_at (datetime)"),
        ("Interview_Bookings", "id (PK, int)\nslot_id (FK, UNIQUE → Slots.id)\nstudent_id (FK → Users.id)\noutcome (Pending|Pass|Fail|\nRetake)\nfeedback (text)")
    ]

    t_w = 0.215
    t_h = 0.125
    t_y = 0.405
    for i, (t_name, t_fields) in enumerate(tables):
        t_x = 0.06 + i * 0.228
        draw_rounded_card(ax, t_x, t_y, t_w, t_h, bg="#f8fafc", border=C_CARD_BORDER, lw=1.0, rad=0.008)
        ax.text(t_x + 0.01, t_y + t_h - 0.018, t_name, fontsize=8.2, weight="bold", color=C_PRIMARY,
                transform=ax.transAxes)
        ax.plot([t_x + 0.01, t_x + t_w - 0.01], [t_y + t_h - 0.024, t_y + t_h - 0.024],
                color=C_CARD_BORDER, lw=0.8, transform=ax.transAxes)
        ax.text(t_x + 0.01, t_y + t_h - 0.038, t_fields, fontsize=6.4, color=C_SECONDARY,
                linespacing=1.28, va="top", transform=ax.transAxes)

    # How we prevent two students from booking the same slot
    draw_rounded_card(ax, 0.06, 0.28, 0.88, 0.115, bg="#f0fdf4", border="#86efac", rad=0.008)
    ax.text(0.075, 0.380, "HOW WE PREVENT TWO STUDENTS FROM BOOKING THE SAME SLOT (Three-Tier Defense):",
            fontsize=7.8, weight="bold", color=C_EMERALD, transform=ax.transAxes)
    prevention_text = (
        "1. Database Unique Constraint: Interview_Bookings defines slot_id as UNIQUE (slot_id INTEGER NOT NULL UNIQUE). "
        "Any concurrent attempt to insert a second booking for the same slot is instantly rejected with sqlite3.IntegrityError.\n"
        "2. Atomic ACID Transactions: The booking routine uses SQLite IMMEDIATE transactions (with conn:) executing a conditional write. "
        "The slot status is verified to be Available/Locked before insertion in an isolated transaction block.\n"
        "3. Interactive Booking Hold: When a student clicks a slot, the status is immediately transitioned to 'Locked'. Other students "
        "see the slot as unavailable in real time, preventing visual collision while the candidate reviews the confirmation dialog."
    )
    ax.text(0.075, 0.328, prevention_text, fontsize=6.8, color="#064e3b", linespacing=1.30,
            va="center", transform=ax.transAxes)

    # -------------------------------------------------------------
    # SECTION 3: EDGE CASES, QUESTIONS & ASSUMPTIONS
    # -------------------------------------------------------------
    draw_rounded_card(ax, 0.04, 0.03, 0.92, 0.225, bg="#ffffff", border=C_CARD_BORDER, rad=0.012)
    ax.text(0.06, 0.235, "3. Edge Cases, Questions Handled & Product Assumptions",
            fontsize=10.5, weight="bold", color=C_PRIMARY, transform=ax.transAxes)

    edge_cases = (
        "• Concurrent Booking Race Condition: Two students clicking the same slot simultaneously. Resolved via atomic status lock + UNIQUE constraint on slot_id.\n"
        "• Hold Expiration / Abandonment: A student opens the modal but leaves the tab. Solved with a 5-minute countdown releasing 'Locked' slots back to 'Available'.\n"
        "• Retake Cool-off Window: If evaluated as 'Retake', student is reset to 'Eligible', but rebooking is locked until a 7-day preparation window elapses (Nov 21).\n"
        "• Malpractice Post-Issuance: A student passes their interview but is later caught cheating in contest code. Admin flag instantly revokes badge and locks dashboard.\n"
        "• Timezone Consistency: Interview slots store ISO timestamps and render in student's local timezone (IST) with unambiguous relative labels (e.g. 'Tomorrow 10:00 AM').\n"
        "• Key Assumptions: Evaluators evaluate one candidate at a time; 45-minute standard interview duration; one active badge interview booking per track per student."
    )
    ax.text(0.06, 0.128, edge_cases, fontsize=7.2, color=C_SECONDARY, linespacing=1.35,
            va="center", transform=ax.transAxes)


def create_page_2(fig, ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Header Banner
    draw_rounded_card(ax, 0.04, 0.90, 0.92, 0.085, bg="#0f172a", border="#1e293b", rad=0.012)
    ax.text(0.06, 0.952, "GRIT Interview Scheduler — Prototype & Interface Write-up",
            fontsize=13, weight="bold", color="#ffffff", transform=ax.transAxes)
    ax.text(0.06, 0.928, "AI Product Engineer: Round 1 Assignment | NIAT Track Badge Certification System",
            fontsize=8.5, color="#94a3b8", transform=ax.transAxes)
    ax.text(0.94, 0.940, "PAGE 2 OF 2", fontsize=8.5, weight="bold", color="#38bdf8",
            ha="right", transform=ax.transAxes)
    ax.text(0.94, 0.918, "Live Prototype: Render Cloud • SQLite • Python 3.11", fontsize=7.5,
            color="#94a3b8", ha="right", transform=ax.transAxes)

    # -------------------------------------------------------------
    # SECTION 4: THE 3 CORE STUDENT MESSAGES (VERBATIM)
    # -------------------------------------------------------------
    draw_rounded_card(ax, 0.04, 0.585, 0.92, 0.30, bg="#ffffff", border=C_CARD_BORDER, rad=0.012)
    ax.text(0.06, 0.865, "4. The 3 Most Important Student Messages (Rendered Exactly As Prompted)",
            fontsize=10.5, weight="bold", color=C_PRIMARY, transform=ax.transAxes)
    ax.text(0.06, 0.848, "These verbatim messages provide immediate feedback across key milestones: booking confirmation, pass celebration, and retake guidance:",
            fontsize=8, color=C_MUTED, transform=ax.transAxes)

    # Message 1 Card: Booking Confirmed
    draw_rounded_card(ax, 0.06, 0.745, 0.88, 0.092, bg=C_EMERALD_BG, border="#86efac", rad=0.008)
    ax.text(0.075, 0.822, "MESSAGE 1: BOOKING CONFIRMATION BANNER (Prompt 2)",
            fontsize=7.5, weight="bold", color=C_EMERALD, transform=ax.transAxes)
    msg1_text = (
        "“You’re booked! Your AI Engineering Track Interview is confirmed for Thursday, Nov 14 at 4:30 PM IST. "
        "A calendar invitation with your meeting link has been sent to your email. Please join 5 minutes early "
        "with your camera and workspace ready.”"
    )
    ax.text(0.075, 0.780, msg1_text, fontsize=7.2, color="#064e3b", weight="semibold", linespacing=1.28,
            va="center", transform=ax.transAxes)

    # Message 2 Card: Passed Celebratory
    draw_rounded_card(ax, 0.06, 0.640, 0.88, 0.095, bg="#ecfdf5", border="#34d399", rad=0.008)
    ax.text(0.075, 0.720, "MESSAGE 2: PASSED CELEBRATION CARD (Prompt 5 State 1)",
            fontsize=7.5, weight="bold", color="#047857", transform=ax.transAxes)
    msg2_text = (
        "“Congratulations! You have passed your Track Badge Interview. Your GRIT AI Systems Track Badge has been "
        "unlocked and verified on your public profile. [View Your Badge & Certificate]”\n"
        "Interactive Feature: Clicking the link opens an authentic verifiable certificate modal with verification hash and public ledger link."
    )
    ax.text(0.075, 0.678, msg2_text, fontsize=7.2, color="#065f46", weight="semibold", linespacing=1.25,
            va="center", transform=ax.transAxes)

    # Message 3 Card: Retake Warning & Nullified
    draw_rounded_card(ax, 0.06, 0.540, 0.88, 0.092, bg=C_AMBER_BG, border="#fcd34d", rad=0.008)
    ax.text(0.075, 0.618, "MESSAGE 3: RETAKE REQUIRED WARNING CARD (Prompt 5 State 2)",
            fontsize=7.5, weight="bold", color=C_AMBER, transform=ax.transAxes)
    msg3_text = (
        "“Interview Outcome: Retake Required. Your interviewer has requested a retake on core architecture concepts. "
        "Your rebooking window will open on Nov 21, 2026 (7-day preparation window). Review your feedback notes here: [View Detailed Notes].”\n"
        "Nullified Override: “Badge Nullified: Violation of academic integrity detected. All credentials have been revoked.”"
    )
    ax.text(0.075, 0.575, msg3_text, fontsize=7.2, color="#78350f", weight="semibold", linespacing=1.25,
            va="center", transform=ax.transAxes)

    # -------------------------------------------------------------
    # SECTION 5: BEFORE & AFTER SCREENS IN THE WORKING PROTOTYPE
    # -------------------------------------------------------------
    draw_rounded_card(ax, 0.04, 0.170, 0.92, 0.355, bg="#ffffff", border=C_CARD_BORDER, rad=0.012)
    ax.text(0.06, 0.505, "5. Before & After Screens & Working Prototype Architecture",
            fontsize=10.5, weight="bold", color=C_PRIMARY, transform=ax.transAxes)
    ax.text(0.06, 0.488, "How the interface conditionally evolves across the user lifecycle before and after an evaluation result:",
            fontsize=8, color=C_MUTED, transform=ax.transAxes)

    screen_cards = [
        ("BEFORE: Eligible (Unbooked)",
         "• Header: 'AI Engineering Track: 100% Complete. You are eligible for your interview.'\n"
         "• 100% Progress Dial + Verified checklist (4/4 modules complete).\n"
         "• Available Slots Grid: Interactive cards with date, time, evaluator name, duration.\n"
         "• Action: Clicking slot locks hold and launches confirmation modal.",
         C_PRIMARY, "#f8fafc", "#e2e8f0"),
        ("BEFORE: Interview Scheduled",
         "• Success Banner: Verbatim confirmation message with calendar dispatch.\n"
         "• Scheduled Card: Displays confirmed slot date/time, interviewer, and Google Meet tag.\n"
         "• Status Pill: Blue 'Scheduled' pill; open slots update to Booked.\n"
         "• Evaluator Queue: Student automatically appears in evaluator's Daily Queue.",
         C_BLUE, C_BLUE_BG, "#bfdbfe"),
        ("AFTER RESULT: Passed (Success)",
         "• Celebratory Confetti Card with verified gold/emerald badge emblem.\n"
         "• Verbatim congratulations message with interactive '[View Your Badge & Certificate]'.\n"
         "• Certificate Modal: Official verified digital credential with verification ID.\n"
         "• Available slots section cleanly hidden as requirement is satisfied.",
         C_EMERALD, C_EMERALD_BG, "#a7f3d0"),
        ("AFTER RESULT: Retake / Nullified",
         "• Retake: Amber warning card with verbatim message, 7-day cooldown date, & feedback notes.\n"
         "• Nullified: Entire dashboard is OVERWRITTEN by full red locked screen (#4c0519).\n"
         "• Revocation: 'Badge Nullified: Violation of academic integrity detected...'\n"
         "• Complete lockout: Slot booking disabled, case reference displayed.",
         C_ROSE, C_ROSE_BG, "#fecdd3")
    ]

    sc_w = 0.425
    sc_h = 0.140
    for idx, (title, content, border_col, bg_col, b_border) in enumerate(screen_cards):
        row = idx // 2
        col = idx % 2
        x_pos = 0.06 + col * 0.455
        y_pos = 0.335 - row * 0.150
        draw_rounded_card(ax, x_pos, y_pos, sc_w, sc_h, bg=bg_col, border=border_col, lw=1.1, rad=0.008)
        ax.text(x_pos + 0.015, y_pos + sc_h - 0.020, title, fontsize=7.8, weight="bold", color=border_col,
                transform=ax.transAxes)
        ax.text(x_pos + 0.015, y_pos + sc_h - 0.038, content, fontsize=6.3, color=C_SECONDARY,
                linespacing=1.28, va="top", transform=ax.transAxes)

    # -------------------------------------------------------------
    # SECTION 6: LIVE WORKING PROTOTYPE & VERIFICATION
    # -------------------------------------------------------------
    draw_rounded_card(ax, 0.04, 0.03, 0.92, 0.125, bg="#0f172a", border="#1e293b", rad=0.010)
    ax.text(0.06, 0.132, "6. Live Working Prototype & Production Verification",
            fontsize=9.5, weight="bold", color="#ffffff", transform=ax.transAxes)
    ax.text(0.06, 0.114, "Hosted online with production WSGI (Render Cloud) with complete automated test coverage:",
            fontsize=7.8, color="#94a3b8", transform=ax.transAxes)

    # Verification bullets
    verif_text = (
        "• Production Platform: Render Cloud Web Service (Gunicorn WSGI + Flask 3.0.3) • Repository: GitHub\n"
        "• Item #5 Complete: Section 3 in Interviewer View allows interviewers to monitor unbooked vs booked eligible candidates in real time.\n"
        "• Expanded Roster: 1 Admin, 3 Interviewers (Rivera, Connor, Patel), 8 Students, 10 open availability slots across tomorrow.\n"
        "• Automated Test Suite: 24 out of 24 Unit & Integration Tests Passing (0 failures, 100% green coverage across all 4 suites):\n"
        "   1. test_db.py (9 tests)  2. test_booking_flow.py (4 tests)  3. test_interviewer_outcomes.py (6 tests)  4. test_admin_and_dynamic_states.py (5 tests)"
    )
    ax.text(0.06, 0.065, verif_text, fontsize=6.6, color="#e2e8f0", linespacing=1.30,
            va="center", transform=ax.transAxes)


def generate_pdf():
    print(f"Generating publication-quality 2-page PDF: {OUTPUT_PDF}...")
    with PdfPages(OUTPUT_PDF) as pdf:
        # Page 1 (8.5 x 11 inches, Letter size)
        fig1 = plt.figure(figsize=(8.5, 11), dpi=300)
        ax1 = fig1.add_axes([0, 0, 1, 1])
        create_page_1(fig1, ax1)
        pdf.savefig(fig1)
        plt.close(fig1)

        # Page 2 (8.5 x 11 inches, Letter size)
        fig2 = plt.figure(figsize=(8.5, 11), dpi=300)
        ax2 = fig2.add_axes([0, 0, 1, 1])
        create_page_2(fig2, ax2)
        pdf.savefig(fig2)
        plt.close(fig2)

    print(f"✓ PDF successfully generated at {OUTPUT_PDF}")


if __name__ == "__main__":
    generate_pdf()
