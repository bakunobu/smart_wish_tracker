# Daily Statistics Design Specification

## API Endpoint Design

### `/api/daily-stats` (GET)

**Response Format:**
```json
{
    "success": true,
    "stats": {
        "finished_tasks": 3,
        "total_sessions": 5,
        "total_time_seconds": 2700,
        "total_time_formatted": "45m",
        "completion_percentage": 60.0,
        "mood_emoji": "😊",
        "historical_context": {
            "days_in_period": 14,
            "percentile_25": 1800,
            "percentile_75": 3600,
            "current_rank": "middle"
        }
    }
}
```

**Error Response:**
```json
{
    "success": false,
    "error": "Database error message",
    "stats": {
        "finished_tasks": 0,
        "total_sessions": 0,
        "total_time_seconds": 0,
        "total_time_formatted": "0m",
        "completion_percentage": 0,
        "mood_emoji": "😊",
        "historical_context": null
    }
}
```

## UI Design for Statistics Block

### Location
- Position: Below the timer controls in the red hatched area
- Width: Match timer container width
- Height: Compact, approximately 80-100px

### Layout Structure
```
┌─────────────────────────────┐
│  📊 Daily Stats             │
│  ┌─────┬─────────┬─────────┐ │
│  │ 😊  │   3/5   │  45m    │ │
│  │     │ tasks   │ spent   │ │
│  └─────┴─────────┴─────────┘ │
│         60% completed        │
└─────────────────────────────┘
```

### Components Breakdown

1. **Header**
   - Text: "📊 Daily Stats"
   - Small font, consistent with app styling

2. **Main Metrics Row (3 columns)**
   - **Column 1: Mood Emoji**
     - Large emoji (😢/😊/😄)
     - Centered, 1.5em font-size
   
   - **Column 2: Completed Tasks**
     - Format: "X/Y tasks" 
     - X = finished_tasks, Y = total_sessions
     - Primary metric, highlighted
   
   - **Column 3: Time Spent**
     - Format: "XXm spent" or "Xh XXm" for longer durations
     - Secondary metric

3. **Bottom Status Bar**
   - Format: "XX% completed"
   - Full width, smaller text
   - Color coding:
     - Green for ≥75%
     - Yellow for 50-74%  
     - Red for <50%

### CSS Classes Needed
- `.daily-stats-container`
- `.daily-stats-header`
- `.daily-stats-grid`
- `.mood-indicator`
- `.tasks-metric`
- `.time-metric`
- `.completion-bar`

## Visual Styling Guidelines

### Color Scheme (matching existing app)
- Background: `#0f3460` (same as timer container)
- Text: White
- Accent: `#4cc9f0` (cyan blue)
- Success: `#4CAF50` (green)
- Warning: `#FFC107` (amber)
- Danger: `#F44336` (red)

### Typography
- Header: 0.9em, consistent with task panel
- Main metrics: 1.1em, bold
- Completion percentage: 0.85em

### Spacing
- Matches timer container padding (20px)
- Internal spacing: 10px gaps
- Border-radius: 15px (slightly smaller than main container)

## Responsive Design
- Mobile: Stack metrics vertically
- Desktop: Keep horizontal 3-column layout

## Animation/Transitions
- Smooth emoji changes (0.3s transition)
- Number counter animation for metrics updates
- Subtle pulse effect when stats refresh

## Integration Points

### JavaScript Functions Needed
- `fetchDailyStats()` - Get data from API
- `renderDailyStats(data)` - Update DOM
- `formatTimeDisplay(seconds)` - Format duration
- `getMoodEmoji(time, percentiles)` - Determine emoji
- `refreshDailyStats()` - Called after timer events

### Timer Integration
- Refresh stats after session completion
- Refresh stats after session stop
- Refresh stats on page load
- Optional: Real-time updates during active session

## Accessibility
- Proper ARIA labels
- Color contrast compliance
- Screen reader friendly text for emoji
- Semantic HTML structure