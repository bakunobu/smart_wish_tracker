import random
import threading
import webbrowser
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
from database import Database
from task import Task
from launch import Launch
import grid_manager


def create_app():
    app = Flask(__name__)
    db = Database()
    grid_manager.init_db()  # Initialize contributions database

    # Generate random contribution data
    def generate_contributions():
        contributions = {}
        # Start from one year ago
        today = datetime.now()
        year_ago = today - timedelta(days=365)

        current_date = year_ago
        while current_date <= today:
            # Random number of contributions (0-4)
            # Weighted distribution: most days have 0-1, fewer have 2-3, rare days have 4
            num = random.random()
            if num < 0.6:
                count = 0
            elif num < 0.8:
                count = 1
            elif num < 0.9:
                count = 2
            elif num < 0.97:
                count = 3
            else:
                count = 4

            # Store in format YYYY-MM-DD
            date_str = current_date.strftime("%Y-%m-%d")
            contributions[date_str] = count
            current_date += timedelta(days=1)

        return contributions

    @app.route("/")
    def index():
        contributions = generate_contributions()
        
        # Get active tasks for dropdown
        tasks = Task.list_all(db=db)
        
        # Get recent launch history
        launches = grid_manager.get_launch_history(days=7)
        
        return render_template(
            "index.html",
            contributions=contributions,
            tasks=tasks,
            launches=launches
        )

    # API Endpoints
    @app.route('/start_launch', methods=['POST'])
    def start_launch():
        data = request.json
        task_id = data.get('task_id')
        
        if not task_id:
            return jsonify({'error': 'Task ID is required'}), 400
        
        # Create new launch
        launch_id = db.create_launch(
            task_id=task_id,
            project_id=Task.from_db(task_id, db).project_id,
            start_time=datetime.now()
        )
        
        return jsonify({'launch_id': launch_id})

    @app.route('/pause_launch/<int:launch_id>', methods=['PATCH'])
    def pause_launch(launch_id):
        db.update_launch(launch_id, state='paused')
        return jsonify({'success': True})

    @app.route('/resume_launch/<int:launch_id>', methods=['PATCH'])
    def resume_launch(launch_id):
        db.update_launch(launch_id, state='running')
        return jsonify({'success': True})

    @app.route('/abort_launch/<int:launch_id>', methods=['DELETE'])
    def abort_launch(launch_id):
        db.delete_launch(launch_id)
        return jsonify({'success': True})

    @app.route('/finish_launch/<int:launch_id>', methods=['PATCH'])
    def finish_launch(launch_id):
        data = request.json
        minutes = data.get('minutes')
        
        if minutes is None:
            return jsonify({'error': 'Minutes are required'}), 400
        
        # Update launch with end time and duration
        db.update_launch(
            launch_id,
            end_time=datetime.now(),
            duration=minutes,
            state='completed'
        )
        
        # Add contribution to grid
        today = datetime.now().strftime("%Y-%m-%d")
        grid_manager.add_contribution(today, minutes)
        
        return jsonify({'success': True})

    @app.route('/adjust_time/<int:launch_id>', methods=['PATCH'])
    def adjust_time(launch_id):
        data = request.json
        new_minutes = data.get('minutes')
        
        if new_minutes is None:
            return jsonify({'error': 'Minutes are required'}), 400
        
        # Get current launch
        launch = db.get_launch(launch_id)
        if not launch:
            return jsonify({'error': 'Launch not found'}), 404
        
        # Update duration
        db.update_launch(launch_id, duration=new_minutes)
        
        # Update grid contribution
        date_str = datetime.fromisoformat(launch['start_time']).strftime("%Y-%m-%d")
        grid_manager.add_contribution(date_str, new_minutes - launch['duration'])
        
        return jsonify({'success': True})

    @app.route('/get_tasks')
    def get_tasks():
        tasks = Task.list_all(db=db)
        return jsonify([{
            'id': task.id,
            'name': task.name
        } for task in tasks])

    @app.route('/get_launches')
    def get_launches():
        launches = db.list_launches(limit=10)
        return jsonify([{
            'id': launch['id'],
            'task_name': launch['task_name'],
            'start_time': launch['start_time'],
            'end_time': launch['end_time'],
            'duration': launch['duration']
        } for launch in launches])

    @app.route('/create_task', methods=['POST'])
    def create_task():
        data = request.json
        name = data.get('name')
        
        if not name:
            return jsonify({'error': 'Task name is required'}), 400
        
        task_id = db.create_task(name)
        return jsonify({'task_id': task_id})

    return app


# For running directly
if __name__ == "__main__":
    import random
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
