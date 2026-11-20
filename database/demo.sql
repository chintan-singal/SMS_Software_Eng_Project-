-- Optional synthetic records for a fresh setup.sql database.
-- A local password is generated at import time and displayed once at the end.
USE student_management;
SET @demo_password = REPLACE(UUID(), '-', '');
START TRANSACTION;
INSERT INTO Department (DepartmentID, DeptCode, DeptName)
VALUES (1, 'DEMO', 'Demo Engineering');
INSERT INTO Program (ProgramID, ProgramCode, ProgramName, DepartmentID)
VALUES (1, 'DEMO-B', 'Demo Engineering Programme', 1);
INSERT INTO Person (PersonID, Name, Email, Password, Role) VALUES
(101, 'Demo Student', 'student@example.test', @demo_password, 'Student'),
(201, 'Demo Faculty', 'faculty@example.test', @demo_password, 'Faculty'),
(301, 'Demo Admin', 'admin@example.test', @demo_password, 'Admin');
INSERT INTO Student (StudentID, RollNo, ProgramID, Semester, AdmissionYear)
VALUES (101, 'DEMO101', 1, 1, 2026);
INSERT INTO Faculty (FacultyID, DepartmentID, Designation) VALUES (201, 1, 'Lecturer');
INSERT INTO Admin (AdminID, RoleType) VALUES (301, 'SuperAdmin');
INSERT INTO Course (CourseID, CourseName, Credits, DepartmentID, Semester)
VALUES (11, 'Demo Database Systems', 4, 1, 1);
INSERT INTO Teaches (FacultyID, CourseID) VALUES (201, 11);
INSERT INTO Enrollment (StudentID, CourseID, EnrollmentDate, Status)
VALUES (101, 11, CURRENT_DATE(), 'Active');
COMMIT;
SELECT @demo_password AS local_demo_password;

