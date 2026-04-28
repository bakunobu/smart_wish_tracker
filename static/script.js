// Function to generate a random contribution level (0-4)
function getRandomLevel() {
    const num = Math.random();
    if (num < 0.6) return 0; // 60% chance for no contribution
    if (num < 0.8) return 1; // 20% chance for low contribution
    if (num < 0.9) return 2; // 10% chance for medium contribution
    if (num < 0.97) return 3; // 7% chance for high contribution
    return 4; // 3% chance for very high contribution
}

// Function to create the contribution grid
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

    // Create the actual grid (53 weeks x 7 days)
    for (let week = 0; week < 53; week++) {
        // Add month label at the start of each row (first week of the month)
        if (week % 4 === 0 && week < 52) { // Approximate: every 4 weeks = 1 month
            const monthLabel = document.createElement('div');
            monthLabel.textContent = months[Math.floor(week / 4)];
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
            const cell = document.createElement('div');
            cell.className = `contribution-day level-${getRandomLevel()}`;
            
            // Add tooltip with date and contribution count (simulated)
            const contributionCount = Math.floor(Math.random() * 5); // 0-4 contributions
            const date = `2023-01-01 + ${week * 7 + day} days`; // Simulated date
            cell.title = `${contributionCount} contribution(s) on ${date}`;
            
            grid.appendChild(cell);
        }
    }
}

// Initialize the grid when page loads
window.addEventListener('load', createGrid);