#!/usr/bin/env python3
"""
Test to verify bug: Reservations that start before report period are ignored
"""
import pandas as pd
from datetime import date
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.period_generator import Period, generate_periods
from modules.availability_engine import get_availability_status

print("\n" + "="*70)
print("Testing: Reservations that start before report period")
print("="*70)

# Create a fake reservation that starts BEFORE the report period
# Check-in: Oct 21, Check-out: Oct 25
fake_reservation = pd.DataFrame({
    'Nom du logement': ['Test Apartment'],
    'Date d\'arrivée': [pd.Timestamp('2025-10-21')],
    'Date de sortie': [pd.Timestamp('2025-10-25')],
    'Statut': ['Confirmée'],
    'Location avec TVA': [300],
    'nuits': [4]
})

print("\nTest Reservation:")
print(f"  Apartment: Test Apartment")
print(f"  Check-in: 2025-10-21")
print(f"  Check-out: 2025-10-25")
print(f"  (Guest occupies: Oct 21, 22, 23, 24)")

# Report period starts AFTER check-in: Oct 22 - Oct 31
report_start = date(2025, 10, 22)
report_end = date(2025, 10, 31)

print(f"\nReport Period: {report_start} to {report_end}")

# Generate periods
periods = generate_periods(report_start, report_end, period_days=1)

print(f"\nTesting availability for each day in report period:")
print("-" * 70)

for period in periods[:10]:  # Test first 10 days
    status = get_availability_status('Test Apartment', period, fake_reservation)

    # What SHOULD the status be?
    day = period.start
    if day >= date(2025, 10, 21) and day < date(2025, 10, 25):
        expected = "Réservé"
    else:
        expected = "Disponible"

    match = "✓" if status == expected else "✗"

    print(f"{match} {period.start}: {status:12} (expected: {expected})")

    if status != expected:
        print(f"   ^^^ BUG FOUND! Reservation is being ignored!")

print("\n" + "="*70 + "\n")
