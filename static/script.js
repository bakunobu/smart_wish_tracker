// Timer functionality for launch-based tracking
let timerInterval;
let seconds = 0;
let paused = false;
let currentLaunchId = null;

// DOM elements
const timerDisplay = document.getElementById('timer-display');
const startPauseBtn = document.getElementById('start-pause-btn');
const abortBtn = document.getElementById('abort-btn');
const finishBtn = document.getElementById('finish-btn');
const taskSelect = document.getElementById('task-select');
const newTaskBtn = document.getElementById('new-task-btn');
const launchTable = document.getElementById('launch-history-table').querySelector('tbody');

// Format time as HH:MM:SS
function formatTime(totalSeconds) {
    const hrs = Math.floor(totalSeconds / 3600);
    const mins = Math.floor((totalSeconds % 3600) / 60);
    const secs = totalSeconds % 60;
    
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Update timer display
function updateTimer() {
    if (!paused) seconds++;
    timerDisplay.textContent = formatTime(seconds);
}

// Start or pause timer
startPauseBtn.addEventListener('click', () => {
    if (!taskSelect.value) {
        alert('Please select a task first');
        return;
    }
    
    if (startPauseBtn.textContent === 'Start') {
        // Start new launch
        fetch('/start_launch', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                task_id: taskSelect.value
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.launch_id) {
                currentLaunchId = data.launch_id;
                seconds = 0;
                paused = false;
                timerInterval = setInterval(updateTimer, 1000);
                
                // Update UI
                startPauseBtn.textContent = 'Pause';
                abortBtn.disabled = false;
                finishBtn.disabled = false;
                taskSelect.disabled = true;
            }
        });
    } else if (startPauseBtn.textContent === 'Pause') {
        // Pause current launch
        paused = true;
        startPauseBtn.textContent = 'Resume';
        
        // Update server
        fetch(`/pause_launch/${currentLaunchId}`, {
            method: 'PATCH'
        });
    } else if (startPauseBtn.textContent === 'Resume') {
        // Resume paused launch
        paused = false;
        startPauseBtn.textContent = 'Pause';
        
        // Update server
        fetch(`/resume_launch/${currentLaunchId}`, {
            method: 'PATCH'
        });
    }
});

// Abort current launch
abortBtn.addEventListener('click', () => {
    clearInterval(timerInterval);
    
    // Delete launch record
    fetch(`/abort_launch/${currentLaunchId}`, {
        method: 'DELETE'
    })
    .then(() => {
        resetTimerUI();
    });
});

// Finish current launch
finishBtn.addEventListener('click', () => {
    clearInterval(timerInterval);
    
    // Calculate minutes
    const minutes = Math.round(seconds / 60);
    
    // Complete launch
    fetch(`/finish_launch/${currentLaunchId}`, {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ minutes })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            resetTimerUI();
            loadLaunchHistory();
        }
    });
});

// Reset timer UI
function resetTimerUI() {
    seconds = 0;
    paused = false;
    currentLaunchId = null;
    timerDisplay.textContent = '00:00:00';
    
    // Update buttons
    startPauseBtn.textContent = 'Start';
    abortBtn.disabled = true;
    finishBtn.disabled = true;
    taskSelect.disabled = false;
}

// Create new task
newTaskBtn.addEventListener('click', () => {
    const taskName = prompt('Enter new task name:');
    if (taskName) {
        fetch('/create_task', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ name: taskName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.task_id) {
                // Add to dropdown
                const option = document.createElement('option');
                option.value = data.task_id;
                option.textContent = taskName;
                taskSelect.appendChild(option);
                
                // Select new task
                taskSelect.value = data.task_id;
            }
        });
    }
});

// Load tasks for dropdown
function loadTasks() {
    fetch('/get_tasks')
    .then(response => response.json())
    .then(tasks => {
        tasks.forEach(task => {
            const option = document.createElement('option');
            option.value = task.id;
            option.textContent = task.name;
            taskSelect.appendChild(option);
        });
    });
}

// Load launch history
function loadLaunchHistory() {
    fetch('/get_launches')
    .then(response => response.json())
    .then(launches => {
        // Clear existing rows
        launchTable.innerHTML = '';
        
        // Add new rows
        launches.forEach(launch => {
            const row = document.createElement('tr');
            
            // Format times
            const startTime = new Date(launch.start_time).toLocaleTimeString();
            const endTime = launch.end_time ? new Date(launch.end_time).toLocaleTimeString() : 'N/A';
            const duration = launch.duration ? formatTime(launch.duration * 60) : 'N/A';
            
            row.innerHTML = `
                <td>${launch.task_name}</td>
                <td>${startTime}</td>
                <td>${endTime}</td>
                <td>${duration}</td>
            `;
            
            launchTable.appendChild(row);
        });
    });
}

// Adjust time for completed launch
function adjustTime(launchId) {
    const newMinutes = prompt('Enter adjusted time in minutes:');
    if (newMinutes && !isNaN(newMinutes)) {
        fetch(`/adjust_time/${launchId}`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ minutes: parseInt(newMinutes) })
        })
        .then(() => {
            loadLaunchHistory();
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    loadLaunchHistory();
    
    // Disable buttons initially
    abortBtn.disabled = true;
    finishBtn.disabled = true;
});