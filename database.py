# database.py
"""
Database module with custom ORM-like implementation.
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


class ORM:
    """
    Base class for ORM-like functionality.
    """
    TABLE_NAME = None
    COLUMNS = []
    
    @classmethod
    def create_table(cls, conn):
        """Create table for model if not exists."""
        columns = ",\n    ".join(cls.COLUMNS)
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                {columns}
            )
        """)
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary."""
        instance = cls()
        for key, value in data.items():
            setattr(instance, key, value)
        return instance
    
    def to_dict(self):
        """Convert instance to dictionary."""
        return {col: getattr(self, col) for col in self.COLUMNS if hasattr(self, col)}


class Problem(ORM):
    TABLE_NAME = 'problems'
    COLUMNS = [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'name TEXT NOT NULL',
        'description TEXT',
        'created_date TEXT NOT NULL',
        'updated_date TEXT NOT NULL',
        "status TEXT DEFAULT 'active'"
    ]


class Project(ORM):
    TABLE_NAME = 'projects'
    COLUMNS = [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'name TEXT NOT NULL',
        'description TEXT',
        'problem_id INTEGER',
        'created_date TEXT NOT NULL',
        'updated_date TEXT NOT NULL',
        "status TEXT DEFAULT 'active'",
        'FOREIGN KEY (problem_id) REFERENCES problems (id)'
    ]


class Task(ORM):
    TABLE_NAME = 'tasks'
    COLUMNS = [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'name TEXT NOT NULL',
        'description TEXT',
        'project_id INTEGER',
        'expected_duration INTEGER',
        "status TEXT DEFAULT 'active'",
        'created_date TEXT NOT NULL',
        'updated_date TEXT NOT NULL',
        'FOREIGN KEY (project_id) REFERENCES projects (id)'
    ]


class Event(ORM):
    TABLE_NAME = 'events'
    COLUMNS = [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'project_id INTEGER',
        'topic TEXT NOT NULL',
        'duration INTEGER DEFAULT 15',
        'created_date TEXT NOT NULL',
        'updated_date TEXT NOT NULL',
        'FOREIGN KEY (project_id) REFERENCES projects (id)'
    ]


class Launch(ORM):
    TABLE_NAME = 'launches'
    COLUMNS = [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'task_id INTEGER NOT NULL',
        'project_id INTEGER NOT NULL',
        'start_time DATETIME NOT NULL',
        'end_time DATETIME',
        'paused_duration INTEGER DEFAULT 0',
        "status TEXT CHECK(status IN ('running', 'paused', 'aborted', 'completed'))",
        'adjusted_time INTEGER',
        'created_date TEXT NOT NULL',
        'updated_date TEXT NOT NULL',
        'FOREIGN KEY (task_id) REFERENCES tasks (id)',
        'FOREIGN KEY (project_id) REFERENCES projects (id)'
    ]


class ProblemProject(ORM):
    TABLE_NAME = 'problem_projects'
    COLUMNS = [
        'problem_id INTEGER',
        'project_id INTEGER',
        'PRIMARY KEY (problem_id, project_id)',
        'FOREIGN KEY (problem_id) REFERENCES problems (id) ON DELETE CASCADE',
        'FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE'
    ]


class Database:
    """
    Database class with ORM-like CRUD operations.
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize the database with required tables."""
        models = [Problem, Project, Task, Event, Launch, ProblemProject]
        with self.get_connection() as conn:
            for model in models:
                model.create_table(conn)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_project_id ON events (project_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_problem_id ON projects (problem_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks (project_id)")
    
    def _create(self, model, data):
        """Generic create method for ORM models."""
        current_time = datetime.now().isoformat()
        data['created_date'] = current_time
        data['updated_date'] = current_time
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            query = f"INSERT INTO {model.TABLE_NAME} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(data.values()))
            return cursor.lastrowid
    
    def _get(self, model, item_id):
        """Generic get method for ORM models."""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {model.TABLE_NAME} WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # Implement similar generic methods for update, delete, list
    # ...
    
    # Problem CRUD
    def create_problem(self, name: str, description: str = "") -> int:
        return self._create(Problem, {"name": name, "description": description})
    
    def get_problem(self, problem_id: int) -> Optional[Dict[str, Any]]:
        return self._get(Problem, problem_id)
    
    # Implement other CRUD methods using the generic pattern
    # ...
    
    def create_problem(self, name: str, description: str = "") -> int:
        """
        Create a new problem.
        
        Args:
            name (str): Name of the problem
            description (str): Description of the problem
            
        Returns:
            int: ID of the created problem
        """
        current_time = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO problems (name, description, created_date, updated_date) VALUES (?, ?, ?, ?)",
                (name, description, current_time, current_time)
            )
            return cursor.lastrowid
            
    def create_project(self, name: str, description: str = "", problem_id: int = None) -> int:
        """
        Create a new project.
        
        Args:
            name (str): Name of the project
            description (str): Description of the project
            problem_id (int): ID of the parent problem
            
        Returns:
            int: ID of the created project
        """
        current_time = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO projects (name, description, problem_id, created_date, updated_date) VALUES (?, ?, ?, ?, ?)",
                (name, description, problem_id, current_time, current_time)
            )
            return cursor.lastrowid
            
    def create_task(self, name: str, description: str = "", project_id: int = None, expected_duration: int = None) -> int:
        """
        Create a new task.
        
        Args:
            name (str): Name of the task
            description (str): Description of the task
            project_id (int): ID of the parent project
            expected_duration (int): Expected duration in minutes
            
        Returns:
            int: ID of the created task
        """
        current_time = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (name, description, project_id, expected_duration, created_date, updated_date) VALUES (?, ?, ?, ?, ?, ?)",
                (name, description, project_id, expected_duration, current_time, current_time)
            )
            return cursor.lastrowid
    
    def get_problem(self, problem_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a problem by ID.
        
        Args:
            problem_id (int): ID of the problem
            
        Returns:
            Dict or None: Problem data if found, None otherwise
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
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
            cursor.execute("""
                SELECT p.*, pr.name as problem_name, pr.id as problem_id 
                FROM projects p 
                LEFT JOIN problems pr ON p.problem_id = pr.id 
                WHERE p.id = ?
            """, (project_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a task by ID.
        
        Args:
            task_id (int): ID of the task
            
        Returns:
            Dict or None: Task data if found, None otherwise
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, p.name as project_name, p.id as project_id 
                FROM tasks t 
                LEFT JOIN projects p ON t.project_id = p.id 
                WHERE t.id = ?
            """, (task_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def update_problem(self, problem_id: int, name: Optional[str] = None, 
                      description: Optional[str] = None, status: Optional[str] = None) -> bool:
        """
        Update a problem.
        
        Args:
            problem_id (int): ID of the problem to update
            name (str, optional): New name for the problem
            description (str, optional): New description for the problem
            status (str, optional): New status for the problem
            
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
        
        params.append(problem_id)
        query = f"UPDATE problems SET {', '.join(updates)} WHERE id = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount > 0
            
    def update_project(self, project_id: int, name: Optional[str] = None, 
                      description: Optional[str] = None, status: Optional[str] = None, problem_id: Optional[int] = None) -> bool:
        """
        Update a project.
        
        Args:
            project_id (int): ID of the project to update
            name (str, optional): New name for the project
            description (str, optional): New description for the project
            status (str, optional): New status for the project
            problem_id (int, optional): ID of the parent problem
            
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
        
        if problem_id is not None:
            updates.append("problem_id = ?")
            params.append(problem_id)
        
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
            
    def update_task(self, task_id: int, name: Optional[str] = None, 
                   description: Optional[str] = None, status: Optional[str] = None, 
                   project_id: Optional[int] = None, expected_duration: Optional[int] = None) -> bool:
        """
        Update a task.
        
        Args:
            task_id (int): ID of the task to update
            name (str, optional): New name for the task
            description (str, optional): New description for the task
            status (str, optional): New status for the task
            project_id (int, optional): ID of the parent project
            expected_duration (int, optional): New expected duration in minutes
            
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
        
        if project_id is not None:
            updates.append("project_id = ?")
            params.append(project_id)
        
        if expected_duration is not None:
            updates.append("expected_duration = ?")
            params.append(expected_duration)
        
        # Always update the updated_date
        updates.append("updated_date = ?")
        params.append(datetime.now().isoformat())
        
        if not updates:
            return False
        
        params.append(task_id)
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount > 0
    
    def delete_problem(self, problem_id: int) -> bool:
        """
        Delete a problem and its associated projects and tasks.
        
        Args:
            problem_id (int): ID of the problem to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Delete associated tasks first
            cursor.execute("DELETE FROM tasks WHERE project_id IN (SELECT id FROM projects WHERE problem_id = ?)", (problem_id,))
            # Then delete associated projects
            cursor.execute("DELETE FROM projects WHERE problem_id = ?", (problem_id,))
            # Then delete the problem
            cursor.execute("DELETE FROM problems WHERE id = ?", (problem_id,))
            return cursor.rowcount > 0
            
    def delete_project(self, project_id: int) -> bool:
        """
        Delete a project and its associated tasks and events.
        
        Args:
            project_id (int): ID of the project to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Delete associated tasks first
            cursor.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
            # Delete associated events first (due to foreign key constraint)
            cursor.execute("DELETE FROM events WHERE project_id = ?", (project_id,))
            # Then delete the project
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            return cursor.rowcount > 0
            
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task.
        
        Args:
            task_id (int): ID of the task to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0
    
    def list_problems(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all problems, optionally filtered by status.
        
        Args:
            status (str, optional): Filter problems by status
            
        Returns:
            List of problem dictionaries
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if status:
                cursor.execute("SELECT * FROM problems WHERE status = ? ORDER BY updated_date DESC", (status,))
            else:
                cursor.execute("SELECT * FROM problems ORDER BY updated_date DESC")
            
            return [dict(row) for row in cursor.fetchall()]
            
    def list_projects(self, status: Optional[str] = None, problem_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all projects, optionally filtered by status and problem.
        
        Args:
            status (str, optional): Filter projects by status
            problem_id (int, optional): Filter projects by parent problem
            
        Returns:
            List of project dictionaries
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT p.*, pr.name as problem_name, pr.id as problem_id FROM projects p LEFT JOIN problems pr ON p.problem_id = pr.id"
            conditions = []
            params = []
            
            if status:
                conditions.append("p.status = ?")
                params.append(status)
            
            if problem_id:
                conditions.append("p.problem_id = ?")
                params.append(problem_id)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY p.updated_date DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
    def list_tasks(self, status: Optional[str] = None, project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all tasks, optionally filtered by status and project.
        
        Args:
            status (str, optional): Filter tasks by status
            project_id (int, optional): Filter tasks by parent project
            
        Returns:
            List of task dictionaries
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT t.*, p.name as project_name, p.id as project_id FROM tasks t LEFT JOIN projects p ON t.project_id = p.id"
            conditions = []
            params = []
            
            if status:
                conditions.append("t.status = ?")
                params.append(status)
            
            if project_id:
                conditions.append("t.project_id = ?")
                params.append(project_id)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY t.updated_date DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
    # Launch CRUD operations
    def create_launch(self, task_id: int, project_id: int, start_time: datetime) -> int:
        """
        Create a new launch.
        
        Args:
            task_id (int): ID of the associated task
            project_id (int): ID of the associated project
            start_time (datetime): Start time of the launch
            
        Returns:
            int: ID of the created launch
        """
        current_time = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO launches (task_id, project_id, start_time, status, created_date, updated_date)
                VALUES (?, ?, ?, 'running', ?, ?)
                """,
                (task_id, project_id, start_time.isoformat(), current_time, current_time)
            )
            return cursor.lastrowid
            
    def update_launch(self, launch_id: int, end_time: Optional[datetime] = None,
                     paused_duration: Optional[int] = None, status: Optional[str] = None,
                     duration: Optional[int] = None, adjusted_time: Optional[int] = None) -> bool:
        """
        Update a launch.
        
        Args:
            launch_id (int): ID of the launch to update
            end_time (datetime, optional): End time of the launch
            paused_duration (int, optional): Total paused duration in seconds
            status (str, optional): New status of the launch
            adjusted_time (int, optional): Manually adjusted time in minutes
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        updates = []
        params = []
        
        if end_time is not None:
            updates.append("end_time = ?")
            params.append(end_time.isoformat())
        
        if paused_duration is not None:
            updates.append("paused_duration = ?")
            params.append(paused_duration)
            
        if status is not None:
            updates.append("status = ?")
            params.append(status)
            
        if duration is not None:
            updates.append("duration = ?")
            params.append(duration)
            
        if adjusted_time is not None:
            updates.append("adjusted_time = ?")
            params.append(adjusted_time)
            
        # Always update the updated_date
        updates.append("updated_date = ?")
        params.append(datetime.now().isoformat())
        
        if not updates:
            return False
            
        params.append(launch_id)
        query = f"UPDATE launches SET {', '.join(updates)} WHERE id = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount > 0
            
    def get_launch(self, launch_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a launch by ID.
        
        Args:
            launch_id (int): ID of the launch
            
        Returns:
            Dict or None: Launch data if found, None otherwise
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.*, t.name as task_name, p.name as project_name
                FROM launches l
                JOIN tasks t ON l.task_id = t.id
                JOIN projects p ON l.project_id = p.id
                WHERE l.id = ?
            """, (launch_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
    def list_launches(self, task_id: Optional[int] = None, project_id: Optional[int] = None,
                     status: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List launches with optional filters.
        
        Args:
            task_id (int, optional): Filter by task ID
            project_id (int, optional): Filter by project ID
            status (str, optional): Filter by status
            
        Returns:
            List of launch dictionaries
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT l.*, t.name as task_name, p.name as project_name
                FROM launches l
                JOIN tasks t ON l.task_id = t.id
                JOIN projects p ON l.project_id = p.id
            """
            conditions = []
            params = []
            
            if task_id is not None:
                conditions.append("l.task_id = ?")
                params.append(task_id)
                
            if project_id is not None:
                conditions.append("l.project_id = ?")
                params.append(project_id)
                
            if status is not None:
                conditions.append("l.status = ?")
                params.append(status)
                
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY l.start_time DESC"
            
            cursor.execute(query, params)
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
    
    def add_problem_project(self, problem_id: int, project_id: int) -> bool:
        """
        Associate a project with a problem (many-to-many relationship).
        
        Args:
            problem_id (int): ID of the problem
            project_id (int): ID of the project
            
        Returns:
            bool: True if association was successful, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO problem_projects (problem_id, project_id) VALUES (?, ?)",
                    (problem_id, project_id)
                )
                return cursor.rowcount > 0
            except Exception:
                return False
    
    def remove_problem_project(self, problem_id: int, project_id: int) -> bool:
        """
        Remove association between a problem and project.
        
        Args:
            problem_id (int): ID of the problem
            project_id (int): ID of the project
            
        Returns:
            bool: True if removal was successful, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM problem_projects WHERE problem_id = ? AND project_id = ?",
                (problem_id, project_id)
            )
            return cursor.rowcount > 0
    
    def get_projects_by_problem(self, problem_id: int) -> List[Dict[str, Any]]:
        """
        Get all projects associated with a specific problem.
        
        Args:
            problem_id (int): ID of the problem
            
        Returns:
            List of project dictionaries
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, pr.name as problem_name, pr.id as problem_id
                FROM projects p
                INNER JOIN problem_projects pp ON p.id = pp.project_id
                LEFT JOIN problems pr ON pp.problem_id = pr.id
                WHERE pp.problem_id = ?
                ORDER BY p.updated_date DESC
            """, (problem_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_problems_by_project(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get all problems associated with a specific project.
        
        Args:
            project_id (int): ID of the project
            
        Returns:
            List of problem dictionaries
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pr.*
                FROM problems pr
                INNER JOIN problem_projects pp ON pr.id = pp.problem_id
                WHERE pp.project_id = ?
                ORDER BY pr.updated_date DESC
            """, (project_id,))
            return [dict(row) for row in cursor.fetchall()]