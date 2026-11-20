from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import datetime

# ==========================================
# INITIALIZE FLASK & DATABASE
# ==========================================
app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'
app.config['SESSION_COOKIE_NAME'] = 'admin_session'

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:YOUR_PASSWORD@localhost/YOUR_DB_NAME'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)

with app.app_context():
    db.create_all()

# ==========================================
# DATABASE MODELS (from models.py)
# ==========================================

# --- CORE TABLES ---
class Person(db.Model):
    __tablename__ = 'Person'
    PersonID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100))
    DOB = db.Column(db.Date)
    Gender = db.Column(db.String(1))
    Email = db.Column(db.String(120), unique=True)
    Phone = db.Column(db.String(20))
    Address = db.Column(db.String(255))
    Password = db.Column(db.String(255))
    Role = db.Column(db.Enum('Student', 'Faculty', 'Admin'))

class Department(db.Model):
    __tablename__ = 'Department'
    DepartmentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DeptCode = db.Column(db.String(20), unique=True)
    DeptName = db.Column(db.String(100))

class Program(db.Model):
    __tablename__ = 'Program'
    ProgramID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ProgramCode = db.Column(db.String(20), unique=True)
    ProgramName = db.Column(db.String(100))
    DepartmentID = db.Column(db.Integer, db.ForeignKey('Department.DepartmentID'))
    department = db.relationship('Department', backref='programs')

# --- ROLES ---
class Student(db.Model):
    __tablename__ = 'Student'
    StudentID = db.Column(db.Integer, db.ForeignKey('Person.PersonID'), primary_key=True)
    RollNo = db.Column(db.String(30), unique=True)
    ProgramID = db.Column(db.Integer, db.ForeignKey('Program.ProgramID'))
    Semester = db.Column(db.Integer)
    AdmissionYear = db.Column(db.Integer)
    
    person = db.relationship('Person', backref='student_profile')
    program = db.relationship('Program', backref='students')

class Faculty(db.Model):
    __tablename__ = 'Faculty'
    FacultyID = db.Column(db.Integer, db.ForeignKey('Person.PersonID'), primary_key=True)
    Designation = db.Column(db.String(60))
    DepartmentID = db.Column(db.Integer, db.ForeignKey('Department.DepartmentID'))
    Qualification = db.Column(db.String(120))
    
    person = db.relationship('Person', backref='faculty_profile')
    department = db.relationship('Department', backref='faculty')

class Admin(db.Model):
    __tablename__ = 'Admin'
    AdminID = db.Column(db.Integer, db.ForeignKey('Person.PersonID'), primary_key=True)
    RoleType = db.Column(db.Enum('SuperAdmin', 'DeptAdmin', 'FinanceAdmin'))
    person = db.relationship('Person', backref='admin_profile')

# --- ACADEMICS & EXTRAS ---
class Course(db.Model):
    __tablename__ = 'Course'
    CourseID = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    CourseName = db.Column(db.String(120))
    Credits = db.Column(db.Integer)
    DepartmentID = db.Column(db.Integer, db.ForeignKey('Department.DepartmentID'))
    Semester = db.Column(db.Integer)
    
    department = db.relationship('Department', backref='courses')

class Teaches(db.Model):
    __tablename__ = 'Teaches'
    FacultyID = db.Column(db.Integer, db.ForeignKey('Faculty.FacultyID'), primary_key=True)
    CourseID = db.Column(db.Integer, db.ForeignKey('Course.CourseID'), primary_key=True)

class Enrollment(db.Model):
    __tablename__ = 'Enrollment'
    EnrollmentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StudentID = db.Column(db.Integer, db.ForeignKey('Student.StudentID'))
    CourseID = db.Column(db.Integer, db.ForeignKey('Course.CourseID'))
    Status = db.Column(db.Enum('Active', 'Dropped', 'Completed'))

class Request(db.Model):
    __tablename__ = 'Request'
    RequestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StudentID = db.Column(db.Integer, db.ForeignKey('Student.StudentID'))
    RequestType = db.Column(db.Enum('InfoUpdate','Certificate','IDReissue'))
    RequestDate = db.Column(db.DateTime)
    Status = db.Column(db.Enum('Pending','Approved','Rejected'))
    
    student = db.relationship('Student', backref='requests')

class Announcement(db.Model):
    __tablename__ = 'Announcement'
    AnnouncementID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PostedBy = db.Column(db.Integer, db.ForeignKey('Person.PersonID'))
    Message = db.Column(db.Text)
    DatePosted = db.Column(db.DateTime)
    
    poster = db.relationship('Person', backref='announcements')

# ==========================================
# MIDDLEWARE
# ==========================================
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ==========================================
# AUTH HELPER FUNCTIONS
# ==========================================
def check_admin_access():
    return session.get('role') == 'Admin'

# ==========================================
# BLUEPRINTS (from login.py)
# ==========================================
login_bp = Blueprint('auth', __name__)

@login_bp.route('/')
def home():
    return render_template('index.html')

@login_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.home'))

@login_bp.route('/invalid-login')
def invalid_login():
    return render_template('invalid-login.html')

# --- Student Login ---
@login_bp.route('/student', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        identifier = request.form.get('enrollmentId')
        password = request.form.get('password')
        
        student = Student.query.filter((Student.StudentID == identifier) | (Student.RollNo == identifier)).first()
        
        if student and student.person.Password == password:
            session['user_id'] = student.StudentID
            session['role'] = 'Student'
            session['name'] = student.person.Name
            return redirect(url_for('student_dashboard'))
        
        return render_template('invalid-login.html')
    return render_template('student/index.html')

# --- Faculty Login ---
@login_bp.route('/faculty', methods=['GET', 'POST'])
def faculty_login():
    if request.method == 'POST':
        faculty_id = request.form.get('facultyId')
        password = request.form.get('password')
        fac = Faculty.query.filter_by(FacultyID=faculty_id).first()
        if fac and fac.person.Password == password:
            session['user_id'] = fac.FacultyID
            session['role'] = 'Faculty'
            session['name'] = fac.person.Name
            return redirect(url_for('faculty_dashboard'))
        return render_template('invalid-login.html')
    return render_template('faculty/index.html')

# --- Admin Login ---
@login_bp.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_id = request.form.get('adminId')
        password = request.form.get('password')
        adm = Admin.query.filter_by(AdminID=admin_id).first()
        if adm and adm.person.Password == password:
            session['user_id'] = adm.AdminID
            session['role'] = 'Admin'
            session['name'] = adm.person.Name
            return redirect(url_for('admin_dashboard.dashboard'))
        return render_template('invalid-login.html')
    return render_template('admin/index.html')

# ==========================================
# ADMIN BLUEPRINT (from admin.py)
# ==========================================
admin_bp = Blueprint('admin_dashboard', __name__)

# ---------------------------------------------------
# 1. DASHBOARD
# ---------------------------------------------------
@admin_bp.route('/admin/dashboard')
def dashboard():
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))
    
    stats = {
        'student_count': Student.query.count(),
        'faculty_count': Faculty.query.count(),
        'course_count': Course.query.count(),
        'pending_requests': Request.query.filter_by(Status='Pending').count()
    }
    return render_template('admin/dashboard.html', user_name=session.get('name'), stats=stats)

# ---------------------------------------------------
# 2. MANAGE USERS (Search + Add + Delete)
# ---------------------------------------------------
@admin_bp.route('/admin/users', methods=['GET', 'POST'])
def users():
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))

    # --- HANDLE ADDING NEW USER ---
    if request.method == 'POST':
        try:
            role = request.form.get('role')
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            
            new_person = Person(Name=name, Email=email, Password=password, Role=role)
            db.session.add(new_person)
            db.session.flush()

            if role == 'Student':
                new_student = Student(
                    StudentID=new_person.PersonID,
                    RollNo=request.form.get('roll_no'),
                    ProgramID=request.form.get('program_id'),
                    Semester=request.form.get('semester'),
                    AdmissionYear=2023
                )
                db.session.add(new_student)
            elif role == 'Faculty':
                new_faculty = Faculty(
                    FacultyID=new_person.PersonID,
                    Designation=request.form.get('designation'),
                    DepartmentID=request.form.get('department_id'),
                    Qualification=request.form.get('qualification')
                )
                db.session.add(new_faculty)
            
            db.session.commit()
            flash(f"{role} added successfully!")
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding user: {str(e)}")
        return redirect(url_for('admin_dashboard.users'))

    # --- HANDLE SEARCH & DISPLAY ---
    query = request.args.get('q')
    
    student_q = db.session.query(Student, Person, Program).join(Person).join(Program)
    faculty_q = db.session.query(Faculty, Person, Department).join(Person).join(Department)

    if query:
        search = f"%{query}%"
        student_q = student_q.filter(or_(Person.Name.like(search), Student.RollNo.like(search)))
        faculty_q = faculty_q.filter(or_(Person.Name.like(search), Faculty.Designation.like(search)))

    students = student_q.all()
    faculty = faculty_q.all()
    
    programs = Program.query.all()
    departments = Department.query.all()

    return render_template('admin/users.html', user_name=session.get('name'), 
                           students=students, faculty=faculty, programs=programs, departments=departments)

@admin_bp.route('/admin/delete_user/<int:user_id>/<string:role>')
def delete_user(user_id, role):
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))
    
    try:
        person = Person.query.get(user_id)
        if person:
            db.session.delete(person)
            db.session.commit()
            flash(f"{role} deleted successfully.")
    except Exception as e:
        flash("Error deleting user.")
    return redirect(url_for('admin_dashboard.users'))

# ---------------------------------------------------
# 3. COURSES (Search + Add + Delete)
# ---------------------------------------------------
@admin_bp.route('/admin/courses', methods=['GET', 'POST'])
def courses():
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))

    # --- HANDLE ADD COURSE ---
    if request.method == 'POST':
        try:
            new_course = Course(
                CourseName=request.form.get('course_name'),
                Credits=request.form.get('credits'),
                DepartmentID=request.form.get('department_id'),
                Semester=request.form.get('semester')
            )
            db.session.add(new_course)
            db.session.commit()
            flash("Course added successfully!")
        except:
            flash("Error adding course.")
        return redirect(url_for('admin_dashboard.courses'))

    # --- SEARCH & DISPLAY ---
    query = request.args.get('q')
    course_q = db.session.query(Course, Department).join(Department)
    
    if query:
        search = f"%{query}%"
        course_q = course_q.filter(or_(Course.CourseName.like(search), Department.DeptName.like(search)))
        
    courses = course_q.all()
    departments = Department.query.all()

    return render_template('admin/courses.html', user_name=session.get('name'), 
                           courses=courses, departments=departments)

@admin_bp.route('/admin/delete_course/<int:course_id>')
def delete_course(course_id):
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))
    course = Course.query.get(course_id)
    if course:
        db.session.delete(course)
        db.session.commit()
    return redirect(url_for('admin_dashboard.courses'))

# ---------------------------------------------------
# 4. APPROVALS (Approve/Reject)
# ---------------------------------------------------
@admin_bp.route('/admin/approvals')
def approvals():
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))
    
    requests = db.session.query(Request, Student, Person)\
        .join(Student, Request.StudentID == Student.StudentID)\
        .join(Person, Student.StudentID == Person.PersonID)\
        .filter(Request.Status == 'Pending').all()
        
    return render_template('admin/approvals.html', user_name=session.get('name'), requests=requests)

@admin_bp.route('/admin/approve_request/<int:req_id>/<action>')
def process_request(req_id, action):
    if 'user_id' not in session or session.get('role') != 'Admin':
        flash("You must be logged in as Admin to approve requests.", "error")
        return redirect(url_for('auth.admin_login'))
    
    try:
        req = Request.query.get(req_id)
        if req:
            req.Status = 'Approved' if action == 'approve' else 'Rejected'
            db.session.commit()
            flash(f"Request {req.Status}.", "success")
        else:
            flash("Request not found.", "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Error processing request: {str(e)}", "error")
    finally:
        db.session.close()
    
    response = redirect(url_for('admin_dashboard.approvals'))
    return response

# ---------------------------------------------------
# 5. ANNOUNCEMENTS
# ---------------------------------------------------
@admin_bp.route('/admin/announcements')
def announcements():
    if not check_admin_access(): return redirect(url_for('auth.admin_login'))
    announcements = Announcement.query.order_by(Announcement.DatePosted.desc()).all()
    return render_template('admin/announcements.html', user_name=session.get('name'), announcements=announcements)

@admin_bp.route('/admin/announcements/post', methods=['POST'])
def post_announcement():
    if 'user_id' not in session or session.get('role') != 'Admin':
        flash("You must be logged in as Admin to post announcements.", "error")
        return redirect(url_for('auth.admin_login'))
    
    try:
        message = request.form.get('message')
        if not message or message.strip() == '':
            flash("Announcement message cannot be empty.", "warning")
        else:
            new_announcement = Announcement(
                PostedBy=session.get('user_id'),
                Message=message,
                DatePosted=datetime.datetime.now()
            )
            db.session.add(new_announcement)
            db.session.commit()
            flash("Announcement posted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error posting announcement: {str(e)}", "error")
    finally:
        db.session.close()
    
    response = redirect(url_for('admin_dashboard.announcements'))
    return response

# ==========================================
# REGISTER BLUEPRINTS
# ==========================================
app.register_blueprint(login_bp)
app.register_blueprint(admin_bp)

# ==========================================
# RUN APPLICATION
# ==========================================
if __name__ == '__main__':
    app.run(debug=True, port=5003)
