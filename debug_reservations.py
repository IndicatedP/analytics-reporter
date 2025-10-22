#!/usr/bin/env python3
"""
Debug script to check reservations for a specific apartment and date
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent))

from modules.data_loader import load_and_prepare_data
from modules.period_generator import Period
from modules.availability_engine import get_availability_status, get_reservations_for_apartment

# Load data
base_path = Path(__file__).parent
mapping_file = base_path / "Fichier de mapping par appartement.xlsx"

# Ask user for reservations file
print("\nAvailable reservation files:")
csv_files = list(base_path.glob("Liste*.csv"))
for i, f in enumerate(csv_files, 1):
    print(f"  {i}. {f.name}")

if not csv_files:
    print("No reservation files found!")
    sys.exit(1)

choice = input(f"\nSelect file (1-{len(csv_files)}): ").strip()
reservations_file = csv_files[int(choice) - 1]

print(f"\nLoading: {reservations_file.name}")
merged, mapping = load_and_prepare_data(str(mapping_file), str(reservations_file))

# Get apartment name
print(f"\nFound {merged['Nom du logement'].nunique()} unique apartments")
apartment = input("Enter apartment name (or leave blank for first one): ").strip()

if not apartment:
    apartment = merged['Nom du logement'].dropna().iloc[0]
    print(f"Using: {apartment}")

# Get reservations for this apartment
apt_res = get_reservations_for_apartment(apartment, merged)

print(f"\n{'='*70}")
print(f"Reservations for: {apartment}")
print(f"{'='*70}")

if apt_res.empty:
    print("No reservations found for this apartment")
else:
    print(f"\nFound {len(apt_res)} reservation(s):\n")

    date_col = 'Date d\'arrivée'
    sortie_col = 'Date de sortie'

    for idx, res in apt_res.iterrows():
        checkin = res[date_col]
        checkout = res[sortie_col]
        status = res.get('Statut', 'N/A')

        print(f"  Check-in:  {checkin.strftime('%Y-%m-%d')}")
        print(f"  Check-out: {checkout.strftime('%Y-%m-%d')}")
        print(f"  Status: {status}")
        print(f"  Nights: {(checkout - checkin).days}")
        print()

# Test a specific date
test_date_str = input("Enter a date to check (YYYY-MM-DD): ").strip()
if test_date_str:
    try:
        test_date = date.fromisoformat(test_date_str)
        period = Period(test_date, test_date)

        status = get_availability_status(apartment, period, merged)

        print(f"\n{'='*70}")
        print(f"Availability for {apartment} on {test_date}")
        print(f"{'='*70}")
        print(f"\nStatus: {status}")

        # Show which reservations overlap
        print(f"\nReservations overlapping with {test_date}:")
        found_overlap = False
        for idx, res in apt_res.iterrows():
            checkin = res[date_col].date()
            checkout = res[sortie_col].date()

            # Check overlap
            if not (checkout < test_date or checkin > test_date):
                found_overlap = True
                print(f"  ✓ {checkin} to {checkout}")

        if not found_overlap:
            print("  (none)")

    except ValueError:
        print("Invalid date format")

print()
