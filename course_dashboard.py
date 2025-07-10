#!/usr/bin/env python3
"""
Moodle Course Dashboard
Access grades, lecture notes, and PDF summaries for any course
"""

import sys
import os
import json
import requests
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union

from moodle_client import MoodleAPIClient
from pdf_summarizer import PDFSummarizer
from grade_analyzer import GradeAnalyzer
import config

def select_course(client):
    """
    Display available courses and let the user select one
    
    Returns:
        Tuple of (course_id, course_name, course_shortname) or (None, None, None) if no selection
    """
    # Get all courses
    courses = client.get_courses()
    
    if not courses:
        print("No courses found.")
        return None, None, None
    
    # Display courses
    print("\nYour enrolled courses:")
    print("-" * 60)
    for i, course in enumerate(courses, 1):
        print(f"{i}. {course['fullname']} ({course['shortname']})")
    
    # Get user selection
    try:
        selection = int(input("\nEnter the number of the course to explore (0 to exit): "))
        if selection == 0:
            return None, None, None
        if 1 <= selection <= len(courses):
            course = courses[selection - 1]
            return course['id'], course['fullname'], course['shortname']
        else:
            print("Invalid selection.")
            return None, None, None
    except ValueError:
        print("Please enter a valid number.")
        return None, None, None

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

def download_file(url, token, destination):
    """
    Download a file from Moodle
    
    Args:
        url: URL of the file to download
        token: Moodle API token
        destination: Path to save the file to
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Add token to URL
        if '?' in url:
            full_url = f"{url}&token={token}"
        else:
            full_url = f"{url}?token={token}"
        
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # Download the file
        response = requests.get(full_url, stream=True)
        response.raise_for_status()
        
        # Save the file
        with open(destination, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
            
        return True, f"Downloaded to {destination}"
    except Exception as e:
        return False, f"Error downloading file: {e}"

def sanitize_filename(filename):
    """
    Sanitize a filename to be safe for all operating systems
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Replace invalid characters
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:196] + ext
        
    return filename

def display_lecture_notes(lecture_notes, course_shortname=None, download=False, token=None, summarize=False):
    """
    Display lecture notes in a readable format and optionally download them
    
    Args:
        lecture_notes: List of lecture note modules
        course_shortname: Short name of the course for organizing downloads
        download: Whether to download the files
        token: Moodle API token for downloading files
        summarize: Whether to generate summaries for PDF files
    
    Returns:
        List of modules with download status if download=True, otherwise None
    """
    if not lecture_notes:
        print("No lecture notes found for this course.")
        return None
    
    print(f"\nFound {len(lecture_notes)} lecture notes:")
    print("-" * 60)
    
    # Group by section
    sections = {}
    for module in lecture_notes:
        section_name = module.get('section_name', 'Unknown Section')
        if section_name not in sections:
            sections[section_name] = []
        sections[section_name].append(module)
    
    # Create download directory if needed
    if download:
        # Create download directory
        if course_shortname:
            download_dir = Path(os.path.expanduser("~/Downloads/MoodleLectures")) / sanitize_filename(course_shortname)
        else:
            download_dir = Path(os.path.expanduser("~/Downloads/MoodleLectures"))
        
        download_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nDownloading files to {download_dir}")
        
        # Initialize PDF summarizer if summarization is requested
        pdf_summarizer = None
        if summarize:
            try:
                pdf_summarizer = PDFSummarizer(api_key=config.OPENAI_API_KEY)
                print("PDF summarizer initialized successfully")
            except Exception as e:
                print(f"Error initializing PDF summarizer: {e}")
                print("PDF summarization will be skipped")
    
    # Display by section
    for section_name, modules in sections.items():
        print(f"\n{section_name}:")
        
        # Create section directory if downloading
        if download and course_shortname:
            section_dir = os.path.join(download_dir, sanitize_filename(section_name))
            os.makedirs(section_dir, exist_ok=True)
        
        for i, module in enumerate(modules, 1):
            module_type = module.get('modname', 'unknown')
            module_name = module.get('name', f"Item {i}")
            
            print(f"  {i}. [{module_type}] {module_name}")
            
            # Create module directory if downloading
            if download and course_shortname:
                module_dir = os.path.join(section_dir, sanitize_filename(module_name))
                
                # For single files, don't create an extra directory
                if module_type == 'resource' and 'contents' in module and len(module['contents']) == 1:
                    module_dir = section_dir
            
            # Show file details if available
            if 'contents' in module:
                for content in module['contents']:
                    filename = content.get('filename', 'Unnamed file')
                    filesize = content.get('filesize', 0) / 1024  # KB
                    print(f"     - {filename} ({filesize:.1f} KB)")
                    
                    if 'fileurl' in content:
                        file_url = content.get('fileurl')
                        print(f"       URL: {file_url}")
                        
                        # Download the file if requested
                        if download and token:
                            safe_filename = sanitize_filename(filename)
                            file_path = download_dir / safe_filename
                            
                            success, message = download_file(file_url, token, file_path)
                            if success:
                                print(f"       ✓ {message}")
                            else:
                                print(f"       ✗ {message}")
                            
                            # Save download result
                            download_results.append({
                                'module': module_name,
                                'file': filename,
                                'success': success,
                                'message': message,
                                'path': str(file_path),
                                'summary': None
                            })
                            
                            # Generate summary for PDF files if requested
                            if summarize and pdf_summarizer and file_path.suffix.lower() == '.pdf':
                                try:
                                    print(f"       ⟳ Generating summary for {file_path.name}...")
                                    summary = pdf_summarizer.summarize_pdf(
                                        str(file_path),
                                        module.get('course', 0),
                                        module.get('id', 0)
                                    )
                                    download_results[-1]['summary'] = summary
                                    print(f"       ✓ Summary generated successfully")
                                except Exception as e:
                                    print(f"       ✗ Error generating summary: {e}")
            
            # Show URL if it's a URL resource
            elif module_type == 'url' and 'url' in module:
                url = module.get('url')
                print(f"     URL: {url}")
                
                # Save URL to a text file if downloading
                if download and course_shortname:
                    os.makedirs(module_dir, exist_ok=True)
                    url_file_path = os.path.join(module_dir, sanitize_filename(f"{module_name}.url.txt"))
                    
                    try:
                        with open(url_file_path, 'w') as f:
                            f.write(f"URL: {url}\n")
                            f.write(f"Name: {module_name}\n")
                            f.write(f"Section: {section_name}\n")
                        
                        print(f"       ✓ Saved URL to {url_file_path}")
                        download_results.append({
                            'module': module_name,
                            'file': f"{module_name}.url.txt",
                            'success': True,
                            'message': f"Saved URL to {url_file_path}",
                            'path': url_file_path,
                            'summary': None
                        })
                    except Exception as e:
                        print(f"       ✗ Error saving URL: {e}")
                        download_results.append({
                            'module': module_name,
                            'file': f"{module_name}.url.txt",
                            'success': False,
                            'message': f"Error saving URL: {e}",
                            'path': None,
                            'summary': None
                        })
    
    if download:
        # Summary of download results
        successful = sum(1 for result in download_results if result['success'])
        print(f"\nDownload summary: {successful}/{len(download_results)} files downloaded successfully")
        return download_results
    
    return None

def view_pdf_summaries(client, course_id, course_name):
    """
    View summaries of PDF files for a course
    
        client: MoodleAPIClient instance
        course_id: ID of the course
        course_name: Name of the course
    """
    # Initialize PDF summarizer
    try:
        pdf_summarizer = PDFSummarizer(api_key=config.OPENAI_API_KEY)
    except Exception as e:
        print(f"\nError initializing PDF summarizer: {e}")
        return
    
    # Get summaries for this course
    try:
        summaries = pdf_summarizer.get_all_summaries(course_id=course_id)
    except Exception as e:
        print(f"\nError retrieving summaries: {e}")
        return
    
    if not summaries:
        print(f"\nNo PDF summaries found for {course_name}.")
        return
    
    while True:
        # Display summaries
        print(f"\nPDF Summaries for {course_name}:")
        print("-" * 60)
        for i, summary in enumerate(summaries, 1):
            print(f"{i}. {summary['filename']} (Generated: {summary['created_at']})")
        print(f"{len(summaries) + 1}. Back to course menu")
        
        # Get user selection
        try:
            selection = int(input("\nEnter the number of the summary to view (or select 'Back'): "))
            
            if selection == len(summaries) + 1:
                return
            
            if 1 <= selection <= len(summaries):
                summary = summaries[selection - 1]
                
                # Display the summary
                print("\n" + "=" * 80)
                print(f"Summary of {summary['filename']}")
                print(f"Generated on {summary['created_at']}")
                print("=" * 80)
                print(summary['summary'])
                print("=" * 80)
                
                # Ask if user wants to delete this summary
                delete = input("\nDelete this summary? (y/n): ").lower()
                if delete == 'y':
                    try:
                        pdf_summarizer.delete_summary(summary['id'])
                        print("Summary deleted.")
                        # Refresh the summaries list
                        summaries = pdf_summarizer.get_all_summaries(course_id=course_id)
                        if not summaries:
                            print(f"\nNo more PDF summaries for {course_name}.")
                            return
                    except Exception as e:
                        print(f"Error deleting summary: {e}")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a valid number.")

def view_grade_analyses(client, course_id, course_name):
    """
    View AI-generated analyses of grades for a course
    
    Args:
        client: MoodleAPIClient instance
        course_id: ID of the course
        course_name: Name of the course
    """
    # Check if OpenAI API key is set
    if not config.OPENAI_API_KEY:
        print("\nError: OpenAI API key is not set in config.py")
        print("Please add your API key to config.py and try again")
        return
    
    # Initialize grade analyzer
    try:
        grade_analyzer = GradeAnalyzer(api_key=config.OPENAI_API_KEY)
    except Exception as e:
        print(f"\nError initializing grade analyzer: {e}")
        return
    
    while True:
        # Get analyses for this course
        try:
            analyses = grade_analyzer.get_all_analyses(course_id=course_id)
        except Exception as e:
            print(f"\nError retrieving grade analyses: {e}")
            return
        
        print(f"\nGrade Analyses for {course_name}:")
        print("-" * 60)
        
        if not analyses:
            print("No grade analyses found for this course.")
            
            # Ask if user wants to generate a new analysis
            generate = input("\nGenerate a new grade analysis? (y/n): ").lower()
            if generate == 'y':
                generate_grade_analysis(client, grade_analyzer, course_id, course_name)
                continue
            else:
                return
        
        # Display analyses
        for i, analysis in enumerate(analyses, 1):
            print(f"{i}. Grade analysis from {analysis['created_at']}")
        print(f"{len(analyses) + 1}. Generate new analysis")
        print(f"{len(analyses) + 2}. Back to course menu")
        
        # Get user selection
        try:
            selection = int(input("\nEnter your choice: "))
            
            if selection == len(analyses) + 2:
                return
            
            if selection == len(analyses) + 1:
                generate_grade_analysis(client, grade_analyzer, course_id, course_name)
                continue
            
            if 1 <= selection <= len(analyses):
                analysis = analyses[selection - 1]
                
                # Display the analysis
                print("\n" + "=" * 80)
                print(f"Grade Analysis for {course_name}")
                print(f"Generated on {analysis['created_at']}")
                print("=" * 80)
                print(analysis['analysis'])
                print("=" * 80)
                
                # Ask if user wants to delete this analysis
                delete = input("\nDelete this analysis? (y/n): ").lower()
                if delete == 'y':
                    try:
                        grade_analyzer.delete_analysis(analysis['id'])
                        print("Analysis deleted.")
                    except Exception as e:
                        print(f"Error deleting analysis: {e}")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a valid number.")

def generate_grade_analysis(client, grade_analyzer, course_id, course_name):
    """
    Generate a new grade analysis for a course
    
    Args:
        client: MoodleAPIClient instance
        grade_analyzer: GradeAnalyzer instance
        course_id: ID of the course
        course_name: Name of the course
    """
    print(f"\nGenerating grade analysis for {course_name}...")
    
    try:
        # Get grades
        grades = client.get_user_grades(course_id)
        
        if not grades or 'usergrades' not in grades or not grades['usergrades']:
            print("No grades available for analysis.")
            return
        
        user_grades = grades['usergrades'][0]
        
        if 'gradeitems' not in user_grades or not user_grades['gradeitems']:
            print("No grade items available for analysis.")
            return
        
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
        analysis = grade_analyzer.analyze_grades(course_id, grade_items)
        print("Grade analysis generated successfully.")
        
    except Exception as e:
        print(f"Error generating grade analysis: {e}")
        return

def course_menu(client, course_id, course_name, course_shortname):
    """
    Display and handle the course menu
    
    Args:
        client: MoodleAPIClient instance
        course_id: ID of the course
        course_name: Name of the course
        course_shortname: Short name of the course
    """
    while True:
        print(f"\n{course_name} - Menu")
        print("-" * 60)
        print("1. View Grades")
        print("2. View Lecture Notes")
        print("3. Download Lecture Notes")
        print("4. Download & Summarize Lecture Notes")
        print("5. View PDF Summaries")
        print("6. Analyze Grades with AI")
        print("7. Back to Course Selection")
        
        try:
            option = int(input("\nEnter your choice: "))
            
            if option == 1:
                # Get and display grades
                print(f"\nRetrieving grades for {course_name}...")
                grades = get_course_grades(client, course_id)
                display_grades(grades, course_name)
                input("\nPress Enter to continue...")
                
            elif option == 2:
                # Get and display lecture notes
                print(f"\nRetrieving lecture notes for {course_name}...")
                lecture_notes = get_lecture_notes(client, course_id)
                display_lecture_notes(lecture_notes)
                input("\nPress Enter to continue...")
                
            elif option == 3:
                # Get, display and download lecture notes
                print(f"\nRetrieving lecture notes for {course_name}...")
                lecture_notes = get_lecture_notes(client, course_id)
                
                if lecture_notes:
                    # Ask for confirmation before downloading
                    confirm = input(f"\nFound {len(lecture_notes)} lecture materials. Download them all? (y/n): ").lower()
                    
                    if confirm == 'y':
                        # Get token for downloading
                        token = client.token
                        display_lecture_notes(lecture_notes, course_shortname, download=True, token=token)
                    else:
                        print("Download canceled.")
                        display_lecture_notes(lecture_notes)
                
                input("\nPress Enter to continue...")
                
            elif option == 4:
                # Download and summarize lecture notes
                print(f"\nRetrieving lecture notes for {course_name}...")
                lecture_notes = get_lecture_notes(client, course_id)
                
                if lecture_notes:
                    # Check if OpenAI API key is set
                    if not config.OPENAI_API_KEY:
                        print("\nError: OpenAI API key is not set in config.py")
                        print("Please add your API key to config.py and try again")
                        input("\nPress Enter to continue...")
                        continue
                    
                    # Ask for confirmation before downloading and summarizing
                    confirm = input(f"\nFound {len(lecture_notes)} lecture materials. Download and summarize them? (y/n): ").lower()
                    
                    if confirm == 'y':
                        # Get token for downloading
                        token = client.token
                        display_lecture_notes(lecture_notes, course_shortname, download=True, token=token, summarize=True)
                    else:
                        print("Download and summarization canceled.")
                        display_lecture_notes(lecture_notes)
                
                input("\nPress Enter to continue...")
                
            elif option == 5:
                # View PDF summaries
                view_pdf_summaries(client, course_id, course_name)
                input("\nPress Enter to continue...")
                
            elif option == 6:
                # Analyze grades with AI
                view_grade_analyses(client, course_id, course_name)
                input("\nPress Enter to continue...")
                
            elif option == 7:
                # Return to course selection
                return
                
            else:
                print("Invalid option. Please try again.")
                
        except ValueError:
            print("Please enter a valid number.")

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
        course_id, course_name, course_shortname = select_course(client)
        
        if not course_id:
            break
            
        # Display course menu
        course_menu(client, course_id, course_name, course_shortname)
    
    print("\nThank you for using the Moodle Course Dashboard!")

if __name__ == "__main__":
    main()
