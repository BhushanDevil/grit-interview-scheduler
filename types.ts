/**
 * TypeScript Data Models and Enums for GRIT Interview Scheduler
 */

export type UserRole = 'Student' | 'Interviewer' | 'Admin';

export type EligibilityStatus = 'Eligible' | 'Scheduled' | 'Passed' | 'Failed' | 'Nullified';

export type SlotStatus = 'Available' | 'Locked' | 'Booked';

export type BookingOutcome = 'Pending' | 'Pass' | 'Fail' | 'Retake';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  created_at?: string;
}

export interface TrackEligibility {
  id: number;
  student_id: number;
  track_name: string;
  status: EligibilityStatus;
  created_at?: string;
  updated_at?: string;
  // Joined relation fields
  student_name?: string;
  student_email?: string;
}

export interface InterviewerSlot {
  id: number;
  interviewer_id: number;
  start_time: string;
  status: SlotStatus;
  created_at?: string;
  // Joined relation fields
  interviewer_name?: string;
  interviewer_email?: string;
}

export interface InterviewBooking {
  id: number;
  slot_id: number;
  student_id: number;
  outcome: BookingOutcome;
  feedback: string | null;
  created_at?: string;
  updated_at?: string;
  // Joined relation fields
  student_name?: string;
  student_email?: string;
  interviewer_name?: string;
  start_time?: string;
}
