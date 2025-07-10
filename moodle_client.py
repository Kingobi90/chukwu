#!/usr/bin/env python3
"""
Moodle API Client for Concordia University
This module provides a client for interacting with Concordia University's Moodle web services API.
"""

import requests
from typing import Dict, Any, List, Optional
import json
import os
from urllib.parse import urljoin

try:
    import config
except ImportError:
    print("Warning: config.py not found. Please create it based on config_example.py")
    # Provide fallback defaults
    class config:
        MOODLE_URL = "https://moodle.concordia.ca"
        API_TOKEN = None
        DEFAULT_PARAMS = {"moodlewsrestformat": "json"}


class MoodleAPIClient:
    """Client for interacting with Moodle's Web Services API."""
    
    def __init__(self, base_url: str = None, token: str = None):
        """
        Initialize the Moodle API client.
        
        Args:
            base_url: The base URL of the Moodle instance (default: from config)
            token: Your Moodle API token (default: from config)
        """
        self.base_url = base_url or config.MOODLE_URL
        self.token = token or config.API_TOKEN
        
        if not self.token:
            raise ValueError("API token is required. Set it in config.py or pass it to the constructor.")
        
        # Ensure the base URL ends with a slash
        if not self.base_url.endswith('/'):
            self.base_url += '/'
            
        # Web service endpoint
        self.ws_endpoint = urljoin(self.base_url, "webservice/rest/server.php")
        
        # Default parameters for all requests
        self.default_params = {
            "wstoken": self.token,
            **config.DEFAULT_PARAMS
        }
    
    def _make_request(self, wsfunction: str, additional_params: Dict[str, Any] = None, handle_errors: bool = True) -> Dict[str, Any]:
        """
        Make a request to the Moodle API.
        
        Args:
            wsfunction: The Moodle web service function to call
            additional_params: Additional parameters to include in the request
            handle_errors: Whether to raise exceptions for API errors
            
        Returns:
            The JSON response from the API
        """
        params = {
            "wsfunction": wsfunction,
            **self.default_params
        }
        
        if additional_params:
            params.update(additional_params)
        
        try:
            response = requests.get(self.ws_endpoint, params=params)
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Check for Moodle API errors
            if isinstance(data, dict) and data.get('exception'):
                error_msg = f"Moodle API error: {data.get('message', 'Unknown error')}"
                if handle_errors:
                    raise Exception(error_msg)
                else:
                    print(f"Warning: {error_msg}")
                    return {"error": error_msg}
                
            return data
        except requests.exceptions.RequestException as e:
            if handle_errors:
                raise
            else:
                print(f"Warning: Request failed: {e}")
                return {"error": str(e)}
    
    def is_function_available(self, wsfunction: str) -> bool:
        """
        Check if a specific Moodle API function is available.
        
        Args:
            wsfunction: The Moodle web service function to check
            
        Returns:
            True if the function is available, False otherwise
        """
        try:
            # Try to call the function with minimal parameters
            result = self._make_request(wsfunction, handle_errors=False)
            # If we get an 'invalid parameter' error, the function exists but needs parameters
            # If we get a 'access control exception', the function exists but we don't have permission
            # If we get a 'function does not exist', the function is not available
            
            if isinstance(result, dict) and result.get('error'):
                error = result.get('error')
                if "does not exist" in error:
                    return False
                # Other errors might indicate the function exists but needs parameters or permissions
                return True
            return True
        except Exception:
            return False
    
    def get_site_info(self) -> Dict[str, Any]:
        """
        Get information about the Moodle site.
        
        Returns:
            Site information including version, user details, etc.
        """
        return self._make_request("core_webservice_get_site_info")
    
    def get_courses(self) -> List[Dict[str, Any]]:
        """
        Get the list of courses the user is enrolled in.
        
        Returns:
            List of course information
        """
        return self._make_request("core_enrol_get_users_courses", {
            "userid": self.get_site_info().get("userid")
        })
    
    def get_course_contents(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Get the contents of a specific course.
        
        Args:
            course_id: The ID of the course
            
        Returns:
            List of course sections with their contents
        """
        return self._make_request("core_course_get_contents", {
            "courseid": course_id
        })
    
    def get_calendar_events(self, 
                           events_from: Optional[str] = None, 
                           events_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Get calendar events within a specified time range.
        
        Args:
            events_from: Start date (ISO format YYYY-MM-DD)
            events_to: End date (ISO format YYYY-MM-DD)
            
        Returns:
            Dictionary containing events and warnings
        """
        params = {}
        if events_from:
            params["timestart"] = events_from
        if events_to:
            params["timeend"] = events_to
            
        return self._make_request("core_calendar_get_calendar_events", params)
    
    def get_assignments(self, course_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get assignments for all courses or a specific course.
        
        Args:
            course_id: Optional course ID to filter assignments
            
        Returns:
            Dictionary containing courses and their assignments or an empty dict if not available
        """
        # Check if this function is available in the Moodle instance
        if not self.is_function_available("mod_assign_get_assignments"):
            print("Warning: The assignments API function is not available on this Moodle instance")
            return {"courses": [], "warnings": [{"message": "API function not available"}]}
            
        params = {}
        if course_id:
            params["courseids"] = [course_id]
        
        try:    
            return self._make_request("mod_assign_get_assignments", params)
        except Exception as e:
            print(f"Error getting assignments: {e}")
            return {"courses": [], "warnings": [{"message": str(e)}]}
    
    def get_user_grades(self, course_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get grades for the current user.
        
        Args:
            course_id: Optional course ID to filter grades
            
        Returns:
            Dictionary containing grade items or an empty dict if not available
        """
        # Check if this function is available in the Moodle instance
        if not self.is_function_available("gradereport_user_get_grade_items"):
            print("Warning: The grades API function is not available on this Moodle instance")
            return {"usergrades": [], "warnings": [{"message": "API function not available"}]}
        
        try:
            user_id = self.get_site_info().get("userid")
            params = {"userid": user_id}
            
            if course_id:
                params["courseid"] = course_id
                
            return self._make_request("gradereport_user_get_grade_items", params)
        except Exception as e:
            print(f"Error getting grades: {e}")
            return {"usergrades": [], "warnings": [{"message": str(e)}]}


if __name__ == "__main__":
    # Example usage
    try:
        client = MoodleAPIClient()
        site_info = client.get_site_info()
        print(f"Connected to {site_info.get('sitename', 'Moodle')} as {site_info.get('fullname', 'User')}")
        print(f"Moodle version: {site_info.get('release', 'Unknown')}")
    except Exception as e:
        print(f"Error: {e}")
        print("Please make sure your config.py file is set up correctly with your API token.")
