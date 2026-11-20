from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import pooling
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY"
app.config['SESSION_COOKIE_NAME'] = 'student_session'

# --------------------- DATABASE CONFIGURATION ---------------------
dbconfig = {
    "user": "root",
    "password": "YOUR_PASSWORD",
    "host": "localhost",
    "database": "YOUR_DB_NAME"
}

# Connection Pool
cnxpool = pooling.MySQLConnectionPool(
    pool_name="student_pool",
    pool_size=5,
    **dbconfig
)

def get_connection():
    return cnxpool.get_connection()

# --------------------- LOGIN REQUIRED DECORATOR ---------------------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "student_id" not in session:
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrapper

# --------------------- CONTEXT PROCESSOR ---------------------
@app.context_processor
def inject_user():
    return dict(user_name=session.get('student_name'))

# -----------------------------------------------------------
#                       AUTHENTICATION
# -----------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("student/login.html")

@app.route("/student/login", methods=["POST"], endpoint='student_login')
def login():
    student_id_input = request.form.get("student_id")
    password_input = request.form.get("password")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT PersonID, Name, Role, Password
        FROM Person 
        WHERE (Email = %s OR PersonID = %s) AND Role = 'Student'
    """, (student_id_input, student_id_input))

    user = cursor.fetchone()

    student_details = None
    if user:
        cursor.execute("SELECT ProgramID, Semester FROM Student WHERE StudentID = %s", (user['PersonID'],))
        student_details = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and user['Password'] == password_input:
        session['student_id'] = user['PersonID']
        session['student_name'] = user['Name']
        session['role'] = 'Student'
        if student_details:
            session['program_id'] = student_details['ProgramID']
            session['semester'] = student_details['Semester']
        return redirect(url_for('student_dashboard'))
    else:
        flash("Invalid Credentials or Access Denied.", "danger")
        return redirect(url_for('index'))

@app.route("/student/logout", endpoint='student_logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

# -----------------------------------------------------------
#                       DASHBOARD
# -----------------------------------------------------------
@app.route("/student/dashboard", endpoint='student_dashboard')
@login_required
def dashboard():
    sid = session["student_id"]
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.ProgramName 
        FROM Program p 
        JOIN Student s ON s.ProgramID = p.ProgramID 
        WHERE s.StudentID = %s
    """, (sid,))
    prog = cursor.fetchone()
    program_name = prog['ProgramName'] if prog else "N/A"

    cursor.execute("""
        SELECT c.CourseName, p.Name as faculty_name
        FROM Enrollment e
        JOIN Course c ON c.CourseID = e.CourseID
        LEFT JOIN Teaches t ON t.CourseID = c.CourseID
        LEFT JOIN Person p ON p.PersonID = t.FacultyID
        WHERE e.StudentID = %s
    """, (sid,))
    courses = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*) as cnt
        FROM Assignment a
        JOIN Enrollment e ON e.CourseID = a.CourseID
        LEFT JOIN Submission s ON s.AssignmentID = a.AssignmentID AND s.StudentID = e.StudentID
        WHERE e.StudentID = %s AND s.SubmissionID IS NULL
    """, (sid,))
    pending_tasks = cursor.fetchone()['cnt']

    cursor.execute("""
        SELECT c.CourseID, 
               SUM(CASE WHEN a.Status='Present' THEN 1 ELSE 0 END) as attended,
               COUNT(a.AttendanceID) as total
        FROM Enrollment e
        JOIN Course c ON c.CourseID = e.CourseID
        LEFT JOIN Attendance a ON a.CourseID = c.CourseID AND a.StudentID = e.StudentID
        WHERE e.StudentID = %s
        GROUP BY c.CourseID
    """, (sid,))
    att_data = cursor.fetchall()
    
    total_pct = 0
    if att_data:
        course_pcts = []
        for rec in att_data:
            if rec['total'] > 0:
                course_pcts.append((float(rec['attended']) / float(rec['total'])) * 100)
            else:
                course_pcts.append(0)
        total_pct = round(sum(course_pcts) / len(course_pcts), 2)

    cursor.execute("""
        SELECT Message, DatePosted 
        FROM Announcement 
        ORDER BY DatePosted DESC LIMIT 5
    """)
    announcements = cursor.fetchall()

    cursor.execute("SELECT Grade FROM ExamResult WHERE StudentID = %s", (sid,))
    results = cursor.fetchall()

    grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
    total_points = 0.0
    valid_grades = 0
    
    for r in results:
        if r['Grade']:
            base = str(r['Grade']).strip()[0].upper() 
            if base in grade_points:
                total_points += grade_points[base]
                valid_grades += 1
    
    cgpa = round(total_points / valid_grades, 2) if valid_grades > 0 else 0.0

    # Fetch recent graded assignments
    cursor.execute("""
        SELECT a.Title, a.MaxMarks, c.CourseName, s.Marks as obtained_marks, s.SubmittedAt
        FROM Submission s
        JOIN Assignment a ON s.AssignmentID = a.AssignmentID
        JOIN Course c ON a.CourseID = c.CourseID
        WHERE s.StudentID = %s AND s.Marks IS NOT NULL
        ORDER BY s.SubmittedAt DESC LIMIT 5
    """, (sid,))
    recent_assignments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("student/dashboard.html",
                           user_program=program_name,
                           courses=courses,
                           pending_tasks=pending_tasks,
                           attendance=total_pct,
                           announcements=announcements,
                           cgpa=cgpa,
                           recent_assignments=recent_assignments,
                           current_date=datetime.now().strftime("%B %d, %Y"))

# -----------------------------------------------------------
#                       COURSES
# -----------------------------------------------------------
@app.route("/student/courses", endpoint='student_courses')
@login_required
def student_courses():
    sid = session["student_id"]
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.CourseID, c.CourseName, c.Credits, c.Semester,
               p.Name as faculty_name
        FROM Enrollment e
        JOIN Course c ON c.CourseID = e.CourseID
        LEFT JOIN Teaches t ON t.CourseID = c.CourseID
        LEFT JOIN Person p ON p.PersonID = t.FacultyID
        WHERE e.StudentID = %s
    """, (sid,))
    my_courses = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("student/courses.html", courses=my_courses)

# -----------------------------------------------------------
#               ASSIGNMENTS & SUBMISSION
# -----------------------------------------------------------
@app.route("/student/assignments", endpoint='student_assignments')
@login_required
def assignments():
    sid = session["student_id"]
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.AssignmentID, a.Title, a.Description, a.MaxMarks, 
               DATE_FORMAT(a.Deadline, '%d %b %Y') as Deadline,
               c.CourseName,
               s.SubmissionID, s.SubmittedAt, s.Marks as obtained_marks
        FROM Enrollment e
        JOIN Assignment a ON a.CourseID = e.CourseID
        JOIN Course c ON c.CourseID = a.CourseID
        LEFT JOIN Submission s ON s.AssignmentID = a.AssignmentID AND s.StudentID = e.StudentID
        WHERE e.StudentID = %s
        ORDER BY a.Deadline DESC
    """, (sid,))
    all_assignments = cursor.fetchall()

    cursor.close()
    conn.close()

    pending = [x for x in all_assignments if not x['SubmissionID']]
    completed = [x for x in all_assignments if x['SubmissionID']]

    return render_template("student/assignments.html",
                           pending_assignments=pending,
                           completed_assignments=completed)

@app.route("/student/submit_assignment", methods=["POST"], endpoint='student_submit_assignment')
@login_required
def submit_assignment():
    sid = session["student_id"]
    aid = request.form.get("assignment_id")
    link = request.form.get("document_link")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Document (UploadedBy, Title, FileType, FilePath, UploadedOn, AccessLevel)
            VALUES (%s, %s, 'link', %s, NOW(), 'Private')
        """, (sid, f"Submission for Assign {aid}", link))
        doc_id = cursor.lastrowid

        cursor.execute("SELECT SubmissionID FROM Submission WHERE AssignmentID=%s AND StudentID=%s",
                       (aid, sid))
        existing = cursor.fetchone()

        if existing:
            sub_id = existing[0]
            cursor.execute("UPDATE Submission SET SubmittedAt=NOW() WHERE SubmissionID=%s", (sub_id,))
        else:
            cursor.execute("""
                INSERT INTO Submission (AssignmentID, StudentID, SubmittedAt)
                VALUES (%s, %s, NOW())
            """, (aid, sid))
            sub_id = cursor.lastrowid

        cursor.execute("INSERT INTO SubmissionDocument (SubmissionID, DocumentID) VALUES (%s, %s)",
                       (sub_id, doc_id))

        conn.commit()
        flash("Assignment Submitted Successfully!", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error: {e}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("student_assignments"))

# -----------------------------------------------------------
#                       GRADES
# -----------------------------------------------------------
@app.route("/student/grades", endpoint='student_grades')
@login_required
def grades():
    sid = session["student_id"]
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.CourseName, ex.ExamType, ex.MaxMarks, er.MarksObtained, er.Grade, ex.ExamDate
        FROM ExamResult er
        JOIN Exam ex ON er.ExamID = ex.ExamID
        JOIN Course c ON c.CourseID = ex.CourseID
        WHERE er.StudentID = %s
        ORDER BY ex.ExamDate DESC
    """, (sid,))
    grades_data = cursor.fetchall()

    for g in grades_data:
        if g['MarksObtained'] is not None:
            g['percentage'] = round((float(g['MarksObtained']) / float(g['MaxMarks'])) * 100, 1)
        else:
            g['percentage'] = 0

    cursor.close()
    conn.close()
    return render_template("student/grades.html", grades=grades_data)

# -----------------------------------------------------------
#                       ATTENDANCE
# -----------------------------------------------------------
@app.route("/student/attendance", endpoint='student_attendance')
@login_required
def attendance():
    sid = session["student_id"]
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.CourseID, c.CourseName,
               SUM(CASE WHEN a.Status='Present' THEN 1 ELSE 0 END) as classes_attended,
               COUNT(a.AttendanceID) as total_classes
        FROM Enrollment e
        JOIN Course c ON c.CourseID = e.CourseID
        LEFT JOIN Attendance a ON a.CourseID = c.CourseID AND a.StudentID = e.StudentID
        WHERE e.StudentID = %s
        GROUP BY c.CourseID
    """, (sid,))
    records = cursor.fetchall()

    for r in records:
        if r['total_classes'] > 0:
            r['pct'] = round((float(r['classes_attended']) / float(r['total_classes'])) * 100, 1)
        else:
            r['pct'] = 0.0

    overall = 0
    if records:
        overall = round(sum(r['pct'] for r in records) / len(records), 1)

    cursor.close()
    conn.close()
    return render_template("student/attendance.html",
                           attendance_records=records,
                           overall_attendance=overall)

# -----------------------------------------------------------
#                       TIMETABLE
# -----------------------------------------------------------
@app.route("/student/timetable", endpoint='student_timetable')
@login_required
def timetable():
    sid = session["student_id"]
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT t.DayOfWeek, t.StartTime, t.EndTime, t.RoomNo, c.CourseName
        FROM Timetable t
        JOIN Enrollment e ON e.CourseID = t.CourseID
        JOIN Course c ON c.CourseID = t.CourseID
        WHERE e.StudentID = %s
        ORDER BY t.DayOfWeek, t.StartTime
    """, (sid,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    # Create schedule_by_day dict
    schedule_by_day = {day: {} for day in days}
    time_slots = set()
    
    for r in rows:
        day = r['DayOfWeek']
        time_slot = f"{str(r['StartTime'])[:5]} - {str(r['EndTime'])[:5]}"
        time_slots.add(time_slot)
        
        if day in schedule_by_day:
            schedule_by_day[day][time_slot] = {
                "CourseName": r["CourseName"],
                "RoomNo": r["RoomNo"]
            }
    
    time_slots = sorted(list(time_slots))

    return render_template("student/timetable.html",
                           schedule_by_day=schedule_by_day,
                           time_slots=time_slots,
                           days=days)

# -----------------------------------------------------------
#                       FEES
# -----------------------------------------------------------
@app.route("/student/fees", endpoint='student_fees')
@login_required
def fees():
    sid = session["student_id"]
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT PaymentID, Amount, PaymentDate, PaymentType, Status
        FROM Payment
        WHERE StudentID = %s
        ORDER BY PaymentDate DESC
    """, (sid,))
    payments = cursor.fetchall()

    cursor.close()
    conn.close()

    total_due = sum(float(p['Amount']) for p in payments if p['Status'] == 'Pending')

    return render_template("student/fees.html",
                           payments=payments,
                           total_due=total_due)


# -----------------------------------------------------------
#                    PAYMENT PORTALS
# -----------------------------------------------------------
@app.route("/student/payment_portals", endpoint='student_payment_portals')
@login_required
def payment_portals():
    invoice = request.args.get('invoice')
    # Simple static list for portals; replace with DB-driven list if available
    portals = [
        {"name": "Bank Transfer", "url": "https://www.examplebank.com/portal"},
        {"name": "UPI/QR", "url": "https://www.exampleupi.com/pay"}
    ]
    return render_template('student/payment_portals.html', portals=portals, invoice=invoice)


# -----------------------------------------------------------
#                    ANNOUNCEMENT DETAIL
# -----------------------------------------------------------
@app.route('/student/announcement/<int:announcement_id>', endpoint='student_announcement')
@login_required
def student_announcement(announcement_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT AnnouncementID, Message, DatePosted, PostedBy as PostedByID FROM Announcement WHERE AnnouncementID = %s", (announcement_id,))
    ann = cursor.fetchone()
    # Try to fetch poster name if available
    if ann and ann.get('PostedByID'):
        cursor.execute("SELECT Name FROM Person WHERE PersonID = %s", (ann['PostedByID'],))
        poster = cursor.fetchone()
        ann['PostedByName'] = poster['Name'] if poster else None

    cursor.close()
    conn.close()
    if not ann:
        return redirect(url_for('student_dashboard'))
    return render_template('student/announcement.html', announcement=ann)

# -----------------------------------------------------------
#                       FEEDBACK
# -----------------------------------------------------------
@app.route("/student/feedback", methods=["GET", "POST"], endpoint='student_feedback')
@login_required
def feedback():
    sid = session["student_id"]
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        cid = request.form.get("course_id")
        rating = request.form.get("rating")
        comment = request.form.get("comments")

        cursor.execute("SELECT FacultyID FROM Teaches WHERE CourseID = %s LIMIT 1", (cid,))
        fac = cursor.fetchone()

        if fac:
            try:
                cursor.execute("""
                    INSERT INTO Feedback (StudentID, FacultyID, CourseID, Rating, Comments)
                    VALUES (%s, %s, %s, %s, %s)
                """, (sid, fac['FacultyID'], cid, rating, comment))
                conn.commit()
                flash("Feedback Submitted!", "success")
            except Exception as e:
                conn.rollback()
                flash(f"Error: {e}", "danger")
        else:
            flash("No faculty assigned to this course.", "warning")

    cursor.execute("""
        SELECT c.CourseID, c.CourseName
        FROM Enrollment e
        JOIN Course c ON c.CourseID = e.CourseID
        WHERE e.StudentID = %s
    """, (sid,))
    courses = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("student/feedback.html", courses=courses)

# -----------------------------------------------------------
#                       REQUESTS
# -----------------------------------------------------------
@app.route("/student/request", methods=["GET", "POST"], endpoint='student_request')
@login_required
def request_page():
    sid = session["student_id"]
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        rtype = request.form.get("request_type")
        try:
            cursor.execute("""
                INSERT INTO Request (StudentID, RequestType, RequestDate, Status)
                VALUES (%s, %s, NOW(), 'Pending')
            """, (sid, rtype))
            conn.commit()
            flash("Request Created!", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()
        
        # Redirect to GET to prevent form resubmission on page reload
        return redirect(url_for('student_request'))

    cursor.execute("""
        SELECT * FROM Request
        WHERE StudentID = %s
        ORDER BY RequestDate DESC
    """, (sid,))
    req_history = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("student/request.html", requests=req_history)

# -----------------------------------------------------------
#                       START SERVER
# -----------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
