# Smart Wish Tracker - Setup Instructions

## Features Implemented ✅

- **Enhanced Home Page**: Based on countdown.html with task management
- **5-Slot Task Management**: Up to 5 tasks with auto-reordering
- **Emoji Action Buttons**: 
  - 🏃 Run (starts timer with selected task)
  - ✏️ Edit (modify task name)
  - 🗑️ Delete (removes task and reorders)
  - ➕ Add (create new task)
- **Smart Integration**: Tasks sync between panel and timer center
- **Autocomplete**: Suggestions start from 2nd character, Tab to complete
- **Database Storage**: SQLite backend with localStorage fallback
- **Responsive Design**: Works on desktop and mobile

## Setup Instructions

### 1. Install Flask
```bash
pip3 install flask
```

### 2. Run the Application
```bash
cd app
python3 app.py
```

### 3. Open in Browser
Navigate to: http://localhost:5000

## How to Use

### Task Management
1. **Add Task**: Click ➕ in empty slot or center "Add Task"
2. **Run Task**: Click 🏃 to load task into timer
3. **Edit Task**: Click ✏️ to rename task
4. **Delete Task**: Click 🗑️ to remove (others auto-reorder)

### Timer Integration
1. Select task from panel or add via center
2. Click "Start" to begin countdown
3. Tasks from panel stay saved after timer stops
4. Ad-hoc tasks can be saved to panel

### Autocomplete
1. Type 2+ characters when adding/editing
2. Press Tab to cycle through suggestions
3. Use arrow keys to navigate
4. Press Enter or click to select

## File Structure
```
smart_wish_tracker/
├── app/
│   ├── app.py          # Flask backend with SQLite
│   └── tasks.db        # SQLite database (auto-created)
├── templates/
│   └── countdown.html  # Enhanced UI with task management
└── SETUP.md           # This file
```

## Database Schema
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    position INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `GET /api/tasks/suggestions?q=query` - Autocomplete

## Troubleshooting

### Flask Not Found
Install Flask: `pip3 install flask`

### Port Already in Use
Change port in app.py: `app.run(debug=True, port=5001)`

### Database Permission Issues
Ensure write permissions in app/ directory

## Browser Compatibility
- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

The app works offline using localStorage if database fails.