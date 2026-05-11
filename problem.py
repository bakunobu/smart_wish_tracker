# problem.py
"""
Problem class for managing top-level problems with associated projects.
"""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from database import Database

if TYPE_CHECKING:
    from project import Project


class Problem:
    """
    A class to represent a problem with a name, description, and associated projects.
    """
    
    def __init__(self, name: str, description: str = "",
                 db: Optional[Database] = None, problem_id: Optional[int] = None):
        """
        Initialize a Problem instance.
        
        Args:
            name (str): The name of the problem
            description (str): Description of the problem
            db (Database): Database instance for persistence
            problem_id (int): ID of the problem in the database (if loading existing)
        """
        self.name = name
        self.description = description
        self.problem_id = problem_id
        self.db = db or Database()
        
        # If this is a new problem, save it to the database
        if problem_id is None:
            self.problem_id = self.db.create_problem(name, description)
        
    def add_project(self, name: str, description: str = "") -> 'Project':
        """
        Add a new project to the problem.
        
        Args:
            name (str): Name of the project
            description (str): Description of the project
            
        Returns:
            Project: The newly created project
        """
        from project import Project  # Import here to avoid circular imports
        project = Project(name, description, db=self.db)
        if self.problem_id and project.project_id:
            self.db.add_problem_project(self.problem_id, project.project_id)
        return project
        
    def get_projects(self) -> List['Project']:
        """
        Get all projects associated with this problem.
        
        Returns:
            List of Project instances
        """
        from project import Project  # Import here to avoid circular imports
        if not self.problem_id:
            return []
        
        projects_data = self.db.get_projects_by_problem(self.problem_id)
        return [
            Project(
                name=project['name'],
                description=project['description'],
                db=self.db,
                project_id=project['id']
            ) for project in projects_data
        ]
        
    def update(self, name: Optional[str] = None, description: Optional[str] = None) -> bool:
        """
        Update the problem in the database.
        
        Args:
            name (str): New name for the problem
            description (str): New description for the problem
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if self.problem_id is None:
            return False
            
        return self.db.update_problem(self.problem_id, name, description)
        
    def delete(self) -> bool:
        """
        Delete the problem from the database.
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if self.problem_id is None:
            return False
            
        success = self.db.delete_problem(self.problem_id)
        if success:
            self.problem_id = None
        return success
        
    def __str__(self) -> str:
        """String representation of the problem."""
        problem_id_str = f"id={self.problem_id}, " if self.problem_id else ""
        return f"Problem({problem_id_str}name='{self.name}', description='{self.description}')"

    def __repr__(self) -> str:
        """String representation for debugging."""
        return self.__str__()
        
    @classmethod
    def from_db(cls, problem_id: int, db: Optional[Database] = None) -> 'Problem':
        """
        Create a Problem instance from the database.
        
        Args:
            problem_id (int): ID of the problem to load
            db (Database): Database instance (optional)
            
        Returns:
            Problem: Problem instance populated with data from the database
        """
        db = db or Database()
        problem_data = db.get_problem(problem_id)
        if not problem_data:
            raise ValueError(f"Problem with id {problem_id} not found")
            
        return cls(
            name=problem_data['name'],
            description=problem_data['description'],
            db=db,
            problem_id=problem_id
        )
        
    @classmethod
    def list_all(cls, db: Optional[Database] = None) -> List['Problem']:
        """
        List all problems.
        
        Args:
            db (Database): Database instance (optional)
            
        Returns:
            List of Problem instances
        """
        db = db or Database()
        problems_data = db.list_problems()
        
        return [
            cls(
                name=problem['name'],
                description=problem['description'],
                db=db,
                problem_id=problem['id']
            ) for problem in problems_data
        ]