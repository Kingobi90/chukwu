#!/usr/bin/env python3
"""
Download course content from Moodle
"""

import sys
import os
import json
import requests
from urllib.parse import urlparse, unquote
from pathlib import Path

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from moodle_client import MoodleAPIClient

def download_file(url, token, destination):
    """
    Download a file from Moodle
    
    Args:
        url: URL of the file
        token: Moodle API token
        destination: Path to save the file
    
    Returns:
        True if download was successful, False otherwise
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    # Add token to URL if it's a Moodle URL
    if 'pluginfile.php' in url:
        if '?' in url:
            url += f"&token={token}"
        else:
            url += f"?token={token}"
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded: {destination}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def get_filename_from_url(url):
    """Extract filename from URL"""
    parsed = urlparse(url)
    path = unquote(parsed.path)
    return os.path.basename(path)

def download_course_content(client, course_id, output_dir):
    """
    Download all available content for a course
    
    Args:
        client: MoodleAPIClient instance
        course_id: ID of the course
        output_dir: Directory to save files
    """
    # Get course details to use as folder name
    courses = client.get_courses()
    course_name = next((c['shortname'] for c in courses if c['id'] == course_id), f"course_{course_id}")
    
    # Create sanitized folder name
    safe_course_name = "".join(c if c.isalnum() else "_" for c in course_name)
    course_dir = os.path.join(output_dir, safe_course_name)
    
    # Get course contents
    contents = client.get_course_contents(course_id)
    
    # Track download statistics
    stats = {
        'total_files': 0,
        'downloaded': 0,
        'failed': 0
    }
    
    # Process each section
    for section in contents:
        section_name = section.get('name', 'Unnamed Section')
        if not section_name or section_name == "Unnamed Section":
            section_name = f"Section {section.get('section', 0)}"
        
        # Create sanitized section folder name
        safe_section_name = "".join(c if c.isalnum() else "_" for c in section_name)
        section_dir = os.path.join(course_dir, safe_section_name)
        
        # Process each module in the section
        for module in section.get('modules', []):
            module_name = module.get('name', 'Unnamed Module')
            module_type = module.get('modname', 'unknown')
            
            # Handle different module types
            if module_type == 'resource':
                # Direct file resources
                for content in module.get('contents', []):
                    stats['total_files'] += 1
                    file_url = content.get('fileurl')
                    if file_url:
                        filename = content.get('filename', get_filename_from_url(file_url))
                        file_path = os.path.join(section_dir, filename)
                        
                        if download_file(file_url, client.token, file_path):
                            stats['downloaded'] += 1
                        else:
                            stats['failed'] += 1
            
            elif module_type == 'folder':
                # Folder resources
                folder_name = "".join(c if c.isalnum() else "_" for c in module_name)
                folder_dir = os.path.join(section_dir, folder_name)
                
                for content in module.get('contents', []):
                    stats['total_files'] += 1
                    file_url = content.get('fileurl')
                    if file_url:
                        filename = content.get('filename', get_filename_from_url(file_url))
                        file_path = os.path.join(folder_dir, filename)
                        
                        if download_file(file_url, client.token, file_path):
                            stats['downloaded'] += 1
                        else:
                            stats['failed'] += 1
            
            elif module_type == 'url':
                # URL resources - save as .url file
                if 'contents' not in module and module.get('url'):
                    stats['total_files'] += 1
                    url_name = "".join(c if c.isalnum() else "_" for c in module_name)
                    url_file = os.path.join(section_dir, f"{url_name}.url")
                    
                    try:
                        os.makedirs(os.path.dirname(url_file), exist_ok=True)
                        with open(url_file, 'w') as f:
                            f.write(f"[InternetShortcut]\nURL={module.get('url')}")
                        print(f"Saved URL: {url_file}")
                        stats['downloaded'] += 1
                    except Exception as e:
                        print(f"Error saving URL {module_name}: {e}")
                        stats['failed'] += 1
    
    return stats

def main():
    # Directory to save downloaded files
    output_dir = os.path.expanduser("~/Downloads/MoodleCourses")
    
    try:
        client = MoodleAPIClient()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set up your config.py file with your API token.")
        return
    
    # Get list of courses
    courses = client.get_courses()
    
    if not courses:
        print("No courses found.")
        return
    
    # Display available courses
    print("Available courses:")
    for i, course in enumerate(courses, 1):
        print(f"{i}. {course['fullname']} ({course['shortname']})")
    
    # Ask which course to download
    try:
        selection = int(input("\nEnter the number of the course to download (0 for all): "))
        
        if selection == 0:
            # Download all courses
            for course in courses:
                print(f"\nDownloading content for: {course['fullname']}")
                stats = download_course_content(client, course['id'], output_dir)
                print(f"Downloaded {stats['downloaded']} of {stats['total_files']} files ({stats['failed']} failed)")
        elif 1 <= selection <= len(courses):
            # Download selected course
            course = courses[selection - 1]
            print(f"\nDownloading content for: {course['fullname']}")
            stats = download_course_content(client, course['id'], output_dir)
            print(f"Downloaded {stats['downloaded']} of {stats['total_files']} files ({stats['failed']} failed)")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Please enter a valid number.")
    
    print(f"\nFiles have been downloaded to: {output_dir}")

if __name__ == "__main__":
    main()
