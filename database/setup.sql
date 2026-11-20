-- Run once on a fresh MySQL instance or a new student_management database.
CREATE DATABASE student_management;
USE student_management;

-- 1. SCHEMA DEFINITION
-- ==========================================

-- ========= CORE =========
CREATE TABLE Person (
PersonID INT AUTO_INCREMENT PRIMARY KEY,
Name VARCHAR(100) NOT NULL,
DOB DATE,
Gender CHAR(1),
Email VARCHAR(120) UNIQUE NOT NULL,
Phone VARCHAR(20),
Address VARCHAR(255),
Password VARCHAR(255) NOT NULL,
Role ENUM('Student','Faculty','Admin') NOT NULL
);
CREATE TABLE Department (
DepartmentID INT AUTO_INCREMENT PRIMARY KEY,
DeptCode VARCHAR(20) UNIQUE NOT NULL,
DeptName VARCHAR(100) NOT NULL
);
CREATE TABLE Program (
ProgramID INT AUTO_INCREMENT PRIMARY KEY,
ProgramCode VARCHAR(20) UNIQUE NOT NULL,
ProgramName VARCHAR(100) NOT NULL,
DepartmentID INT NOT NULL,
FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
);
-- Subclasses
CREATE TABLE Student (
StudentID INT PRIMARY KEY,
RollNo VARCHAR(30) UNIQUE NOT NULL,
ProgramID INT NOT NULL,
Semester INT NOT NULL,
AdmissionYear INT NOT NULL,
FOREIGN KEY (StudentID) REFERENCES Person(PersonID),
FOREIGN KEY (ProgramID) REFERENCES Program(ProgramID)
);
CREATE TABLE Faculty (
FacultyID INT PRIMARY KEY,
Designation VARCHAR(60),
DepartmentID INT NOT NULL,
Qualification VARCHAR(120),
FOREIGN KEY (FacultyID) REFERENCES Person(PersonID),
FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
);
CREATE TABLE Admin (
AdminID INT PRIMARY KEY,
RoleType ENUM('SuperAdmin','DeptAdmin','FinanceAdmin') NOT NULL,
FOREIGN KEY (AdminID) REFERENCES Person(PersonID)
);
-- ========= ACADEMICS =========
CREATE TABLE Course (
CourseID INT AUTO_INCREMENT PRIMARY KEY,
CourseName VARCHAR(120) NOT NULL,
Credits INT NOT NULL,
DepartmentID INT NOT NULL,
Semester INT NOT NULL,
FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
);
CREATE TABLE Teaches (
FacultyID INT NOT NULL,
CourseID INT NOT NULL,
PRIMARY KEY (FacultyID, CourseID),
FOREIGN KEY (FacultyID) REFERENCES Faculty(FacultyID),
FOREIGN KEY (CourseID) REFERENCES Course(CourseID)
);
CREATE TABLE Enrollment (
EnrollmentID INT AUTO_INCREMENT PRIMARY KEY,
StudentID INT NOT NULL,
CourseID INT NOT NULL,
EnrollmentDate DATE NOT NULL,
Status ENUM('Active','Dropped','Completed') NOT NULL,
UNIQUE (StudentID, CourseID),
FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
FOREIGN KEY (CourseID) REFERENCES Course(CourseID)
);
CREATE TABLE Prerequisite (
CourseID INT NOT NULL,
PrerequisiteCourseID INT NOT NULL,
PRIMARY KEY (CourseID, PrerequisiteCourseID),
FOREIGN KEY (CourseID) REFERENCES Course(CourseID),
FOREIGN KEY (PrerequisiteCourseID) REFERENCES Course(CourseID)
);
-- ========= ASSIGNMENTS & SUBMISSIONS =========
CREATE TABLE Assignment (
AssignmentID INT AUTO_INCREMENT PRIMARY KEY,
CourseID INT NOT NULL,
CreatedBy INT NOT NULL,
Title VARCHAR(120) NOT NULL,
Description TEXT,
Deadline DATETIME NOT NULL,
MaxMarks INT NOT NULL,
FOREIGN KEY (CourseID) REFERENCES Course(CourseID),
FOREIGN KEY (CreatedBy) REFERENCES Faculty(FacultyID)
);
CREATE TABLE Submission (
SubmissionID INT AUTO_INCREMENT PRIMARY KEY,
AssignmentID INT NOT NULL,
StudentID INT NOT NULL,
SubmittedAt DATETIME NOT NULL,
Marks INT,
Comments TEXT,
UNIQUE (AssignmentID, StudentID),
FOREIGN KEY (AssignmentID) REFERENCES Assignment(AssignmentID) ON DELETE CASCADE,
FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
);
CREATE TABLE SubmissionEvaluation (
EvaluationID INT AUTO_INCREMENT PRIMARY KEY,
SubmissionID INT NOT NULL,
FacultyID INT NOT NULL,
MarksGiven INT NOT NULL,
Comments TEXT,
EvaluatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (SubmissionID) REFERENCES Submission(SubmissionID) ON DELETE CASCADE,
FOREIGN KEY (FacultyID) REFERENCES Faculty(FacultyID)
);
-- ========= EXAMS =========
CREATE TABLE Exam (
ExamID INT AUTO_INCREMENT PRIMARY KEY,
CourseID INT NOT NULL,
ConductedBy INT NOT NULL,
ExamType ENUM('Midterm','Final','Quiz') NOT NULL,
ExamDate DATETIME NOT NULL,
MaxMarks INT NOT NULL,
FOREIGN KEY (CourseID) REFERENCES Course(CourseID),
FOREIGN KEY (ConductedBy) REFERENCES Faculty(FacultyID)
);
CREATE TABLE ExamResult (
ExamResultID INT AUTO_INCREMENT PRIMARY KEY,
ExamID INT NOT NULL,
StudentID INT NOT NULL,
MarksObtained INT NOT NULL,
Grade CHAR(2),
UNIQUE (ExamID, StudentID),
FOREIGN KEY (ExamID) REFERENCES Exam(ExamID) ON DELETE CASCADE,
FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
);
CREATE TABLE ExamEvaluation (
EvaluationID INT AUTO_INCREMENT PRIMARY KEY,
ExamResultID INT NOT NULL,
FacultyID INT NOT NULL,
MarksGiven INT NOT NULL,
Comments TEXT,
EvaluatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (ExamResultID) REFERENCES ExamResult(ExamResultID) ON DELETE CASCADE,
FOREIGN KEY (FacultyID) REFERENCES Faculty(FacultyID)
);
-- ========= ATTENDANCE =========
CREATE TABLE Attendance (
AttendanceID INT AUTO_INCREMENT PRIMARY KEY,
CourseID INT NOT NULL,
StudentID INT NOT NULL,
RecordedBy INT NOT NULL,
ClassDate DATE NOT NULL,
Status ENUM('Present','Absent') NOT NULL,
VerifiedBy INT,
VerifiedAt DATETIME,
UNIQUE (CourseID, StudentID, ClassDate),
FOREIGN KEY (CourseID) REFERENCES Course(CourseID),
FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
FOREIGN KEY (RecordedBy) REFERENCES Faculty(FacultyID),
FOREIGN KEY (VerifiedBy) REFERENCES Admin(AdminID)
);
-- ========= FINANCE & REQUESTS =========
CREATE TABLE Payment (
PaymentID INT AUTO_INCREMENT PRIMARY KEY,
StudentID INT NOT NULL,
Amount DECIMAL(10,2) NOT NULL,
PaymentDate DATETIME NOT NULL,
PaymentType ENUM('Tuition','Fine','Hostel','Other') NOT NULL,
Status ENUM('Paid','Pending') NOT NULL,
FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
);
CREATE TABLE PaymentAudit (
AuditID INT AUTO_INCREMENT PRIMARY KEY,
PaymentID INT NOT NULL,
AdminID INT NOT NULL,
Action ENUM('Verified','Flagged','Adjusted','Refunded','Commented') NOT NULL,
Notes TEXT,
OccurredAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (PaymentID) REFERENCES Payment(PaymentID) ON DELETE CASCADE,
FOREIGN KEY (AdminID) REFERENCES Admin(AdminID)
);
CREATE TABLE Request (
RequestID INT AUTO_INCREMENT PRIMARY KEY,
StudentID INT NOT NULL,
RequestType ENUM('InfoUpdate','Certificate','IDReissue') NOT NULL,
RequestDate DATETIME NOT NULL,
Status ENUM('Pending','Approved','Rejected') NOT NULL,
ApprovedBy INT,
ApprovedAt DATETIME,
FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
FOREIGN KEY (ApprovedBy) REFERENCES Admin(AdminID)
);
-- ========= ANNOUNCEMENTS =========
CREATE TABLE Announcement (
AnnouncementID INT AUTO_INCREMENT PRIMARY KEY,
PostedBy INT NOT NULL,
Message TEXT NOT NULL,
DatePosted DATETIME NOT NULL,
FOREIGN KEY (PostedBy) REFERENCES Person(PersonID)
);
CREATE TABLE AnnouncementCourse (
AnnouncementID INT NOT NULL,
CourseID INT NOT NULL,
PRIMARY KEY (AnnouncementID, CourseID),
FOREIGN KEY (AnnouncementID) REFERENCES Announcement(AnnouncementID) ON DELETE CASCADE,
FOREIGN KEY (CourseID) REFERENCES Course(CourseID)
);
CREATE TABLE AnnouncementDepartment (
AnnouncementID INT NOT NULL,
DepartmentID INT NOT NULL,
PRIMARY KEY (AnnouncementID, DepartmentID),
FOREIGN KEY (AnnouncementID) REFERENCES Announcement(AnnouncementID) ON DELETE CASCADE,
FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
);
-- ========= DOCUMENTS =========
CREATE TABLE Document (
DocumentID INT AUTO_INCREMENT PRIMARY KEY,
UploadedBy INT NOT NULL,
Title VARCHAR(150) NOT NULL,
FileType VARCHAR(16) NOT NULL,
FilePath VARCHAR(255) NOT NULL,
UploadedOn DATETIME NOT NULL,
AccessLevel ENUM('Public','CourseOnly','Private') NOT NULL,
FOREIGN KEY (UploadedBy) REFERENCES Person(PersonID)
);
CREATE TABLE CourseDocument (
CourseID INT NOT NULL,
DocumentID INT NOT NULL,
PRIMARY KEY (CourseID, DocumentID),
FOREIGN KEY (CourseID) REFERENCES Course(CourseID) ON DELETE CASCADE,
FOREIGN KEY (DocumentID) REFERENCES Document(DocumentID) ON DELETE CASCADE
);
CREATE TABLE AssignmentDocument (
AssignmentID INT NOT NULL,
DocumentID INT NOT NULL,
PRIMARY KEY (AssignmentID, DocumentID),
FOREIGN KEY (AssignmentID) REFERENCES Assignment(AssignmentID) ON DELETE CASCADE,
FOREIGN KEY (DocumentID) REFERENCES Document(DocumentID) ON DELETE CASCADE
);
CREATE TABLE SubmissionDocument (
SubmissionID INT NOT NULL,
DocumentID INT NOT NULL,
PRIMARY KEY (SubmissionID, DocumentID),
FOREIGN KEY (SubmissionID) REFERENCES Submission(SubmissionID) ON DELETE CASCADE,
FOREIGN KEY (DocumentID) REFERENCES Document(DocumentID) ON DELETE CASCADE
);
CREATE TABLE PaymentDocument (
PaymentID INT NOT NULL,
DocumentID INT NOT NULL,
PRIMARY KEY (PaymentID, DocumentID),
FOREIGN KEY (PaymentID) REFERENCES Payment(PaymentID) ON DELETE CASCADE,
FOREIGN KEY (DocumentID) REFERENCES Document(DocumentID) ON DELETE CASCADE
);
CREATE TABLE RequestDocument (
RequestID INT NOT NULL,
DocumentID INT NOT NULL,
PRIMARY KEY (RequestID, DocumentID),
FOREIGN KEY (RequestID) REFERENCES Request(RequestID) ON DELETE CASCADE,
FOREIGN KEY (DocumentID) REFERENCES Document(DocumentID) ON DELETE CASCADE
);
-- ========= FEEDBACK =========
CREATE TABLE Feedback (
FeedbackID INT AUTO_INCREMENT PRIMARY KEY,
StudentID INT NOT NULL,
FacultyID INT NOT NULL,
CourseID INT NOT NULL,
Rating INT NOT NULL CHECK (Rating BETWEEN 1 AND 5),
Comments TEXT,
CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
FOREIGN KEY (FacultyID) REFERENCES Faculty(FacultyID),
FOREIGN KEY (CourseID) REFERENCES Course(CourseID)
);
CREATE INDEX idx_feedback_faculty ON Feedback(FacultyID, CourseID, CreatedAt);
CREATE INDEX idx_feedback_student ON Feedback(StudentID, CreatedAt);
-- ========= TIMETABLE =========
CREATE TABLE Timetable (
TimetableID INT AUTO_INCREMENT PRIMARY KEY,
CourseID INT NOT NULL,
DayOfWeek ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') NOT NULL,
StartTime TIME NOT NULL,
EndTime TIME NOT NULL,
RoomNo VARCHAR(20) NOT NULL,
Type ENUM('Lecture','Lab','Exam') NOT NULL,
FOREIGN KEY (CourseID) REFERENCES Course(CourseID)
);
