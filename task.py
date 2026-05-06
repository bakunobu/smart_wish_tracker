# task.py
"""
Task class for managing tasks with names, estimated time, and integration with Event class.
"""
from datetime import datetime
from typing import Optional

# Import the Event class from event.py
from event import Event
import grid_manager

class Task:
    """
    A class to represent a task with a name, estimated time, and contribution tracking.
    """
    
    def __init__(self, name: str, estimated_time: int, event_topic: Optional[str] = None):
        """
        Initialize a Task instance.
        
        Args:
            name (str): The name of the task
            estimated_time (int): Estimated time to complete the task in minutes
            event_topic (str, optional): Topic for the associated Event. If None, uses task name.
        """
        self.name = name
        self.estimated_time = estimated_time
        self.event_topic = event_topic or name
        self.event = Event(self.event_topic, self.estimated_time)
        
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
        
    def __str__(self) -> str:
        """String representation of the task."""
        return f"Task(name='{self.name}', estimated_time={self.estimated_time}min)"
        
    def __repr__(self) -> str:
        """String representation for debugging."""
        return self.__str__()