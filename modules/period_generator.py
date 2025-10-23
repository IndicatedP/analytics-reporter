"""
Period Generator Module
Generate date range periods and monthly summaries for availability reports.
"""
from datetime import datetime, date, timedelta
from typing import List, Tuple, Union
from calendar import monthrange
import pandas as pd


class Period:
    """Represents a date period for availability reporting"""

    def __init__(self, start: date, end: date, label: str = None):
        self.start = start
        self.end = end
        self.label = label or self.format_label(start, end)

    @staticmethod
    def format_label(start: date, end: date) -> str:
        """Format period label as DD/MM - DD/MM"""
        return f"{start.strftime('%d/%m')} - {end.strftime('%d/%m')}"

    def __repr__(self):
        return f"Period({self.label}: {self.start} to {self.end})"

    def overlaps_with(self, start: date, end: date) -> bool:
        """Check if this period overlaps with a date range"""
        return not (end < self.start or start > self.end)

    def contains_date(self, check_date: date) -> bool:
        """Check if this period contains a specific date"""
        return self.start <= check_date <= self.end


class MonthPeriod:
    """Represents a monthly summary period"""

    def __init__(self, year: int, month: int):
        self.year = year
        self.month = month
        self.start = date(year, month, 1)
        # Get last day of month
        last_day = monthrange(year, month)[1]
        self.end = date(year, month, last_day)
        self.label = self.format_label()

    def format_label(self) -> str:
        """Format monthly label as 'Month YYYY - Mois complet'"""
        month_names_en = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return f"{month_names_en[self.month - 1]} {self.year} - Mois complet"

    def __repr__(self):
        return f"MonthPeriod({self.label})"

    def get_periods(self) -> Tuple[date, date]:
        """Get start and end dates"""
        return self.start, self.end


def generate_periods(
    start_date: date,
    end_date: date,
    period_days: int = 3
) -> List[Period]:
    """
    Generate regular periods (e.g., 3-4 day periods) within a date range.

    Args:
        start_date: Start date of the range
        end_date: End date of the range
        period_days: Number of days per period (default 3)

    Returns:
        List of Period objects
    """
    if start_date > end_date:
        raise ValueError("Start date must be before or equal to end date")

    periods = []
    current = start_date

    while current <= end_date:
        # Calculate period end (either period_days later or end_date)
        period_end = min(current + timedelta(days=period_days - 1), end_date)

        # Create period
        period = Period(current, period_end)
        periods.append(period)

        # Move to next period
        current = period_end + timedelta(days=1)

    return periods


def generate_monthly_periods(start_date: date, end_date: date) -> List[MonthPeriod]:
    """
    Generate monthly summary periods within a date range.

    Args:
        start_date: Start date of the range
        end_date: End date of the range

    Returns:
        List of MonthPeriod objects
    """
    if start_date > end_date:
        raise ValueError("Start date must be before or equal to end date")

    months = []
    current_year = start_date.year
    current_month = start_date.month

    end_year = end_date.year
    end_month = end_date.month

    while (current_year, current_month) <= (end_year, end_month):
        month_period = MonthPeriod(current_year, current_month)
        months.append(month_period)

        # Move to next month
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1

    return months


def generate_weekday_weekend_periods(
    start_date: date,
    end_date: date
) -> List[Period]:
    """
    Generate periods split by weekday (Mon-Thu) and weekend (Fri-Sun).

    Args:
        start_date: Start date of the range
        end_date: End date of the range

    Returns:
        List of Period objects (alternating weekday and weekend periods)
    """
    if start_date > end_date:
        raise ValueError("Start date must be before or equal to end date")

    periods = []
    current = start_date

    while current <= end_date:
        weekday = current.weekday()  # 0=Monday, 6=Sunday

        if weekday <= 3:  # Monday-Thursday
            # Weekday period: Monday to Thursday
            # Find the next Thursday or end_date
            days_until_thursday = 3 - weekday
            period_end = min(current + timedelta(days=days_until_thursday), end_date)

            period = Period(current, period_end)
            periods.append(period)

            # Move to next Friday
            current = period_end + timedelta(days=1)

        else:  # Friday-Sunday
            # Weekend period: Friday to Sunday
            # Find the next Sunday or end_date
            days_until_sunday = 6 - weekday
            period_end = min(current + timedelta(days=days_until_sunday), end_date)

            period = Period(current, period_end)
            periods.append(period)

            # Move to next Monday
            current = period_end + timedelta(days=1)

    return periods


def generate_all_periods(
    start_date: date,
    end_date: date,
    period_days: int = 3
) -> Tuple[List[Period], List[MonthPeriod]]:
    """
    Generate both regular periods and monthly summaries.

    Args:
        start_date: Start date of the range
        end_date: End date of the range
        period_days: Number of days per period (default 3)

    Returns:
        Tuple of (regular_periods, monthly_periods)
    """
    regular_periods = generate_periods(start_date, end_date, period_days)
    monthly_periods = generate_monthly_periods(start_date, end_date)

    return regular_periods, monthly_periods


def interleave_periods_with_months(
    periods: List[Period],
    monthly_periods: List[MonthPeriod]
) -> List[Tuple[str, Union[Period, MonthPeriod]]]:
    """
    Interleave regular periods with monthly summaries.
    For the report, we show periods for each month, then the monthly summary.

    Args:
        periods: List of regular periods
        monthly_periods: List of monthly periods

    Returns:
        List of tuples (type, period) where type is 'period' or 'month'
    """
    result = []
    month_index = 0

    for period in periods:
        # Check if we've moved to a new month
        if month_index < len(monthly_periods):
            current_month = monthly_periods[month_index]

            # Check if this period starts in a different month than where we are
            if period.start.month != current_month.month or period.start.year != current_month.year:
                # We've moved past this month, add the monthly summary
                result.append(('month', current_month))
                month_index += 1

        # Add the regular period
        result.append(('period', period))

    # Add any remaining monthly summaries
    while month_index < len(monthly_periods):
        result.append(('month', monthly_periods[month_index]))
        month_index += 1

    return result


def group_periods_by_month(
    periods: List[Period],
    monthly_periods: List[MonthPeriod]
) -> List[Tuple[MonthPeriod, List[Period]]]:
    """
    Group regular periods by their corresponding month.

    Args:
        periods: List of regular periods
        monthly_periods: List of monthly periods

    Returns:
        List of tuples (MonthPeriod, [Period]) for each month
    """
    result = []

    for month_period in monthly_periods:
        # Find all periods that fall within this month
        month_periods = []
        for period in periods:
            # A period belongs to a month if it starts in that month
            if period.start.year == month_period.year and period.start.month == month_period.month:
                month_periods.append(period)

        result.append((month_period, month_periods))

    return result


if __name__ == "__main__":
    # Test the module
    print("\n" + "="*60)
    print("Testing Period Generator")
    print("="*60 + "\n")

    # Test with sample dates
    start = date(2025, 10, 22)
    end = date(2025, 12, 31)

    print(f"Date range: {start} to {end}")
    print()

    # Generate periods
    regular_periods = generate_periods(start, end, period_days=3)
    print(f"Generated {len(regular_periods)} regular periods:")
    for i, p in enumerate(regular_periods[:10], 1):  # Show first 10
        days = (p.end - p.start).days + 1
        print(f"  {i}. {p.label} ({days} days)")
    if len(regular_periods) > 10:
        print(f"  ... and {len(regular_periods) - 10} more")
    print()

    # Generate monthly periods
    monthly = generate_monthly_periods(start, end)
    print(f"Generated {len(monthly)} monthly periods:")
    for i, m in enumerate(monthly, 1):
        print(f"  {i}. {m.label}")
    print()

    # Group by month
    grouped = group_periods_by_month(regular_periods, monthly)
    print("Periods grouped by month:")
    for month_period, month_periods in grouped:
        print(f"\n  {month_period.label}:")
        print(f"    {len(month_periods)} periods")
        for p in month_periods[:3]:  # Show first 3
            print(f"    - {p.label}")
        if len(month_periods) > 3:
            print(f"    - ... and {len(month_periods) - 3} more")

    print("\n" + "="*60 + "\n")
