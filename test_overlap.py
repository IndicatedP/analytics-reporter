#!/usr/bin/env python3
"""
Test overlap detection for reservations that start before the report period
"""
from datetime import date
from modules.period_generator import Period
from modules.availability_engine import check_overlap

print("\n" + "="*70)
print("Testing Overlap Detection")
print("="*70)

# Test case: Reservation starts Oct 21, ends Oct 25
# Report period: Oct 22 - Oct 24
res_start = date(2025, 10, 21)
res_end = date(2025, 10, 25)

period = Period(date(2025, 10, 22), date(2025, 10, 24))

print(f"\nReservation: {res_start} to {res_end}")
print(f"Period: {period.start} to {period.end}")

overlaps = check_overlap(res_start, res_end, period.start, period.end)

print(f"\nOverlaps? {overlaps}")
print(f"Expected: True (reservation should be detected)")

if overlaps:
    print("✓ PASS: Overlap correctly detected")
else:
    print("✗ FAIL: Overlap NOT detected - THIS IS THE BUG")

# Additional test cases
print("\n" + "-"*70)
print("Additional Test Cases:")
print("-"*70)

test_cases = [
    # (res_start, res_end, period_start, period_end, expected)
    (date(2025, 10, 20), date(2025, 10, 23), date(2025, 10, 22), date(2025, 10, 24), True, "Starts before, ends during"),
    (date(2025, 10, 23), date(2025, 10, 26), date(2025, 10, 22), date(2025, 10, 24), True, "Starts during, ends after"),
    (date(2025, 10, 20), date(2025, 10, 26), date(2025, 10, 22), date(2025, 10, 24), True, "Completely overlaps"),
    (date(2025, 10, 18), date(2025, 10, 21), date(2025, 10, 22), date(2025, 10, 24), False, "Ends before period"),
    (date(2025, 10, 25), date(2025, 10, 27), date(2025, 10, 22), date(2025, 10, 24), False, "Starts after period"),
]

all_passed = True
for res_s, res_e, per_s, per_e, expected, description in test_cases:
    result = check_overlap(res_s, res_e, per_s, per_e)
    status = "✓" if result == expected else "✗"
    if result != expected:
        all_passed = False
    print(f"{status} {description}: {result} (expected {expected})")

print("\n" + "="*70)
if all_passed and overlaps:
    print("ALL TESTS PASSED - Overlap detection is working correctly")
    print("\nIf the app still shows availability incorrectly, the issue might be:")
    print("1. Date format/parsing in the uploaded CSV")
    print("2. Timezone issues (datetime vs date)")
    print("3. Checkout date interpretation (inclusive vs exclusive)")
else:
    print("TESTS FAILED - There is a bug in overlap detection")
print("="*70 + "\n")
