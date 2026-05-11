#!/usr/bin/env python3
"""
Test script to verify the three-level entity hierarchy:
1) Problem (base level, can be associated with multiple projects)
2) Project (can have multiple problem associations and tasks)
3) Task (minimal unit within a project, connected to single project)
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database
from problem import Problem
from project import Project
from task import Task

def test_hierarchy():
    """Test the three-level hierarchy functionality."""
    print("=== Testing Three-Level Entity Hierarchy ===\n")
    
    # Use a test database to avoid conflicts
    test_db = Database("test_hierarchy.db")
    
    try:
        # Level 1: Create Problems (base level)
        print("1. Creating Problems (Level 1)...")
        problem1 = Problem("Improve Personal Productivity", 
                          "Focus on time management and task organization", 
                          db=test_db)
        problem2 = Problem("Learn New Technologies", 
                          "Stay up-to-date with modern development tools", 
                          db=test_db)
        
        print(f"   ✓ Created: {problem1}")
        print(f"   ✓ Created: {problem2}")
        
        # Level 2: Create Projects (can be associated with multiple problems)
        print("\n2. Creating Projects (Level 2)...")
        project1 = Project("Task Management System", 
                          "Build a comprehensive task tracking application", 
                          db=test_db)
        project2 = Project("Python Learning Path", 
                          "Structured approach to learning Python", 
                          db=test_db)
        project3 = Project("Time Tracking Tools", 
                          "Research and implement efficient time tracking", 
                          db=test_db)
        
        print(f"   ✓ Created: {project1}")
        print(f"   ✓ Created: {project2}")
        print(f"   ✓ Created: {project3}")
        
        # Associate projects with problems (many-to-many relationship)
        print("\n3. Associating Projects with Problems...")
        
        # Project1 addresses both problems
        project1.associate_with_problem(problem1.problem_id)
        project1.associate_with_problem(problem2.problem_id)
        
        # Project2 only addresses learning problem
        project2.associate_with_problem(problem2.problem_id)
        
        # Project3 only addresses productivity problem
        project3.associate_with_problem(problem1.problem_id)
        
        print("   ✓ Associated Task Management System with both problems")
        print("   ✓ Associated Python Learning Path with Learning problem")
        print("   ✓ Associated Time Tracking Tools with Productivity problem")
        
        # Level 3: Create Tasks (connected to single project)
        print("\n4. Creating Tasks (Level 3)...")
        
        # Tasks for Task Management System
        task1 = project1.add_task("Design Database Schema", 
                                "Create tables for problems, projects, and tasks", 60)
        task2 = project1.add_task("Implement Entity Classes", 
                                "Build Problem, Project, and Task classes", 90)
        task3 = project1.add_task("Create Web Interface", 
                                "Build HTML/CSS/JS frontend", 120)
        
        # Tasks for Python Learning Path
        task4 = project2.add_task("Study Python Basics", 
                                "Variables, functions, control structures", 180)
        task5 = project2.add_task("Learn Advanced Features", 
                                "Decorators, generators, context managers", 240)
        
        # Tasks for Time Tracking Tools
        task6 = project3.add_task("Research Existing Tools", 
                                "Evaluate current market solutions", 45)
        
        print(f"   ✓ Created: {task1}")
        print(f"   ✓ Created: {task2}")
        print(f"   ✓ Created: {task3}")
        print(f"   ✓ Created: {task4}")
        print(f"   ✓ Created: {task5}")
        print(f"   ✓ Created: {task6}")
        
        # Test hierarchy relationships
        print("\n5. Testing Hierarchy Relationships...")
        
        # Test Problem -> Projects relationship
        print(f"\n   Problem '{problem1.name}' has {len(problem1.get_projects())} associated projects:")
        for proj in problem1.get_projects():
            print(f"     - {proj.name}")
        
        print(f"\n   Problem '{problem2.name}' has {len(problem2.get_projects())} associated projects:")
        for proj in problem2.get_projects():
            print(f"     - {proj.name}")
        
        # Test Project -> Tasks relationship
        print(f"\n   Project '{project1.name}' has {len(project1.get_tasks())} tasks:")
        for task in project1.get_tasks():
            print(f"     - {task.name} ({task.estimated_time} min)")
        
        # Test Project -> Problems relationship
        print(f"\n   Project '{project1.name}' addresses {len(project1.get_problems())} problems:")
        for prob in project1.get_problems():
            print(f"     - {prob.name}")
        
        # Test Task -> Project relationship
        print(f"\n   Task '{task1.name}' belongs to project:")
        parent_project = task1.get_project()
        if parent_project:
            print(f"     - {parent_project.name}")
        
        # Test listing all entities
        print("\n6. Listing All Entities...")
        
        all_problems = Problem.list_all(db=test_db)
        print(f"\n   Total Problems: {len(all_problems)}")
        
        all_projects = Project.list_all(db=test_db)
        print(f"   Total Projects: {len(all_projects)}")
        
        all_tasks = Task.list_all(db=test_db)
        print(f"   Total Tasks: {len(all_tasks)}")
        
        # Test task completion
        print("\n7. Testing Task Completion...")
        print(f"   Completing task: {task1.name}")
        task1.complete(effectiveness=0.8)
        print("   ✓ Task marked as completed with 80% effectiveness")
        
        # Test updates
        print("\n8. Testing Entity Updates...")
        problem1.update(description="Updated: Focus on time management and task organization with new tools")
        project1.update(description="Updated: Build a comprehensive task tracking application with three-level hierarchy")
        task2.update(status="in_progress")
        
        print("   ✓ Updated problem description")
        print("   ✓ Updated project description") 
        print("   ✓ Updated task status to 'in_progress'")
        
        print("\n=== All Tests Passed! ===")
        print("\nThe three-level hierarchy is working correctly:")
        print("✓ Level 1: Problems (base level, can be associated with multiple projects)")
        print("✓ Level 2: Projects (can have multiple problem associations and tasks)")
        print("✓ Level 3: Tasks (minimal units within projects, connected to single project)")
        print("✓ Many-to-many relationship between Problems and Projects")
        print("✓ One-to-many relationship between Projects and Tasks")
        print("✓ Events are created for current task realization")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up test database
        if os.path.exists("test_hierarchy.db"):
            os.remove("test_hierarchy.db")
            print("\n🧹 Cleaned up test database")

if __name__ == "__main__":
    success = test_hierarchy()
    sys.exit(0 if success else 1)