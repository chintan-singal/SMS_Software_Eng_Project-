# Software Requirements Specification (SRS): Student Management System (SMS)

Owner: Person 2 (Requirements Engineer and System Analyst) | Version 1.0 | Source: `StudentManagementSystem-DBS`

## 1. Introduction
**Purpose.** Specify what SMS must do and how well, as input to design, implementation and testing.
**Scope.** A web application with three role-based portals (Student, Faculty, Admin) behind one gateway, sharing one MySQL database (`student_management`, 31 tables).
**Definitions.** PK = primary key, FK = foreign key, CGPA = cumulative grade point average, MoSCoW = Must/Should/Could priority.
**References.** Repository README, `student_database.sql`, `app.py`, `faculty.py`, `admin.py`.

## 2. Overall Description
| Item | Description |
|---|---|
| Product perspective | Browser client, Flask servers (gateway 5000, student 5001, faculty 5002, admin 5003), MySQL database |
| User classes | Student, Faculty, Admin (SuperAdmin, DeptAdmin, FinanceAdmin) |
| Operating environment | Python 3, Flask, MySQL 8, modern browser; Windows, Linux or macOS |
| Assumptions | Admins create users (no self sign-up); one seeded program (B.Tech CSE); a course can have several faculty |
| Constraints | MySQL as DBMS; Python/Flask stack; separate session cookie per portal |
| Seed data | 42 students, 13 faculty, 2 admins, 15 courses (the SQL comment says 50 students but 42 rows exist) |

## 3. Functional Requirements
Priority: **M** Must, **S** Should, **C** Could. Status: **Impl** found in code, **Plan** planned or schema-only.

### 3.1 Login and gateway
| ID | Requirement | Pri | Status |
|---|---|---|---|
| FR-01 | Landing page lets the user choose Student, Faculty or Admin portal | M | Impl (README) |
| FR-02 | Authenticate by email or ID and password, and verify the role matches the portal | M | Impl |
| FR-03 | Protected pages redirect unauthenticated users to login | M | Impl |
| FR-04 | Logout clears the session | M | Impl |
| FR-05 | Failed login shows an error message | M | Impl |

### 3.2 Student portal
| ID | Requirement | Pri | Status |
|---|---|---|---|
| FR-S1 | Dashboard: program, enrolled courses with faculty, pending assignments, attendance %, CGPA, latest 5 announcements, recent graded work | M | Impl |
| FR-S2 | View enrolled courses (name, credits, semester, faculty) | M | Impl |
| FR-S3 | View assignments as pending and completed with deadline and marks | M | Impl |
| FR-S4 | Submit an assignment by document link; resubmission updates the time | M | Impl |
| FR-S5 | View exam results with marks, grade and percentage | M | Impl |
| FR-S6 | View per-course and overall attendance percentage | M | Impl |
| FR-S7 | View weekly timetable grid | S | Impl |
| FR-S8 | View payments, total pending dues and payment portal links | S | Impl |
| FR-S9 | Open an announcement in detail | C | Impl |
| FR-S10 | Submit course feedback (rating 1 to 5, comment) | S | Impl |
| FR-S11 | Raise InfoUpdate / Certificate / IDReissue requests and view history | M | Impl |
| FR-S12 | Sign up for a course with prerequisite check | S | Plan (README mentions it; no route found) |

### 3.3 Faculty portal
| ID | Requirement | Pri | Status |
|---|---|---|---|
| FR-F1 | Dashboard: course count, distinct student count, ungraded submissions, last 3 feedback, own announcements | M | Impl |
| FR-F2 | View courses taught and enrolled students (filter by course) | M | Impl |
| FR-F3 | Create assignments (course, title, description, deadline, max marks) | M | Impl |
| FR-F4 | View ungraded submissions with document link; grade with marks and comments; log in SubmissionEvaluation | M | Impl |
| FR-F5 | Mark attendance per student, course and date; reject duplicates | M | Impl |
| FR-F6 | Create exams (Midterm, Final, Quiz) and enter or update marks; validate the student exists | M | Impl |
| FR-F7 | View feedback given by students | S | Impl |
| FR-F8 | Post announcements scoped to a course or department | S | Impl |
| FR-F9 | Share documents by link, optionally attached to a course | S | Impl |
| FR-F10 | Auto-compute letter grade from marks and record ExamEvaluation | M | Plan (Grade is never set today, so CGPA ignores new results) |

### 3.4 Admin portal
| ID | Requirement | Pri | Status |
|---|---|---|---|
| FR-A1 | Dashboard counts: students, faculty, courses, pending requests | M | Impl |
| FR-A2 | Add Student or Faculty, search users, delete user | M | Impl |
| FR-A3 | Add, search and delete courses | M | Impl |
| FR-A4 | Approve or reject pending requests | M | Impl (ApprovedBy/ApprovedAt not set) |
| FR-A5 | Post and list announcements | S | Impl |
| FR-A6 | Verify attendance records (VerifiedBy) | C | Plan |
| FR-A7 | Audit payments (verify, flag, adjust, refund, comment) | C | Plan |
| FR-A8 | Manage departments, programs, prerequisites, timetable | C | Plan |

**Totals:** 35 requirements: 23 Must, 8 Should, 4 Could. 30 implemented, 5 planned (FR-S12, FR-F10, FR-A6, FR-A7, FR-A8).

## 4. Non-Functional Requirements
| ID | Category | Requirement | Current state |
|---|---|---|---|
| NFR-SEC-01 | Security | Each portal serves only its own role | Met (session role check) |
| NFR-SEC-02 | Security | Passwords stored as salted hashes | **Not met** (plain text in `Person.Password`) |
| NFR-SEC-03 | Security | State changes use POST with CSRF protection; secrets from environment variables | **Not met** (delete links use GET; keys hard-coded) |
| NFR-PERF-01 | Performance | Typical page loads in under 3 s for 50 concurrent users | Not measured |
| NFR-USE-01 | Usability | One dashboard per role, consistent navigation | Prototype-validated |
| NFR-REL-01 | Reliability | Multi-step writes are transactional with rollback | Met in student submission |
| NFR-INT-01 | Data integrity | Foreign keys and unique pairs: enrollment, submission, exam result, attendance per date | Met in schema |
| NFR-MNT-01 | Maintainability | Modular files per role; shared configuration | Partly (DB settings repeated) |
| NFR-POR-01 | Portability | Windows, Linux, macOS with Python 3 and MySQL | Met |
| NFR-AVL-01 | Availability | One launcher for the four services | Not met (four manual commands) |

## 5. External Interfaces
| Interface | Description |
|---|---|
| User interface | Browser pages rendered by Flask templates |
| Software interface | Flask apps to MySQL via `mysql.connector` (student) and SQLAlchemy (faculty, admin) |
| External services | Payment portals (links only), document hosting (URLs only) |
