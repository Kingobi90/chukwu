"""Async Moodle API Service"""

from typing import Dict, Any, List
import httpx

from app.core.config import settings


class MoodleService:
    """Async Moodle API client using httpx"""
    
    def __init__(self, token: str = None):
        self.base_url = settings.MOODLE_URL
        self.token = token or settings.MOODLE_API_TOKEN
        self.ws_endpoint = f"{self.base_url}/webservice/rest/server.php"
        
        self.default_params = {
            "wstoken": self.token,
            "moodlewsrestformat": "json"
        }
    
    async def _make_request(self, wsfunction: str, additional_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make async request to Moodle API"""
        params = {
            "wsfunction": wsfunction,
            **self.default_params
        }
        
        if additional_params:
            params.update(additional_params)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.ws_endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict) and data.get('exception'):
                raise Exception(f"Moodle API error: {data.get('message', 'Unknown error')}")
            
            return data
    
    async def get_site_info(self) -> Dict[str, Any]:
        """Get Moodle site information"""
        return await self._make_request("core_webservice_get_site_info")
    
    async def get_courses(self) -> List[Dict[str, Any]]:
        """Get user's enrolled courses"""
        site_info = await self.get_site_info()
        user_id = site_info.get("userid")
        
        return await self._make_request("core_enrol_get_users_courses", {
            "userid": user_id
        })
    
    async def get_course_contents(self, course_id: int) -> List[Dict[str, Any]]:
        """Get course contents"""
        return await self._make_request("core_course_get_contents", {
            "courseid": course_id
        })
    
    async def get_assignments(self, course_id: int = None) -> Dict[str, Any]:
        """Get assignments"""
        params = {}
        if course_id:
            params["courseids"] = [course_id]
        
        return await self._make_request("mod_assign_get_assignments", params)
    
    async def get_calendar_events(self) -> Dict[str, Any]:
        """Get calendar events"""
        return await self._make_request("core_calendar_get_calendar_events")
