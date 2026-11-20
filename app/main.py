import requests
from flask import Flask, request, Response, render_template, redirect

app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    # Determine the target port
    # Student portal routes: starts with student, enrollment, feedback, request, etc.
    if path.startswith('student') or path.startswith('enrollment') or path.startswith('feedback') or path.startswith('request'):
        target_port = 5001
        # If requesting the base student login, forward to the root of the student server
        target_path = '' if path in ['student', 'student/'] else path
    # Faculty portal routes: starts with faculty, assignments, submissions, attendance, exams, documents, etc.
    elif path.startswith('faculty') or path.startswith('assignments') or path.startswith('submissions') or path.startswith('attendance') or path.startswith('exams') or path.startswith('documents'):
        target_port = 5002
        target_path = '' if path in ['faculty', 'faculty/'] else path
    # Admin portal routes: starts with admin, approvals, announcements, etc.
    elif path.startswith('admin') or path.startswith('approvals') or path.startswith('announcements'):
        target_port = 5003
        target_path = path
    else:
        # Fallback for static assets and other requests
        target_port = 5001
        target_path = path

    url = f"http://127.0.0.1:{target_port}/{target_path}"
    
    # Forward the request details (method, headers, data, cookies, query params)
    headers = {key: value for key, value in request.headers if key.lower() not in ['host', 'content-length']}
    
    try:
        response = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            params=request.args,
            allow_redirects=False # Handle redirects manually to rewrite Location headers
        )
    except Exception as e:
        return Response(f"Backend service error: {e}", 502)

    # Create proxy response
    res = Response(response.content, response.status_code)
    
    # Copy headers back, rewriting Redirect location to keep the client on port 5000
    for key, value in response.headers.items():
        if key.lower() not in ['content-encoding', 'transfer-encoding', 'content-length']:
            if key.lower() == 'location':
                value = value.replace(':5001/', ':5000/').replace(':5002/', ':5000/').replace(':5003/', ':5000/')
                # If backend redirected to its root, map it to the proxy entry page
                if value == 'http://127.0.0.1:5000/' or value == '/':
                    if target_port == 5001:
                        value = '/student'
                    elif target_port == 5002:
                        value = '/faculty'
            res.headers[key] = value
            
    return res

if __name__ == '__main__':
    app.run(debug=True, port=5000)
