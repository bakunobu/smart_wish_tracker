# task.py
"""
Task class for managing tasks with names, estimated time, and integration with Event class.
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

# Import the Event class from event.py
from event import Event
from database import Database
import grid_manager

if TYPE_CHECKING:
    from project import Project

class Task:
    """
    A class to represent a task with a name, estimated time, and contribution tracking.
    """
    
    def __init__(self, name: str, estimated_time: int, description: str = "", 
                 event_topic: Optional[str] = None, db: Optional[Database] = None, 
                 project_id: Optional[int] = None, task_id: Optional[int] = None):
        """
        Initialize a Task instance.
        
        Args:
            name (str): The name of the task
            estimated_time (int): Estimated time to complete the task in minutes
            description (str): Description of the task
            event_topic (str, optional): Topic for the associated Event. If None, uses task name.
            db (Database): Database instance for persistence
            project_id (int): ID of the parent project
            task_id (int): ID of the task in the database (if loading existing)
        """
        self.name = name
        self.estimated_time = estimated_time
        self.description = description
        self.event_topic = event_topic or name
        self.project_id = project_id
        self.task_id = task_id
        self.db = db or Database()
        
        # If this is a new task, save it to the database
        if task_id is None and project_id is not None:
            self.task_id = self.db.create_task(name, description, project_id, estimated_time)
        
        # Create an associated event for this task if we have both IDs
        self.event = None
        if self.project_id is not None:
            self.event = Event(self.event_topic, estimated_time, db=self.db, project_id=self.project_id)
        
    def add_contribution(self, amount: float = 1.0, include_task_label: bool = True) -> None:
        """
        Add a contribution for this task to the grid.
        
        By default, adds one contribution (amount = 1.0) to today's entry
        with the task name as a label.
        
        Args:
            amount (float): The amount to contribute (default is 1.0)
            include_task_label (bool): Whether to include the task name in the contribution
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # If we need to track the task label, we could store it in a separate table
        # For now, we'll just add the contribution with the amount
        grid_manager.add_contribution(today_str, amount)
        
        # Also trigger the event's contribution mechanism
        if self.event:
            self.event.add_contribution(amount)
        
    def complete(self, effectiveness: float = 1.0) -> None:
        """
        Mark the task as completed and add a contribution to the grid.
        
        Args:
            effectiveness (float): How effectively the task was completed (0.0 to 1.0)
        """
        # Calculate contribution amount based on estimated time and effectiveness
        # For example, a 60-minute task with 100% effectiveness = 1.0 contribution
        # A 30-minute task with 100% effectiveness = 0.5 contribution
        base_amount = self.estimated_time / 60.0
        final_amount = base_amount * effectiveness
        
        self.add_contribution(final_amount)
        
        # Update task status in database
        if self.task_id:
            self.db.update_task(self.task_id, status='completed')
    
    def get_project(self) -> Optional['Project']:
        """
        Get the parent project of this task.
        
        Returns:
            Project instance if found, None otherwise
        """
        if not self.project_id:
            return None
        
        from project import Project  # Import here to avoid circular imports
        try:
            return Project.from_db(self.project_id, db=self.db)
        except ValueError:
            return None
    
    def update(self, name: Optional[str] = None, description: Optional[str] = None, 
               expected_duration: Optional[int] = None, status: Optional[str] = None) -> bool:
        """
        Update the task in the database.
        
        Args:
            name (str): New name for the task
            description (str): New description for the task
            expected_duration (int): New expected duration in minutes
            status (str): New status for the task
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if self.task_id is None:
            return False
            
        success = self.db.update_task(self.task_id, name, description, status, 
                                    self.project_id, expected_duration)
        
        # Update local attributes if successful
        if success:
            if name is not None:
                self.name = name
            if description is not None:
                self.description = description
            if expected_duration is not None:
                self.estimated_time = expected_duration
                
        return success
        
    def delete(self) -> bool:
        """
        Delete the task from the database.
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if self.task_id is None:
            return False
            
        success = self.db.delete_task(self.task_id)
        if success:
            self.task_id = None
            # Also delete associated event
            if self.event:
                self.event.delete()
        return success
        
    def __str__(self) -> str:
        """String representation of the task."""
        task_id_str = f"id={self.task_id}, " if self.task_id else ""
        project_str = f"project_id={self.project_id}, " if self.project_id else ""
        return f"Task({task_id_str}{project_str}name='{self.name}', estimated_time={self.estimated_time}min)"
        
    def __repr__(self) -> str:
        """String representation for debugging."""
        return self.__str__()
    
    @classmethod
    def from_db(cls, task_id: int, db: Optional[Database] = None) -> 'Task':
        """
        Create a Task instance from the database.
        
        Args:
            task_id (int): ID of the task to load
            db (Database): Database instance (optional)
            
        Returns:
            Task: Task instance populated with data from the database
        """
        db = db or Database()
        task_data = db.get_task(task_id)
        if not task_data:
            raise ValueError(f"Task with id {task_id} not found")
            
        return cls(
            name=task_data['name'],
            estimated_time=task_data.get('expected_duration', 15),
            description=task_data.get('description', ''),
            db=db,
            project_id=task_data.get('project_id'),
            task_id=task_id
        )
        
    @classmethod
    def list_all(cls, db: Optional[Database] = None, project_id: Optional[int] = None) -> List['Task']:
        """
        List all tasks, optionally filtered by project.
        
        Args:
            db (Database): Database instance (optional)
            project_id (int): Filter tasks by project ID (optional)
            
        Returns:
            List of Task instances
        """
        db = db or Database()
        tasks_data = db.list_tasks(project_id=project_id)
        
        return [
            cls(
                name=task['name'],
                estimated_time=task.get('expected_duration', 15),
                description=task.get('description', ''),
                db=db,
                project_id=task.get('project_id'),
                task_id=task['id']
            ) for task in tasks_data
        ]