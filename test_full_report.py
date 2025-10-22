#!/usr/bin/env python3
"""
Full integration test - Generate a complete report with all date ranges
"""
from pathlib import Path
from datetime import date
import sys

sys.path.insert(0, str(Path(__file__).parent))

from modules.data_loader import load_and_prepare_data
from modules.period_generator import generate_periods, generate_monthly_periods
from modules.report_generator import create_report


def main():
    print("\n" + "="*70)
    print("FULL INTEGRATION TEST - Analytics Reporter")
    print("="*70)

    # File paths
    base_path = Path(__file__).parent
    mapping_file = base_path / "Fichier de mapping par appartement.xlsx"
    reservations_file = base_path / "Liste des réservations-22-10-2025-31-10-2025.csv"

    # Output file
    output_file = base_path / "Rapport_disponibilite_GENERATED.xlsx"

    print(f"\nInput files:")
    print(f"  Mapping: {mapping_file.name}")
    print(f"  Reservations: {reservations_file.name}")
    print(f"\nOutput file: {output_file.name}")

    # Load data
    print("\n" + "-"*70)
    merged, mapping = load_and_prepare_data(str(mapping_file), str(reservations_file))

    # Get date range from reservations
    date_col = 'Date d\'arrivée'
    sortie_col = 'Date de sortie'
    start_date = merged[date_col].min().date()
    end_date = merged[sortie_col].max().date()

    print(f"\nGenerating report for full date range:")
    print(f"  From: {start_date}")
    print(f"  To: {end_date}")
    print(f"  Duration: {(end_date - start_date).days + 1} days")

    # Generate periods
    print("\n" + "-"*70)
    print("Generating periods...")
    periods = generate_periods(start_date, end_date, period_days=3)
    monthly_periods = generate_monthly_periods(start_date, end_date)

    print(f"  Regular periods: {len(periods)}")
    print(f"  Monthly periods: {len(monthly_periods)}")

    # Create report
    print("\n" + "-"*70)
    print("Creating Excel report...")

    wb = create_report(
        merged,
        mapping,
        periods,
        monthly_periods,
        str(output_file)
    )

    # Summary
    print("\n" + "="*70)
    print("REPORT GENERATION COMPLETE!")
    print("="*70)
    print(f"\nReport details:")
    print(f"  Sheets: {len(wb.sheetnames)}")
    print(f"  Sheet names: {', '.join(wb.sheetnames)}")
    print(f"  Total apartments: {len(mapping)}")
    print(f"  Total reservations: {len(merged)}")
    print(f"  Owners: {', '.join(sorted(mapping['Proprio'].dropna().unique()))}")

    print(f"\n✓ Report saved to: {output_file}")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
