#!/usr/bin/env python3
"""
Web interface for Moodle API Client
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired
import secrets
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from moodle_client import MoodleAPIClient
from pdf_summarizer import PDFSummarizer
from grade_analyzer import GradeAnalyzer
import config

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Create templates directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'), exist_ok=True)

# Custom template filter for converting newlines to <br> tags
@app.template_filter('nl2br')
def nl2br(value):
    """Convert newlines to <br> tags for display in HTML"""
    if value:
        return value.replace('\n', '<br>')
    return ''

# Global variables
moodle_client = None

class LoginForm(FlaskForm):
    """Form for logging in with Moodle API token"""
    token = PasswordField('Moodle API Token', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/')
def index():
    """Home page"""
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    form = LoginForm()
    error = None
    
    if form.validate_on_submit():
        token = form.token.data
        
        try:
            # Try to connect to Moodle with the provided token
            global moodle_client
            moodle_client = MoodleAPIClient(token=token)
            
            # Get user info
            site_info = moodle_client.get_site_info()
            username = site_info.get('fullname')
            
            # Store user info in session
            session['username'] = username
            session['token'] = token
            
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            error = f"Login failed: {str(e)}"
    
    return render_template('login.html', form=form, error=error)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    # Get client
    client = get_client()
    if not client:
        return redirect(url_for('login'))
    
    # Get courses
    try:
        courses = client.get_courses()
    except Exception as e:
        flash(f"Error retrieving courses: {str(e)}", 'danger')
        courses = []
    
    return render_template('dashboard.html', username=session['username'], courses=courses)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    """Course detail page"""
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    # Get client
    client = get_client()
    if not client:
        return redirect(url_for('login'))
    
    # Get course info
    try:
        courses = client.get_courses()
        course = next((c for c in courses if c['id'] == course_id), None)
        
        if not course:
            flash(f"Course with ID {course_id} not found.", 'danger')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"Error retrieving course: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('course_detail.html', course=course)

@app.route('/course/<int:course_id>/grades')
def course_grades(course_id):
    """Course grades page"""
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    # Get client
    client = get_client()
    if not client:
        return redirect(url_for('login'))
    
    # Get course info
    try:
        courses = client.get_courses()
        course = next((c for c in courses if c['id'] == course_id), None)
        
        if not course:
            flash(f"Course with ID {course_id} not found.", 'danger')
            return redirect(url_for('dashboard'))
            
        # Get grades
        grades = client.get_user_grades(course_id)
        
    except Exception as e:
        flash(f"Error retrieving grades: {str(e)}", 'danger')
        grades = None
    
    return render_template('course_grades.html', course=course, grades=grades)

@app.route('/course/<int:course_id>/lecture_notes')
def course_lecture_notes(course_id):
    """Course lecture notes page"""
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    # Get client
    client = get_client()
    if not client:
        return redirect(url_for('login'))
    
    # Get course info
    try:
        courses = client.get_courses()
        course = next((c for c in courses if c['id'] == course_id), None)
        
        if not course:
            flash(f"Course with ID {course_id} not found.", 'danger')
            return redirect(url_for('dashboard'))
            
        # Get course contents
        contents = client.get_course_contents(course_id)
        
        # Extract lecture notes
        lecture_notes = []
        for section in contents:
            section_name = section.get('name', f"Section {section.get('section', 0)}")
            section_modules = []
            
            for module in section.get('modules', []):
                if is_likely_lecture_note(module):
                    module['section_name'] = section_name
                    section_modules.append(module)
            
            if section_modules:
                lecture_notes.append({
                    'name': section_name,
                    'modules': section_modules
                })
        
    except Exception as e:
        flash(f"Error retrieving lecture notes: {str(e)}", 'danger')
        lecture_notes = []
    
    return render_template('course_lecture_notes.html', course=course, lecture_notes=lecture_notes)

@app.route('/course/<int:course_id>/summarize/<int:module_id>/<path:file_url>')
def summarize_pdf(course_id, module_id, file_url):
    """Generate a summary for a PDF file"""
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    # Get client
    client = get_client()
    if not client:
        return redirect(url_for('login'))
    
    # Get course info
    try:
        courses = client.get_courses()
        course = next((c for c in courses if c['id'] == course_id), None)
        
        if not course:
            flash(f"Course with ID {course_id} not found.", 'danger')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"Error retrieving course: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))
    
    # Clean up the file URL
    file_url = file_url.replace('___', '?').replace('__', '&')
    
    # Fix URL format if needed (ensure https:// has double slash)
    if file_url.startswith('https:/') and not file_url.startswith('https://'):
        file_url = file_url.replace('https:/', 'https://')
    elif file_url.startswith('http:/') and not file_url.startswith('http://'):
        file_url = file_url.replace('http:/', 'http://')
        
    # Fix URL encoding issues with percent signs
    if '%25' in file_url:
        file_url = file_url.replace('%25', '%')
    
    try:
        # First download the file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_path = temp_file.name
        
        # Download the file
        headers = {}
        params = {
            'token': session['token']
        }
        
        response = requests.get(file_url, params=params, headers=headers, stream=True)
        response.raise_for_status()
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract file name from Content-Disposition header or URL
        filename = None
        if 'Content-Disposition' in response.headers:
            import re
            disposition = response.headers['Content-Disposition']
            filename = re.findall('filename="(.+)"', disposition)
            if filename:
                filename = filename[0]
        
        if not filename:
            filename = os.path.basename(file_url.split('?')[0])
        
        # Check if file is a PDF
        if not filename.lower().endswith('.pdf'):
            flash("Only PDF files can be summarized.", 'warning')
            os.unlink(temp_path)  # Delete temp file
            return redirect(url_for('course_lecture_notes', course_id=course_id))
        
        # Initialize PDF summarizer
        try:
            pdf_summarizer = PDFSummarizer(api_key=config.OPENAI_API_KEY)
        except Exception as e:
            flash(f"Error initializing PDF summarizer: {str(e)}", 'danger')
            os.unlink(temp_path)  # Delete temp file
            return redirect(url_for('course_lecture_notes', course_id=course_id))
        
        # Generate summary
        try:
            summary = pdf_summarizer.summarize_pdf(temp_path, course_id, module_id, filename)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            # Render summary page
            return render_template('pdf_summary.html', 
                                  course=course, 
                                  filename=filename, 
                                  summary=summary,
                                  file_url=file_url,
                                  generated_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        except Exception as e:
            flash(f"Error generating summary: {str(e)}", 'danger')
            os.unlink(temp_path)  # Delete temp file
            return redirect(url_for('course_lecture_notes', course_id=course_id))
    
    except Exception as e:
        flash(f"Error downloading file: {str(e)}", 'danger')
        return redirect(url_for('course_lecture_notes', course_id=course_id))

@app.route('/delete-summary/<int:summary_id>', methods=['POST'])
def delete_summary(summary_id):
    """Delete a PDF summary"""
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    try:
        # Initialize PDF summarizer
        pdf_summarizer = PDFSummarizer(api_key=config.OPENAI_API_KEY)
        
        # Get the summary to find its course ID for redirection
        summary = pdf_summarizer.get_summary_by_id(summary_id)
        if not summary:
            flash("Summary not found.", 'warning')
            return redirect(url_for('dashboard'))
        
        course_id = summary['course_id']
        
        # Delete the summary
        pdf_summarizer.delete_summary(summary_id)
        
        flash("Summary deleted successfully.", 'success')
        return redirect(url_for('course_summaries', course_id=course_id))
    except Exception as e:
        flash(f"Error deleting summary: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))

@app.route('/course/<int:course_id>/summaries')
def course_summaries(course_id):
    """View all PDF summaries for a course"""
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    # Get client
    client = get_client()
    if not client:
        return redirect(url_for('login'))
    
    # Get course info
    try:
        courses = client.get_courses()
        course = next((c for c in courses if c['id'] == course_id), None)
        
        if not course:
            flash(f"Course with ID {course_id} not found.", 'danger')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"Error retrieving course: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))
    
    # Get summaries
    try:
        pdf_summarizer = PDFSummarizer(api_key=config.OPENAI_API_KEY)
        summaries = pdf_summarizer.get_all_summaries(course_id=course_id)
        
        return render_template('course_summaries.html', course=course, summaries=summaries)
    except Exception as e:
        flash(f"Error retrieving summaries: {str(e)}", 'danger')
        return redirect(url_for('course_detail', course_id=course_id))

@app.route('/course/<int:course_id>/download/<path:file_url>')
def download_file(course_id, file_url):
    """Download a file"""
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    # Get client
    client = get_client()
    if not client:
        return redirect(url_for('login'))
    
    try:
        # Get token
        token = session['token']
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Download the file
        file_url = file_url.replace('___', '?').replace('__', '&')
        
        # Fix URL format if needed (ensure https:// has double slash)
        if file_url.startswith('https:/') and not file_url.startswith('https://'):
            file_url = file_url.replace('https:/', 'https://')
        elif file_url.startswith('http:/') and not file_url.startswith('http://'):
            file_url = file_url.replace('http:/', 'http://')
            
        # Fix URL encoding issues with percent signs
        if '%25' in file_url:
            file_url = file_url.replace('%25', '%')
        
        # Add token to URL
        if '?' in file_url:
            full_url = f"{file_url}&token={token}"
        else:
            full_url = f"{file_url}?token={token}"
        
        # Get the filename from the URL
        filename = file_url.split('/')[-1].split('?')[0]
        
        # Download the file
        response = client._session.get(full_url, stream=True)
        response.raise_for_status()
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return send_file(temp_path, as_attachment=True, download_name=filename)
    
    except Exception as e:
        flash(f"Error downloading file: {str(e)}", 'danger')
        return redirect(url_for('course_lecture_notes', course_id=course_id))

def get_client():
    """Get or create Moodle client"""
    global moodle_client
    
    if moodle_client:
        return moodle_client
    
    if 'token' in session:
        try:
            moodle_client = MoodleAPIClient(token=session['token'])
            return moodle_client
        except Exception:
            flash('Session expired. Please login again.', 'warning')
            return None
    
    return None

def is_likely_lecture_note(module):
    """
    Check if a module is likely to be a lecture note
    
    Args:
        module: Module dict from Moodle API
        
    Returns:
        True if the module is likely a lecture note, False otherwise
    """
    # Check module type
    module_type = module.get('modname', '').lower()
    
    # Check module name
    name = module.get('name', '').lower()
    
    # Keywords that might indicate lecture notes
    lecture_keywords = ['lecture', 'notes', 'slides', 'presentation', 'chapter', 'week', 'topic', 'class']
    
    # Check if it's a resource (file) or a URL
    if module_type in ['resource', 'url']:
        # Check if the name contains lecture keywords
        for keyword in lecture_keywords:
            if keyword in name:
                return True
    
    # If it's a folder, check if it might contain lecture notes
    if module_type == 'folder':
        for keyword in lecture_keywords:
            if keyword in name:
                return True
    
    return False

def create_templates():
    """Create HTML templates for the web app"""
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    # Base template
    base_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Moodle API Client{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding-top: 60px; }
        .course-card { height: 100%; }
        .lecture-note { margin-bottom: 10px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-md navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">Moodle API Client</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {% if 'username' in session %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard') }}">Dashboard</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('logout') }}">Logout</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('login') }}">Login</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    # Index template
    index_html = '''{% extends "base.html" %}

{% block title %}Moodle API Client - Home{% endblock %}

{% block content %}
<div class="px-4 py-5 my-5 text-center">
    <h1 class="display-5 fw-bold">Moodle API Client</h1>
    <div class="col-lg-6 mx-auto">
        <p class="lead mb-4">
            Access your Concordia University Moodle courses, grades, and lecture materials.
        </p>
        <div class="d-grid gap-2 d-sm-flex justify-content-sm-center">
            <a href="{{ url_for('login') }}" class="btn btn-primary btn-lg px-4 gap-3">Login with API Token</a>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Login template
    login_html = '''{% extends "base.html" %}

{% block title %}Login - Moodle API Client{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h4 class="mb-0">Login with Moodle API Token</h4>
            </div>
            <div class="card-body">
                {% if error %}
                    <div class="alert alert-danger">{{ error }}</div>
                {% endif %}
                
                <form method="POST" action="{{ url_for('login') }}">
                    {{ form.hidden_tag() }}
                    <div class="mb-3">
                        {{ form.token.label(class="form-label") }}
                        {{ form.token(class="form-control") }}
                        <div class="form-text">
                            You can obtain your token from Moodle. See the 
                            <a href="https://github.com/yourusername/moodle-api-client/blob/main/docs/obtaining_api_token.md" target="_blank">documentation</a>.
                        </div>
                    </div>
                    <div class="d-grid">
                        {{ form.submit(class="btn btn-primary") }}
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Dashboard template
    dashboard_html = '''{% extends "base.html" %}

{% block title %}Dashboard - Moodle API Client{% endblock %}

{% block content %}
<h1 class="mb-4">Welcome, {{ username }}</h1>

<h2 class="mb-3">Your Courses</h2>

<div class="row row-cols-1 row-cols-md-3 g-4">
    {% for course in courses %}
        <div class="col">
            <div class="card course-card">
                <div class="card-body">
                    <h5 class="card-title">{{ course.fullname }}</h5>
                    <p class="card-text"><small class="text-muted">{{ course.shortname }}</small></p>
                </div>
                <div class="card-footer">
                    <a href="{{ url_for('course_detail', course_id=course.id) }}" class="btn btn-primary">View Course</a>
                </div>
            </div>
        </div>
    {% else %}
        <div class="col-12">
            <div class="alert alert-info">You are not enrolled in any courses.</div>
        </div>
    {% endfor %}
</div>
{% endblock %}'''
    
    # Course detail template
    course_detail_html = '''{% extends "base.html" %}

{% block title %}{{ course.fullname }} - Moodle API Client{% endblock %}

{% block content %}
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="{{ url_for('dashboard') }}">Dashboard</a></li>
        <li class="breadcrumb-item active">{{ course.fullname }}</li>
    </ol>
</nav>

<h1 class="mb-4">{{ course.fullname }}</h1>
<p><small class="text-muted">{{ course.shortname }}</small></p>

<div class="row mt-4">
    <div class="col-md-4 mb-3">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Grades</h5>
                <p class="card-text">View your grades for this course.</p>
                <a href="{{ url_for('course_grades', course_id=course.id) }}" class="btn btn-primary">View Grades</a>
            </div>
        </div>
    </div>
    
    <div class="col-md-4 mb-3">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Lecture Notes</h5>
                <p class="card-text">Access lecture notes and materials.</p>
                <a href="{{ url_for('course_lecture_notes', course_id=course.id) }}" class="btn btn-primary">View Lecture Notes</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Course grades template
    course_grades_html = '''{% extends "base.html" %}

{% block title %}Grades: {{ course.fullname }} - Moodle API Client{% endblock %}

{% block content %}
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="{{ url_for('dashboard') }}">Dashboard</a></li>
        <li class="breadcrumb-item"><a href="{{ url_for('course_detail', course_id=course.id) }}">{{ course.fullname }}</a></li>
        <li class="breadcrumb-item active">Grades</li>
    </ol>
</nav>

<h1 class="mb-4">Grades for {{ course.fullname }}</h1>

{% if grades and 'usergrades' in grades and grades.usergrades %}
    {% set user_grades = grades.usergrades[0] %}
    
    {% if 'grade' in user_grades %}
        <div class="alert alert-info">
            <h4>Overall Course Grade: {{ user_grades.grade }}</h4>
        </div>
    {% endif %}
    
    {% if 'gradeitems' in user_grades and user_grades.gradeitems %}
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Assessment</th>
                        <th>Grade</th>
                        <th>Weight</th>
                        <th>Feedback</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in user_grades.gradeitems %}
                        {% if item.itemname and item.itemname|lower != 'course total' %}
                            <tr>
                                <td>{{ item.itemname }}</td>
                                <td>{{ item.gradeformatted|default('-') }}</td>
                                <td>{{ item.weightformatted|default('-') }}</td>
                                <td>{{ item.feedback|default('-') }}</td>
                            </tr>
                        {% endif %}
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <div class="alert alert-warning">No grade items found for this course.</div>
    {% endif %}
    
    {% if 'warnings' in grades and grades.warnings %}
        <div class="alert alert-warning">
            <h5>Warnings:</h5>
            <ul>
                {% for warning in grades.warnings %}
                    <li>{{ warning.message }}</li>
                {% endfor %}
            </ul>
        </div>
    {% endif %}
{% else %}
    <div class="alert alert-warning">
        No grades available for this course. This could be because:
        <ul>
            <li>There are no graded items yet</li>
            <li>The Moodle API doesn't have permission to access grades</li>
            <li>There was an error retrieving the grades</li>
        </ul>
    </div>
{% endif %}
{% endblock %}'''
    
    # Course lecture notes template
    course_lecture_notes_html = '''{% extends "base.html" %}

{% block title %}Lecture Notes: {{ course.fullname }} - Moodle API Client{% endblock %}

{% block content %}
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="{{ url_for('dashboard') }}">Dashboard</a></li>
        <li class="breadcrumb-item"><a href="{{ url_for('course_detail', course_id=course.id) }}">{{ course.fullname }}</a></li>
        <li class="breadcrumb-item active">Lecture Notes</li>
    </ol>
</nav>

<h1 class="mb-4">Lecture Notes for {{ course.fullname }}</h1>

{% if lecture_notes %}
    <div class="accordion" id="lectureNotesAccordion">
        {% for section in lecture_notes %}
            <div class="accordion-item">
                <h2 class="accordion-header" id="heading{{ loop.index }}">
                    <button class="accordion-button {% if not loop.first %}collapsed{% endif %}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{{ loop.index }}">
                        {{ section.name }}
                    </button>
                </h2>
                <div id="collapse{{ loop.index }}" class="accordion-collapse collapse {% if loop.first %}show{% endif %}" data-bs-parent="#lectureNotesAccordion">
                    <div class="accordion-body">
                        <div class="list-group">
                            {% for module in section.modules %}
                                <div class="list-group-item lecture-note">
                                    <h5>{{ module.name }}</h5>
                                    <p><small class="text-muted">Type: {{ module.modname }}</small></p>
                                    
                                    {% if 'contents' in module %}
                                        <ul class="list-unstyled">
                                            {% for content in module.contents %}
                                                <li class="mb-2">
                                                    <div class="d-flex justify-content-between align-items-center">
                                                        <div>
                                                            <i class="bi bi-file-earmark"></i>
                                                            {{ content.filename }}
                                                            <small class="text-muted">({{ (content.filesize / 1024)|round(1) }} KB)</small>
                                                        </div>
                                                        {% if 'fileurl' in content %}
                                                            <a href="{{ url_for('download_file', course_id=course.id, file_url=content.fileurl|replace('?', '___')|replace('&', '__')) }}" 
                                                               class="btn btn-sm btn-outline-primary">
                                                                Download
                                                            </a>
                                                        {% endif %}
                                                    </div>
                                                </li>
                                            {% endfor %}
                                        </ul>
                                    {% elif module.modname == 'url' and 'url' in module %}
                                        <a href="{{ module.url }}" target="_blank" class="btn btn-sm btn-outline-primary">
                                            Open URL
                                        </a>
                                    {% endif %}
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        {% endfor %}
    </div>
{% else %}
    <div class="alert alert-info">No lecture notes found for this course.</div>
{% endif %}
{% endblock %}'''
    
    # Write templates to files
    with open(os.path.join(templates_dir, 'base.html'), 'w') as f:
        f.write(base_html)
    
    with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
        f.write(index_html)
    
    with open(os.path.join(templates_dir, 'login.html'), 'w') as f:
        f.write(login_html)
    
    with open(os.path.join(templates_dir, 'dashboard.html'), 'w') as f:
        f.write(dashboard_html)
    
    with open(os.path.join(templates_dir, 'course_detail.html'), 'w') as f:
        f.write(course_detail_html)
    
    with open(os.path.join(templates_dir, 'course_grades.html'), 'w') as f:
        f.write(course_grades_html)
    
    with open(os.path.join(templates_dir, 'course_lecture_notes.html'), 'w') as f:
        f.write(course_lecture_notes_html)

# Custom template filter for converting newlines to <br> tags
@app.template_filter('nl2br')
def nl2br(value):
    if value:
        return value.replace('\n', '<br>')
    return ''

# Custom template filter for truncating text
@app.template_filter('truncate')
def truncate_filter(s, length=100):
    if not s:
        return ''
    if len(s) <= length:
        return s
    return s[:length] + '...'

@app.route('/course/<int:course_id>/analyze-grades')
def analyze_grades(course_id):
    """Generate an analysis for course grades"""
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    # Get client
    client = get_client()
    if not client:
        return redirect(url_for('login'))
    
    # Get course info
    try:
        courses = client.get_courses()
        course = next((c for c in courses if c['id'] == course_id), None)
        
        if not course:
            flash(f"Course with ID {course_id} not found.", 'danger')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"Error retrieving course: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))
    
    # Get grades
    try:
        grades = client.get_user_grades(course_id)
        
        if not grades or 'usergrades' not in grades or not grades['usergrades']:
            flash("No grades available for analysis.", 'warning')
            return redirect(url_for('course_grades', course_id=course_id))
        
        user_grades = grades['usergrades'][0]
        
        if 'gradeitems' not in user_grades or not user_grades['gradeitems']:
            flash("No grade items available for analysis.", 'warning')
            return redirect(url_for('course_grades', course_id=course_id))
        
        # Format grade items for analysis
        grade_items = []
        for item in user_grades['gradeitems']:
            if item['itemname'] and item['itemname'].lower() != 'course total':
                grade_item = {
                    'id': item.get('id'),
                    'name': item.get('itemname'),
                    'grade': item.get('gradeformatted', '').replace('&nbsp;', ' ').strip(),
                    'percentage': item.get('percentageformatted', '').replace('%', '').strip(),
                    'weight': item.get('weightformatted', '').replace('%', '').strip(),
                    'feedback': item.get('feedback', '').strip(),
                    'max_grade': item.get('grademax')
                }
                grade_items.append(grade_item)
        
        # Add course total if available
        if 'grade' in user_grades:
            grade_items.append({
                'id': 'total',
                'name': 'Course Total',
                'grade': user_grades.get('grade', '').replace('&nbsp;', ' ').strip(),
                'percentage': user_grades.get('percentage', ''),
                'weight': '100',
                'feedback': '',
                'max_grade': 100
            })
        
        # Generate analysis
        try:
            # Initialize grade analyzer
            grade_analyzer = GradeAnalyzer(api_key=config.OPENAI_API_KEY)
            
            # Generate and store analysis
            analysis = grade_analyzer.analyze_grades(course_id, grade_items)
            
            # Get the latest analysis (the one we just created)
            analyses = grade_analyzer.get_all_analyses(course_id)
            if analyses:
                latest_analysis = analyses[0]
                return redirect(url_for('view_analysis', analysis_id=latest_analysis['id']))
            else:
                flash("Error retrieving the generated analysis.", 'danger')
                return redirect(url_for('course_grades', course_id=course_id))
                
        except Exception as e:
            flash(f"Error generating analysis: {str(e)}", 'danger')
            return redirect(url_for('course_grades', course_id=course_id))
            
    except Exception as e:
        flash(f"Error retrieving grades: {str(e)}", 'danger')
        return redirect(url_for('course_grades', course_id=course_id))

@app.route('/course/<int:course_id>/analyses')
def course_analyses(course_id):
    """View all grade analyses for a course"""
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    # Get client
    client = get_client()
    if not client:
        return redirect(url_for('login'))
    
    # Get course info
    try:
        courses = client.get_courses()
        course = next((c for c in courses if c['id'] == course_id), None)
        
        if not course:
            flash(f"Course with ID {course_id} not found.", 'danger')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"Error retrieving course: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))
    
    # Get analyses
    try:
        grade_analyzer = GradeAnalyzer(api_key=config.OPENAI_API_KEY)
        analyses = grade_analyzer.get_all_analyses(course_id=course_id)
        
        return render_template('course_analyses.html', course=course, analyses=analyses)
    except Exception as e:
        flash(f"Error retrieving analyses: {str(e)}", 'danger')
        return redirect(url_for('course_detail', course_id=course_id))

@app.route('/analysis/<int:analysis_id>')
def view_analysis(analysis_id):
    """View a specific grade analysis"""
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    # Get client
    client = get_client()
    if not client:
        return redirect(url_for('login'))
    
    try:
        # Initialize grade analyzer
        grade_analyzer = GradeAnalyzer(api_key=config.OPENAI_API_KEY)
        
        # Get the analysis
        analysis = grade_analyzer.get_analysis(analysis_id)
        if not analysis:
            flash("Analysis not found.", 'danger')
            return redirect(url_for('dashboard'))
        
        # Get course info
        course_id = analysis['course_id']
        courses = client.get_courses()
        course = next((c for c in courses if c['id'] == course_id), None)
        
        if not course:
            flash(f"Course with ID {course_id} not found.", 'danger')
            return redirect(url_for('dashboard'))
        
        return render_template('grade_analysis.html', course=course, analysis=analysis)
    except Exception as e:
        flash(f"Error retrieving analysis: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))

@app.route('/delete-analysis/<int:analysis_id>', methods=['POST'])
def delete_analysis(analysis_id):
    """Delete a grade analysis"""
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    try:
        # Initialize grade analyzer
        grade_analyzer = GradeAnalyzer(api_key=config.OPENAI_API_KEY)
        
        # Get the analysis to find its course ID for redirection
        analysis = grade_analyzer.get_analysis(analysis_id)
        if not analysis:
            flash("Analysis not found.", 'danger')
            return redirect(url_for('dashboard'))
        
        course_id = analysis['course_id']
        
        # Delete the analysis
        grade_analyzer.delete_analysis(analysis_id)
        
        flash("Analysis deleted successfully.", 'success')
        return redirect(url_for('course_analyses', course_id=course_id))
    except Exception as e:
        flash(f"Error deleting analysis: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create template files if they don't exist
    create_templates()
    
    # Run the app
    app.run(debug=True)
    """Create HTML templates for the web app"""
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    # Base template
    base_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Moodle API Client{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding-top: 60px; }
        .course-card { height: 100%; }
        .lecture-note { margin-bottom: 10px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-md navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">Moodle API Client</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {% if 'username' in session %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard') }}">Dashboard</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('logout') }}">Logout</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('login') }}">Login</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    # Index template
    index_html = '''{% extends "base.html" %}

{% block title %}Moodle API Client - Home{% endblock %}

{% block content %}
<div class="px-4 py-5 my-5 text-center">
    <h1 class="display-5 fw-bold">Moodle API Client</h1>
    <div class="col-lg-6 mx-auto">
        <p class="lead mb-4">
            Access your Concordia University Moodle courses, grades, and lecture materials.
        </p>
        <div class="d-grid gap-2 d-sm-flex justify-content-sm-center">
            <a href="{{ url_for('login') }}" class="btn btn-primary btn-lg px-4 gap-3">Login with API Token</a>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Login template
    login_html = '''{% extends "base.html" %}

{% block title %}Login - Moodle API Client{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h4 class="mb-0">Login with Moodle API Token</h4>
            </div>
            <div class="card-body">
                {% if error %}
                    <div class="alert alert-danger">{{ error }}</div>
                {% endif %}
                
                <form method="POST" action="{{ url_for('login') }}">
                    {{ form.hidden_tag() }}
                    <div class="mb-3">
                        {{ form.token.label(class="form-label") }}
                        {{ form.token(class="form-control") }}
                        <div class="form-text">
                            You can obtain your token from Moodle. See the 
                            <a href="https://github.com/yourusername/moodle-api-client/blob/main/docs/obtaining_api_token.md" target="_blank">documentation</a>.
                        </div>
                    </div>
                    <div class="d-grid">
                        {{ form.submit(class="btn btn-primary") }}
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Dashboard template
    dashboard_html = '''{% extends "base.html" %}

{% block title %}Dashboard - Moodle API Client{% endblock %}

{% block content %}
<h1 class="mb-4">Welcome, {{ username }}</h1>

<h2 class="mb-3">Your Courses</h2>

<div class="row row-cols-1 row-cols-md-3 g-4">
    {% for course in courses %}
        <div class="col">
            <div class="card course-card">
                <div class="card-body">
                    <h5 class="card-title">{{ course.fullname }}</h5>
                    <p class="card-text"><small class="text-muted">{{ course.shortname }}</small></p>
                </div>
                <div class="card-footer">
                    <a href="{{ url_for('course_detail', course_id=course.id) }}" class="btn btn-primary">View Course</a>
                </div>
            </div>
        </div>
    {% else %}
        <div class="col-12">
            <div class="alert alert-info">You are not enrolled in any courses.</div>
        </div>
    {% endfor %}
</div>
{% endblock %}'''
    
    # Course detail template
    course_detail_html = '''{% extends "base.html" %}

{% block title %}{{ course.fullname }} - Moodle API Client{% endblock %}

{% block content %}
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="{{ url_for('dashboard') }}">Dashboard</a></li>
        <li class="breadcrumb-item active">{{ course.fullname }}</li>
    </ol>
</nav>

<h1 class="mb-4">{{ course.fullname }}</h1>
<p><small class="text-muted">{{ course.shortname }}</small></p>

<div class="row mt-4">
    <div class="col-md-4 mb-3">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Grades</h5>
                <p class="card-text">View your grades for this course.</p>
                <a href="{{ url_for('course_grades', course_id=course.id) }}" class="btn btn-primary">View Grades</a>
            </div>
        </div>
    </div>
    
    <div class="col-md-4 mb-3">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Lecture Notes</h5>
                <p class="card-text">Access lecture notes and materials.</p>
                <a href="{{ url_for('course_lecture_notes', course_id=course.id) }}" class="btn btn-primary">View Lecture Notes</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Course grades template
    course_grades_html = '''{% extends "base.html" %}

{% block title %}Grades: {{ course.fullname }} - Moodle API Client{% endblock %}

{% block content %}
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="{{ url_for('dashboard') }}">Dashboard</a></li>
        <li class="breadcrumb-item"><a href="{{ url_for('course_detail', course_id=course.id) }}">{{ course.fullname }}</a></li>
        <li class="breadcrumb-item active">Grades</li>
    </ol>
</nav>

<h1 class="mb-4">Grades for {{ course.fullname }}</h1>

{% if grades and 'usergrades' in grades and grades.usergrades %}
    {% set user_grades = grades.usergrades[0] %}
    
    {% if 'grade' in user_grades %}
        <div class="alert alert-info">
            <h4>Overall Course Grade: {{ user_grades.grade }}</h4>
        </div>
    {% endif %}
    
    {% if 'gradeitems' in user_grades and user_grades.gradeitems %}
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Assessment</th>
                        <th>Grade</th>
                        <th>Weight</th>
                        <th>Feedback</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in user_grades.gradeitems %}
                        {% if item.itemname and item.itemname|lower != 'course total' %}
                            <tr>
                                <td>{{ item.itemname }}</td>
                                <td>{{ item.gradeformatted|default('-') }}</td>
                                <td>{{ item.weightformatted|default('-') }}</td>
                                <td>{{ item.feedback|default('-') }}</td>
                            </tr>
                        {% endif %}
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <div class="alert alert-warning">No grade items found for this course.</div>
    {% endif %}
    
    {% if 'warnings' in grades and grades.warnings %}
        <div class="alert alert-warning">
            <h5>Warnings:</h5>
            <ul>
                {% for warning in grades.warnings %}
                    <li>{{ warning.message }}</li>
                {% endfor %}
            </ul>
        </div>
    {% endif %}
{% else %}
    <div class="alert alert-warning">
        No grades available for this course. This could be because:
        <ul>
            <li>There are no graded items yet</li>
            <li>The Moodle API doesn't have permission to access grades</li>
            <li>There was an error retrieving the grades</li>
        </ul>
    </div>
{% endif %}
{% endblock %}'''
    
    # Course lecture notes template
    course_lecture_notes_html = '''{% extends "base.html" %}

{% block title %}Lecture Notes: {{ course.fullname }} - Moodle API Client{% endblock %}

{% block content %}
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="{{ url_for('dashboard') }}">Dashboard</a></li>
        <li class="breadcrumb-item"><a href="{{ url_for('course_detail', course_id=course.id) }}">{{ course.fullname }}</a></li>
        <li class="breadcrumb-item active">Lecture Notes</li>
    </ol>
</nav>

<h1 class="mb-4">Lecture Notes for {{ course.fullname }}</h1>

{% if lecture_notes %}
    <div class="accordion" id="lectureNotesAccordion">
        {% for section in lecture_notes %}
            <div class="accordion-item">
                <h2 class="accordion-header" id="heading{{ loop.index }}">
                    <button class="accordion-button {% if not loop.first %}collapsed{% endif %}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{{ loop.index }}">
                        {{ section.name }}
                    </button>
                </h2>
                <div id="collapse{{ loop.index }}" class="accordion-collapse collapse {% if loop.first %}show{% endif %}" data-bs-parent="#lectureNotesAccordion">
                    <div class="accordion-body">
                        <div class="list-group">
                            {% for module in section.modules %}
                                <div class="list-group-item lecture-note">
                                    <h5>{{ module.name }}</h5>
                                    <p><small class="text-muted">Type: {{ module.modname }}</small></p>
                                    
                                    {% if 'contents' in module %}
                                        <ul class="list-unstyled">
                                            {% for content in module.contents %}
                                                <li class="mb-2">
                                                    <div class="d-flex justify-content-between align-items-center">
                                                        <div>
                                                            <i class="bi bi-file-earmark"></i>
                                                            {{ content.filename }}
                                                            <small class="text-muted">({{ (content.filesize / 1024)|round(1) }} KB)</small>
                                                        </div>
                                                        {% if 'fileurl' in content %}
                                                            <a href="{{ url_for('download_file', course_id=course.id, file_url=content.fileurl|replace('?', '___')|replace('&', '__')) }}" 
                                                               class="btn btn-sm btn-outline-primary">
                                                                Download
                                                            </a>
                                                        {% endif %}
                                                    </div>
                                                </li>
                                            {% endfor %}
                                        </ul>
                                    {% elif module.modname == 'url' and 'url' in module %}
                                        <a href="{{ module.url }}" target="_blank" class="btn btn-sm btn-outline-primary">
                                            Open URL
                                        </a>
                                    {% endif %}
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        {% endfor %}
    </div>
{% else %}
    <div class="alert alert-info">No lecture notes found for this course.</div>
{% endif %}
{% endblock %}'''
    
    # Write templates to files
    with open(os.path.join(templates_dir, 'base.html'), 'w') as f:
        f.write(base_html)
    
    with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
        f.write(index_html)
    
    with open(os.path.join(templates_dir, 'login.html'), 'w') as f:
        f.write(login_html)
    
    with open(os.path.join(templates_dir, 'dashboard.html'), 'w') as f:
        f.write(dashboard_html)
    
    with open(os.path.join(templates_dir, 'course_detail.html'), 'w') as f:
        f.write(course_detail_html)
    
    with open(os.path.join(templates_dir, 'course_grades.html'), 'w') as f:
        f.write(course_grades_html)
    
    with open(os.path.join(templates_dir, 'course_lecture_notes.html'), 'w') as f:
        f.write(course_lecture_notes_html)
