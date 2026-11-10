-- GRIT Interview Scheduler - Initial Dummy Seed Data
-- 1 Admin user, 1 Interviewer user, 3 Student users
-- Students eligible for "AI Systems Track" and "AI Engineering Track"
-- 4 Available Interviewer_Slots for tomorrow

PRAGMA foreign_keys = ON;

-- Clear any existing records for fresh idempotent seeding
DELETE FROM Interview_Bookings;
DELETE FROM Interviewer_Slots;
DELETE FROM Track_Eligibility;
DELETE FROM Users;

-- Reset autoincrement sequences
DELETE FROM sqlite_sequence WHERE name IN ('Users', 'Track_Eligibility', 'Interviewer_Slots', 'Interview_Bookings');

-- 1. Insert Users (1 Admin, 1 Interviewer, 3 Students)
INSERT INTO Users (name, email, role) VALUES 
('Eleanor Vance', 'admin@grit.edu', 'Admin'),
('Dr. Marcus Rivera', 'marcus.rivera@grit.edu', 'Interviewer'),
('Alex Rivera', 'alex.rivera@grit.edu', 'Student'),
('Bianca Chen', 'bianca.chen@grit.edu', 'Student'),
('Devon Brooks', 'devon.brooks@grit.edu', 'Student');

-- 2. Insert Track_Eligibility for the 3 students ("AI Systems Track" and "AI Engineering Track", status: "Eligible")
INSERT INTO Track_Eligibility (student_id, track_name, status)
SELECT id, 'AI Systems Track', 'Eligible'
FROM Users
WHERE role = 'Student';

INSERT INTO Track_Eligibility (student_id, track_name, status)
SELECT id, 'AI Engineering Track', 'Eligible'
FROM Users
WHERE role = 'Student';

-- 3. Insert 4 Interviewer_Slots set to "Available" for tomorrow
-- Times: 09:00, 11:00, 14:00, 16:00 local time
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
