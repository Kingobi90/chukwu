#!/usr/bin/env python3
"""
Extract and display lecture notes for a specific course
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

def get_lecture_notes(client, course_id):
    """
    Get all lecture notes for a course
    
    Args:
        client: MoodleAPIClient instance
        course_id: ID of the course
        
    Returns:
        List of lecture note modules
    """
    # Get course contents
    sections = client.get_course_contents(course_id)
    
    # List to store lecture notes
    lecture_notes = []
    
    # Process each section
    for section in sections:
        section_name = section.get('name', f"Section {section.get('section', 0)}")
        
        # Process each module in the section
        for module in section.get('modules', []):
            # Check if this module is likely a lecture note
            if is_likely_lecture_note(module):
                # Add section name to the module for context
                module['section_name'] = section_name
                lecture_notes.append(module)
    
    return lecture_notes

def display_lecture_notes(lecture_notes):
    """
    Display lecture notes in a readable format
    
    Args:
        lecture_notes: List of lecture note modules
    """
    if not lecture_notes:
        print("No lecture notes found for this course.")
        return
    
    print(f"\nFound {len(lecture_notes)} lecture notes:")
    print("-" * 60)
    
    # Group by section
    sections = {}
    for module in lecture_notes:
        section_name = module.get('section_name', 'Unknown Section')
        if section_name not in sections:
            sections[section_name] = []
        sections[section_name].append(module)
    
    # Display by section
    for section_name, modules in sections.items():
        print(f"\n{section_name}:")
        
        for i, module in enumerate(modules, 1):
            module_type = module.get('modname', 'unknown')
            module_name = module.get('name', f"Item {i}")
            
            print(f"  {i}. [{module_type}] {module_name}")
            
            # Show file details if available
            if 'contents' in module:
                for content in module['contents']:
                    filename = content.get('filename', 'Unnamed file')
                    filesize = content.get('filesize', 0) / 1024  # KB
                    print(f"     - {filename} ({filesize:.1f} KB)")
                    if 'fileurl' in content:
                        print(f"       URL: {content.get('fileurl')}")
            
            # Show URL if it's a URL resource
            elif module_type == 'url' and 'url' in module:
                print(f"     URL: {module.get('url')}")

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
    
    # Get lecture notes
    print(f"\nRetrieving lecture notes for {course['fullname']}...")
    lecture_notes = get_lecture_notes(client, course['id'])
    
    # Display lecture notes
    display_lecture_notes(lecture_notes)
    
    # Option to download
    if lecture_notes:
        download = input("\nWould you like to download these lecture notes? (y/n): ")
        if download.lower() == 'y':
            print("\nDownload functionality not implemented in this example.")
            print("You can use the course_content_downloader.py script to download course files.")

if __name__ == "__main__":
    main()
