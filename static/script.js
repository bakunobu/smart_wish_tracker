// Function to create the contribution grid using data from Flask
function createGrid() {
    const grid = document.getElementById('grid');
    const weekLabels = document.getElementById('week-labels');
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    // Start date (one year ago from today)
    const today = new Date();
    const oneYearAgo = new Date(today);
    oneYearAgo.setFullYear(today.getFullYear() - 1);
    
    // Set to the first Sunday before or on oneYearAgo
    const dayOfWeek = oneYearAgo.getDay();
    oneYearAgo.setDate(oneYearAgo.getDate() - dayOfWeek);
    
    // Store the starting date for reference
    let currentDate = new Date(oneYearAgo);
    
    // Create week labels (month indicators at the start of each month)
    for (let week = 0; week < 53; week++) {
        // Create a new Date object for this week
        const weekDate = new Date(currentDate);
        weekDate.setDate(weekDate.getDate() + (week * 7));
        
        const weekLabel = document.createElement('span');
        
        // Check if this is the first week of a month by looking at the day of the month
        // If the date is in the first 7 days of the month, it's the first week
        if (weekDate.getDate() <= 7) {
            weekLabel.textContent = months[weekDate.getMonth()].substring(0, 3);
        } else {
            weekLabel.textContent = '';
        }
        
        weekLabels.appendChild(weekLabel);
    }
    
    // Reset date for grid creation
    currentDate = new Date(oneYearAgo);
    
    // Create the actual grid (53 weeks x 7 days)
    for (let week = 0; week < 53; week++) {
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