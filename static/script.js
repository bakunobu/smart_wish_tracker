// Function to create the contribution grid using data from Flask
function createGrid() {
    const grid = document.getElementById('grid');
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    // Create days of the week labels (left side)
    const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    for (let i = 0; i < weekDays.length; i++) {
        const dayLabel = document.createElement('div');
        dayLabel.textContent = weekDays[i];
        dayLabel.className = 'day-label';
        grid.appendChild(dayLabel);
    }

    // Start date (one year ago from today)
    const today = new Date();
    const oneYearAgo = new Date(today);
    oneYearAgo.setFullYear(today.getFullYear() - 1);
    
    // Create the actual grid (53 weeks x 7 days)
    let currentDate = new Date(oneYearAgo);
    
    for (let week = 0; week < 53; week++) {
        // Add month label at the start of each row (first week of the month)
        if (week % 4 === 0 && week < 52) { // Approximate: every 4 weeks = 1 month
            const monthLabel = document.createElement('div');
            monthLabel.textContent = months[currentDate.getMonth()];
            monthLabel.className = 'month-label';
            grid.appendChild(monthLabel);
        } else {
            // Empty cell for alignment
            const emptyCell = document.createElement('div');
            emptyCell.className = 'placeholder';
            grid.appendChild(emptyCell);
        }
        
        // Create cells for each day of the week
        for (let day = 0; day < 7; day++) {
            // Format date as YYYY-MM-DD to match the Python data
            const dateStr = currentDate.toISOString().split('T')[0];
            
            // Get contribution count for this date from the Flask-provided data
            const count = contributions[dateStr] || 0;
            
            // Create cell with appropriate level based on contribution count
            const cell = document.createElement('div');
            cell.className = `contribution-day level-${count}`;
            
            // Add tooltip with date and contribution count
            cell.title = `${count} contribution(s) on ${dateStr}`;
            
            grid.appendChild(cell);
            
            // Move to next day
            currentDate.setDate(currentDate.getDate() + 1);
        }
    }
}

// Initialize the grid when page loads
window.addEventListener('load', createGrid);