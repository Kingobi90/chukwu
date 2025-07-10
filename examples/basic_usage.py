#!/usr/bin/env python3
"""
Basic usage example for the Moodle API Client
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from moodle_client import MoodleAPIClient

def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def main():
    # Create a client instance
    try:
        client = MoodleAPIClient()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set up your config.py file with your API token.")
        return
    
    # Get and display site info
    print("Getting site info...")
    site_info = client.get_site_info()
    print(f"Connected to {site_info.get('sitename')} as {site_info.get('fullname')}")
    print(f"User ID: {site_info.get('userid')}")
    print(f"Moodle version: {site_info.get('release')}")
    print()
    
    # Get and display courses
    print("Getting enrolled courses...")
    courses = client.get_courses()
    print(f"You are enrolled in {len(courses)} courses:")
    for course in courses:
        print(f"- {course.get('fullname')} (ID: {course.get('id')})")
    print()
    
    # If there are courses, get details for the first one
    if courses:
        course_id = courses[0]['id']
        course_name = courses[0]['fullname']
        
        print(f"Getting details for course: {course_name}...")
        
        # Get course contents
        contents = client.get_course_contents(course_id)
        print(f"Course has {len(contents)} sections")
        
        # Get assignments for this course
        assignments = client.get_assignments(course_id)
        if 'courses' in assignments and assignments['courses']:
            course_assignments = assignments['courses'][0].get('assignments', [])
            print(f"Found {len(course_assignments)} assignments:")
            for assignment in course_assignments:
                due_date = datetime.fromtimestamp(assignment.get('duedate', 0))
                print(f"- {assignment.get('name')} (Due: {due_date.strftime('%Y-%m-%d %H:%M')})")
        else:
            print("No assignments found for this course")
        
        # Get grades for this course
        try:
            grades = client.get_user_grades(course_id)
            print(f"Retrieved grade information")
        except Exception as e:
            print(f"Could not retrieve grades: {e}")

if __name__ == "__main__":
    main()
