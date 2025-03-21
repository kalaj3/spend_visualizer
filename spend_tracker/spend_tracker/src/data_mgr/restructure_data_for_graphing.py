import calendar
from datetime import datetime, timedelta

from spend_tracker.src.util.classes import (
    CategoryPeriodData,
    CC_Transaction,
    GraphableData,
    PeriodData,
)


def get_date_range(transactions: list[CC_Transaction]):
    """Get the earliest and latest dates from the transactions"""
    if not transactions:
        return datetime.now(), datetime.now()

    dates = [tx.date for tx in transactions]
    return min(dates), max(dates)


def create_month_periods(start_date: datetime, end_date: datetime) -> list[PeriodData]:
    """Create standardized month periods from start date to end date"""
    periods = []

    # Normalize to the start of the month
    current_start = datetime(start_date.year, start_date.month, 1)

    while current_start <= end_date:
        # Get the last day of the current month
        last_day = calendar.monthrange(current_start.year, current_start.month)[1]
        current_end = datetime(
            current_start.year, current_start.month, last_day, 23, 59, 59
        )

        periods.append(PeriodData(current_start, current_end))

        # Move to first day of next month
        if current_start.month == 12:
            current_start = datetime(current_start.year + 1, 1, 1)
        else:
            current_start = datetime(current_start.year, current_start.month + 1, 1)

    return periods


def create_week_periods(start_date: datetime, end_date: datetime) -> list[PeriodData]:
    """Create standardized week periods from start date to end date"""
    periods = []

    # Normalize to the start of the week (Monday)
    days_since_monday = start_date.weekday()
    current_start = start_date - timedelta(days=days_since_monday)
    current_start = datetime(current_start.year, current_start.month, current_start.day)

    while current_start <= end_date:
        current_end = current_start + timedelta(
            days=6, hours=23, minutes=59, seconds=59
        )
        periods.append(PeriodData(current_start, current_end))

        # Move to next Monday
        current_start = current_start + timedelta(days=7)

    return periods


def categorize_transactions(
    periods: list[PeriodData], transactions: list[CC_Transaction]
) -> None:
    """Categorize transactions into the appropriate periods and categories"""
    for transaction in transactions:
        # Find the period this transaction belongs to
        for period in periods:
            if period.start_date <= transaction.date <= period.end_date:
                # Ensure the category exists in this period
                if transaction.category not in period.categories:
                    period.categories[transaction.category] = CategoryPeriodData()

                # Add transaction to the appropriate category
                period.categories[transaction.category].add_transaction(transaction)
                break


def restructure_for_graphing(transactions: list[CC_Transaction]) -> GraphableData:
    """Convert raw transactions into a format suitable for graphing"""
    if not transactions:
        return GraphableData()

    # Get the full date range of the transactions
    start_date, end_date = get_date_range(transactions)

    # Create standardized time periods
    graphable_data = GraphableData()
    graphable_data.months = create_month_periods(start_date, end_date)
    graphable_data.weeks = create_week_periods(start_date, end_date)

    # Categorize transactions into periods
    categorize_transactions(graphable_data.months, transactions)
    categorize_transactions(graphable_data.weeks, transactions)

    return graphable_data
