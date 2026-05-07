# database.py
"""
Database module for storing projects and events in SQLite.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

# Database setup
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DATA_DIR, "projects.db")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


class Database:
    """
    Database class to handle SQLite operations for projects and events.
    """
    
    def __init__(self, db_path: str = DB_PATH):
        """
        Initialize the Database instance.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize the database with required tables."""
        with self.get_connection() as conn:
            # Create projects table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_date TEXT NOT NULL,
                    updated_date TEXT NOT NULL,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Create events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    topic TEXT NOT NULL,
                    duration INTEGER DEFAULT 15,
                    created_date TEXT NOT NULL,
                    updated_date TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            """)
            
            # Create index on project_id for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_project_id ON events (project_id)")
    
    def create_project(self, name: str, description: str = "") -> int:
        """
        Create a new project.
        
        Args:
            name (str): Name of the project
            description (str): Description of the project
            
        Returns:
            int: ID of the created project
        """
        current_time = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO projects (name, description, created_date, updated_date) VALUES (?, ?, ?, ?)",
                (name, description, current_time, current_time)
            )
            return cursor.lastrowid
    
    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a project by ID.
        
        Args:
            project_id (int): ID of the project
            
        Returns:
            Dict or None: Project data if found, None otherwise
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def update_project(self, project_id: int, name: Optional[str] = None, 
                      description: Optional[str] = None, status: Optional[str] = None) -> bool:
        """
        Update a project.
        
        Args:
            project_id (int): ID of the project to update
            name (str, optional): New name for the project
            description (str, optional): New description for the project
            status (str, optional): New status for the project
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        
        # Always update the updated_date
        updates.append("updated_date = ?")
        params.append(datetime.now().isoformat())
        
        if not updates:
            return False
        
        params.append(project_id)
        query = f"UPDATE projects SET {', '.join(updates)} WHERE id = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount > 0
    
    def delete_project(self, project_id: int) -> bool:
        """
        Delete a project and its associated events.
        
        Args:
            project_id (int): ID of the project to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Delete associated events first (due to foreign key constraint)
            cursor.execute("DELETE FROM events WHERE project_id = ?", (project_id,))
            # Then delete the project
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            return cursor.rowcount > 0
    
    def list_projects(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all projects, optionally filtered by status.
        
        Args:
            status (str, optional): Filter projects by status
            
        Returns:
            List of project dictionaries
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if status:
                cursor.execute("SELECT * FROM projects WHERE status = ? ORDER BY updated_date DESC", (status,))
            else:
                cursor.execute("SELECT * FROM projects ORDER BY updated_date DESC")
            
            return [dict(row) for row in cursor.fetchall()]
    
    def create_event(self, project_id: int, topic: str, duration: int = 15) -> int:
        """
        Create a new event for a project.
        
        Args:
            project_id (int): ID of the parent project
            topic (str): Topic of the event
            duration (int): Duration of the event in minutes
            
        Returns:
            int: ID of the created event
        """
        current_time = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO events (project_id, topic, duration, created_date, updated_date) VALUES (?, ?, ?, ?, ?)",
                (project_id, topic, duration, current_time, current_time)
            )
            return cursor.lastrowid
    
    def get_event(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an event by ID.
        
        Args:
            event_id (int): ID of the event
            
        Returns:
            Dict or None: Event data if found, None otherwise
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.*, p.name as project_name 
                FROM events e 
                LEFT JOIN projects p ON e.project_id = p.id 
                WHERE e.id = ?
            """, (event_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def update_event(self, event_id: int, topic: Optional[str] = None, 
                    duration: Optional[int] = None) -> bool:
        """
        Update an event.
        
        Args:
            event_id (int): ID of the event to update
            topic (str, optional): New topic for the event
            duration (int, optional): New duration for the event
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        updates = []
        params = []
        
        if topic is not None:
            updates.append("topic = ?")
            params.append(topic)
        
        if duration is not None:
            updates.append("duration = ?")
            params.append(duration)
        
        # Always update the updated_date
        updates.append("updated_date = ?")
        params.append(datetime.now().isoformat())
        
        if not updates:
            return False
        
        params.append(event_id)
        query = f"UPDATE events SET {', '.join(updates)} WHERE id = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount > 0
    
    def delete_event(self, event_id: int) -> bool:
        """
        Delete an event.
        
        Args:
            event_id (int): ID of the event to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
            return cursor.rowcount > 0
    
    def list_events(self, project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all events, optionally filtered by project.
        
        Args:
            project_id (int, optional): Filter events by project ID
            
        Returns:
            List of event dictionaries
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if project_id:
                cursor.execute("""
                    SELECT e.*, p.name as project_name 
                    FROM events e 
                    LEFT JOIN projects p ON e.project_id = p.id 
                    WHERE e.project_id = ? 
                    ORDER BY e.updated_date DESC
                """, (project_id,))
            else:
                cursor.execute("""
                    SELECT e.*, p.name as project_name 
                    FROM events e 
                    LEFT JOIN projects p ON e.project_id = p.id 
                    ORDER BY e.updated_date DESC
                """)
            
            return [dict(row) for row in cursor.fetchall()]