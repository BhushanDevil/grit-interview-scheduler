-- GRIT Interview Scheduler - Database Schema
-- Compatible with SQLite 3.x and standard SQL relational databases

PRAGMA foreign_keys = ON;

-- 1. Users Table
-- Stores all system users with their assigned role
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK (role IN ('Student', 'Interviewer', 'Admin')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Track_Eligibility Table
-- Tracks which tracks a student is eligible for and their progression status
CREATE TABLE IF NOT EXISTS Track_Eligibility (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    track_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Eligible', 'Scheduled', 'Passed', 'Failed', 'Nullified')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- 3. Interviewer_Slots Table
-- Defines availability slots created by interviewers
CREATE TABLE IF NOT EXISTS Interviewer_Slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interviewer_id INTEGER NOT NULL,
    start_time DATETIME NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Available', 'Locked', 'Booked')) DEFAULT 'Available',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interviewer_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- 4. Interview_Bookings Table
-- Connects a booked slot to a student, tracks the evaluation outcome and feedback
CREATE TABLE IF NOT EXISTS Interview_Bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_id INTEGER NOT NULL UNIQUE,
    student_id INTEGER NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('Pending', 'Pass', 'Fail', 'Retake')) DEFAULT 'Pending',
    feedback TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (slot_id) REFERENCES Interviewer_Slots(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Performance & lookup indices
CREATE INDEX IF NOT EXISTS idx_users_role ON Users(role);
CREATE INDEX IF NOT EXISTS idx_track_eligibility_student ON Track_Eligibility(student_id);
CREATE INDEX IF NOT EXISTS idx_track_eligibility_status ON Track_Eligibility(status);
CREATE INDEX IF NOT EXISTS idx_interviewer_slots_interviewer ON Interviewer_Slots(interviewer_id);
CREATE INDEX IF NOT EXISTS idx_interviewer_slots_status ON Interviewer_Slots(status);
CREATE INDEX IF NOT EXISTS idx_interviewer_slots_start_time ON Interviewer_Slots(start_time);
CREATE INDEX IF NOT EXISTS idx_interview_bookings_slot ON Interview_Bookings(slot_id);
CREATE INDEX IF NOT EXISTS idx_interview_bookings_student ON Interview_Bookings(student_id);
CREATE INDEX IF NOT EXISTS idx_interview_bookings_outcome ON Interview_Bookings(outcome);
