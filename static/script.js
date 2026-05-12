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

// Time Tracker Functionality
let timerInterval = null;
let seconds = 0;
let isRunning = false;

function updateTimerDisplay() {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    document.querySelector('.timer-display').textContent = 
        `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function startTimer() {
    if (!isRunning) {
        isRunning = true;
        document.getElementById('start-stop-btn').textContent = 'Stop';
        document.getElementById('start-stop-btn').classList.remove('start');
        document.getElementById('start-stop-btn').classList.add('stop');
        
        timerInterval = setInterval(() => {
            seconds++;
            updateTimerDisplay();
        }, 1000);
    } else {
        isRunning = false;
        document.getElementById('start-stop-btn').textContent = 'Start';
        document.getElementById('start-stop-btn').classList.remove('stop');
        document.getElementById('start-stop-btn').classList.add('start');
        
        clearInterval(timerInterval);
    }
}

function resetTimer() {
    clearInterval(timerInterval);
    seconds = 0;
    isRunning = false;
    updateTimerDisplay();
    document.getElementById('start-stop-btn').textContent = 'Start';
    document.getElementById('start-stop-btn').classList.remove('stop');
    document.getElementById('start-stop-btn').classList.add('start');
}

// Problem Adder/Selector Functionality
async function loadProjects() {
    try {
        // In a real implementation, this would fetch projects from the server
        // For now, we'll simulate with some sample data
        const projectSelect = document.getElementById('project-select');
        
        // Clear existing options except the first
        while (projectSelect.options.length > 1) {
            projectSelect.remove(1);
        }
        
        // Add sample projects
        const sampleProjects = [
            { id: 1, name: 'Learn Python' },
            { id: 2, name: 'Web Development' },
            { id: 3, name: 'Data Science' }
        ];
        
        sampleProjects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            projectSelect.appendChild(option);
        });
        
        // Load events when a project is selected
        projectSelect.addEventListener('change', loadEvents);
        
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

async function loadEvents() {
    const projectSelect = document.getElementById('project-select');
    const eventSelect = document.getElementById('event-select');
    
    // Clear existing options except the first
    while (eventSelect.options.length > 1) {
        eventSelect.remove(1);
    }
    
    const projectId = projectSelect.value;
    
    if (!projectId) {
        return;
    }
    
    try {
        // In a real implementation, this would fetch events for the selected project from the server
        // For now, we'll simulate with some sample data
        const sampleEvents = {
            '1': [
                { id: 1, topic: 'Learn Python Basics', duration: 60 },
                { id: 2, topic: 'Build a Web Application', duration: 120 },
                { id: 3, topic: 'Study Data Structures', duration: 90 }
            ],
            '2': [
                { id: 4, topic: 'Learn HTML/CSS', duration: 45 },
                { id: 5, topic: 'Study JavaScript', duration: 75 },
                { id: 6, topic: 'Build a Portfolio Site', duration: 180 }
            ],
            '3': [
                { id: 7, topic: 'Learn Pandas', duration: 60 },
                { id: 8, topic: 'Study Machine Learning', duration: 150 },
                { id: 9, topic: 'Work on Data Visualization', duration: 90 }
            ]
        };
        
        const events = sampleEvents[projectId] || [];
        
        events.forEach(event => {
            const option = document.createElement('option');
            option.value = event.id;
            option.textContent = `${event.topic} (${event.duration}min)`;
            eventSelect.appendChild(option);
        });
        
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

async function addProblem(event) {
    event.preventDefault();
    
    const newProjectName = document.getElementById('new-project-name').value;
    const newProjectDesc = document.getElementById('new-project-desc').value;
    const newEventTopic = document.getElementById('new-event-topic').value;
    const eventDuration = document.getElementById('event-duration').value;
    
    // In a real implementation, this would send the data to the server to create a new project and event
    // For now, we'll just show an alert
    alert(`New problem added:\nProject: ${newProjectName}\nDescription: ${newProjectDesc}\nEvent: ${newEventTopic}\nDuration: ${eventDuration} minutes`);
    
    // Reset the form
    document.getElementById('problem-form').reset();
}

// Initialize the grid when page loads
window.addEventListener('load', () => {
    createGrid();
    updateTimerDisplay();
    
    // Set up timer controls
    document.getElementById('start-stop-btn').addEventListener('click', startTimer);
    document.getElementById('reset-btn').addEventListener('click', resetTimer);
    
    // Set up problem form
    document.getElementById('problem-form').addEventListener('submit', addProblem);
    
    // Load projects and events
    loadProjects();
});