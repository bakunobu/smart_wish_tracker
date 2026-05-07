# example_usage.py
"""
Example usage of the project, event, and task classes with database integration.
"""

from datetime import datetime
from project import Project
from task import Task
from database import Database

# Initialize the database
db = Database()

# Create a new project
print("Creating a new project...")
project = Project(
    name="Learn Python",
    description="Learn Python programming language and build projects"
)
print(f"Created project: {project}")

# Add events to the project
print("\nAdding events to the project...")
event1 = project.add_event("Learn Python Basics", 60)
event2 = project.add_event("Build a Web Application", 120)
event3 = project.add_event("Study Data Structures", 90)
print(f"Added events: {event1}, {event2}, {event3}")

# List all events in the project
print("\nListing all events in the project...")
events = project.get_events()
for event in events:
    print(f"- {event}")

# Create a task associated with the project
print("\nCreating a task...")
task = Task(
    name="Complete Python Course",
    estimated_time=180,
    project_id=project.project_id
)
print(f"Created task: {task}")

# Add a contribution for the task
print("\nAdding a contribution for the task...")
task.add_contribution(amount=1.5)
print("Contribution added.")

# Complete the task
print("\nCompleting the task...")
task.complete(effectiveness=0.9)
print("Task completed.")

# List all projects
print("\nListing all projects...")
all_projects = Project.list_all()
for p in all_projects:
    print(f"- {p}")
    # List events for each project
    project_events = p.get_events()
    for event in project_events:
        print(f"  - {event}")

print("\nExample usage completed.")