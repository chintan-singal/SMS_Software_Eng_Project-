import argparse, hashlib, json, logging, os, platform, re, sys, threading, time, uuid, zipfile
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup
from flask import session
from flask_sqlalchemy import SQLAlchemy
from mysql.connector import pooling
from sqlalchemy.engine import URL
from werkzeug.serving import make_server
import pymysql, requests
parser=argparse.ArgumentParser()
for key in ('zip','out','datadir'):parser.add_argument('--'+key,required=True,type=Path)
parser.add_argument('--port',type=int,default=38462)
args=parser.parse_args()
out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
logging.basicConfig(filename=out/'server.log',level=logging.INFO,format='%(asctime)s %(name)s %(levelname)s %(message)s')
started=datetime.now(timezone.utc)
with zipfile.ZipFile(args.zip) as z:z.extractall(out/'source')
src=next((out/'source').rglob('app.py')).parent
sys.path.insert(0,str(src))
password=os.environ.get('SMS_QA_DB_PASSWORD','')
conn=pymysql.connect(host='127.0.0.1',port=args.port,user='root',password=password,autocommit=True)
def query(sql,params=()):
    with conn.cursor() as c:
        c.execute(sql,params)
        return c.fetchall()
def scalar(sql,*args):return query(sql,args)[0][0]
if Path(scalar('select @@datadir')).resolve()!=args.datadir.resolve():raise RuntimeError('Wrong disposable MySQL instance')
name='sms_qa_'+uuid.uuid4().hex[:12]
query('CREATE DATABASE '+name);conn.select_db(name)
uri=URL.create('mysql+pymysql',username='root',password=password,host='127.0.0.1',port=args.port,database=name).render_as_string(hide_password=False)
original_init=SQLAlchemy.init_app
def orm(obj,app):
    app.config['SQLALCHEMY_DATABASE_URI']=uri
    return original_init(obj,app)
original_pool=pooling.MySQLConnectionPool
def pool(**kw):
    kw.update(user='root',password=password,host='127.0.0.1',port=args.port,database=name)
    return original_pool(**kw)
with patch.object(SQLAlchemy,'init_app',orm),patch.object(pooling,'MySQLConnectionPool',pool):
    import admin,faculty,app as student
with admin.app.app_context():admin.db.create_all()
for stmt in (Path(__file__).parent/'fixture.sql').read_text(encoding='utf-8-sig').split(';'):
    if stmt.strip():query(stmt)
servers=[];base={}
for role,module in [('Student',student),('Faculty',faculty),('Admin',admin)]:
    server=make_server('127.0.0.1',0,module.app,threaded=True)
    servers.append(server);base[role]='http://127.0.0.1:'+str(server.server_port)
    threading.Thread(target=server.serve_forever,daemon=True).start()
def counts(tables):return {t:scalar('select count(*) from '+t) for t in tables.split()}
meta={'source':args.zip.name,'sha256':hashlib.sha256(args.zip.read_bytes()).hexdigest(),'started_utc':started.isoformat(),'db':scalar('select version()'),'schema':name,'tables':scalar('select count(*) from information_schema.tables where table_schema=%s',name),'seed':counts('Person Student Faculty Admin Course Timetable Attendance ExamResult Assignment Submission Request'),'portals':base,'os':platform.platform(),'python':platform.python_version(),'packages':{k:version(k) for k in ['Flask','Flask-SQLAlchemy','SQLAlchemy','mysql-connector-python','PyMySQL','requests','playwright']}}
results=[]
def test(id,refs,title,steps,expected,fn):
    start=time.perf_counter()
    try:
        actual=fn();status='PASS' if actual==expected else 'FAIL'
    except Exception as exc:
        actual=type(exc).__name__+': '+str(exc)[:320];status='ERROR'
    level,view={'U':('Unit','White'),'I':('Integration','Gray'),'S':('System','Black')}[id[0]]
    results.append(dict(id=id,level=level,view=view,refs=refs,title=title,steps=steps,expected=expected,actual=actual,status=status,ms=round(1000*(time.perf_counter()-start))))
    print(id,status,repr(actual),flush=True)
def guard(yes):
    with student.app.test_request_context('/'):
        if yes:session['student_id']=101
        res=student.login_required(lambda:'handler ran')()
        return res if isinstance(res,str) else str(res.status_code)+' '+res.location
def attendance(data):
    mock=MagicMock();mock.cursor.return_value.fetchall.return_value=[dict(classes_attended=a,total_classes=b) for a,b in data]
    with student.app.test_request_context('/'),patch.object(student,'get_connection',return_value=mock),patch.object(student,'render_template',side_effect=lambda _,**kw:kw):
        session['student_id']=101
        return student.attendance()['overall_attendance']
test('U01','FR-03','Guest branch','Call the student login decorator in an empty Flask request context.','302 /',lambda:guard(False))
test('U02','FR-03','Signed-in branch','Call the decorator with student 101 in a local unit context.','handler ran',lambda:guard(True))
for i,title,rows,exp in [(3,'Empty attendance history',[],0),(4,'Course with zero meetings',[(0,0)],0.0),(5,'Mean attendance across courses',[(1,2),(1,1)],75.0)]:
    test('U0'+str(i),'FR-S6',title,'Supply cursor rows (attended, total) '+str(rows)+' and capture the overall percentage passed to Jinja.',exp,lambda:attendance(rows))
def rollback_branch():
    db_mock=MagicMock();cur=db_mock.cursor.return_value
    cur.execute.side_effect=RuntimeError('QA simulated write failure')
    with student.app.test_request_context('/student/submit_assignment',method='POST',data={'assignment_id':'1','document_link':'https://example.test/qa'}),patch.object(student,'get_connection',return_value=db_mock):
        session['student_id']=101
        response=student.submit_assignment()
    return {'rollback':db_mock.rollback.call_count,'commit':db_mock.commit.call_count,'cursor closed':cur.close.call_count,'connection closed':db_mock.close.call_count,'status':response.status_code}
test('U06','FR-S4','Submission write error cleanup','Inject a database exception at the first write. Inspect rollback, commit, cleanup and the returned status.',{'rollback':1,'commit':0,'cursor closed':1,'connection closed':1,'status':302},rollback_branch)
s,f,a=[requests.Session() for _ in range(3)]
def hit(agent,role,path,form=None):
    return agent.request('GET' if form is None else 'POST',base[role]+path,data=form,allow_redirects=False,timeout=10)
def body(r):return ' '.join(BeautifulSoup(r.content,'html.parser').stripped_strings)
def loc(r):return str(r.status_code)+' '+r.headers.get('Location','-')
def login(agent,role,who,pwd='demo-only'):
    path,key={'Student':('/student/login','student_id'),'Faculty':('/faculty/login','facultyId'),'Admin':('/admin','adminId')}[role]
    return hit(agent,role,path,{key:who,'password':pwd})
def content(agent,role,path,token):
    r=hit(agent,role,path)
    if path=='/student/attendance':
        texts=[n.get_text(strip=True) for n in BeautifulSoup(r.content,'html.parser').select('aside h3')]
        return {'HTTP':r.status_code,'text present':token in texts}
    return {'HTTP':r.status_code,'text present':token in body(r)}
for i,(agent,role,who) in enumerate([(s,'Student','student@example.test'),(f,'Faculty','201'),(a,'Admin','301')],1):
    test('I0'+str(i),'FR-02',role+' login','POST the seeded '+role.lower()+' form with identifier '+who+' and the fixture password.','302 /'+role.lower()+'/dashboard',lambda:loc(login(agent,role,who)))
for id,ref,agent,role,path,title,token in [
('I04','FR-S1',s,'Student','dashboard','CGPA for grades A and B','3.5'),
('I05','FR-S5',s,'Student','grades','Percentage for 18 out of 20','90.0%'),
('I06','FR-S6',s,'Student','attendance','Attendance from two enrolled courses','75%'),
('I07','FR-S7',s,'Student','timetable','Monday class appears','QA-M01'),
('I08','FR-S7',s,'Student','timetable','Saturday class appears','QA-S06'),
('I09','FR-F1',f,'Faculty','dashboard','Faculty sees a taught course','QA Database Systems'),
('I10','FR-A1',a,'Admin','dashboard','Admin dashboard identifies the user','QA Admin')]:
    route='/'+role.lower()+'/'+path
    test(id,ref,title,'GET '+route+' with the authenticated fixture user. Read the rendered text for '+token+'.',{'HTTP':200,'text present':True},lambda:content(agent,role,route,token))
def feedback(rating):
    marker='QA-rating-'+str(rating)
    r=hit(s,'Student','/student/feedback',dict(course_id=11,rating=rating,comments=marker))
    return {'HTTP':r.status_code,'faculty 201 rows':scalar('select count(*) from Feedback where FacultyID=201 and Rating=%s and Comments=%s',rating,marker)}
for i,rating in [(11,1),(12,5)]:
    test('I'+str(i),'FR-S10','Feedback at rating '+str(rating),'Submit the valid endpoint rating for course 11. Count the matching row assigned to faculty 201.',{'HTTP':200,'faculty 201 rows':1},lambda:feedback(rating))

def rejected_student():
    g=requests.Session();r=login(g,'Student','101','incorrect');page=hit(g,'Student',r.headers['Location'])
    return {'HTTP':page.status_code,'visible error':'Invalid Credentials' in body(page)}
test('S01','FR-05','Student invalid-password feedback','Enter an incorrect password for test student 101. Follow the redirect and read the visible error.',{'HTTP':200,'visible error':True},rejected_student)
def rejected_admin():
    r=login(requests.Session(),'Admin','301','incorrect')
    return {'HTTP':r.status_code,'visible error':bool(re.search('invalid|incorrect|denied',body(r),re.I))}
test('S02','FR-05','Admin invalid-password feedback','Submit a wrong password through the normal admin form. Read the returned page.',{'HTTP':200,'visible error':True},rejected_admin)
def empty():
    g=requests.Session();login(g,'Student','102');return content(g,'Student','/student/assignments','No pending assignments')
test('S03','FR-S3','Student without assignments','Sign in as student 102, who has no enrollments, and open the assignments list.',{'HTTP':200,'text present':True},empty)
def assess():
    create=hit(f,'Faculty','/faculty/assignments/new',dict(course_id=11,title='QA Evidence Task',description='Fixture assignment',deadline='2027-04-01',maxmarks=20))
    listing=hit(s,'Student','/student/assignments')
    aid=BeautifulSoup(listing.content,'html.parser').select_one('input[name=assignment_id]')['value']
    sent=hit(s,'Student','/student/submit_assignment',dict(assignment_id=aid,document_link='https://example.test/qa-work'))
    queue=hit(f,'Faculty','/faculty/submissions')
    sid=BeautifulSoup(queue.content,'html.parser').select_one('input[name=SubmissionID]')['value']
    grade=hit(f,'Faculty','/faculty/submissions/grade',dict(SubmissionID=sid,MarksGiven=16,Feedback='QA reviewed'))
    visible=body(hit(s,'Student','/student/assignments'))
    return {'create':create.status_code,'listed for student':'QA Evidence Task' in body(listing),'submit':sent.status_code,'listed for faculty':'QA Evidence Task' in body(queue),'grade':grade.status_code,'student sees 16/20':bool(re.search(r'Graded:\s*16\s*/\s*20',visible))}
test('S04','FR-F3, FR-S3, FR-S4, FR-F4','Assignment through grading','Faculty creates a 20-mark task. Student submits a link. Faculty grades the submission. Student reopens completed work.',{'create':302,'listed for student':True,'submit':302,'listed for faculty':True,'grade':302,'student sees 16/20':True},assess)
def resubmit():
    r=hit(s,'Student','/student/submit_assignment',dict(assignment_id=1,document_link='https://example.test/revision'))
    return {'redirect':loc(r),'submissions':scalar('select count(*) from Submission where AssignmentID=1 and StudentID=101'),'document links':scalar('select count(*) from SubmissionDocument')}
test('I13','FR-S4','Second submission of the same task','After S04, submit a revised link. Count submission rows for this task and links in the initially empty fixture.',{'redirect':'302 /student/assignments','submissions':1,'document links':2},resubmit)
def approve():
    create=hit(s,'Student','/student/request',{'request_type':'Certificate'})
    q=hit(a,'Admin','/admin/approvals');html=BeautifulSoup(q.content,'html.parser')
    link=next(x['href'] for x in html.select('a[href]') if '/approve_request/' in x['href'] and x['href'].endswith('/approve'))
    dec=hit(a,'Admin',link)
    return {'sent':create.status_code,'certificate queued':'Certificate' in body(q),'decision':dec.status_code,'student sees Approved':'Approved' in body(hit(s,'Student','/student/request'))}
test('S05','FR-S11, FR-A4','Certificate approval across portals','Submit a certificate request as the student. Follow its approval link as admin, then reopen student history.',{'sent':302,'certificate queued':True,'decision':302,'student sees Approved':True},approve)
def logout():
    g=requests.Session();login(g,'Student','101')
    return [loc(hit(g,'Student','/student/logout')),loc(hit(g,'Student','/student/dashboard'))]
test('S06','FR-03, FR-04','Logout invalidates the student session','Log in, select logout, then revisit the same dashboard.',['302 /','302 /'],logout)
def browse():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser=pw.chromium.launch(channel='msedge',headless=True)
        page=browser.new_page(reduced_motion='reduce',viewport={'width':1280,'height':860})
        page.route('**/*',lambda r:r.continue_() if r.request.url.startswith('http://127.0.0.1:') else r.abort())
        page.goto(base['Student']);page.locator('input[name=student_id]').fill('101');page.locator('input[name=password]').fill('demo-only')
        page.locator('input[name=password]').press('Enter')
        page.wait_for_url('**/student/dashboard',timeout=20000)
        page.screenshot(animations='disabled',path=str(out/'student-dashboard.png'))
        page.get_by_role('link',name='Timetable').press('Enter')
        page.wait_for_url('**/student/timetable',timeout=20000)
        page.screenshot(animations='disabled',path=str(out/'student-timetable.png'))
        meta['browser']=browser.version
        value={'page':page.url.split(base['Student'])[1],'weekday room visible':page.get_by_text('Room QA-M01',exact=True).is_visible()}
        browser.close();return value
test('S07','FR-02, FR-S1, FR-S7','Student journey in Edge','Use the real login form and activate the Timetable link on the dashboard. Read the Monday room in the browser.',{'page':'/student/timetable','weekday room visible':True},browse)
assert not (src/'main.py').exists()
results.append(dict(id='B01',level='System',view='Black',refs='FR-01',title='Unified role selector',steps='Inspect the archive for the entry point needed to launch the shared gateway.',expected='Start the shared gateway and select each role.',actual='main.py absent from ZIP. Gateway journey could not start.',status='BLOCKED',ms=None))
meta['end_utc']=datetime.now(timezone.utc).isoformat()
meta['final']=counts('Assignment Submission Document SubmissionDocument SubmissionEvaluation Feedback Request')
meta['assessment']=list(query('select a.Title,s.Marks,a.MaxMarks,e.MarksGiven from Assignment a join Submission s using(AssignmentID) join SubmissionEvaluation e using(SubmissionID)'))
meta['timetable']=list(query("select DayOfWeek,RoomNo from Timetable order by TimetableID"))
meta['request']=list(query('select RequestID,RequestType,Status from Request'))
(out/'results.json').write_text(json.dumps({'run':meta,'cases':results},indent=2),encoding='utf8')
for server in servers:server.shutdown()
conn.close()

