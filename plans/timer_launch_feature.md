# Timer Launch Feature Specification

## Overview
Implements timer sessions ("launches") that connect tasks with time tracking. Each launch:
- Is associated with a task
- Tracks active/paused time
- Contributes to linked project/problem
- Allows time adjustment
- Only completed launches count toward totals

## Database Schema
```sql
CREATE TABLE launches (
    id INTEGER PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id),
    project_id INTEGER NOT NULL REFERENCES projects(id),
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    paused_duration INTEGER DEFAULT 0,  -- in seconds
    status TEXT CHECK(status IN ('running', 'paused', 'aborted', 'completed')),
    adjusted_time INTEGER  -- in minutes
);
```

## Launch Class (launch.py)
```python
class Launch:
    def __init__(self, task_id: int, db: Database):
        self.task_id = task_id
        self.db = db
        self.start_time = datetime.now()
        self.last_paused = None
        self.paused_duration = 0
        self.status = 'running'
        
    def pause(self):
        if self.status == 'running':
            self.last_paused = datetime.now()
            self.status = 'paused'
            
    def resume(self):
        if self.status == 'paused':
            self.paused_duration += (datetime.now() - self.last_paused).seconds
            self.status = 'running'
            
    def abort(self):
        self.status = 'aborted'
        self._save_to_db()
        
    def complete(self):
        self.end_time = datetime.now()
        self.status = 'completed'
        self._save_to_db()
        self._add_contribution()
        
    def adjust_time(self, minutes: int):
        if self.status == 'completed':
            self.adjusted_time = minutes
            self._save_to_db()
            self._add_contribution()
            
    def _add_contribution(self):
        # Calculate actual time spent
        base_time = (self.end_time - self.start_time).seconds // 60
        effective_time = self.adjusted_time or (base_time - self.paused_duration // 60)
        
        # Get associated task and add contribution
        task = Task.from_db(self.task_id)
        task.add_contribution(effective_time / 60)
        
    def _save_to_db(self):
        # Database persistence logic
        ...
```

## Task Integration
### In `task.py`:
```python
class Task:
    ...
    def launch_timer(self) -> Launch:
        """Start a new timer launch for this task"""
        return Launch(self.task_id, db=self.db)
        
    def get_active_launch(self) -> Optional[Launch]:
        """Get currently running launch for this task"""
        # Database query for active launch
        ...
```

## UI Components
1. **Launch Control Panel**:
   - Start/Pause/Resume/Stop buttons
   - Real-time duration display
   - Task selection dropdown

2. **Launch History Grid**:
   - Date, Task, Duration columns
   - Adjust time button for completed launches
   - Filter by project/problem

## Test Plan
1. Unit tests for all Launch state transitions
2. Integration test: Start → Pause → Resume → Complete workflow
3. UI test: Time adjustment persistence
4. Validation: Unfinished launches don't contribute to totals