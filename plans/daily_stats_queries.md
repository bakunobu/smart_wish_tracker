# Daily Statistics SQL Queries

## Core Daily Statistics (for today)

### 1. Number of Finished Tasks (Completed Sessions Today)
```sql
SELECT COUNT(*) as finished_tasks
FROM timer_sessions 
WHERE status = 'completed' 
  AND date(started_at) = date('now');
```

### 2. Total Time Spent Today (Including Unfinished Tasks)
```sql
SELECT SUM(COALESCE(actual_duration, 0)) as total_time_seconds
FROM timer_sessions 
WHERE date(started_at) = date('now') 
  AND status IN ('completed', 'stopped');
```

### 3. Total Sessions Started Today
```sql
SELECT COUNT(*) as total_sessions
FROM timer_sessions 
WHERE date(started_at) = date('now');
```

### 4. Completion Percentage
Calculated as: `(finished_tasks / total_sessions) * 100`

## 2-Week Rolling Statistics (for Emoji Indicator)

### Daily Time Spent for Last 14 Days
```sql
SELECT 
    date(started_at) as session_date,
    SUM(COALESCE(actual_duration, 0)) as daily_time_seconds
FROM timer_sessions 
WHERE date(started_at) >= date('now', '-13 days')
  AND date(started_at) <= date('now')
  AND status IN ('completed', 'stopped')
GROUP BY date(started_at)
ORDER BY session_date;
```

### Combined Query for Daily Stats with Percentile Context
```sql
WITH daily_stats AS (
    -- Today's stats
    SELECT 
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as finished_tasks,
        COUNT(*) as total_sessions,
        SUM(CASE WHEN status IN ('completed', 'stopped') THEN COALESCE(actual_duration, 0) ELSE 0 END) as total_time_seconds,
        CASE 
            WHEN COUNT(*) > 0 THEN 
                ROUND(COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*), 1)
            ELSE 0 
        END as completion_percentage
    FROM timer_sessions 
    WHERE date(started_at) = date('now')
),
rolling_stats AS (
    -- Last 14 days daily totals
    SELECT 
        date(started_at) as session_date,
        SUM(COALESCE(actual_duration, 0)) as daily_time_seconds
    FROM timer_sessions 
    WHERE date(started_at) >= date('now', '-13 days')
      AND date(started_at) <= date('now')
      AND status IN ('completed', 'stopped')
    GROUP BY date(started_at)
),
percentiles AS (
    -- Calculate percentiles from rolling window
    SELECT 
        COUNT(*) as days_count,
        -- SQLite doesn't have native percentile functions, so we'll calculate manually
        (SELECT daily_time_seconds FROM rolling_stats ORDER BY daily_time_seconds LIMIT 1 OFFSET (COUNT(*) * 25 / 100)) as p25,
        (SELECT daily_time_seconds FROM rolling_stats ORDER BY daily_time_seconds LIMIT 1 OFFSET (COUNT(*) * 75 / 100)) as p75
    FROM rolling_stats
)
SELECT 
    ds.finished_tasks,
    ds.total_sessions, 
    ds.total_time_seconds,
    ds.completion_percentage,
    p.p25,
    p.p75,
    p.days_count,
    -- Emoji indicator logic
    CASE 
        WHEN ds.total_time_seconds <= COALESCE(p.p25, 0) THEN '😢'
        WHEN ds.total_time_seconds >= COALESCE(p.p75, ds.total_time_seconds) THEN '😄'
        ELSE '😊'
    END as mood_emoji
FROM daily_stats ds, percentiles p;
```

## Simplified Approach for Better SQLite Compatibility

Since SQLite has limitations with percentile calculations, here's a more practical approach:

### Get Today's Stats
```sql
SELECT 
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as finished_tasks,
    COUNT(*) as total_sessions,
    SUM(CASE WHEN status IN ('completed', 'stopped') THEN COALESCE(actual_duration, 0) ELSE 0 END) as total_time_seconds,
    CASE 
        WHEN COUNT(*) > 0 THEN 
            ROUND(COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*), 1)
        ELSE 0 
    END as completion_percentage
FROM timer_sessions 
WHERE date(started_at) = date('now');
```

### Get 14-Day Rolling Data (separate query)
```sql
SELECT 
    date(started_at) as session_date,
    SUM(COALESCE(actual_duration, 0)) as daily_time_seconds
FROM timer_sessions 
WHERE date(started_at) >= date('now', '-13 days')
  AND date(started_at) <= date('now')
  AND status IN ('completed', 'stopped')
GROUP BY date(started_at)
ORDER BY daily_time_seconds;
```

## Emoji Logic (to be implemented in Python)
- Sort the 14-day results by `daily_time_seconds`
- Calculate 25th percentile: `data[len(data) // 4]`
- Calculate 75th percentile: `data[3 * len(data) // 4]`
- Compare today's time with percentiles to determine emoji

## Edge Cases to Handle
1. **No data today**: Return zeros for all metrics
2. **Less than 14 days of data**: Use available data for percentile calculation
3. **No historical data**: Default to neutral emoji (😊)
4. **Timezone considerations**: All dates use SQLite's date() function which works in UTC