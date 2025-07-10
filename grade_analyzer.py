#!/usr/bin/env python3
"""
Grade Analyzer Module

This module provides functionality to analyze grades using OpenAI's GPT model
and store the analysis in a SQLite database.
"""

import os
import sqlite3
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import openai
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GradeAnalyzer:
    """
    Class for analyzing grades using OpenAI's GPT model and storing the analysis
    in a SQLite database.
    """
    
    def __init__(self, api_key: str = None, db_path: str = None):
        """
        Initialize the GradeAnalyzer with OpenAI API key and database path
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment variable)
            db_path: Path to SQLite database (if None, will use default)
        """
        # Set up OpenAI client
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set it in config.py or pass it to the constructor.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Set up database
        self.db_path = db_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grade_analysis.db')
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table for grade analysis
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS grade_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                analysis TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(course_id, created_at)
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def generate_analysis(self, grades_data: List[Dict[str, Any]]) -> str:
        """
        Generate an analysis of grades using OpenAI's GPT model
        
        Args:
            grades_data: List of grade items with their details
            
        Returns:
            Generated analysis as a string
        """
        try:
            # Format grades data for the prompt
            formatted_grades = json.dumps(grades_data, indent=2)
            
            # Generate analysis using OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an academic advisor analyzing student grades. Provide a comprehensive analysis of the grade data including: performance trends, strengths and weaknesses, areas for improvement, and recommendations for study strategies. Include statistical insights where relevant (averages, comparisons to class means if available, etc). Format your analysis with clear sections and bullet points where appropriate."},
                    {"role": "user", "content": f"Please analyze the following grade data and provide insights:\n\n{formatted_grades}"}
                ],
                max_tokens=1000,
                temperature=0.5
            )
            
            analysis = response.choices[0].message.content
            logger.info("Grade analysis generated successfully")
            return analysis
        except Exception as e:
            logger.error(f"Error generating grade analysis: {e}")
            raise
    
    def store_analysis(self, course_id: int, analysis: str) -> int:
        """
        Store a grade analysis in the database
        
        Args:
            course_id: ID of the course
            analysis: Generated analysis text
            
        Returns:
            ID of the stored analysis
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store analysis
            cursor.execute(
                'INSERT INTO grade_analysis (course_id, analysis, created_at) VALUES (?, ?, ?)',
                (course_id, analysis, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            
            analysis_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Analysis stored with ID {analysis_id}")
            return analysis_id
        except Exception as e:
            logger.error(f"Error storing analysis in database: {e}")
            raise
    
    def analyze_grades(self, course_id: int, grades_data: List[Dict[str, Any]]) -> str:
        """
        Analyze grades and store the analysis
        
        Args:
            course_id: ID of the course
            grades_data: List of grade items with their details
            
        Returns:
            Generated analysis
        """
        try:
            # Generate analysis
            analysis = self.generate_analysis(grades_data)
            
            # Store analysis in database
            self.store_analysis(course_id, analysis)
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing grades: {e}")
            raise
    
    def get_analysis(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific analysis from the database
        
        Args:
            analysis_id: ID of the analysis to retrieve
            
        Returns:
            Analysis dictionary if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get analysis
            cursor.execute('SELECT * FROM grade_analysis WHERE id = ?', (analysis_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting analysis from database: {e}")
            return None
    
    def get_all_analyses(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Get all analyses for a course from the database
        
        Args:
            course_id: ID of the course
            
        Returns:
            List of analysis dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get analyses
            cursor.execute('SELECT * FROM grade_analysis WHERE course_id = ? ORDER BY created_at DESC', (course_id,))
            
            rows = cursor.fetchall()
            analyses = [dict(row) for row in rows]
            conn.close()
            
            return analyses
        except Exception as e:
            logger.error(f"Error getting analyses from database: {e}")
            return []
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """
        Delete an analysis from the database
        
        Args:
            analysis_id: ID of the analysis to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete analysis
            cursor.execute('DELETE FROM grade_analysis WHERE id = ?', (analysis_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Analysis {analysis_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting analysis from database: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    import config
    
    # Sample grade data
    sample_grades = [
        {
            "id": 1,
            "name": "Midterm Exam",
            "grade": 85,
            "max_grade": 100,
            "percentage": 85.0,
            "feedback": "Good work on the theoretical questions."
        },
        {
            "id": 2,
            "name": "Assignment 1",
            "grade": 18,
            "max_grade": 20,
            "percentage": 90.0,
            "feedback": "Excellent problem-solving approach."
        },
        {
            "id": 3,
            "name": "Quiz 1",
            "grade": 8,
            "max_grade": 10,
            "percentage": 80.0,
            "feedback": "Review concepts from chapter 3."
        }
    ]
    
    try:
        # Initialize analyzer with API key from config
        analyzer = GradeAnalyzer(api_key=config.OPENAI_API_KEY)
        
        # Generate and store analysis
        analysis = analyzer.analyze_grades(course_id=12345, grades_data=sample_grades)
        
        print("Generated Analysis:")
        print(analysis)
        
        # Get all analyses for the course
        all_analyses = analyzer.get_all_analyses(course_id=12345)
        print(f"\nFound {len(all_analyses)} analyses for course 12345")
        
    except Exception as e:
        print(f"Error: {e}")
