# Quest Database Schema Design

## Quest Table Structure

```sql
CREATE TABLE IF NOT EXISTS quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_name TEXT NOT NULL,
    description TEXT NOT NULL,
    quest_type TEXT NOT NULL CHECK (quest_type IN ('stack', 'duration', 'complete')),
    stack_duration_days INTEGER DEFAULT 0,
    stack_min_time_per_day INTEGER DEFAULT 15,
    duration_hours REAL DEFAULT 0.0,
    complete_result TEXT NOT NULL,
    reward_url TEXT,
    reward_image TEXT,
    position INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Field Descriptions

- **id**: Primary key for quest identification
- **short_name**: Brief name for the quest (max 100 chars)
- **description**: Detailed description of the quest
- **quest_type**: Type of quest ('stack', 'duration', or 'complete')
- **stack_duration_days**: Number of days for stack-type quests
- **stack_min_time_per_day**: Minimum time per day in minutes (default 15)
- **duration_hours**: Total duration in hours for duration-type quests
- **complete_result**: Expected result description for complete-type quests
- **reward_url**: URL for the reward
- **reward_image**: URL or path to reward image
- **position**: Position in the quest list (for ordering)
- **is_active**: Whether the quest is currently active
- **created_at**: Timestamp when quest was created

## Database Integration Notes

1. The quests table will be added to the existing SQLite database
2. Position management will handle reordering when quests are activated
3. The is_active flag will track which quest is currently running
4. Quest type determines which fields are required and displayed