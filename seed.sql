-- GRIT Interview Scheduler - Initial Seed Data
-- 1 Admin user, 3 Interviewer users, 8 Student users
-- Students eligible for "AI Systems Track" and "AI Engineering Track"
-- Multiple Interviewer_Slots across evaluators

PRAGMA foreign_keys = ON;

-- Clear any existing records for fresh idempotent seeding
DELETE FROM Interview_Bookings;
DELETE FROM Interviewer_Slots;
DELETE FROM Track_Eligibility;
DELETE FROM Users;

-- Reset autoincrement sequences
DELETE FROM sqlite_sequence WHERE name IN ('Users', 'Track_Eligibility', 'Interviewer_Slots', 'Interview_Bookings');

-- 1. Insert Users
-- Admin
INSERT INTO Users (name, email, role) VALUES 
('Eleanor Vance', 'admin@grit.edu', 'Admin');

-- Interviewers (3 Evaluators)
INSERT INTO Users (name, email, role) VALUES 
('Dr. Marcus Rivera', 'marcus.rivera@grit.edu', 'Interviewer'),
('Prof. Sarah Connor', 'sarah.connor@grit.edu', 'Interviewer'),
('Dr. Vikram Patel', 'vikram.patel@grit.edu', 'Interviewer');

-- Students (8 Candidates)
INSERT INTO Users (name, email, role) VALUES 
('Alex Rivera', 'alex.rivera@grit.edu', 'Student'),
('Bianca Chen', 'bianca.chen@grit.edu', 'Student'),
('Devon Brooks', 'devon.brooks@grit.edu', 'Student'),
('Elena Rostova', 'elena.rostova@grit.edu', 'Student'),
('Carlos Mendez', 'carlos.mendez@grit.edu', 'Student'),
('Aisha Khan', 'aisha.khan@grit.edu', 'Student'),
('Liam O''Connor', 'liam.oconnor@grit.edu', 'Student'),
('Priya Sharma', 'priya.sharma@grit.edu', 'Student');

-- 2. Insert Track_Eligibility for all students (AI Systems Track & AI Engineering Track, status: 'Eligible')
INSERT INTO Track_Eligibility (student_id, track_name, status)
SELECT id, 'AI Systems Track', 'Eligible'
FROM Users
WHERE role = 'Student';

INSERT INTO Track_Eligibility (student_id, track_name, status)
SELECT id, 'AI Engineering Track', 'Eligible'
FROM Users
WHERE role = 'Student';

-- 3. Insert Availability Slots for Tomorrow across the Interviewers
-- Dr. Marcus Rivera (4 slots tomorrow)
INSERT INTO Interviewer_Slots (interviewer_id, start_time, status)
SELECT id, date('now', 'localtime', '+1 day') || ' 09:00:00', 'Available'
FROM Users WHERE email = 'marcus.rivera@grit.edu';

INSERT INTO Interviewer_Slots (interviewer_id, start_time, status)
SELECT id, date('now', 'localtime', '+1 day') || ' 11:00:00', 'Available'
FROM Users WHERE email = 'marcus.rivera@grit.edu';

INSERT INTO Interviewer_Slots (interviewer_id, start_time, status)
SELECT id, date('now', 'localtime', '+1 day') || ' 14:00:00', 'Available'
FROM Users WHERE email = 'marcus.rivera@grit.edu';

INSERT INTO Interviewer_Slots (interviewer_id, start_time, status)
SELECT id, date('now', 'localtime', '+1 day') || ' 16:00:00', 'Available'
FROM Users WHERE email = 'marcus.rivera@grit.edu';

-- Prof. Sarah Connor (3 slots tomorrow)
INSERT INTO Interviewer_Slots (interviewer_id, start_time, status)
SELECT id, date('now', 'localtime', '+1 day') || ' 10:00:00', 'Available'
FROM Users WHERE email = 'sarah.connor@grit.edu';

INSERT INTO Interviewer_Slots (interviewer_id, start_time, status)
SELECT id, date('now', 'localtime', '+1 day') || ' 13:00:00', 'Available'
FROM Users WHERE email = 'sarah.connor@grit.edu';

INSERT INTO Interviewer_Slots (interviewer_id, start_time, status)
SELECT id, date('now', 'localtime', '+1 day') || ' 15:30:00', 'Available'
FROM Users WHERE email = 'sarah.connor@grit.edu';

-- Dr. Vikram Patel (3 slots tomorrow)
INSERT INTO Interviewer_Slots (interviewer_id, start_time, status)
SELECT id, date('now', 'localtime', '+1 day') || ' 11:30:00', 'Available'
FROM Users WHERE email = 'vikram.patel@grit.edu';

INSERT INTO Interviewer_Slots (interviewer_id, start_time, status)
SELECT id, date('now', 'localtime', '+1 day') || ' 14:30:00', 'Available'
FROM Users WHERE email = 'vikram.patel@grit.edu';

INSERT INTO Interviewer_Slots (interviewer_id, start_time, status)
SELECT id, date('now', 'localtime', '+1 day') || ' 17:00:00', 'Available'
FROM Users WHERE email = 'vikram.patel@grit.edu';
