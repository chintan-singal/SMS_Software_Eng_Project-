# Requirements Traceability Matrix

Links each requirement to its user story, use case, DFD process (see `system-analysis.md`), data tables and source file. The Test column is left for Person 5 to fill in.
Source files: `app.py` student portal, `faculty.py` faculty portal, `admin.py` admin portal, `main.py` gateway (README; not read), `student_database.sql` schema.

| Req | Pri | Status | Story | Use case | DFD process | Tables | Source | Test |
|---|---|---|---|---|---|---|---|---|
| FR-01 | M | Impl | US-01 | UC-01 | 1.2 | none | main.py | TBD |
| FR-02 | M | Impl | US-02 | UC-01 | 1.1 | Person, Student, Faculty, Admin | all portals | TBD |
| FR-03 | M | Impl | US-02 | UC-01 | 1.1 | none (session) | all portals | TBD |
| FR-04 | M | Impl | US-02 | UC-01 | 1.1 | none (session) | all portals | TBD |
| FR-05 | M | Impl | US-02 | UC-01 | 1.1 | Person | all portals | TBD |
| FR-S1 | M | Impl | US-03 | none | 2.x, 4.1 | Student, Enrollment, Course, Teaches, Submission, Attendance, ExamResult, Announcement | app.py | TBD |
| FR-S2 | M | Impl | US-03 | none | 2.1 | Course, Enrollment, Teaches | app.py | TBD |
| FR-S3 | M | Impl | US-04 | UC-02 | 2.2 | Assignment, Submission | app.py | TBD |
| FR-S4 | M | Impl | US-04 | UC-02 | 2.2 | Document, Submission, SubmissionDocument | app.py | TBD |
| FR-S5 | M | Impl | US-05 | none | 2.3 | Exam, ExamResult | app.py | TBD |
| FR-S6 | M | Impl | US-06 | none | 2.4 | Attendance, Enrollment | app.py | TBD |
| FR-S7 | S | Impl | US-07 | none | 2.5 | Timetable, Enrollment | app.py | TBD |
| FR-S8 | S | Impl | US-08 | none | 3.3 | Payment | app.py | TBD |
| FR-S9 | C | Impl | none | none | 4.1 | Announcement | app.py | TBD |
| FR-S10 | S | Impl | US-10 | none | 4.2 | Feedback, Teaches | app.py | TBD |
| FR-S11 | M | Impl | US-09 | UC-05 | 3.2 | Request | app.py | TBD |
| FR-S12 | S | Plan | US-20 | none | 2.1 | Enrollment, Prerequisite | none yet | TBD |
| FR-F1 | M | Impl | none | none | 2.x, 4.2 | Teaches, Enrollment, Submission, Feedback, Announcement | faculty.py | TBD |
| FR-F2 | M | Impl | none | none | 2.1 | Teaches, Enrollment, Student | faculty.py | TBD |
| FR-F3 | M | Impl | US-11 | none | 2.2 | Assignment | faculty.py | TBD |
| FR-F4 | M | Impl | US-12 | UC-03 | 2.2 | Submission, SubmissionEvaluation, Document | faculty.py | TBD |
| FR-F5 | M | Impl | US-13 | UC-04 | 2.4 | Attendance | faculty.py | TBD |
| FR-F6 | M | Impl | US-14 | UC-07 | 2.3 | Exam, ExamResult | faculty.py | TBD |
| FR-F7 | S | Impl | none | none | 4.2 | Feedback | faculty.py | TBD |
| FR-F8 | S | Impl | US-15 | UC-08 | 4.1 | Announcement, AnnouncementCourse, AnnouncementDepartment | faculty.py | TBD |
| FR-F9 | S | Impl | none | none | 4.1 | Document, CourseDocument | faculty.py | TBD |
| FR-F10 | M | Plan | none | UC-07 | 2.3 | ExamResult, ExamEvaluation | none yet | TBD |
| FR-A1 | M | Impl | US-19 | none | 3.1 | Student, Faculty, Course, Request | admin.py | TBD |
| FR-A2 | M | Impl | US-16 | UC-06 | 3.1 | Person, Student, Faculty | admin.py | TBD |
| FR-A3 | M | Impl | US-17 | none | 2.1 | Course | admin.py | TBD |
| FR-A4 | M | Impl | US-18 | UC-05 | 3.2 | Request | admin.py | TBD |
| FR-A5 | S | Impl | none | UC-08 | 4.1 | Announcement | admin.py | TBD |
| FR-A6 | C | Plan | none | none | 2.4 | Attendance | none yet | TBD |
| FR-A7 | C | Plan | none | none | 3.3 | Payment, PaymentAudit | none yet | TBD |
| FR-A8 | C | Plan | none | none | 2.1, 2.5 | Department, Program, Prerequisite, Timetable | none yet | TBD |

## Non-functional requirements to design and test
| NFR | Addressed in | Open item |
|---|---|---|
| NFR-SEC-01 | Session role checks in each portal | Test for cross-role access |
| NFR-SEC-02 | Not met | Change request: hash passwords |
| NFR-SEC-03 | Not met | Change request: POST deletes, environment secrets |
| NFR-REL-01 | Student submission transaction | Test rollback |
| NFR-INT-01 | Schema keys and UNIQUE constraints | Test duplicate rejection |
| NFR-PERF-01, NFR-AVL-01 | Not measured / not met | Test plan and launcher script |

## Coverage summary
35 functional requirements: 30 Impl, 5 Plan. Every Must requirement has a use case or a DFD process and at least one source file, except the planned FR-F10.
