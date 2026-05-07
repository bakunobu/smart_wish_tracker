from flask import Flask, render_template
import random
from datetime import datetime, timedelta
from database import Database

def create_app():
    app = Flask(__name__)
    
    # Initialize the database
    db = Database()
    
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
            date_str = current_date.strftime('%Y-%m-%d')
            contributions[date_str] = count
            current_date += timedelta(days=1)
            
        return contributions
    
    @app.route('/')
    def index():
        contributions = generate_contributions()
        return render_template('index.html', contributions=contributions)
    
    return app

# For running directly
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)