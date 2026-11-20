# Student Management System

A software engineering project built with Flask and MySQL. Students submit work and view academic records, faculty manage coursework and grades, and administrators manage users, courses and requests. This repository brings the application together with Chintan Kumar Singal’s architecture, development, testing and QA deliverables.

## Repository guide

| Location | Contents |
| --- | --- |
| [app/](app/) | Gateway, three Flask portals, Jinja templates, stylesheets and images |
| [database/](database/) | MySQL setup, optional synthetic demo data and the supplied schema export |
| [Architecture and design](Architecture/Software-Architecture-and-Design.pdf) | System architecture, HLD, LLD, database design and technology choices |
| [Architecture diagrams](Architecture/diagrams/) | Editable Mermaid sources and SVG figures from the documented baseline |
| [Testing and patch release](Testing/Software-Testing-and-Patch-Release.pdf) | Test strategy, case results, defect analysis and planned fixes |
| [QA evidence and runner](Testing/baseline/README.txt) | Reproduction instructions, SQL fixtures, case results, server log and screenshots |
| [Team presentation](SMS-Integrated-SDLC.pptx) | Integrated SDLC presentation and team responsibilities |

## Source and testing baseline

The application files in `app/` come from [MukundXplore/StudentManagementSystem-DBS, commit d77c73f](https://github.com/MukundXplore/StudentManagementSystem-DBS/tree/d77c73ff499f3a638fb7976fae70dd54e4739322). This revision has four processes. The gateway listens on port 5000 and routes to Student (5001), Faculty (5002) and Admin (5003).

The design and QA documents identify their own source: the earlier three-portal `SMS-DBS-master.zip`. That archive lacked the gateway. Its verification run recorded **23 passed, 3 failed and 1 blocked** using a 22-table fixture. Those results describe that archive. Both the upstream schema and the supplied schema export define **31 tables**.

The gateway revision was also smoke-tested locally on MySQL 8.0.44 with the included setup and synthetic demo scripts. All 31 tables were created. Student, Faculty and Admin each signed in through the gateway and reached their dashboard (HTTP 200).

## Run locally

Requirements: Python 3.11, MySQL 8 and four local terminals. The examples use PowerShell from the repository root.

1. Create a virtual environment, install the application dependencies and make a private working copy for local credentials.

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   New-Item -ItemType Directory -Force .local | Out-Null
   Copy-Item -Recurse app .local/app
   ```

2. Open a MySQL client from the repository root on a fresh local instance where the database name `student_management` is available. Run:

   ```sql
   SOURCE database/setup.sql;
   SOURCE database/demo.sql;
   ```

   The first script creates the database, tables and indexes using upstream table-name casing. The optional second script creates three synthetic users and prints their local demo password. Use student ID **101**, faculty ID **201** or admin ID **301** with that password. The [supplied schema dump](database/reference/student_management_schema.sql) is retained as a reference and is a separate schema definition.

3. In the private copy under `.local/app/`, configure the MySQL user, password, host and database name in `app.py` (`dbconfig`) and the SQLAlchemy connection URIs in `faculty.py` and `admin.py`. Use `student_management` as the database name. Replace the Flask secret-key placeholders in the gateway and each portal with private local values. The portal entry files set their own connections; editing `config.py` alone does not configure them.

4. Run one command per terminal, each from the repository root:

   ```powershell
   .\.venv\Scripts\python.exe .local/app/app.py
   .\.venv\Scripts\python.exe .local/app/faculty.py
   .\.venv\Scripts\python.exe .local/app/admin.py
   .\.venv\Scripts\python.exe .local/app/main.py
   ```

   Open [the local role selector](http://127.0.0.1:5000/) and choose a portal.

