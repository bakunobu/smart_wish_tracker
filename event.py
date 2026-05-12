# event.py
"""
Event class for managing events with topics, durations, and contributions.
"""

from datetime import datetime
from typing import List, Optional
import grid_manager
from database import Database


class Event:
    """
    A class to represent an event with a topic, duration, and contribution tracking.
    """

    def __init__(self, topic: str, duration: int = 15, db: Optional[Database] = None, project_id: Optional[int] = None, event_id: Optional[int] = None):
        """
        Initialize an Event instance.

        Args:
            topic (str): The topic of the event
            duration (int): Duration of the event in minutes (default is 15)
            db (Database): Database instance for persistence
            project_id (int): ID of the parent project
            event_id (int): ID of the event in the database (if loading existing)
        """
        self.topic = topic
        self.duration = duration
        self.project_id = project_id
        self.event_id = event_id
        self.db = db or Database()
        
        # If this is a new event and has a project_id, save it to the database
        if event_id is None and project_id is not None:
            self.event_id = self.db.create_event(project_id, topic, duration)

    def add_contribution(self, amount: float = 1.0) -> None:
        """
        Add a contribution for this event to the grid.

        By default, adds one contribution (amount = 1.0) to today's entry.

        Args:
            amount (float): The amount to contribute (default is 1.0)
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        grid_manager.add_contribution(today_str, amount)

    def update(self, topic: Optional[str] = None, duration: Optional[int] = None) -> bool:
        """
        Update the event in the database.
        
        Args:
            topic (str): New topic for the event
            duration (int): New duration for the event
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if self.event_id is None:
            return False
            
        return self.db.update_event(self.event_id, topic, duration)
        
    def delete(self) -> bool:
        """
        Delete the event from the database.
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if self.event_id is None:
            return False
            
        success = self.db.delete_event(self.event_id)
        if success:
            self.event_id = None
        return success
        
    def __str__(self) -> str:
        """String representation of the event."""
        event_id_str = f"id={self.event_id}, " if self.event_id else ""
        project_str = f"project_id={self.project_id}, " if self.project_id else ""
        return f"Event({event_id_str}{project_str}topic='{self.topic}', duration={self.duration}min)"

    def __repr__(self) -> str:
        """String representation for debugging."""
        return self.__str__()
        
    @classmethod
    def from_db(cls, event_id: int, db: Optional[Database] = None) -> 'Event':
        """
        Create an Event instance from the database.
        
        Args:
            event_id (int): ID of the event to load
            db (Database): Database instance (optional)
            
        Returns:
            Event: Event instance populated with data from the database
        """
        db = db or Database()
        event_data = db.get_event(event_id)
        if not event_data:
            raise ValueError(f"Event with id {event_id} not found")
            
        return cls(
            topic=event_data['topic'],
            duration=event_data['duration'],
            db=db,
            project_id=event_data['project_id'],
            event_id=event_id
        )
        
    @classmethod
    def list_all(cls, db: Optional[Database] = None, project_id: Optional[int] = None) -> List['Event']:
        """
        List all events, optionally filtered by project.
        
        Args:
            db (Database): Database instance (optional)
            project_id (int): Filter events by project ID (optional)
            
        Returns:
            List of Event instances
        """
        db = db or Database()
        events_data = db.list_events(project_id)
        
        return [
            cls(
                topic=event['topic'],
                duration=event['duration'],
                db=db,
                project_id=event['project_id'],
                event_id=event['id']
            ) for event in events_data
        ]