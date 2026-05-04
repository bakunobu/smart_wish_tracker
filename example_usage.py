# example_usage.py

from grid_manager import (
    init_db,
    add_contribution,
    ensure_today_exists,
    get_recent_contributions,
    generate_weekly_grid_html,
)


def main():
    # Initialize DB and ensure today is included
    init_db()
    ensure_today_exists()

    # Add sample contributions (date, amount)
    sample_data = [
        ("2025-04-01", 100.0),
        ("2025-04-02", 50.0),
        ("2025-04-03", 200.0),  # High value → darker color
        ("2025-04-04", 0.0),
        ("2025-04-05", 75.0),
    ]

    for date_str, amount in sample_data:
        add_contribution(date_str, amount)

    # Fetch recent data and generate HTML grid
    data = get_recent_contributions(days=35)
    html = generate_weekly_grid_html(data)

    # Save to file
    with open("contribution_grid.html", "w", encoding="utf-8") as f:
        f.write(f"<h3>🏦 Self Banksta Contribution Grid (Last 35 Days)</h3>{html}")

    print("✅ Grid generated and saved to contribution_grid.html")


if __name__ == "__main__":
    main()
