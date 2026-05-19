import os
import sqlite3
import json
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__, template_folder='../templates')

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), 'tasks.db')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tasks table"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                position INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Initialize database on startup
init_db()

@app.route('/')
def index():
    return render_template('countdown.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks ordered by position"""
    try:
        with get_db() as conn:
            cursor = conn.execute('SELECT id, name, position FROM tasks ORDER BY position')
            tasks = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            "success": True,
            "tasks": tasks
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({"success": False, "error": "Task name is required"}), 400

        name = data['name'].strip()
        if not name:
            return jsonify({"success": False, "error": "Task name cannot be empty"}), 400

        with get_db() as conn:
            # Check if task already exists
            cursor = conn.execute('SELECT id FROM tasks WHERE name = ?', (name,))
            if cursor.fetchone():
                return jsonify({"success": False, "error": "Task with this name already exists"}), 409

            # Check if we have space for new task
            cursor = conn.execute('SELECT COUNT(*) as count FROM tasks')
            task_count = cursor.fetchone()['count']
            if task_count >= 5:
                return jsonify({"success": False, "error": "Maximum of 5 tasks reached"}), 403

            # Find first available position
            cursor = conn.execute('SELECT position FROM tasks ORDER BY position')
            existing_positions = [row['position'] for row in cursor.fetchall()]
            new_position = 0
            while new_position in existing_positions and new_position < 5:
                new_position += 1

            if new_position >= 5:
                return jsonify({"success": False, "error": "No available slot for new task"}), 403

            # Insert new task
            cursor = conn.execute(
                'INSERT INTO tasks (name, position) VALUES (?, ?)',
                (name, new_position)
            )
            task_id = cursor.lastrowid
            conn.commit()

        return jsonify({
            "success": True,
            "data": {"id": task_id, "name": name, "position": new_position}
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({"success": False, "error": "Task name is required"}), 400

        name = data['name'].strip()
        if not name:
            return jsonify({"success": False, "error": "Task name cannot be empty"}), 400

        with get_db() as conn:
            # Check if task exists
            cursor = conn.execute('SELECT id, position FROM tasks WHERE id = ?', (task_id,))
            task = cursor.fetchone()
            if not task:
                return jsonify({"success": False, "error": "Task not found"}), 404

            # Check if another task has the same name
            cursor = conn.execute('SELECT id FROM tasks WHERE name = ? AND id != ?', (name, task_id))
            if cursor.fetchone():
                return jsonify({"success": False, "error": "Another task with this name already exists"}), 409

            # Update task
            conn.execute('UPDATE tasks SET name = ? WHERE id = ?', (name, task_id))
            conn.commit()

        return jsonify({
            "success": True,
            "data": {"id": task_id, "name": name, "position": task['position']}
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task and reorder remaining tasks"""
    try:
        with get_db() as conn:
            # Get task to delete
            cursor = conn.execute('SELECT position FROM tasks WHERE id = ?', (task_id,))
            task = cursor.fetchone()
            if not task:
                return jsonify({"success": False, "error": "Task not found"}), 404

            deleted_position = task['position']

            # Delete the task
            conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))

            # Reorder remaining tasks (move tasks down to fill the gap)
            conn.execute(
                'UPDATE tasks SET position = position - 1 WHERE position > ?',
                (deleted_position,)
            )
            conn.commit()

        return jsonify({
            "success": True,
            "message": "Task deleted successfully"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/tasks/suggestions')
def get_suggestions():
    """Get task name suggestions for autocomplete"""
    try:
        query = request.args.get('q', '').strip()
        if len(query) < 2:
            return jsonify({"success": True, "suggestions": []})

        with get_db() as conn:
            cursor = conn.execute(
                'SELECT name FROM tasks WHERE name LIKE ? LIMIT 5',
                (f'%{query}%',)
            )
            suggestions = [row['name'] for row in cursor.fetchall()]

        return jsonify({
            "success": True,
            "suggestions": suggestions
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
