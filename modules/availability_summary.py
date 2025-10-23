"""
Availability Summary Module
Calculate availability summaries by apartment category for each period.
"""
import pandas as pd
from typing import Dict, List
from modules.period_generator import Period
from modules.availability_engine import get_availability_status, AvailabilityStatus


def calculate_availability_summary(
    apartments: pd.DataFrame,
    period: Period,
    reservations: pd.DataFrame
) -> Dict[str, Dict[str, int]]:
    """
    Calculate availability summary by category for a period.

    Args:
        apartments: DataFrame with apartments and their categories
        period: Period to check
        reservations: DataFrame with all reservations

    Returns:
        Dict mapping category to counts: {category: {'disponible': X, 'reserve': Y, 'surbooking': Z}}
    """
    summary = {}

    # Get unique categories
    categories = apartments['catégorie'].dropna().unique()

    for category in categories:
        if category == 0 or pd.isna(category):
            continue

        # Get all apartments of this category
        category_apartments = apartments[apartments['catégorie'] == category]

        counts = {
            'disponible': 0,
            'reserve': 0,
            'surbooking': 0,
            'total': len(category_apartments)
        }

        # Check status for each apartment
        for _, apt in category_apartments.iterrows():
            apt_name = apt['Nom du logement']
            status = get_availability_status(apt_name, period, reservations)

            if status == AvailabilityStatus.DISPONIBLE:
                counts['disponible'] += 1
            elif status == AvailabilityStatus.RESERVE:
                counts['reserve'] += 1
            elif status == AvailabilityStatus.SURBOOKING:
                counts['surbooking'] += 1

        summary[str(category)] = counts

    return summary


def format_availability_summary(summary: Dict[str, Dict[str, int]]) -> str:
    """
    Format availability summary as a readable string.

    Args:
        summary: Summary dict from calculate_availability_summary

    Returns:
        Formatted string
    """
    lines = []

    # Sort categories
    category_order = {
        'studio': 1,
        '1 chambre': 2,
        '2 chambres': 3,
        '3 chambres': 4,
        '4 chambres': 5,
        '5 chambres': 6,
        '6 chambres': 7
    }

    sorted_categories = sorted(
        summary.keys(),
        key=lambda x: category_order.get(x, 999)
    )

    for category in sorted_categories:
        counts = summary[category]
        line = f"{category}: {counts['disponible']}D / {counts['reserve']}R"
        if counts['surbooking'] > 0:
            line += f" / {counts['surbooking']}S"
        lines.append(line)

    return " | ".join(lines) if lines else "No data"


def create_summary_rows_for_report(
    apartments: pd.DataFrame,
    periods: List[Period],
    reservations: pd.DataFrame
) -> pd.DataFrame:
    """
    Create summary rows for the report showing availability counts by category.

    Args:
        apartments: DataFrame with apartments
        periods: List of periods
        reservations: DataFrame with reservations

    Returns:
        DataFrame with category summary rows
    """
    categories = sorted(apartments['catégorie'].dropna().unique())
    categories = [c for c in categories if c != 0]

    # Create rows for each category showing counts
    data = {}

    for period in periods:
        summary = calculate_availability_summary(apartments, period, reservations)

        # Create column data for this period
        col_data = []
        for category in categories:
            cat_str = str(category)
            if cat_str in summary:
                counts = summary[cat_str]
                # Format: "5D / 3R / 1S"
                value = f"{counts['disponible']}D/{counts['reserve']}R"
                if counts['surbooking'] > 0:
                    value += f"/{counts['surbooking']}S"
                col_data.append(value)
            else:
                col_data.append("")

        data[period.label] = col_data

    # Create DataFrame
    index = [f"Disponibilité - {cat}" for cat in categories]
    df = pd.DataFrame(data, index=index)

    return df


if __name__ == "__main__":
    # Test the module
    from pathlib import Path
    from modules.data_loader import load_and_prepare_data
    from modules.period_generator import generate_periods
    from datetime import date
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))

    print("\n" + "="*70)
    print("Testing Availability Summary")
    print("="*70)

    # Load data
    base_path = Path(__file__).parent.parent
    mapping_file = base_path / "Fichier de mapping par appartement.xlsx"
    reservations_file = base_path / "Liste des réservations-22-10-2025-31-10-2025.csv"

    merged, mapping = load_and_prepare_data(str(mapping_file), str(reservations_file))

    # Generate periods
    start = date(2025, 10, 22)
    end = date(2025, 10, 31)
    periods = generate_periods(start, end, period_days=3)

    print(f"\nTesting with {len(periods)} periods\n")

    # Test summary for first period
    period = periods[0]
    print(f"Period: {period.label}")
    summary = calculate_availability_summary(mapping, period, merged)

    print("\nAvailability by category:")
    for category, counts in summary.items():
        print(f"  {category}:")
        print(f"    Disponible: {counts['disponible']}")
        print(f"    Réservé: {counts['reserve']}")
        print(f"    Surbooking: {counts['surbooking']}")
        print(f"    Total: {counts['total']}")

    print("\nFormatted:")
    print(f"  {format_availability_summary(summary)}")

    print("\n" + "="*70 + "\n")
