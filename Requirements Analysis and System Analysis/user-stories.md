# User Stories and Acceptance Criteria

Actors: Student, Faculty, Admin (primary); Payment portal and Document host (external, link only).

| ID | As a | I want to | So that | Acceptance criteria | Req | Incr |
|---|---|---|---|---|---|---|
| US-01 | User | choose my portal on a landing page | I reach the right login | Three role options shown; each opens its login | FR-01 | 1 |
| US-02 | User | log in with my email or ID and password | I see only my own data | Correct role and password opens dashboard; wrong one shows an error | FR-02, FR-05 | 1 |
| US-03 | Student | see courses, attendance %, CGPA and pending work on one dashboard | I know where I stand | All widgets load from my records | FR-S1, FR-S2 | 2 |
| US-04 | Student | submit an assignment by pasting a link | faculty can review it | Saved once per assignment; resubmission updates time; success message | FR-S3, FR-S4 | 2 |
| US-05 | Student | see marks, grade and percentage per exam | I can track performance | Rows sorted newest first | FR-S5 | 2 |
| US-06 | Student | see attendance per course | I avoid shortages | Percentage per course and overall shown | FR-S6 | 2 |
| US-07 | Student | see my weekly timetable | I know class times and rooms | Grid by day and time | FR-S7 | 2 |
| US-08 | Student | see my fees and dues | I can pay on time | Pending total equals sum of pending payments | FR-S8 | 2 |
| US-09 | Student | raise a certificate, ID or info-update request | admin can act on it | Saved as Pending and listed in history | FR-S11 | 2 |
| US-10 | Student | rate a course and comment | faculty gets feedback | Rating 1 to 5 stored against the course's faculty | FR-S10 | 2 |
| US-11 | Faculty | create an assignment with deadline and max marks | students can submit | Appears for enrolled students | FR-F3 | 3 |
| US-12 | Faculty | grade ungraded submissions with comments | students get results | Graded item leaves pending list; evaluation logged | FR-F4 | 3 |
| US-13 | Faculty | mark attendance for a course and date | records stay accurate | Duplicate student, course, date is rejected | FR-F5 | 3 |
| US-14 | Faculty | create exams and enter marks | results are available | Unknown student ID rejected; repeat entry updates marks | FR-F6 | 3 |
| US-15 | Faculty | post an announcement to a course or department | the right audience is informed | Linked to the chosen course or department | FR-F8 | 3 |
| US-16 | Admin | add and remove students and faculty | the user base is current | Person plus role row created in one transaction | FR-A2 | 4 |
| US-17 | Admin | add and remove courses | the catalogue is current | Course listed with department and semester | FR-A3 | 4 |
| US-18 | Admin | approve or reject pending requests | students get a decision | Status changes; request leaves pending list | FR-A4 | 4 |
| US-19 | Admin | see system counts on a dashboard | I can monitor usage | Students, faculty, courses, pending requests shown | FR-A1 | 4 |
| US-20 | Student | sign up for courses whose prerequisites I have met | I can plan my term | (Backlog) enrollment saved only if prerequisites passed | FR-S12 | 5 |
