#!/usr/bin/env python3
"""
Track upcoming assignments and deadlines from Moodle
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from moodle_client import MoodleAPIClient

def get_upcoming_assignments(client, days_ahead=14):
    """
    Get all upcoming assignments due within the specified number of days
    
    Args:
        client: MoodleAPIClient instance
        days_ahead: Number of days to look ahead for deadlines
        
    Returns:
        List of upcoming assignments sorted by due date
    """
    # Get all courses
    courses = client.get_courses()
    
    # Dictionary to store course names by ID for later reference
    course_names = {course['id']: course['fullname'] for course in courses}
    
    # Get assignments for all courses
    all_assignments = client.get_assignments()
    
    # Current timestamp and cutoff timestamp
    now = datetime.now()
    cutoff = now + timedelta(days=days_ahead)
    
    # List to store upcoming assignments
    upcoming = []
    
    # Process all assignments
    if 'courses' in all_assignments:
        for course in all_assignments['courses']:
            course_id = course['id']
            course_name = course_names.get(course_id, f"Course {course_id}")
            
            for assignment in course.get('assignments', []):
                # Convert due date from timestamp to datetime
                if assignment.get('duedate', 0) > 0:
                    due_date = datetime.fromtimestamp(assignment['duedate'])
                    
                    # Check if it's due within the specified period and not past due
                    if now <= due_date <= cutoff:
                        upcoming.append({
                            'course_name': course_name,
                            'course_id': course_id,
                            'name': assignment['name'],
                            'due_date': due_date,
                            'description': assignment.get('intro', ''),
                            'id': assignment['id'],
                            'link': assignment.get('introattachments', [])
                        })
    
    # Sort by due date (earliest first)
    upcoming.sort(key=lambda x: x['due_date'])
    
    return upcoming

def get_upcoming_events(client, days_ahead=14):
    """
    Get all upcoming calendar events within the specified number of days
    
    Args:
        client: MoodleAPIClient instance
        days_ahead: Number of days to look ahead for events
        
    Returns:
        List of upcoming events sorted by date
    """
    # Calculate time range
    now = datetime.now()
    from_date = int(now.timestamp())
    to_date = int((now + timedelta(days=days_ahead)).timestamp())
    
    # Get calendar events
    events_data = client.get_calendar_events(events_from=from_date, events_to=to_date)
    
    # Process events
    upcoming_events = []
    
    if 'events' in events_data:
        for event in events_data['events']:
            event_time = datetime.fromtimestamp(event.get('timestart', 0))
            
            upcoming_events.append({
                'name': event.get('name', 'Unnamed event'),
                'description': event.get('description', ''),
                'course_name': event.get('course', {}).get('fullname', 'N/A'),
                'date': event_time,
                'type': event.get('eventtype', 'unknown'),
                'id': event.get('id')
            })
    
    # Sort by date
    upcoming_events.sort(key=lambda x: x['date'])
    
    return upcoming_events

def main():
    # Number of days to look ahead
    days_ahead = 14
    
    try:
        client = MoodleAPIClient()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set up your config.py file with your API token.")
        return
    
    print(f"Looking for deadlines in the next {days_ahead} days...\n")
    
    # Get upcoming assignments
    assignments = get_upcoming_assignments(client, days_ahead)
    
    # Display assignments
    if assignments:
        print(f"Found {len(assignments)} upcoming assignments:")
        print("-" * 60)
        
        for i, assignment in enumerate(assignments, 1):
            days_left = (assignment['due_date'] - datetime.now()).days
            hours_left = int((assignment['due_date'] - datetime.now()).total_seconds() / 3600)
            
            if days_left > 0:
                time_left = f"{days_left} days"
            else:
                time_left = f"{hours_left} hours"
                
            print(f"{i}. {assignment['name']}")
            print(f"   Course: {assignment['course_name']}")
            print(f"   Due: {assignment['due_date'].strftime('%Y-%m-%d %H:%M')} ({time_left} left)")
            print()
    else:
        print("No upcoming assignments found.")
    
    # Get upcoming events
    events = get_upcoming_events(client, days_ahead)
    
    # Filter out assignment events to avoid duplication
    events = [e for e in events if e['type'] != 'assign']
    
    # Display events
    if events:
        print(f"\nFound {len(events)} upcoming events:")
        print("-" * 60)
        
        for i, event in enumerate(events, 1):
            print(f"{i}. {event['name']}")
            print(f"   Course: {event['course_name']}")
            print(f"   Date: {event['date'].strftime('%Y-%m-%d %H:%M')}")
            print(f"   Type: {event['type']}")
            print()
    else:
        print("\nNo upcoming events found.")

if __name__ == "__main__":
    main()
