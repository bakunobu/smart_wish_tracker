# grid_manager.py
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DATA_DIR, "contributions.db")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Color scale: from light green to dark green
COLORS = [
    "#e6ffed",  # No activity
    "#c3e6cd",
    "#9fd8b8",
    "#7bc9a3",
    "#56bb8e",
    "#3ca77d",
    "#2f946c",
    "#1f805c",
    "#106c4c",
    "#035c3b"   # Highest activity
]
MAX_COLOR_LEVEL = len(COLORS) - 1


def init_db():
    """Initialize the contributions database."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contributions (
                date TEXT PRIMARY KEY,
                value REAL DEFAULT 0.0
            )
        """)
    ensure_today_exists()


def ensure_today_exists():
    """Ensure today's date is in the DB (auto-shift)."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM contributions WHERE date = ?", (today_str,))
        if cursor.fetchone() is None:
            conn.execute("INSERT INTO contributions (date, value) VALUES (?, 0.0)", (today_str,))


def add_contribution(date_str: str, amount: float):
    """
    Add or update contribution for a given date.
    
    Args:
        date_str: Date in 'YYYY-MM-DD' format
        amount: Numeric value (e.g., deposit, interest earned)
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO contributions (date, value)
            VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET value = excluded.value
        """, (date_str, amount))


def get_min_max_value() -> Tuple[float, float]:
    """Get min/max values for scaling intensity."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(value), MAX(value) FROM contributions")
        row = cursor.fetchone()
        mn, mx = row
        return (mn or 0.0, mx or 1.0)


def value_to_color(value: float) -> str:
    """Map a numeric value to a color."""
    if value == 0:
        return COLORS[0]
    _, max_val = get_min_max_value()
    if max_val == 0:
        return COLORS[0]
    level = int((value / max_val) * MAX_COLOR_LEVEL)
    level = max(1, min(MAX_COLOR_LEVEL, level))  # Clamp between 1–9
    return COLORS[level]


def get_recent_contributions(days: int = 35) -> List[Tuple[str, float, str]]:
    """
    Get last N days of contributions with colors.
    
    Returns:
        List of (date, value, hex_color)
    """
    # Generate all dates in the requested range
    today = datetime.now()
    start_date = today - timedelta(days=days)
    
    # Create a dictionary with all dates in the range initialized to 0
    date_values = {}
    current_date = start_date
    while current_date <= today:
        date_str = current_date.strftime("%Y-%m-%d")
        date_values[date_str] = 0.0  # Default to 0 if no record
        current_date += timedelta(days=1)
    
    # Get actual values from the database
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, value FROM contributions
            WHERE date >= ?
            ORDER BY date
        """, (start_date.strftime("%Y-%m-%d"),))
        rows = cursor.fetchall()
    
    # Update the dictionary with actual values from the database
    for date_str, val in rows:
        date_values[date_str] = val or 0.0
    
    # Convert to the required format
    result = []
    for date_str in sorted(date_values.keys()):
        val = date_values[date_str]
        color = value_to_color(val)
        result.append((date_str, val, color))

    return result


def generate_weekly_grid_html(data: List[Tuple[str, float, str]]) -> str:
    """
    Generate an HTML table representing a weekly grid (last ~5 weeks).
    """
    # Group by week
    weeks = {}
    for date_str, value, color in data:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        week_key = d.strftime("%Y-W%U")
        weekday = d.weekday()  # 0=Mon → 6=Sun
        if week_key not in weeks:
            weeks[week_key] = [""] * 7
        weeks[week_key][weekday] = f'<div style="background:{color}; width:20px; height:20px; border:1px solid #ddd;"></div>'

    # Build HTML
    html = """
    <style>
        .grid { display: inline-block; font-family: monospace; }
        .week { margin-bottom: 2px; }
        .label { width: 30px; text-align: right; font-size: 12px; color: #555; }
    </style>
    <div class="grid">
    """

    sorted_weeks = sorted(weeks.keys())
    for week_key in sorted_weeks:
        days = weeks[week_key]
        html += '<div class="week">'
        for i, cell in enumerate(days):
            html += cell if cell else '<div style="width:20px; height:20px; display:inline-block;"></div>'
        html += '</div><br>'

    html += "</div>"
    return html