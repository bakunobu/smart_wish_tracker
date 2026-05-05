# event.py
"""
Event class for managing events with topics, durations, and contributions.
"""
from datetime import datetime, timedelta
from typing import Optional
import grid_manager

class Event:
    """
    A class to represent an event with a topic, duration, and contribution tracking.
    """
    
    def __init__(self, topic: str, duration: int = 15):
        """
        Initialize an Event instance.
        
        Args:
            topic (str): The topic of the event
            duration (int): Duration of the event in minutes (default is 15)
        """
        self.topic = topic
        self.duration = duration
        
    def add_contribution(self, amount: float = 1.0) -> None:
        """
        Add a contribution for this event to the grid.
        
        By default, adds one contribution (amount = 1.0) to today's entry.
        
        Args:
            amount (float): The amount to contribute (default is 1.0)
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        grid_manager.add_contribution(today_str, amount)
        
    def __str__(self) -> str:
        """String representation of the event."""
        return f"Event(topic='{self.topic}', duration={self.duration}min)"
        
    def __repr__(self) -> str:
        """String representation for debugging."""
        return self.__str__()