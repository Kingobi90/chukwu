#!/usr/bin/env python3
"""
Explore a specific Moodle course's content
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from moodle_client import MoodleAPIClient

def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def select_course(client):
    """
    Display available courses and let the user select one
    
    Returns:
        Tuple of (course_id, course_name) or (None, None) if no selection
    """
    # Get all courses
    courses = client.get_courses()
    
    if not courses:
        print("No courses found.")
        return None, None
    
    # Display courses
    print("\nYour enrolled courses:")
    print("-" * 60)
    for i, course in enumerate(courses, 1):
        print(f"{i}. {course['fullname']} ({course['shortname']})")
    
    # Get user selection
    try:
        selection = int(input("\nEnter the number of the course to explore (0 to exit): "))
        if selection == 0:
            return None, None
        if 1 <= selection <= len(courses):
            course = courses[selection - 1]
            return course['id'], course['fullname']
        else:
            print("Invalid selection.")
            return None, None
    except ValueError:
        print("Please enter a valid number.")
        return None, None

def explore_course_sections(client, course_id):
    """
    Display and explore the sections of a course
    """
    # Get course contents (sections)
    sections = client.get_course_contents(course_id)
    
    if not sections:
        print("No content found for this course.")
        return
    
    # Display sections
    print("\nCourse sections:")
    print("-" * 60)
    for i, section in enumerate(sections, 1):
        section_name = section.get('name')
        if not section_name:
            section_name = f"Section {section.get('section', i)}"
        
        module_count = len(section.get('modules', []))
        print(f"{i}. {section_name} ({module_count} items)")
    
    # Get user selection
    try:
        selection = int(input("\nEnter the number of the section to explore (0 to go back): "))
        if selection == 0:
            return
        if 1 <= selection <= len(sections):
            explore_section_modules(sections[selection - 1])
        else:
            print("Invalid selection.")
    except ValueError:
        print("Please enter a valid number.")

def explore_section_modules(section):
    """
    Display and explore the modules within a section
    """
    modules = section.get('modules', [])
    
    if not modules:
        print("No modules found in this section.")
        return
    
    # Display modules
    print(f"\nModules in {section.get('name', 'this section')}:")
    print("-" * 60)
    for i, module in enumerate(modules, 1):
        module_type = module.get('modname', 'unknown')
        module_name = module.get('name', f"Item {i}")
        print(f"{i}. [{module_type}] {module_name}")
    
    # Get user selection
    try:
        selection = int(input("\nEnter the number of the module to view details (0 to go back): "))
        if selection == 0:
            return
        if 1 <= selection <= len(modules):
            display_module_details(modules[selection - 1])
        else:
            print("Invalid selection.")
    except ValueError:
        print("Please enter a valid number.")

def display_module_details(module):
    """
    Display detailed information about a module
    """
    module_type = module.get('modname', 'unknown')
    module_name = module.get('name', 'Unnamed module')
    
    print(f"\nDetails for: {module_name}")
    print(f"Type: {module_type}")
    print("-" * 60)
    
    # Handle different module types
    if module_type == 'resource':
        # File resource
        print("This is a file resource.")
        if 'contents' in module:
            for content in module['contents']:
                print(f"Filename: {content.get('filename')}")
                print(f"Size: {content.get('filesize', 0) / 1024:.1f} KB")
                print(f"Type: {content.get('mimetype', 'unknown')}")
                if 'fileurl' in content:
                    print(f"URL: {content.get('fileurl')}")
    
    elif module_type == 'url':
        # URL resource
        print("This is a URL resource.")
        if 'url' in module:
            print(f"URL: {module.get('url')}")
    
    elif module_type == 'folder':
        # Folder resource
        print("This is a folder containing multiple files:")
        if 'contents' in module:
            for i, content in enumerate(module['contents'], 1):
                print(f"{i}. {content.get('filename')} ({content.get('filesize', 0) / 1024:.1f} KB)")
    
    elif module_type == 'assign':
        # Assignment
        print("This is an assignment.")
        if 'dates' in module:
            for date_info in module['dates']:
                label = date_info.get('label', 'Date')
                timestamp = date_info.get('timestamp', 0)
                if timestamp > 0:
                    date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
                    print(f"{label}: {date_str}")
    
    elif module_type == 'forum':
        # Forum
        print("This is a discussion forum.")
        if 'description' in module:
            print("\nDescription:")
            print(module.get('description', 'No description available.'))
    
    elif module_type == 'quiz':
        # Quiz
        print("This is a quiz.")
        if 'dates' in module:
            for date_info in module['dates']:
                label = date_info.get('label', 'Date')
                timestamp = date_info.get('timestamp', 0)
                if timestamp > 0:
                    date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
                    print(f"{label}: {date_str}")
    
    else:
        # Other module types
        print(f"This is a {module_type} module.")
        if 'description' in module:
            print("\nDescription:")
            print(module.get('description', 'No description available.'))
    
    # Show any available contents
    if 'contents' in module and module_type not in ['resource', 'folder']:
        print("\nContents:")
        for content in module['contents']:
            print(f"- {content.get('filename', 'Unnamed file')} ({content.get('filesize', 0) / 1024:.1f} KB)")
    
    input("\nPress Enter to continue...")

def main():
    try:
        client = MoodleAPIClient()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set up your config.py file with your API token.")
        return
    
    # Get and display site info
    site_info = client.get_site_info()
    print(f"Connected to {site_info.get('sitename')} as {site_info.get('fullname')}")
    
    while True:
        # Select a course
        course_id, course_name = select_course(client)
        if not course_id:
            break
        
        print(f"\nExploring course: {course_name}")
        
        # Course exploration menu
        while True:
            print("\nOptions:")
            print("1. Browse course content")
            print("2. View course participants")
            print("3. Back to course selection")
            
            try:
                option = int(input("\nSelect an option: "))
                
                if option == 1:
                    explore_course_sections(client, course_id)
                elif option == 2:
                    print("\nParticipants feature is not implemented in this example.")
                    # In a full implementation, you would call an API function to get participants
                elif option == 3:
                    break
                else:
                    print("Invalid option.")
            except ValueError:
                print("Please enter a valid number.")
    
    print("\nThank you for using the Moodle Explorer!")

if __name__ == "__main__":
    main()
