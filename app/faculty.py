from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'
app.config['SESSION_COOKIE_NAME'] = 'faculty_session'

# ==========================================
# DATABASE CONFIGURATION
# ==========================================
# Updated with the password you provided: 'YOUR_PASSWORD'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:YOUR_PASSWORD@localhost/YOUR_DB_NAME'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# MODELS
# ==========================================
class Person(db.Model):
    __tablename__ = 'Person'
    PersonID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Role = db.Column(db.Enum('Student', 'Faculty', 'Admin'), nullable=False)

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_faculty_profile(user_id):
    """Fetches the detailed profile required by the sidebar/header."""
    sql = text("""
        SELECT P.Name as FullName, P.Email, D.DeptName as Department, 
               SUBSTRING_INDEX(P.Name, ' ', 1) as FirstName
        FROM Person P
        JOIN Faculty F ON P.PersonID = F.FacultyID
        JOIN Department D ON F.DepartmentID = D.DepartmentID
        WHERE P.PersonID = :uid
    """)
    result = db.session.execute(sql, {'uid': user_id}).fetchone()
    return result

def get_my_courses(user_id):
    """Fetches courses taught by the logged-in faculty."""
    sql = text("""
        SELECT C.CourseID, C.CourseName
        FROM Course C
        JOIN Teaches T ON C.CourseID = T.CourseID
        WHERE T.FacultyID = :uid
    """)
    return db.session.execute(sql, {'uid': user_id}).fetchall()

# ==========================================
# ROUTES
# ==========================================

# --- LOGIN ---
@app.route('/')
def index():
    return render_template('faculty/login.html')

@app.route('/faculty/login', methods=['POST'])
def login():
    login_id = request.form.get('facultyId')
    password = request.form.get('password')

    user = Person.query.filter(
        (Person.Email == login_id) | (Person.PersonID == login_id)
    ).first()

    if user and user.Password == password:
        if user.Role == 'Faculty':
            session['user_id'] = user.PersonID
            session['role'] = user.Role
            return redirect(url_for('dashboard'))
        else:
            flash("Access Denied. Faculty portal only.")
    else:
        flash("Invalid Credentials.")
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# --- DASHBOARD ---
@app.route('/faculty/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('index'))
    
    fid = session['user_id']
    faculty = get_faculty_profile(fid)
    
    # 1. Stats Queries
    # Count Active Courses
    count_courses = db.session.execute(text("SELECT COUNT(*) FROM Teaches WHERE FacultyID=:fid"), {'fid':fid}).scalar()
    
    # Count Total Students
    count_students = db.session.execute(text("SELECT COUNT(DISTINCT StudentID) FROM Enrollment E JOIN Teaches T ON E.CourseID=T.CourseID WHERE T.FacultyID=:fid"), {'fid':fid}).scalar()
    
    # Count Pending Submissions (Marks IS NULL)
    count_pending = db.session.execute(text("""
        SELECT COUNT(*) 
        FROM Submission S 
        JOIN Assignment A ON S.AssignmentID = A.AssignmentID 
        WHERE A.CreatedBy = :fid AND S.Marks IS NULL
    """), {'fid':fid}).scalar()

    stats = {
        "total_courses": count_courses,
        "total_students": count_students,
        "pending_submissions": count_pending 
    }

    # 2. Courses List
    sql_courses = text("""
        SELECT C.CourseID, C.CourseName, C.Semester, C.Credits, D.DeptName
        FROM Course C
        JOIN Teaches T ON C.CourseID = T.CourseID
        JOIN Department D ON C.DepartmentID = D.DepartmentID
        WHERE T.FacultyID = :fid
    """)
    courses = db.session.execute(sql_courses, {'fid': fid}).fetchall()

    # 3. Recent Feedback
    sql_feedback = text("SELECT Comments, Rating FROM Feedback WHERE FacultyID = :fid ORDER BY CreatedAt DESC LIMIT 3")
    feedback = db.session.execute(sql_feedback, {'fid': fid}).fetchall()

    # 4. Announcements
    sql_ann = text("""
        SELECT Message, DatePosted, 
               CASE WHEN CourseID IS NOT NULL THEN 'Course' ELSE 'Department' END as TargetID
        FROM Announcement A
        LEFT JOIN AnnouncementCourse AC ON A.AnnouncementID = AC.AnnouncementID
        WHERE A.PostedBy = :fid ORDER BY DatePosted DESC LIMIT 3
    """)
    announcements = db.session.execute(sql_ann, {'fid': fid}).fetchall()

    return render_template('faculty/dashboard.html', 
                           faculty=faculty, 
                           stats=stats, 
                           courses=courses, 
                           feedback=feedback,
                           announcements=announcements,
                           current_date=datetime.now().strftime("%B %d, %Y"))


# --- COURSES ---
@app.route('/faculty/courses')
def courses():
    if 'user_id' not in session: return redirect(url_for('index'))
    fid = session['user_id']
    faculty = get_faculty_profile(fid)

    sql = text("""
        SELECT C.CourseID, C.CourseName, 
               CONCAT(D.DeptCode, '-', C.CourseID) as CourseCode, 
               C.Credits, C.Semester, D.DeptName as DepartmentName
        FROM Course C
        JOIN Teaches T ON C.CourseID = T.CourseID
        JOIN Department D ON C.DepartmentID = D.DepartmentID
        WHERE T.FacultyID = :fid
    """)
    my_courses = db.session.execute(sql, {'fid': fid}).fetchall()

    announcements = db.session.execute(text("SELECT Message, DatePosted, 'All' as TargetID FROM Announcement WHERE PostedBy=:fid LIMIT 3"), {'fid':fid}).fetchall()

    return render_template('faculty/courses.html', faculty=faculty, courses=my_courses, announcements=announcements)


# --- STUDENTS ---
@app.route('/faculty/students')
def students():
    if 'user_id' not in session: return redirect(url_for('index'))
    fid = session['user_id']
    faculty = get_faculty_profile(fid)
    
    course_id = request.args.get('course_id')
    
    sql = """
        SELECT P.PersonID as StudentID, P.Name as FirstName, '' as LastName, P.Email, 
               Prog.ProgramName, C.CourseName
        FROM Student S
        JOIN Person P ON S.StudentID = P.PersonID
        JOIN Program Prog ON S.ProgramID = Prog.ProgramID
        JOIN Enrollment E ON S.StudentID = E.StudentID
        JOIN Course C ON E.CourseID = C.CourseID
        JOIN Teaches T ON E.CourseID = T.CourseID
        WHERE T.FacultyID = :fid
    """
    params = {'fid': fid}

    if course_id:
        sql += " AND C.CourseID = :cid"
        params['cid'] = course_id
    
    students_list = db.session.execute(text(sql), params).fetchall()
    courses = get_my_courses(fid)

    return render_template('faculty/students.html', 
                           faculty=faculty, 
                           students=students_list, 
                           courses=courses, 
                           selected_course=int(course_id) if course_id else None)


# --- ASSIGNMENTS ---
@app.route('/faculty/assignments', methods=['GET', 'POST'])
def assignments():
    if 'user_id' not in session: return redirect(url_for('index'))
    fid = session['user_id']
    faculty = get_faculty_profile(fid)

    # 1. Fetch Assignments
    sql = text("""
        SELECT A.AssignmentID, A.Title, A.Description, A.Deadline, A.MaxMarks, C.CourseName as CourseCode
        FROM Assignment A
        JOIN Course C ON A.CourseID = C.CourseID
        WHERE A.CreatedBy = :fid
    """)
    assignments_list = db.session.execute(sql, {'fid': fid}).fetchall()
    courses = get_my_courses(fid)
    
    # 2. Dynamic Right Sidebar Stats
    pending_count = db.session.execute(text("""
        SELECT COUNT(*) FROM Submission S 
        JOIN Assignment A ON S.AssignmentID = A.AssignmentID 
        WHERE A.CreatedBy = :fid AND S.Marks IS NULL
    """), {'fid': fid}).scalar()
    
    upcoming_exams = db.session.execute(text("""
        SELECT COUNT(*) FROM Exam 
        WHERE ConductedBy = :fid AND ExamDate >= NOW()
    """), {'fid': fid}).scalar()

    return render_template('faculty/assignments.html', 
                           faculty=faculty, 
                           assignments=assignments_list, 
                           courses=courses,
                           pending_submissions=pending_count, 
                           upcoming_exams=upcoming_exams)

@app.route('/faculty/assignments/new', methods=['POST'])
def create_assignment():
    if 'user_id' not in session: return redirect(url_for('index'))
    fid = session['user_id']
    
    course_id = request.form.get('course_id')
    title = request.form.get('title')
    desc = request.form.get('description')
    deadline = request.form.get('deadline')
    max_marks = request.form.get('maxmarks')

    sql = text("""
        INSERT INTO Assignment (CourseID, CreatedBy, Title, Description, Deadline, MaxMarks)
        VALUES (:cid, :fid, :title, :desc, :deadline, :max)
    """)
    db.session.execute(sql, {'cid': course_id, 'fid': fid, 'title': title, 'desc': desc, 'deadline': deadline, 'max': max_marks})
    db.session.commit()
    flash("Assignment Created!")
    return redirect(url_for('assignments'))


# --- SUBMISSIONS ---
@app.route('/faculty/submissions')
def submissions():
    if 'user_id' not in session: return redirect(url_for('index'))
    fid = session['user_id']
    faculty = get_faculty_profile(fid)
    course_id = request.args.get('course_id')

    # Filter out assignments that have already been graded (Marks IS NULL)
    sql = """
        SELECT Sub.SubmissionID, Sub.SubmittedAt, Sub.Marks, Sub.Comments,
               P.Name as FirstName, '' as LastName, 
               A.Title as AssignmentTitle, A.MaxMarks, C.CourseName as CourseCode,
               COALESCE(D.FilePath, '#') as DriveLink
        FROM Submission Sub
        JOIN Assignment A ON Sub.AssignmentID = A.AssignmentID
        JOIN Person P ON Sub.StudentID = P.PersonID
        JOIN Course C ON A.CourseID = C.CourseID
        LEFT JOIN SubmissionDocument SD ON Sub.SubmissionID = SD.SubmissionID
        LEFT JOIN Document D ON SD.DocumentID = D.DocumentID
        WHERE A.CreatedBy = :fid AND Sub.Marks IS NULL
    """
    params = {'fid': fid}
    if course_id:
        sql += " AND C.CourseID = :cid"
        params['cid'] = course_id

    subs = db.session.execute(text(sql), params).fetchall()
    courses = get_my_courses(fid)

    return render_template('faculty/submissions.html', 
                           faculty=faculty, 
                           submissions=subs, 
                           courses=courses,
                           selected_course=int(course_id) if course_id else None)

@app.route('/faculty/submissions/grade', methods=['POST'])
def grade_submission():
    if 'user_id' not in session: return redirect(url_for('index'))
    
    sub_id = request.form.get('SubmissionID')
    marks = request.form.get('MarksGiven')
    feedback = request.form.get('Feedback')
    
    # Update Submission Table (Marks IS NULL checks will now fail, removing it from view)
    sql = text("UPDATE Submission SET Marks = :m, Comments = :c WHERE SubmissionID = :sid")
    db.session.execute(sql, {'m': marks, 'c': feedback, 'sid': sub_id})
    
    # Log Evaluation
    sql_eval = text("""
        INSERT INTO SubmissionEvaluation (SubmissionID, FacultyID, MarksGiven, Comments, EvaluatedAt)
        VALUES (:sid, :fid, :m, :c, NOW())
    """)
    db.session.execute(sql_eval, {'sid': sub_id, 'fid': session['user_id'], 'm': marks, 'c': feedback})
    
    db.session.commit()
    return redirect(url_for('submissions'))


# --- ATTENDANCE ---
@app.route('/faculty/attendance', methods=['GET', 'POST'])
def attendance():
    if 'user_id' not in session: return redirect(url_for('index'))
    fid = session['user_id']
    faculty = get_faculty_profile(fid)
    
    courses = get_my_courses(fid)
    students_list = []
    selected_course = request.args.get('course_id')

    if request.method == 'POST':
        cid = request.form.get('course_id')
        sid = request.form.get('student_id')
        status = request.form.get('status')
        date = request.form.get('date') or datetime.now().strftime('%Y-%m-%d')

        try:
            sql = text("""
                INSERT INTO Attendance (CourseID, StudentID, RecordedBy, ClassDate, Status)
                VALUES (:cid, :sid, :fid, :date, :status)
            """)
            db.session.execute(sql, {'cid': cid, 'sid': sid, 'fid': fid, 'date': date, 'status': status})
            db.session.commit()
            flash("Attendance Marked!")
        except Exception as e:
            flash("Error: Attendance likely already marked for this student/date.")
        
        return redirect(url_for('attendance', course_id=cid))

    if selected_course:
        sql = text("""
            SELECT P.PersonID as StudentID, P.Name as FirstName, '' as LastName
            FROM Enrollment E
            JOIN Person P ON E.StudentID = P.PersonID
            WHERE E.CourseID = :cid
        """)
        students_list = db.session.execute(sql, {'cid': selected_course}).fetchall()

    return render_template('faculty/attendance.html', 
                           faculty=faculty, 
                           courses=courses, 
                           students=students_list, 
                           selected_course=int(selected_course) if selected_course else None)


# --- EXAMS ---
@app.route('/faculty/exams', methods=['GET', 'POST'])
def exams():
    if 'user_id' not in session: return redirect(url_for('index'))
    fid = session['user_id']
    faculty = get_faculty_profile(fid)
    courses = get_my_courses(fid)
    
    if request.method == 'POST':
        cid = request.form.get('course_id')
        title = request.form.get('title')
        etype = request.form.get('exam_type')
        date = request.form.get('exam_date')
        max_m = request.form.get('max_marks')

        sql = text("""
            INSERT INTO Exam (CourseID, ConductedBy, ExamType, ExamDate, MaxMarks)
            VALUES (:cid, :fid, :etype, :date, :max)
        """)
        db.session.execute(sql, {'cid': cid, 'fid': fid, 'etype': etype, 'date': date, 'max': max_m})
        db.session.commit()
        return redirect(url_for('exams'))

    selected_course = request.args.get('course_id')
    students_list = []
    
    sql_exams = text("""
        SELECT E.ExamID, C.CourseName, E.ExamType, 
               DATE_FORMAT(E.ExamDate, '%d %b %Y %H:%i') as ExamDateTime,
               E.MaxMarks
        FROM Exam E
        JOIN Course C ON E.CourseID = C.CourseID
        WHERE E.ConductedBy = :fid
        ORDER BY E.ExamDate DESC
    """)
    exams_list = db.session.execute(sql_exams, {'fid': fid}).fetchall()

    if selected_course:
        sql_stud = text("SELECT P.PersonID as StudentID, P.Name as FirstName, '' as LastName FROM Enrollment E JOIN Person P ON E.StudentID=P.PersonID WHERE E.CourseID=:cid")
        students_list = db.session.execute(sql_stud, {'cid': selected_course}).fetchall()

    return render_template('faculty/exams.html', 
                           faculty=faculty, 
                           courses=courses, 
                           exams=exams_list,
                           students=students_list, 
                           selected_course=int(selected_course) if selected_course else None)

@app.route('/faculty/exams/enter-marks', methods=['POST'])
def enter_marks():
    if 'user_id' not in session: return redirect(url_for('index'))
    
    eid = request.form.get('exam_id')
    sid = request.form.get('student_id')
    marks = request.form.get('marks')
    
    try:
        # 1. First, strictly check if this Student exists
        check_student = db.session.execute(
            text("SELECT 1 FROM Student WHERE StudentID = :sid"), 
            {'sid': sid}
        ).fetchone()

        if not check_student:
            flash(f"Error: Student ID '{sid}' does not exist!", "error")
            return redirect(url_for('exams'))

        # 2. If student exists, proceed to save marks
        sql = text("""
            INSERT INTO ExamResult (ExamID, StudentID, MarksObtained) VALUES (:eid, :sid, :m)
            ON DUPLICATE KEY UPDATE MarksObtained = :m
        """)
        db.session.execute(sql, {'eid': eid, 'sid': sid, 'm': marks})
        db.session.commit()
        
        flash(f"Marks successfully updated for Student {sid}", "success")

    except IntegrityError:
        db.session.rollback()
        flash("Database Error: Invalid Exam ID or Student ID.", "error")
    except Exception as e:
        db.session.rollback()
        flash(f"An unexpected error occurred: {str(e)}", "error")

    return redirect(url_for('exams'))

# --- FEEDBACK ---
@app.route('/faculty/feedback')
def feedback():
    if 'user_id' not in session: return redirect(url_for('index'))
    fid = session['user_id']
    faculty = get_faculty_profile(fid)

    sql = text("""
        SELECT F.Comments, F.Rating, F.CreatedAt, P.Name as FirstName, '' as LastName, C.CourseName
        FROM Feedback F
        JOIN Person P ON F.StudentID = P.PersonID
        JOIN Course C ON F.CourseID = C.CourseID
        WHERE F.FacultyID = :fid
        ORDER BY F.CreatedAt DESC
    """)
    feedbacks = db.session.execute(sql, {'fid': fid}).fetchall()

    return render_template('faculty/feedback.html', faculty=faculty, feedbacks=feedbacks)


# --- ANNOUNCEMENTS ---
@app.route('/faculty/announcements', methods=['GET', 'POST'])
def announcements():
    if 'user_id' not in session: return redirect(url_for('index'))
    fid = session['user_id']
    faculty = get_faculty_profile(fid)

    if request.method == 'POST':
        scope = request.form.get('scope')
        target = request.form.get('target')
        msg = request.form.get('message')
        
        sql = text("INSERT INTO Announcement (PostedBy, Message, DatePosted) VALUES (:fid, :msg, NOW())")
        result = db.session.execute(sql, {'fid': fid, 'msg': msg})
        ann_id = result.lastrowid
        
        if scope == 'Course' and target:
            db.session.execute(text("INSERT INTO AnnouncementCourse (AnnouncementID, CourseID) VALUES (:aid, :cid)"), {'aid': ann_id, 'cid': target})
        elif scope == 'Department' and target:
             db.session.execute(text("INSERT INTO AnnouncementDepartment (AnnouncementID, DepartmentID) VALUES (:aid, :did)"), {'aid': ann_id, 'did': target})
             
        db.session.commit()
        return redirect(url_for('announcements'))

    sql = text("""
        SELECT Message, DatePosted, 'All' as TargetID, 'General' as TargetType 
        FROM Announcement WHERE PostedBy = :fid ORDER BY DatePosted DESC
    """)
    anns = db.session.execute(sql, {'fid': fid}).fetchall()

    return render_template('faculty/announcements.html', faculty=faculty, announcements=anns)


# --- DOCUMENTS ---
@app.route('/faculty/documents', methods=['GET', 'POST'])
def documents():
    if 'user_id' not in session: return redirect(url_for('index'))
    fid = session['user_id']
    faculty = get_faculty_profile(fid)
    courses = get_my_courses(fid)

    if request.method == 'POST':
        title = request.form.get('title')
        link = request.form.get('gdrive_link')
        cid = request.form.get('course_id') or None
        
        sql = text("""
            INSERT INTO Document (UploadedBy, Title, FileType, FilePath, UploadedOn, AccessLevel)
            VALUES (:fid, :title, 'link', :link, NOW(), 'CourseOnly')
        """)
        result = db.session.execute(sql, {'fid': fid, 'title': title, 'link': link})
        doc_id = result.lastrowid
        
        if cid:
            db.session.execute(text("INSERT INTO CourseDocument (CourseID, DocumentID) VALUES (:cid, :did)"), {'cid': cid, 'did': doc_id})
        
        db.session.commit()
        return redirect(url_for('documents'))

    sql = text("""
        SELECT D.Title, D.FilePath, D.UploadedOn, D.FileType, CD.CourseID
        FROM Document D
        LEFT JOIN CourseDocument CD ON D.DocumentID = CD.DocumentID
        WHERE D.UploadedBy = :fid
    """)
    docs = db.session.execute(sql, {'fid': fid}).fetchall()

    return render_template('faculty/documents.html', faculty=faculty, documents=docs, courses=courses)


if __name__ == '__main__':
    app.run(debug=True, port=5002)