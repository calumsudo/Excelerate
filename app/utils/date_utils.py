# app/utils/date_utils.py

from datetime import datetime, timedelta
from typing import List


def get_most_recent_friday(from_date: datetime = None) -> datetime:
    """Get the most recent Friday from a given date."""
    if from_date is None:
        from_date = datetime.now()

    # Get days since most recent Friday (Friday is 4 in Python's datetime)
    # If today is Friday, days_since_friday will be 0
    days_since_friday = (from_date.weekday() - 4) % 7

    # Subtract days to get to most recent Friday
    friday = from_date - timedelta(days=days_since_friday)

    # Set time to midnight
    return friday.replace(hour=0, minute=0, second=0, microsecond=0)


def get_available_fridays(num_weeks: int = 52) -> List[datetime]:
    """Get a list of previous Fridays for the dropdown."""
    fridays = []
    current = get_most_recent_friday()

    for _ in range(num_weeks):
        fridays.append(current)
        current = current - timedelta(days=7)

    return fridays


def format_date_for_display(date: datetime) -> str:
    """Format date for display in the UI."""
    return date.strftime("%B %d, %Y")


def format_date_for_file(date: datetime) -> str:
    """Format date for use in filenames."""
    return date.strftime("%Y%m%d")
