"""
Data models and Enums for GRIT Interview Scheduler.
Represents tables: Users, Track_Eligibility, Interviewer_Slots, Interview_Bookings.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


class UserRole(str, Enum):
    STUDENT = "Student"
    INTERVIEWER = "Interviewer"
    ADMIN = "Admin"


class EligibilityStatus(str, Enum):
    ELIGIBLE = "Eligible"
    SCHEDULED = "Scheduled"
    PASSED = "Passed"
    FAILED = "Failed"
    NULLIFIED = "Nullified"


class SlotStatus(str, Enum):
    AVAILABLE = "Available"
    LOCKED = "Locked"
    BOOKED = "Booked"


class BookingOutcome(str, Enum):
    PENDING = "Pending"
    PASS = "Pass"
    FAIL = "Fail"
    RETAKE = "Retake"


@dataclass
class User:
    id: Optional[int]
    name: str
    email: str
    role: UserRole
    created_at: Optional[datetime] = None


@dataclass
class TrackEligibility:
    id: Optional[int]
    student_id: int
    track_name: str
    status: EligibilityStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class InterviewerSlot:
    id: Optional[int]
    interviewer_id: int
    start_time: str
    status: SlotStatus
    created_at: Optional[datetime] = None


@dataclass
class InterviewBooking:
    id: Optional[int]
    slot_id: int
    student_id: int
    outcome: BookingOutcome = BookingOutcome.PENDING
    feedback: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
