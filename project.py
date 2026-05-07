# project.py
"""
Project class for managing projects with name, description, and associated events.
"""

from datetime import datetime
from typing import List, Optional
from database import Database
from event import Event


class Project:
    """
    A class to represent a project with a name, description, and associated events.
    """
    
    def __init__(self, name: str, description: str = "", 
                 db: Database = None, project_id: int = None):
        """
        Initialize a Project instance.
        
        Args:
            name (str): The name of the project
            description (str): Description of the project
            db (Database): Database instance for persistence
            project_id (int): ID of the project in the database (if loading existing)
        """
        self.name = name
        self.description = description
        self.project_id = project_id
        self.db = db or Database()
        
        # If this is a new project, save it to the database
        if project_id is None:
            self.project_id = self.db.create_project(name, description)
        
    def add_event(self, topic: str, duration: int = 15) -> Event:
        """
        Add a new event to the project.
        
        Args:
            topic (str): Topic of the event
            duration (int): Duration of the event in minutes
            
        Returns:
            Event: The newly created event
        """
        event = Event(topic, duration, db=self.db, project_id=self.project_id)
        return event
        
    def get_events(self) -> List[Event]:
        """
        Get all events associated with this project.
        
        Returns:
            List of Event instances
        """
        return Event.list_all(db=self.db, project_id=self.project_id)
        
    def update(self, name: str = None, description: str = None) -> bool:
        """
        Update the project in the database.
        
        Args:
            name (str): New name for the project
            description (str): New description for the project
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if self.project_id is None:
            return False
            
        return self.db.update_project(self.project_id, name, description)
        
    def delete(self) -> bool:
        """
        Delete the project from the database.
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if self.project_id is None:
            return False
            
        success = self.db.delete_project(self.project_id)
        if success:
            self.project_id = None
        return success
        
    def __str__(self) -> str:
        """String representation of the project."""
        project_id_str = f"id={self.project_id}, " if self.project_id else ""
        return f"Project({project_id_str}name='{self.name}', description='{self.description}')"

    def __repr__(self) -> str:
        """String representation for debugging."""
        return self.__str__()
        
    @classmethod
    def from_db(cls, project_id: int, db: Database = None) -> 'Project':
        """
        Create a Project instance from the database.
        
        Args:
            project_id (int): ID of the project to load
            db (Database): Database instance (optional)
            
        Returns:
            Project: Project instance populated with data from the database
        """
        db = db or Database()
        project_data = db.get_project(project_id)
        if not project_data:
            raise ValueError(f"Project with id {project_id} not found")
            
        return cls(
            name=project_data['name'],
            description=project_data['description'],
            db=db,
            project_id=project_id
        )
        
    @classmethod
    def list_all(cls, db: Database = None) -> List['Project']:
        """
        List all projects.
        
        Args:
            db (Database): Database instance (optional)
            
        Returns:
            List of Project instances
        """
        db = db or Database()
        projects_data = db.list_projects()
        
        return [
            cls(
                name=project['name'],
                description=project['description'],
                db=db,
                project_id=project['id']
            ) for project in projects_data
        ]