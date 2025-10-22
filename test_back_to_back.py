#!/usr/bin/env python3
"""
Test back-to-back reservations (checkout and checkin on same day)
"""
import pandas as pd
from datetime import date
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.period_generator import Period
from modules.availability_engine import get_availability_status

print("\n" + "="*70)
print("Testing: Back-to-back reservations (checkout = checkin)")
print("="*70)

# Two reservations:
# A: Check-in Oct 21, Check-out Oct 25 (occupies 21, 22, 23, 24)
# B: Check-in Oct 25, Check-out Oct 28 (occupies 25, 26, 27)
fake_reservations = pd.DataFrame({
    'Nom du logement': ['Test Apartment', 'Test Apartment'],
    'Date d\'arrivée': [pd.Timestamp('2025-10-21'), pd.Timestamp('2025-10-25')],
    'Date de sortie': [pd.Timestamp('2025-10-25'), pd.Timestamp('2025-10-28')],
    'Statut': ['Confirmée', 'Confirmée'],
    'Location avec TVA': [300, 250],
    'nuits': [4, 3]
})

print("\nReservation A:")
print("  Check-in: 2025-10-21, Check-out: 2025-10-25")
print("  (Guest A occupies: Oct 21, 22, 23, 24)")

print("\nReservation B:")
print("  Check-in: 2025-10-25, Check-out: 2025-10-28")
print("  (Guest B occupies: Oct 25, 26, 27)")

print("\n" + "-"*70)
print("Testing each day:")
print("-"*70)

test_dates = [
    (date(2025, 10, 23), "Réservé", "Guest A"),
    (date(2025, 10, 24), "Réservé", "Guest A"),
    (date(2025, 10, 25), "Réservé", "Guest B (A checked out, B checked in)"),
    (date(2025, 10, 26), "Réservé", "Guest B"),
    (date(2025, 10, 27), "Réservé", "Guest B"),
    (date(2025, 10, 28), "Disponible", "Guest B checked out"),
]

all_passed = True
for test_date, expected, description in test_dates:
    period = Period(test_date, test_date)
    status = get_availability_status('Test Apartment', period, fake_reservations)

    match = "✓" if status == expected else "✗"
    if status != expected:
        all_passed = False

    print(f"{match} {test_date}: {status:12} (expected: {expected:12}) - {description}")

print("\n" + "="*70)
if all_passed:
    print("✓ PERFECT! Back-to-back reservations work correctly")
    print("  Oct 25 shows 'Réservé' (only Guest B, no overbooking)")
else:
    print("✗ FAILED! There's still an issue")
print("="*70 + "\n")
