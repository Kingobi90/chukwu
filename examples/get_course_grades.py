#!/usr/bin/env python3
"""
Retrieve and display grades for a specific course
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from moodle_client import MoodleAPIClient

def find_course_by_name(client, course_name):
    """
    Find a course by its name or code
    
    Args:
        client: MoodleAPIClient instance
        course_name: Name or code of the course to find
        
    Returns:
        Course dict if found, None otherwise
    """
    courses = client.get_courses()
    
    # Try to find an exact match first
    for course in courses:
        if course_name.lower() in course['fullname'].lower() or course_name.lower() in course['shortname'].lower():
            return course
    
    return None

def extract_grades_from_course_contents(client, course_id):
    """
    Extract grades by parsing course contents
    This is a fallback method when the grades API is not available
    
    Args:
        client: MoodleAPIClient instance
        course_id: ID of the course
        
    Returns:
        List of dictionaries containing grade information
    """
    try:
        # Get course contents
        contents = client.get_course_contents(course_id)
        
        # List to store grade items
        grade_items = []
        
        # Look for modules that might contain grades
        for section in contents:
            for module in section.get('modules', []):
                module_type = module.get('modname', '').lower()
                module_name = module.get('name', '')
                
                # Check if this module might have grade information
                if module_type in ['assign', 'quiz', 'workshop', 'forum'] and 'completiondata' in module:
                    completion = module.get('completiondata', {})
                    grade_info = completion.get('grade', None)
                    
                    if grade_info is not None:
                        grade_items.append({
                            'name': module_name,
                            'type': module_type,
                            'grade': str(grade_info) if grade_info else 'Not graded',
                        })
        
        return grade_items
    except Exception as e:
        print(f"Error extracting grades from course contents: {e}")
        return []

def get_course_grades(client, course_id):
    """
    Get grades for a specific course
    
    Args:
        client: MoodleAPIClient instance
        course_id: ID of the course
        
    Returns:
        Dictionary containing grade information or a list of grade items
    """
    try:
        # First try to get grades using the official API
        grades = client.get_user_grades(course_id)
        
        # Check if we got meaningful data
        if grades and 'usergrades' in grades and grades['usergrades']:
            return grades
            
        print("The grades API didn't return useful data. Trying alternative method...")
        
        # If the API didn't work, try extracting grades from course contents
        grade_items = extract_grades_from_course_contents(client, course_id)
        
        if grade_items:
            return grade_items
        else:
            print("Could not extract grades from course contents either.")
            return None
    except Exception as e:
        print(f"Error retrieving grades: {e}")
        
        # Try the fallback method
        print("Trying alternative method to find grades...")
        grade_items = extract_grades_from_course_contents(client, course_id)
        
        if grade_items:
            return grade_items
        else:
            return None

def display_grades(grades, course_name):
    """
    Display grades in a readable format
    
    Args:
        grades: Dictionary containing grade information
        course_name: Name of the course
    """
    if not grades:
        print(f"No grades found for {course_name}.")
        return
    
    # Handle the case where we're getting grades from a different source
    if isinstance(grades, dict) and 'error' in grades:
        print(f"Error retrieving grades: {grades['error']}")
        return
        
    # Display course information
    print(f"\nGrades for {course_name}")
    print("-" * 60)
    
    # Handle the case where we have usergrades from the API
    if isinstance(grades, dict) and 'usergrades' in grades and grades['usergrades']:
        # Extract user grades
        user_grades = grades['usergrades'][0] if grades['usergrades'] else {}
        
        # Display overall course grade if available
        if 'coursename' in user_grades and 'grade' in user_grades:
            print(f"Overall Course Grade: {user_grades.get('grade', 'Not available')}")
        
        # Display individual grade items
        if 'gradeitems' in user_grades and user_grades['gradeitems']:
            print("\nIndividual Assessments:")
            
            for item in user_grades['gradeitems']:
                item_name = item.get('itemname')
                
                # Skip course total or items without names
                if not item_name:
                    continue
                    
                if item_name.lower() == 'course total':
                    continue
                    
                grade = item.get('gradeformatted', 'Not graded')
                weight = item.get('weightformatted', 'N/A')
                
                print(f"- {item_name}")
                print(f"  Grade: {grade}")
                if weight != 'N/A':
                    print(f"  Weight: {weight}")
                
                # Show feedback if available
                if 'feedback' in item and item['feedback']:
                    print(f"  Feedback: {item['feedback']}")
                
                print()
        
        # Check for warnings
        if 'warnings' in grades and grades['warnings']:
            print("\nWarnings:")
            for warning in grades['warnings']:
                print(f"- {warning.get('message', 'Unknown warning')}")
    
    # If we have manually extracted grades
    elif isinstance(grades, list):
        print("\nAssessments:")
        for item in grades:
            name = item.get('name', 'Unnamed assessment')
            grade = item.get('grade', 'Not graded')
            
            print(f"- {name}")
            print(f"  Grade: {grade}")
            print()
    
    # Check for warnings
    if 'warnings' in grades and grades['warnings']:
        print("\nWarnings:")
        for warning in grades['warnings']:
            print(f"- {warning.get('message', 'Unknown warning')}")

def main():
    # Course to search for
    course_name = "ENGR 290"
    
    try:
        client = MoodleAPIClient()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set up your config.py file with your API token.")
        return
    
    # Get and display site info
    site_info = client.get_site_info()
    print(f"Connected to {site_info.get('sitename')} as {site_info.get('fullname')}")
    
    # Find the course
    print(f"\nSearching for course: {course_name}")
    course = find_course_by_name(client, course_name)
    
    if not course:
        print(f"Course '{course_name}' not found.")
        return
    
    print(f"Found course: {course['fullname']} ({course['shortname']})")
    
    # Get grades
    print(f"\nRetrieving grades for {course['fullname']}...")
    grades = get_course_grades(client, course['id'])
    
    # Display grades
    display_grades(grades, course['fullname'])
    
    # Alternative method if API doesn't work
    if not grades or 'usergrades' not in grades or not grades['usergrades']:
        print("\nNote: The Moodle API might not have permission to access grades.")
        print("You may need to access grades through the Moodle web interface.")

if __name__ == "__main__":
    main()
