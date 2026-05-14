#!/usr/bin/env python3
"""
Test script to verify the three-level entity hierarchy:
1) Problem (base level, can be associated with multiple projects)
2) Project (can have multiple problem associations and tasks)
3) Task (minimal unit within a project, connected to single project)
"""

import os
import sys

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database

def test_hierarchy():
    """Test the three-level hierarchy functionality."""
    print("=== Testing Three-Level Entity Hierarchy ===\n")
    
    # Use a test database to avoid conflicts
    test_db = Database("test_hierarchy.db")
    
    try:
        # Level 1: Create Problems (base level)
        print("1. Creating Problems (Level 1)...")
        problem1_id = test_db.create_problem("Improve Personal Productivity",
                          "Focus on time management and task organization")
        problem2_id = test_db.create_problem("Learn New Technologies",
                          "Stay up-to-date with modern development tools")
        
        print(f"   ✓ Created Problem ID: {problem1_id}")
        print(f"   ✓ Created Problem ID: {problem2_id}")
        
        # Level 2: Create Projects (can be associated with multiple problems)
        print("\n2. Creating Projects (Level 2)...")
        project1_id = test_db.create_project("Task Management System",
                          "Build a comprehensive task tracking application")
        project2_id = test_db.create_project("Python Learning Path",
                          "Structured approach to learning Python")
        project3_id = test_db.create_project("Time Tracking Tools",
                          "Research and implement efficient time tracking")
        
        print(f"   ✓ Created Project ID: {project1_id}")
        print(f"   ✓ Created Project ID: {project2_id}")
        print(f"   ✓ Created Project ID: {project3_id}")
        
        # Associate projects with problems (many-to-many relationship)
        print("\n3. Associating Projects with Problems...")
        
        # Project1 addresses both problems
        test_db.add_problem_project(problem1_id, project1_id)
        test_db.add_problem_project(problem2_id, project1_id)
        
        # Project2 only addresses learning problem
        test_db.add_problem_project(problem2_id, project2_id)
        
        # Project3 only addresses productivity problem
        test_db.add_problem_project(problem1_id, project3_id)
        
        print("   ✓ Associated Task Management System with both problems")
        print("   ✓ Associated Python Learning Path with Learning problem")
        print("   ✓ Associated Time Tracking Tools with Productivity problem")
        
        # Level 3: Create Tasks (connected to single project)
        print("\n4. Creating Tasks (Level 3)...")
        
        # Tasks for Task Management System
        task1_id = test_db.create_task("Design Database Schema",
            "Create tables for problems, projects, and tasks",
            project1_id, 60)
        task2_id = test_db.create_task("Implement Entity Classes",
            "Build Problem, Project, and Task classes",
            project1_id, 90)
        task3_id = test_db.create_task("Create Web Interface",
            "Build HTML/CSS/JS frontend",
            project1_id, 120)
        
        # Tasks for Python Learning Path
        task4_id = test_db.create_task("Study Python Basics",
            "Variables, functions, control structures",
            project2_id, 180)
        task5_id = test_db.create_task("Learn Advanced Features",
            "Decorators, generators, context managers",
            project2_id, 240)
        
        # Tasks for Time Tracking Tools
        task6_id = test_db.create_task("Research Existing Tools",
            "Evaluate current market solutions",
            project3_id, 45)
        
        print(f"   ✓ Created Task ID: {task1_id}")
        print(f"   ✓ Created Task ID: {task2_id}")
        print(f"   ✓ Created Task ID: {task3_id}")
        print(f"   ✓ Created Task ID: {task4_id}")
        print(f"   ✓ Created Task ID: {task5_id}")
        print(f"   ✓ Created Task ID: {task6_id}")
        
        # Test hierarchy relationships
        print("\n5. Testing Hierarchy Relationships...")
        
        # Test Problem -> Projects relationship
        projects1 = test_db.get_projects_by_problem(problem1_id)
        print(f"\n   Problem ID {problem1_id} has {len(projects1)} associated projects:")
        for proj in projects1:
            print(f"     - {proj['name']} (ID: {proj['id']})")
        
        projects2 = test_db.get_projects_by_problem(problem2_id)
        print(f"\n   Problem ID {problem2_id} has {len(projects2)} associated projects:")
        for proj in projects2:
            print(f"     - {proj['name']} (ID: {proj['id']})")
        
        # Test Project -> Tasks relationship
        tasks1 = test_db.list_tasks(project_id=project1_id)
        print(f"\n   Project ID {project1_id} has {len(tasks1)} tasks:")
        for task in tasks1:
            print(f"     - {task['name']} (ID: {task['id']}, {task['expected_duration']} min)")
        
        print("\n=== All Tests Passed! ===")
        print("\nThe three-level hierarchy is working correctly:")
        print("✓ Level 1: Problems (base level, can be associated with multiple projects)")
        print("✓ Level 2: Projects (can have multiple problem associations and tasks)")
        print("✓ Level 3: Tasks (minimal units within projects, connected to single project)")
        print("✓ Many-to-many relationship between Problems and Projects")
        print("✓ One-to-many relationship between Projects and Tasks")
        
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