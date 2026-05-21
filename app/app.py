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
    """Initialize database with tasks table and timer history tables"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                position INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS timer_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                session_id TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                planned_duration INTEGER NOT NULL,
                actual_duration INTEGER,
                status TEXT NOT NULL DEFAULT 'active',
                creation_source TEXT DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS task_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL UNIQUE,
                first_created TIMESTAMP,
                total_attempts INTEGER DEFAULT 0,
                successful_runs INTEGER DEFAULT 0,
                total_seconds_planned INTEGER DEFAULT 0,
                total_seconds_spent INTEGER DEFAULT 0,
                last_session TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        conn.execute('''CREATE INDEX IF NOT EXISTS idx_timer_sessions_task_name ON timer_sessions(task_name)''')
        conn.execute('''CREATE INDEX IF NOT EXISTS idx_timer_sessions_session_id ON timer_sessions(session_id)''')
        conn.execute('''CREATE INDEX IF NOT EXISTS idx_task_statistics_task_name ON task_statistics(task_name)''')
        
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

# Timer Session Management Endpoints

@app.route('/api/timer/start', methods=['POST'])
def start_timer_session():
    """Start a new timer session"""
    try:
        data = request.get_json()
        task_name = data.get('task_name', '').strip()
        session_id = data.get('session_id', '')
        planned_duration = data.get('planned_duration', 1500)  # Default 25 minutes
        creation_source = data.get('creation_source', 'manual')
        
        if not task_name or not session_id:
            return jsonify({"success": False, "error": "Task name and session ID required"}), 400
        
        with get_db() as conn:
            # End any existing active session for this session_id
            conn.execute(
                "UPDATE timer_sessions SET status = 'stopped', ended_at = CURRENT_TIMESTAMP WHERE session_id = ? AND status = 'active'",
                (session_id,)
            )
            
            # Create new session
            cursor = conn.execute('''
                INSERT INTO timer_sessions (task_name, session_id, planned_duration, creation_source)
                VALUES (?, ?, ?, ?)
            ''', (task_name, session_id, planned_duration, creation_source))
            
            session_db_id = cursor.lastrowid
            
            # Update or create task statistics
            update_task_statistics(conn, task_name, 'start')
            
            conn.commit()
        
        return jsonify({
            "success": True,
            "session_id": session_db_id,
            "message": "Timer session started"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/timer/stop', methods=['PUT'])
def stop_timer_session():
    """Stop timer session (unsuccessful completion)"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', '')
        actual_duration = data.get('actual_duration', 0)
        
        if not session_id:
            return jsonify({"success": False, "error": "Session ID required"}), 400
        
        with get_db() as conn:
            # Update session record
            cursor = conn.execute('''
                UPDATE timer_sessions
                SET status = 'stopped', ended_at = CURRENT_TIMESTAMP, actual_duration = ?
                WHERE session_id = ? AND status = 'active'
            ''', (actual_duration, session_id))
            
            if cursor.rowcount == 0:
                return jsonify({"success": False, "error": "No active session found"}), 404
            
            # Get task name for statistics update
            cursor = conn.execute(
                'SELECT task_name FROM timer_sessions WHERE session_id = ? AND status = "stopped" ORDER BY id DESC LIMIT 1',
                (session_id,)
            )
            
            row = cursor.fetchone()
            if row:
                task_name = row[0]
                update_task_statistics(conn, task_name, 'stop', actual_duration)
            
            conn.commit()
        
        return jsonify({
            "success": True,
            "message": "Timer session stopped"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/timer/complete', methods=['PUT'])
def complete_timer_session():
    """Complete timer session (successful completion)"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', '')
        actual_duration = data.get('actual_duration', 0)
        
        if not session_id:
            return jsonify({"success": False, "error": "Session ID required"}), 400
        
        with get_db() as conn:
            # Update session record
            cursor = conn.execute('''
                UPDATE timer_sessions
                SET status = 'completed', ended_at = CURRENT_TIMESTAMP, actual_duration = ?
                WHERE session_id = ? AND status = 'active'
            ''', (actual_duration, session_id))
            
            if cursor.rowcount == 0:
                return jsonify({"success": False, "error": "No active session found"}), 404
            
            # Get task name for statistics update
            cursor = conn.execute(
                'SELECT task_name FROM timer_sessions WHERE session_id = ? AND status = "completed" ORDER BY id DESC LIMIT 1',
                (session_id,)
            )
            
            row = cursor.fetchone()
            if row:
                task_name = row[0]
                update_task_statistics(conn, task_name, 'complete', actual_duration)
            
            conn.commit()
        
        return jsonify({
            "success": True,
            "message": "Timer session completed successfully"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/timer/history')
def get_timer_history():
    """Get timer session history, optionally filtered by task"""
    try:
        task_name = request.args.get('task', '')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        with get_db() as conn:
            if task_name:
                cursor = conn.execute('''
                    SELECT id, task_name, session_id, started_at, ended_at,
                           planned_duration, actual_duration, status, creation_source
                    FROM timer_sessions
                    WHERE task_name = ?
                    ORDER BY started_at DESC
                    LIMIT ? OFFSET ?
                ''', (task_name, limit, offset))
            else:
                cursor = conn.execute('''
                    SELECT id, task_name, session_id, started_at, ended_at,
                           planned_duration, actual_duration, status, creation_source
                    FROM timer_sessions
                    ORDER BY started_at DESC
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
            
            sessions = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            "success": True,
            "sessions": sessions,
            "count": len(sessions)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/timer/stats')
def get_timer_stats():
    """Get aggregated timer statistics"""
    try:
        task_name = request.args.get('task', '')
        
        with get_db() as conn:
            if task_name:
                cursor = conn.execute('''
                    SELECT task_name, first_created, total_attempts, successful_runs,
                           total_seconds_planned, total_seconds_spent, last_session, updated_at
                    FROM task_statistics
                    WHERE task_name = ?
                ''', (task_name,))
                
                row = cursor.fetchone()
                if row:
                    stats = dict(row)
                    stats['success_rate'] = round((stats['successful_runs'] / max(stats['total_attempts'], 1)) * 100, 1)
                    return jsonify({"success": True, "stats": stats})
                else:
                    return jsonify({"success": False, "error": "Task not found"}), 404
            else:
                cursor = conn.execute('''
                    SELECT task_name, first_created, total_attempts, successful_runs,
                           total_seconds_planned, total_seconds_spent, last_session, updated_at
                    FROM task_statistics
                    ORDER BY last_session DESC
                ''')
                
                all_stats = []
                for row in cursor.fetchall():
                    stats = dict(row)
                    stats['success_rate'] = round((stats['successful_runs'] / max(stats['total_attempts'], 1)) * 100, 1)
                    all_stats.append(stats)
                
                return jsonify({
                    "success": True,
                    "stats": all_stats,
                    "count": len(all_stats)
                })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/timer/export')
def export_timer_data():
    """Export timer data as JSON"""
    try:
        format_type = request.args.get('format', 'json').lower()
        
        with get_db() as conn:
            # Export sessions
            cursor = conn.execute('''
                SELECT id, task_name, session_id, started_at, ended_at,
                       planned_duration, actual_duration, status, creation_source, created_at
                FROM timer_sessions
                ORDER BY started_at DESC
            ''')
            sessions = [dict(row) for row in cursor.fetchall()]
            
            # Export statistics
            cursor = conn.execute('''
                SELECT task_name, first_created, total_attempts, successful_runs,
                       total_seconds_planned, total_seconds_spent, last_session, updated_at
                FROM task_statistics
            ''')
            statistics = [dict(row) for row in cursor.fetchall()]
        
        from datetime import datetime
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "sessions": sessions,
            "statistics": statistics
        }
        
        if format_type == 'json':
            response = jsonify(export_data)
            response.headers['Content-Disposition'] = f'attachment; filename=timer_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            return response
        else:
            return jsonify({"success": False, "error": "Only JSON format supported"}), 400
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/timer/cleanup', methods=['DELETE'])
def cleanup_old_data():
    """Clean up old timer session data"""
    try:
        days = int(request.args.get('days', 90))  # Default 90 days
        
        with get_db() as conn:
            # Delete old sessions
            cursor = conn.execute('''
                DELETE FROM timer_sessions
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            
            deleted_sessions = cursor.rowcount
            
            # Recalculate statistics for affected tasks
            cursor = conn.execute('SELECT DISTINCT task_name FROM task_statistics')
            task_names = [row[0] for row in cursor.fetchall()]
            
            for task_name in task_names:
                recalculate_task_statistics(conn, task_name)
            
            conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Cleaned up {deleted_sessions} old sessions",
            "deleted_sessions": deleted_sessions
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def update_task_statistics(conn, task_name, action, actual_duration=0):
    """Update task statistics based on timer action"""
    
    # Get or create statistics record
    cursor = conn.execute('''
        INSERT OR IGNORE INTO task_statistics (task_name, first_created)
        VALUES (?, CURRENT_TIMESTAMP)
    ''', (task_name,))
    
    if action == 'start':
        conn.execute('''
            UPDATE task_statistics
            SET total_attempts = total_attempts + 1,
                last_session = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE task_name = ?
        ''', (task_name,))
    
    elif action == 'complete':
        conn.execute('''
            UPDATE task_statistics
            SET successful_runs = successful_runs + 1,
                total_seconds_spent = total_seconds_spent + ?,
                last_session = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE task_name = ?
        ''', (actual_duration, task_name))
    
    elif action == 'stop':
        conn.execute('''
            UPDATE task_statistics
            SET total_seconds_spent = total_seconds_spent + ?,
                last_session = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE task_name = ?
        ''', (actual_duration, task_name))


def recalculate_task_statistics(conn, task_name):
    """Recalculate statistics for a task from session data"""
    cursor = conn.execute('''
        SELECT
            COUNT(*) as total_attempts,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_runs,
            SUM(COALESCE(actual_duration, 0)) as total_seconds_spent,
            MIN(created_at) as first_created,
            MAX(started_at) as last_session
        FROM timer_sessions
        WHERE task_name = ?
    ''', (task_name,))
    
    row = cursor.fetchone()
    if row:
        conn.execute('''
            UPDATE task_statistics
            SET total_attempts = ?,
                successful_runs = ?,
                total_seconds_spent = ?,
                first_created = COALESCE(first_created, ?),
                last_session = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE task_name = ?
        ''', (row[0], row[1], row[2], row[3], row[4], task_name))


@app.route('/api/daily-stats')
def get_daily_stats():
    """Get daily statistics for today with mood indicator based on 2-week rolling performance"""
    try:
        with get_db() as conn:
            # Get today's statistics
            today_cursor = conn.execute('''
                SELECT
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as finished_tasks,
                    COUNT(*) as total_sessions,
                    SUM(CASE WHEN status IN ('completed', 'stopped') THEN COALESCE(actual_duration, 0) ELSE 0 END) as total_time_seconds,
                    CASE
                        WHEN COUNT(*) > 0 THEN
                            ROUND(COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*), 1)
                        ELSE 0
                    END as completion_percentage
                FROM timer_sessions
                WHERE date(started_at) = date('now')
            ''')
            
            today_stats = today_cursor.fetchone()
            
            # Get 14-day rolling data for percentile calculation
            rolling_cursor = conn.execute('''
                SELECT
                    date(started_at) as session_date,
                    SUM(COALESCE(actual_duration, 0)) as daily_time_seconds
                FROM timer_sessions
                WHERE date(started_at) >= date('now', '-13 days')
                  AND date(started_at) <= date('now')
                  AND status IN ('completed', 'stopped')
                GROUP BY date(started_at)
                ORDER BY daily_time_seconds
            ''')
            
            rolling_data = [row['daily_time_seconds'] for row in rolling_cursor.fetchall()]
            
            # Calculate percentiles and mood emoji
            mood_emoji = '😊'  # Default neutral
            percentile_25 = 0
            percentile_75 = 0
            current_rank = 'middle'
            
            if rolling_data:
                rolling_data.sort()
                data_len = len(rolling_data)
                percentile_25 = rolling_data[data_len // 4] if data_len >= 4 else rolling_data[0]
                percentile_75 = rolling_data[3 * data_len // 4] if data_len >= 4 else rolling_data[-1]
                
                today_time = today_stats['total_time_seconds'] or 0
                
                if today_time <= percentile_25:
                    mood_emoji = '😢'
                    current_rank = 'bottom'
                elif today_time >= percentile_75:
                    mood_emoji = '😄'
                    current_rank = 'top'
                else:
                    mood_emoji = '😊'
                    current_rank = 'middle'
            
            # Format time display
            total_seconds = today_stats['total_time_seconds'] or 0
            if total_seconds < 60:
                time_formatted = f"{total_seconds}s"
            elif total_seconds < 3600:
                minutes = total_seconds // 60
                time_formatted = f"{minutes}m"
            else:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                time_formatted = f"{hours}h {minutes}m"
            
            return jsonify({
                "success": True,
                "stats": {
                    "finished_tasks": today_stats['finished_tasks'] or 0,
                    "total_sessions": today_stats['total_sessions'] or 0,
                    "total_time_seconds": total_seconds,
                    "total_time_formatted": time_formatted,
                    "completion_percentage": today_stats['completion_percentage'] or 0,
                    "mood_emoji": mood_emoji,
                    "historical_context": {
                        "days_in_period": len(rolling_data),
                        "percentile_25": percentile_25,
                        "percentile_75": percentile_75,
                        "current_rank": current_rank
                    }
                }
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "stats": {
                "finished_tasks": 0,
                "total_sessions": 0,
                "total_time_seconds": 0,
                "total_time_formatted": "0m",
                "completion_percentage": 0,
                "mood_emoji": "😊",
                "historical_context": None
            }
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
