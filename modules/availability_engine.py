"""
Availability Engine Module
Calculate availability status and occupancy rates for apartments.
"""
import pandas as pd
from datetime import date
from typing import List, Dict
from modules.period_generator import Period, MonthPeriod


class AvailabilityStatus:
    """Constants for availability status"""
    DISPONIBLE = "Disponible"
    RESERVE = "Réservé"
    SURBOOKING = "Surbooking"


def get_reservations_for_apartment(
    apartment_name: str,
    reservations: pd.DataFrame
) -> pd.DataFrame:
    """
    Get all reservations for a specific apartment.

    Args:
        apartment_name: Name of the apartment
        reservations: DataFrame with all reservations

    Returns:
        Filtered DataFrame with reservations for this apartment
    """
    return reservations[reservations['Nom du logement'] == apartment_name].copy()


def check_overlap(
    res_start: date,
    res_end: date,
    period_start: date,
    period_end: date
) -> bool:
    """
    Check if a reservation overlaps with a period.

    Args:
        res_start: Reservation start date
        res_end: Reservation end date
        period_start: Period start date
        period_end: Period end date

    Returns:
        True if there is overlap, False otherwise
    """
    # Reservations overlap if:
    # reservation starts before period ends AND reservation ends after period starts
    return not (res_end < period_start or res_start > period_end)


def get_availability_status(
    apartment_name: str,
    period: Period,
    reservations: pd.DataFrame
) -> str:
    """
    Determine availability status for an apartment in a given period.

    Args:
        apartment_name: Name of the apartment
        period: Period object to check
        reservations: DataFrame with all reservations

    Returns:
        One of: "Disponible", "Réservé", or "Surbooking"
    """
    # Get reservations for this apartment
    apt_reservations = get_reservations_for_apartment(apartment_name, reservations)

    if apt_reservations.empty:
        return AvailabilityStatus.DISPONIBLE

    # Count overlapping reservations
    date_arrivee = 'Date d\'arrivée'
    date_sortie = 'Date de sortie'

    overlapping_count = 0
    for _, res in apt_reservations.iterrows():
        res_start = res[date_arrivee].date() if hasattr(res[date_arrivee], 'date') else res[date_arrivee]
        res_end = res[date_sortie].date() if hasattr(res[date_sortie], 'date') else res[date_sortie]

        if check_overlap(res_start, res_end, period.start, period.end):
            overlapping_count += 1

    if overlapping_count == 0:
        return AvailabilityStatus.DISPONIBLE
    elif overlapping_count == 1:
        return AvailabilityStatus.RESERVE
    else:
        return AvailabilityStatus.SURBOOKING


def calculate_occupancy_rate(
    apartment_name: str,
    periods: List[Period],
    reservations: pd.DataFrame
) -> float:
    """
    Calculate occupancy rate for an apartment across multiple periods.
    Occupancy rate = (number of reserved periods) / (total periods) * 100

    Args:
        apartment_name: Name of the apartment
        periods: List of Period objects to check
        reservations: DataFrame with all reservations

    Returns:
        Occupancy rate as a percentage (0-100)
    """
    if not periods:
        return 0.0

    reserved_count = 0
    for period in periods:
        status = get_availability_status(apartment_name, period, reservations)
        if status in [AvailabilityStatus.RESERVE, AvailabilityStatus.SURBOOKING]:
            reserved_count += 1

    occupancy_rate = (reserved_count / len(periods)) * 100
    return occupancy_rate


def calculate_monthly_occupancy(
    apartment_name: str,
    month_period: MonthPeriod,
    regular_periods: List[Period],
    reservations: pd.DataFrame
) -> float:
    """
    Calculate occupancy rate for an apartment for a specific month.

    Args:
        apartment_name: Name of the apartment
        month_period: MonthPeriod object
        regular_periods: All regular periods
        reservations: DataFrame with all reservations

    Returns:
        Occupancy rate as a percentage (0-100)
    """
    # Filter periods that belong to this month
    month_periods = [
        p for p in regular_periods
        if p.start.year == month_period.year and p.start.month == month_period.month
    ]

    return calculate_occupancy_rate(apartment_name, month_periods, reservations)


def get_availability_matrix(
    apartments: List[str],
    periods: List[Period],
    reservations: pd.DataFrame
) -> pd.DataFrame:
    """
    Create a matrix of availability statuses for all apartments and periods.

    Args:
        apartments: List of apartment names
        periods: List of Period objects
        reservations: DataFrame with all reservations

    Returns:
        DataFrame with apartments as rows and periods as columns
    """
    data = {}

    for period in periods:
        statuses = []
        for apartment in apartments:
            status = get_availability_status(apartment, period, reservations)
            statuses.append(status)
        data[period.label] = statuses

    df = pd.DataFrame(data, index=apartments)
    return df


def get_occupancy_summary(
    apartments: List[str],
    monthly_periods: List[MonthPeriod],
    regular_periods: List[Period],
    reservations: pd.DataFrame
) -> pd.DataFrame:
    """
    Create a summary of monthly occupancy rates for all apartments.

    Args:
        apartments: List of apartment names
        monthly_periods: List of MonthPeriod objects
        regular_periods: All regular periods
        reservations: DataFrame with all reservations

    Returns:
        DataFrame with apartments as rows and months as columns
    """
    data = {}

    for month in monthly_periods:
        rates = []
        for apartment in apartments:
            rate = calculate_monthly_occupancy(
                apartment, month, regular_periods, reservations
            )
            rates.append(f"{rate:.1f}%")
        data[month.label] = rates

    df = pd.DataFrame(data, index=apartments)
    return df


def get_reservations_in_period(
    period: Period,
    reservations: pd.DataFrame
) -> pd.DataFrame:
    """
    Get all reservations that overlap with a given period.

    Args:
        period: Period to check
        reservations: DataFrame with all reservations

    Returns:
        Filtered DataFrame with overlapping reservations
    """
    date_arrivee = 'Date d\'arrivée'
    date_sortie = 'Date de sortie'

    mask = reservations.apply(
        lambda row: check_overlap(
            row[date_arrivee].date() if hasattr(row[date_arrivee], 'date') else row[date_arrivee],
            row[date_sortie].date() if hasattr(row[date_sortie], 'date') else row[date_sortie],
            period.start,
            period.end
        ),
        axis=1
    )

    return reservations[mask]


if __name__ == "__main__":
    # Test the module
    from pathlib import Path
    from modules.data_loader import load_and_prepare_data
    from modules.period_generator import generate_periods, generate_monthly_periods

    print("\n" + "="*60)
    print("Testing Availability Engine")
    print("="*60 + "\n")

    # Load sample data
    base_path = Path(__file__).parent.parent
    mapping_file = base_path / "Fichier de mapping par appartement.xlsx"
    reservations_file = base_path / "Liste des réservations-22-10-2025-31-10-2025.csv"

    merged, mapping = load_and_prepare_data(str(mapping_file), str(reservations_file))

    # Generate periods
    start = date(2025, 10, 22)
    end = date(2025, 10, 31)
    periods = generate_periods(start, end, period_days=3)
    monthly = generate_monthly_periods(start, end)

    print(f"Testing with {len(periods)} periods from {start} to {end}\n")

    # Test with a few apartments
    test_apartments = merged['Nom du logement'].dropna().unique()[:5]

    for apartment in test_apartments:
        print(f"\nApartment: {apartment}")
        for period in periods[:3]:  # First 3 periods
            status = get_availability_status(apartment, period, merged)
            print(f"  {period.label}: {status}")

        # Monthly occupancy
        if monthly:
            rate = calculate_monthly_occupancy(apartment, monthly[0], periods, merged)
            print(f"  {monthly[0].label}: {rate:.1f}% occupied")

    print("\n" + "="*60 + "\n")
