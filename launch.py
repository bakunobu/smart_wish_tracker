"""
Launch class for managing timer sessions connected to tasks and projects.
"""
from datetime import datetime
from typing import Optional
from database import Database


class Launch:
    """
    Represents a timer session (launch) connected to a task.
    """
    
    def __init__(self, task_id: int, project_id: int, db: Database):
        """
        Initialize a new launch instance.
        
        Args:
            task_id: ID of the associated task
            project_id: ID of the associated project
            db: Database instance
        """
        self.task_id = task_id
        self.project_id = project_id
        self.db = db
        self.start_time = datetime.now()
        self.last_paused: Optional[datetime] = None
        self.paused_duration = 0
        self.status = 'running'
        self.end_time: Optional[datetime] = None
        self.adjusted_time: Optional[int] = None
        self.launch_id = self.db.create_launch(task_id, project_id, self.start_time)
        
    def pause(self):
        """Pause the running launch."""
        if self.status == 'running':
            self.last_paused = datetime.now()
            self.status = 'paused'
            self._save_to_db()
            
    def resume(self):
        """Resume a paused launch."""
        if self.status == 'paused' and self.last_paused:
            self.paused_duration += (datetime.now() - self.last_paused).seconds
            self.last_paused = None
            self.status = 'running'
            self._save_to_db()
            
    def abort(self):
        """Abort the launch without saving time."""
        self.status = 'aborted'
        self.end_time = datetime.now()
        self._save_to_db()
        
    def complete(self):
        """Complete the launch and save time to task."""
        self.end_time = datetime.now()
        self.status = 'completed'
        self._save_to_db()
        self._add_contribution()
        
    def adjust_time(self, minutes: int):
        """Adjust the recorded time for a completed launch."""
        if self.status == 'completed':
            self.adjusted_time = minutes
            self._save_to_db()
            self._add_contribution()
            
    def _add_contribution(self):
        """Calculate and add contribution to the task."""
        if not self.end_time:
            return
            
        # Calculate actual time spent
        base_minutes = (self.end_time - self.start_time).seconds // 60
        effective_minutes = self.adjusted_time or (base_minutes - self.paused_duration // 60)
        
        # Add contribution (1.0 = 60 minutes)
        from task import Task  # Avoid circular import
        task = Task.from_db(self.task_id, db=self.db)
        task.add_contribution(effective_minutes / 60.0)
        
    def _save_to_db(self):
        """Save current state to database."""
        if not self.launch_id:
            return
            
        self.db.update_launch(
            launch_id=self.launch_id,
            end_time=self.end_time,
            paused_duration=self.paused_duration,
            status=self.status,
            adjusted_time=self.adjusted_time
        )
        
    @classmethod
    def from_db(cls, launch_id: int, db: Database) -> 'Launch':
        """
        Create Launch instance from database record.
        
        Args:
            launch_id: ID of the launch to load
            db: Database instance
            
        Returns:
            Launch instance
        """
        data = db.get_launch(launch_id)
        if not data:
            raise ValueError(f"Launch with id {launch_id} not found")
            
        launch = cls(data['task_id'], data['project_id'], db)
        launch.launch_id = launch_id
        launch.start_time = datetime.fromisoformat(data['start_time'])
        launch.end_time = datetime.fromisoformat(data['end_time']) if data['end_time'] else None
        launch.paused_duration = data['paused_duration']
        launch.status = data['status']
        launch.adjusted_time = data['adjusted_time']
        return launch