#!/usr/bin/env python3
"""
PDF Summarizer Module
Extracts text from PDFs and generates summaries using OpenAI's API
"""

import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import logging

# PDF text extraction
import PyPDF2

# OpenAI API for summarization
import openai
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pdf_summarizer')

# Default database path
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'summaries.db')

class PDFSummarizer:
    """Class for extracting text from PDFs and generating summaries using OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None, db_path: str = DEFAULT_DB_PATH):
        """
        Initialize the PDF summarizer
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment variable)
            db_path: Path to SQLite database for storing summaries
        """
        # Set up OpenAI API
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set it in config.py or pass it to the constructor.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Set up database
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database for storing summaries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create summaries table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                module_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                summary TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(course_id, module_id, file_name)
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def extract_text_from_pdf(self, pdf_path: str, max_pages: int = 50) -> str:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            max_pages: Maximum number of pages to extract (to avoid very large files)
            
        Returns:
            Extracted text from the PDF
        """
        try:
            logger.info(f"Extracting text from {pdf_path}")
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                
                # Limit the number of pages to process
                pages_to_process = min(num_pages, max_pages)
                if num_pages > max_pages:
                    logger.warning(f"PDF has {num_pages} pages, only processing first {max_pages}")
                
                # Extract text from each page
                text = ""
                for i in range(pages_to_process):
                    page = reader.pages[i]
                    text += page.extract_text() + "\n\n"
                
                logger.info(f"Successfully extracted {pages_to_process} pages from {pdf_path}")
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def generate_summary(self, text: str, max_tokens: int = 4000) -> str:
        """
        Generate a summary of the text using OpenAI API
        
        Args:
            text: Text to summarize
            max_tokens: Maximum number of tokens to use for the input text
            
        Returns:
            Generated summary
        """
        try:
            logger.info("Generating summary using OpenAI API")
            
            # Truncate text if it's too long (rough estimate: 1 token ≈ 4 chars)
            if len(text) > max_tokens * 4:
                logger.warning(f"Text is too long ({len(text)} chars), truncating to ~{max_tokens} tokens")
                text = text[:max_tokens * 4]
            
            # Generate summary using OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes academic lecture notes and materials. Create a concise but comprehensive summary that captures the key concepts, definitions, and important points from the provided text. Format your summary with clear sections and bullet points where appropriate."},
                    {"role": "user", "content": f"Please summarize the following lecture material:\n\n{text}"}
                ],
                max_tokens=1000,
                temperature=0.5
            )
            
            summary = response.choices[0].message.content
            logger.info("Summary generated successfully")
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise
    
    def summarize_pdf(self, pdf_path: str, course_id: int, module_id: int, filename: str = None) -> str:
        """
        Extract text from a PDF and generate a summary
        
        Args:
            pdf_path: Path to the PDF file
            course_id: ID of the course
            module_id: ID of the module
            filename: Optional name of the file (if not provided, will use basename of pdf_path)
            
        Returns:
            Generated summary
        """
        try:
            # Extract text from PDF
            text = self.extract_text_from_pdf(pdf_path)
            
            # Generate summary
            summary = self.generate_summary(text)
            
            # Store summary in database
            file_name = filename if filename else os.path.basename(pdf_path)
            self.store_summary(course_id, module_id, file_name, pdf_path, summary)
            
            return summary
        except Exception as e:
            logger.error(f"Error summarizing PDF: {e}")
            raise
    
    def store_summary(self, course_id: int, module_id: int, file_name: str, file_path: str, summary: str) -> None:
        """
        Store a summary in the database
        
        Args:
            course_id: ID of the course
            module_id: ID of the module
            file_name: Name of the file
            file_path: Path to the file
            summary: Generated summary
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert or replace summary
            cursor.execute('''
            INSERT OR REPLACE INTO summaries 
            (course_id, module_id, file_name, file_path, summary)
            VALUES (?, ?, ?, ?, ?)
            ''', (course_id, module_id, file_name, file_path, summary))
            
            conn.commit()
            conn.close()
            logger.info(f"Summary stored in database for {file_name}")
        except Exception as e:
            logger.error(f"Error storing summary in database: {e}")
            raise
    
    def get_summary(self, course_id: int, module_id: int, file_name: str) -> Optional[str]:
        """
        Get a summary from the database
        
        Args:
            course_id: ID of the course
            module_id: ID of the module
            file_name: Name of the file
            
        Returns:
            Summary if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get summary
            cursor.execute('''
            SELECT summary FROM summaries
            WHERE course_id = ? AND module_id = ? AND file_name = ?
            ''', (course_id, module_id, file_name))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting summary from database: {e}")
            return None
    
    def get_all_summaries(self, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all summaries from the database
        
        Args:
            course_id: Optional course ID to filter summaries
            
        Returns:
            List of summaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get summaries
            if course_id:
                cursor.execute('''
                SELECT * FROM summaries
                WHERE course_id = ?
                ORDER BY created_at DESC
                ''', (course_id,))
            else:
                cursor.execute('''
                SELECT * FROM summaries
                ORDER BY created_at DESC
                ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert rows to dictionaries
            summaries = []
            for row in rows:
                summaries.append(dict(row))
            
            return summaries
        except Exception as e:
            logger.error(f"Error getting summaries from database: {e}")
            return []
    
    def get_summary_by_id(self, summary_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a summary by its ID
        
        Args:
            summary_id: ID of the summary to retrieve
            
        Returns:
            Summary dictionary if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get summary
            cursor.execute('SELECT * FROM summaries WHERE id = ?', (summary_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting summary from database: {e}")
            return None
    
    def delete_summary(self, summary_id: int) -> bool:
        """
        Delete a summary from the database
        
        Args:
            summary_id: ID of the summary to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete summary
            cursor.execute('DELETE FROM summaries WHERE id = ?', (summary_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Summary {summary_id} deleted from database")
            return True
        except Exception as e:
            logger.error(f"Error deleting summary from database: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    try:
        import sys
        
        if len(sys.argv) < 2:
            print("Usage: python pdf_summarizer.py <pdf_path>")
            sys.exit(1)
        
        pdf_path = sys.argv[1]
        
        # Try to get API key from environment
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY environment variable not set")
            api_key = input("Enter your OpenAI API key: ")
        
        summarizer = PDFSummarizer(api_key=api_key)
        
        # Extract text and generate summary
        text = summarizer.extract_text_from_pdf(pdf_path)
        print(f"Extracted {len(text)} characters of text")
        
        summary = summarizer.generate_summary(text)
        print("\nSummary:")
        print("-" * 60)
        print(summary)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
