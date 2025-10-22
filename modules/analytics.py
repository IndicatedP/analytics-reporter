"""
Analytics Module
Calculate average prices and other metrics by category.
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from modules.period_generator import Period, MonthPeriod
from modules.availability_engine import get_reservations_in_period


def get_category_reservations(
    category: str,
    period: Period,
    reservations: pd.DataFrame
) -> pd.DataFrame:
    """
    Get reservations for a specific category within a period.

    Args:
        category: Apartment category (e.g., "studio", "1 chambre")
        period: Period to check
        reservations: DataFrame with all reservations (must include 'catégorie' column)

    Returns:
        Filtered DataFrame with reservations for this category in this period
    """
    # Filter by category
    category_res = reservations[reservations['catégorie'] == category]

    # Get reservations that overlap with the period
    period_res = get_reservations_in_period(period, category_res)

    return period_res


def calculate_average_price(
    category: str,
    period: Period,
    reservations: pd.DataFrame,
    price_column: str = 'Location avec TVA'
) -> float:
    """
    Calculate average price for a category in a given period.

    Args:
        category: Apartment category
        period: Period to check
        reservations: DataFrame with all reservations
        price_column: Column name for price (default: 'Location avec TVA')

    Returns:
        Average price, or NaN if no reservations
    """
    category_res = get_category_reservations(category, period, reservations)

    if category_res.empty:
        return np.nan

    # Calculate average price per night
    # Price is for the whole stay, so divide by number of nights
    total_price = 0
    total_nights = 0

    for _, res in category_res.iterrows():
        price = res[price_column]
        nights = res.get('nuits', 1)  # Use 'nuits' column if available

        if pd.notna(price) and pd.notna(nights) and nights > 0:
            total_price += price
            total_nights += nights

    if total_nights == 0:
        return np.nan

    # Return average price per night
    return total_price / total_nights


def calculate_category_averages(
    categories: List[str],
    period: Period,
    reservations: pd.DataFrame,
    price_column: str = 'Location avec TVA'
) -> Dict[str, float]:
    """
    Calculate average prices for all categories in a period.

    Args:
        categories: List of apartment categories
        period: Period to check
        reservations: DataFrame with all reservations
        price_column: Column name for price

    Returns:
        Dictionary mapping category to average price
    """
    averages = {}

    for category in categories:
        avg_price = calculate_average_price(category, period, reservations, price_column)
        averages[category] = avg_price

    return averages


def format_category_label(category: str) -> str:
    """
    Format category name for display in report.

    Args:
        category: Raw category name

    Returns:
        Formatted category label
    """
    # Handle numeric or invalid categories
    if pd.isna(category) or category == 0:
        return "Non catégorisé"

    # Format standard categories
    category_str = str(category).strip()

    if category_str == "studio":
        return "Prix moyen - studio"
    elif "chambre" in category_str:
        return f"Prix moyen - {category_str}"
    else:
        return f"Prix moyen - {category_str}"


def get_unique_categories(reservations: pd.DataFrame, mapping: pd.DataFrame = None) -> List[str]:
    """
    Get list of unique apartment categories from data.

    Args:
        reservations: DataFrame with reservations
        mapping: Optional mapping DataFrame

    Returns:
        Sorted list of unique categories
    """
    categories = set()

    # Get categories from reservations
    if 'catégorie' in reservations.columns:
        cats = reservations['catégorie'].dropna().unique()
        categories.update(cats)

    # Get categories from mapping if provided
    if mapping is not None and 'catégorie' in mapping.columns:
        cats = mapping['catégorie'].dropna().unique()
        categories.update(cats)

    # Remove invalid categories
    categories = [c for c in categories if c != 0 and pd.notna(c)]

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
        categories,
        key=lambda x: category_order.get(str(x).strip(), 999)
    )

    return sorted_categories


def create_price_summary_rows(
    categories: List[str],
    periods: List[Period],
    reservations: pd.DataFrame
) -> pd.DataFrame:
    """
    Create summary rows showing average prices by category for each period.

    Args:
        categories: List of categories
        periods: List of periods
        reservations: DataFrame with all reservations

    Returns:
        DataFrame with categories as rows and periods as columns
    """
    data = {}

    for period in periods:
        averages = calculate_category_averages(categories, period, reservations)
        prices = [averages.get(cat, np.nan) for cat in categories]
        data[period.label] = prices

    # Create index with formatted category labels
    index = [format_category_label(cat) for cat in categories]

    df = pd.DataFrame(data, index=index)
    return df


def create_monthly_price_summary(
    categories: List[str],
    monthly_periods: List[MonthPeriod],
    regular_periods: List[Period],
    reservations: pd.DataFrame
) -> pd.DataFrame:
    """
    Create monthly price summary (average across all periods in the month).

    Args:
        categories: List of categories
        monthly_periods: List of monthly periods
        regular_periods: All regular periods
        reservations: DataFrame with all reservations

    Returns:
        DataFrame with categories as rows and months as columns
    """
    data = {}

    for month in monthly_periods:
        # Get periods in this month
        month_periods = [
            p for p in regular_periods
            if p.start.year == month.year and p.start.month == month.month
        ]

        # Calculate average price for each category across the month
        month_averages = []
        for category in categories:
            # Get all prices for this category in this month
            prices = []
            for period in month_periods:
                avg = calculate_average_price(category, period, reservations)
                if pd.notna(avg):
                    prices.append(avg)

            # Average of the period averages
            if prices:
                month_avg = np.mean(prices)
            else:
                month_avg = np.nan

            month_averages.append(month_avg)

        data[month.label] = month_averages

    # Create index with formatted category labels
    index = [format_category_label(cat) for cat in categories]

    df = pd.DataFrame(data, index=index)
    return df


if __name__ == "__main__":
    # Test the module
    from pathlib import Path
    from modules.data_loader import load_and_prepare_data
    from modules.period_generator import generate_periods, generate_monthly_periods
    from datetime import date

    print("\n" + "="*60)
    print("Testing Analytics Module")
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

    print(f"Testing with {len(periods)} periods\n")

    # Get categories
    categories = get_unique_categories(merged, mapping)
    print(f"Found {len(categories)} categories: {categories}\n")

    # Test average price calculation
    print("Average prices for first period:")
    for cat in categories:
        avg = calculate_average_price(cat, periods[0], merged)
        if pd.notna(avg):
            print(f"  {format_category_label(cat)}: €{avg:.2f}/night")
        else:
            print(f"  {format_category_label(cat)}: No data")

    print("\n" + "="*60 + "\n")
