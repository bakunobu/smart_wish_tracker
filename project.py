# project.py
"""
Project class for managing projects with name, description, associated events, and tasks.
"""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from database import Database
from event import Event

if TYPE_CHECKING:
    from problem import Problem
    from task import Task


class Project:
    """
    A class to represent a project with a name, description, and associated events and tasks.
    """
    
    def __init__(self, name: str, description: str = "",
                 db: Optional[Database] = None, project_id: Optional[int] = None):
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
        if self.project_id is None:
            raise ValueError("Cannot add event to project without ID")
        event = Event(topic, duration, db=self.db, project_id=self.project_id)
        return event
        
    def get_events(self) -> List[Event]:
        """
        Get all events associated with this project.
        
        Returns:
            List of Event instances
        """
        if self.project_id is None:
            return []
        events_data = self.db.list_events(project_id=self.project_id)
        return [
            Event(
                topic=event['topic'],
                duration=event['duration'],
                db=self.db,
                project_id=event['project_id'],
                event_id=event['id']
            ) for event in events_data
        ]
    
    def add_task(self, name: str, description: str = "", expected_duration: int = 15) -> 'Task':
        """
        Add a new task to the project.
        
        Args:
            name (str): Name of the task
            description (str): Description of the task
            expected_duration (int): Expected duration in minutes
            
        Returns:
            Task: The newly created task
        """
        from task import Task  # Import here to avoid circular imports
        if self.project_id is None:
            raise ValueError("Cannot add task to project without ID")
        task = Task(name, expected_duration, description=description,
                   db=self.db, project_id=self.project_id)
        return task
        
    def get_tasks(self) -> List['Task']:
        """
        Get all tasks associated with this project.
        
        Returns:
            List of Task instances
        """
        from task import Task  # Import here to avoid circular imports
        if not self.project_id:
            return []
        
        tasks_data = self.db.list_tasks(project_id=self.project_id)
        return [
            Task.from_db(task['id'], db=self.db) for task in tasks_data
        ]
    
    def associate_with_problem(self, problem_id: int) -> bool:
        """
        Associate this project with a problem.
        
        Args:
            problem_id (int): ID of the problem to associate with
            
        Returns:
            bool: True if association was successful, False otherwise
        """
        if not self.project_id:
            return False
        return self.db.add_problem_project(problem_id, self.project_id)
    
    def get_problems(self) -> List['Problem']:
        """
        Get all problems associated with this project.
        
        Returns:
            List of Problem instances
        """
        from problem import Problem  # Import here to avoid circular imports
        if not self.project_id:
            return []
        
        problems_data = self.db.get_problems_by_project(self.project_id)
        return [
            Problem(
                name=problem['name'],
                description=problem['description'],
                db=self.db,
                problem_id=problem['id']
            ) for problem in problems_data
        ]
        
    def update(self, name: Optional[str] = None, description: Optional[str] = None) -> bool:
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
    def from_db(cls, project_id: int, db: Optional[Database] = None) -> 'Project':
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
    def list_all(cls, db: Optional[Database] = None) -> List['Project']:
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