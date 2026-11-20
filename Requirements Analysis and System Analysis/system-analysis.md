# System Analysis: Context Diagram and DFD Levels 0, 1 and 2

One diagram per level for the whole system. Numbering is consistent: process 0 (context) is exploded into 1.0 to 4.0 (Level 0), each of those into x.1, x.2 (Level 1), and process 2.2 into 2.2.1 to 2.2.7 (Level 2). GitHub renders the Mermaid blocks below.

## Context diagram
```mermaid
flowchart LR
  ST[Student] <-->|"login, submissions, requests, feedback / dashboard, grades, attendance, fees"| SMS(("0<br/>Student Management<br/>System"))
  FA[Faculty] <-->|"assignments, marks, attendance, notices / courses, students, submissions, feedback"| SMS
  AD[Admin] <-->|"users, courses, approvals, notices / counts, lists, pending requests"| SMS
  SMS -->|"portal links"| PP[["Payment portal (external)"]]
  DH[["Document host (external)"]] -->|"shared file links"| SMS
```

## DFD Level 0
```mermaid
flowchart LR
  ST[Student]
  FA[Faculty]
  AD[Admin]
  P1(("1.0 Authenticate and Route"))
  P2(("2.0 Academic Management"))
  P3(("3.0 Administration"))
  P4(("4.0 Communication"))
  DB[("DB: MySQL database, 31 tables")]
  ST & FA & AD <-->|"credentials, session"| P1
  ST & FA <-->|"coursework, attendance, marks, results"| P2
  ST & AD <-->|"requests, fees, users, approvals"| P3
  ST & FA & AD <-->|"announcements, documents, feedback"| P4
  P1 <--> DB
  P2 <--> DB
  P3 <--> DB
  P4 <--> DB
```

## DFD Level 1 (all four processes exploded)
```mermaid
flowchart LR
  ST[Student]
  FA[Faculty]
  AD[Admin]
  subgraph G1["1.0 Authenticate and Route"]
    P11(("1.1 Authenticate user"))
    P12(("1.2 Route to portal"))
  end
  subgraph G2["2.0 Academic Management"]
    P21(("2.1 Manage courses"))
    P22(("2.2 Assignments and grading"))
    P23(("2.3 Exams and results"))
    P24(("2.4 Attendance"))
    P25(("2.5 Timetable"))
  end
  subgraph G3["3.0 Administration"]
    P31(("3.1 Manage users"))
    P32(("3.2 Requests and approvals"))
    P33(("3.3 Fees and payments"))
  end
  subgraph G4["4.0 Communication"]
    P41(("4.1 Announcements and documents"))
    P42(("4.2 Feedback"))
  end
  D1[("D1 Users")]
  D2[("D2 Courses")]
  D3[("D3 Assignments")]
  D4[("D4 Exams")]
  D5[("D5 Attendance")]
  D6[("D6 Requests, Payments")]
  D7[("D7 Announcements, Documents")]
  D8[("D8 Feedback")]
  D9[("D9 Timetable")]
  ST & FA & AD --> P12 --> P11
  ST --> P22 & P23 & P24 & P25 & P32 & P33 & P41 & P42
  FA --> P21 & P22 & P23 & P24 & P41 & P42
  AD --> P21 & P31 & P32 & P41
  P11 <--> D1
  P31 <--> D1
  P21 <--> D2
  P22 <--> D3
  P23 <--> D4
  P24 <--> D5
  P25 --> D9
  P32 <--> D6
  P33 <--> D6
  P41 <--> D7
  P42 <--> D8
```
Student also reads D2 through 2.1 when viewing courses; faculty reads D2 for course and student lists. Those links are omitted from the picture to keep it readable.

## DFD Level 2 (process 2.2 Assignments and grading)
```mermaid
flowchart LR
  ST[Student]
  FA[Faculty]
  P221(("2.2.1 Create assignment"))
  P222(("2.2.2 View assignments"))
  P223(("2.2.3 Save submission"))
  P224(("2.2.4 Save document link"))
  P225(("2.2.5 List ungraded submissions"))
  P226(("2.2.6 Grade submission"))
  P227(("2.2.7 View marks"))
  DA[("D3 Assignment")]
  DS[("D3 Submission")]
  DE[("D3 SubmissionEvaluation")]
  DD[("D7 Document")]
  FA -->|"course, title, deadline, max marks"| P221 --> DA
  DA --> P222 -->|"assignments with status"| ST
  ST -->|"assignment ID"| P223 --> DS
  ST -->|"document link"| P224 --> DD
  DS --> P225
  DD --> P225
  P225 -->|"ungraded list, link"| FA
  FA -->|"marks, comments"| P226
  P226 --> DS
  P226 --> DE
  DS --> P227 -->|"marks"| ST
```
Steps 2.2.3 and 2.2.4 run in one database transaction, so a failure rolls both back.

## Data store catalogue
| Store | Name | Tables |
|---|---|---|
| D1 | Users | Person, Student, Faculty, Admin, Department, Program |
| D2 | Courses | Course, Teaches, Enrollment, Prerequisite |
| D3 | Assignments | Assignment, Submission, SubmissionEvaluation (+ SubmissionDocument, AssignmentDocument) |
| D4 | Exams | Exam, ExamResult, ExamEvaluation |
| D5 | Attendance | Attendance |
| D6 | Requests, Payments | Request, Payment, PaymentAudit (+ RequestDocument, PaymentDocument) |
| D7 | Announcements, Documents | Announcement, AnnouncementCourse, AnnouncementDepartment, Document, CourseDocument |
| D8 | Feedback | Feedback |
| D9 | Timetable | Timetable |
