"""
Data Loader Module
Load and validate apartment mapping and reservation data.
"""
import pandas as pd
from typing import Tuple
from pathlib import Path


class DataLoaderError(Exception):
    """Custom exception for data loading errors"""
    pass


def load_mapping_file(filepath: str) -> pd.DataFrame:
    """
    Load the apartment mapping file from Excel.

    Args:
        filepath: Path to the Excel file containing apartment mapping

    Returns:
        DataFrame with apartment mapping data

    Raises:
        DataLoaderError: If file cannot be loaded or required columns are missing
    """
    try:
        # Read the Excel file
        excel_file = pd.ExcelFile(filepath)

        # Assuming the data is in the first sheet (or we can make this configurable)
        sheet_name = excel_file.sheet_names[0]
        df = pd.read_excel(filepath, sheet_name=sheet_name)

        # Validate required columns
        required_columns = ['Nom du logement', 'Proprio', 'catégorie']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise DataLoaderError(
                f"Missing required columns in mapping file: {', '.join(missing_columns)}"
            )

        # Clean up apartment names (strip whitespace)
        df['Nom du logement'] = df['Nom du logement'].str.strip()

        print(f"✓ Loaded {len(df)} apartment mappings from {sheet_name}")
        print(f"  Owners: {df['Proprio'].nunique()} unique")
        print(f"  Categories: {df['catégorie'].unique().tolist()}")

        return df

    except FileNotFoundError:
        raise DataLoaderError(f"Mapping file not found: {filepath}")
    except Exception as e:
        raise DataLoaderError(f"Error loading mapping file: {str(e)}")


def load_reservations_file(filepath: str) -> pd.DataFrame:
    """
    Load the reservations file from CSV.

    Args:
        filepath: Path to the CSV file containing reservations

    Returns:
        DataFrame with reservation data

    Raises:
        DataLoaderError: If file cannot be loaded or required columns are missing
    """
    try:
        # Read CSV, skipping the first row which is just the title
        df = pd.read_csv(filepath, skiprows=1, encoding='utf-8')

        # Validate required columns
        required_columns = [
            'Nom du logement',
            'Date d\'arrivée',
            'Date de sortie',
            'Statut',
            'Location avec TVA'
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise DataLoaderError(
                f"Missing required columns in reservations file: {', '.join(missing_columns)}"
            )

        # Clean up apartment names
        df['Nom du logement'] = df['Nom du logement'].str.strip()

        # Parse dates
        df['Date d\'arrivée'] = pd.to_datetime(
            df['Date d\'arrivée'],
            format='%d/%m/%Y',
            errors='coerce'
        )
        df['Date de sortie'] = pd.to_datetime(
            df['Date de sortie'],
            format='%d/%m/%Y',
            errors='coerce'
        )

        # Remove rows with invalid dates
        initial_count = len(df)
        date_cols = ['Date d\'arrivée', 'Date de sortie']
        df = df.dropna(subset=date_cols)
        removed_count = initial_count - len(df)

        if removed_count > 0:
            print(f"  ⚠ Removed {removed_count} reservations with invalid dates")

        # Sort by arrival date
        date_col = 'Date d\'arrivée'
        sortie_col = 'Date de sortie'
        df = df.sort_values(date_col).reset_index(drop=True)

        print(f"✓ Loaded {len(df)} reservations")
        min_date = df[date_col].min().strftime('%Y-%m-%d')
        max_date = df[sortie_col].max().strftime('%Y-%m-%d')
        print(f"  Date range: {min_date} to {max_date}")
        print(f"  Unique apartments: {df['Nom du logement'].nunique()}")
        print(f"  Statuses: {df['Statut'].value_counts().to_dict()}")

        return df

    except FileNotFoundError:
        raise DataLoaderError(f"Reservations file not found: {filepath}")
    except Exception as e:
        raise DataLoaderError(f"Error loading reservations file: {str(e)}")


def merge_data(mapping: pd.DataFrame, reservations: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Merge reservation data with apartment mapping.

    Args:
        mapping: DataFrame with apartment mapping
        reservations: DataFrame with reservations

    Returns:
        Tuple of (merged_reservations, mapping)
        - merged_reservations: Reservations with owner and category info added
        - mapping: Original mapping DataFrame (for reference)

    Raises:
        DataLoaderError: If merge fails
    """
    try:
        # Merge reservations with mapping to get owner and category info
        merged = reservations.merge(
            mapping[['Nom du logement', 'Proprio', 'catégorie', 'commission']],
            on='Nom du logement',
            how='left'
        )

        # Check for reservations without matching apartments
        unmatched = merged[merged['Proprio'].isna()]
        if len(unmatched) > 0:
            unmatched_apartments = unmatched['Nom du logement'].unique()
            print(f"  ⚠ Warning: {len(unmatched)} reservations for {len(unmatched_apartments)} apartments not in mapping:")
            for apt in unmatched_apartments[:5]:  # Show first 5
                print(f"    - {apt}")
            if len(unmatched_apartments) > 5:
                print(f"    ... and {len(unmatched_apartments) - 5} more")

        print(f"✓ Merged {len(merged)} reservations with apartment data")

        return merged, mapping

    except Exception as e:
        raise DataLoaderError(f"Error merging data: {str(e)}")


def validate_data(merged_df: pd.DataFrame, mapping_df: pd.DataFrame) -> bool:
    """
    Validate the merged data for common issues.

    Args:
        merged_df: Merged reservation data
        mapping_df: Apartment mapping data

    Returns:
        True if validation passes, False otherwise
    """
    issues = []

    # Check for missing owners
    missing_owners = merged_df[merged_df['Proprio'].isna()]
    if len(missing_owners) > 0:
        issues.append(f"{len(missing_owners)} reservations without owner information")

    # Check for missing categories
    missing_categories = merged_df[merged_df['catégorie'].isna()]
    if len(missing_categories) > 0:
        issues.append(f"{len(missing_categories)} reservations without category information")

    # Check for invalid date ranges
    date_arrivee = 'Date d\'arrivée'
    date_sortie = 'Date de sortie'
    invalid_dates = merged_df[merged_df[date_arrivee] >= merged_df[date_sortie]]
    if len(invalid_dates) > 0:
        issues.append(f"{len(invalid_dates)} reservations with invalid date ranges")

    if issues:
        print("\n⚠ Data validation warnings:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✓ Data validation passed")
        return True


def load_and_prepare_data(mapping_filepath: str, reservations_filepath: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convenience function to load and prepare all data.

    Args:
        mapping_filepath: Path to mapping Excel file
        reservations_filepath: Path to reservations CSV file

    Returns:
        Tuple of (merged_reservations, mapping)
    """
    print("\n" + "="*60)
    print("Loading Data")
    print("="*60)

    # Load mapping
    mapping = load_mapping_file(mapping_filepath)

    # Load reservations
    reservations = load_reservations_file(reservations_filepath)

    # Merge data
    merged, mapping = merge_data(mapping, reservations)

    # Validate
    validate_data(merged, mapping)

    print("="*60 + "\n")

    return merged, mapping


if __name__ == "__main__":
    # Test the module
    base_path = Path(__file__).parent.parent
    mapping_file = base_path / "Fichier de mapping par appartement.xlsx"
    reservations_file = base_path / "Liste des réservations-22-10-2025-31-10-2025.csv"

    try:
        merged, mapping = load_and_prepare_data(str(mapping_file), str(reservations_file))
        print(f"\nMerged data shape: {merged.shape}")
        print(f"Mapping data shape: {mapping.shape}")
    except DataLoaderError as e:
        print(f"Error: {e}")
