"""
demo_occupancy.py - Quick demo of the occupancy engine
======================================================
Run from the project root:
    python demo_occupancy.py

Shows a full worked example: a 6-stop route, 4 ticket groups,
printed occupancy table and crowd bands per segment.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "backend"))

import pandas as pd
from occupancy import compute_segment_occupancy, IncrementalOccupancy

# ── Sample trip ──────────────────────────────────────────────────────────────
# Route: 6 stops (stop 1 … stop 6), 5 segments
# Bus capacity: 50 passengers
# Ticket groups:
#   Group A — 15 pax board at stop 1, alight at stop 4
#   Group B — 20 pax board at stop 2, alight at stop 6
#   Group C — 10 pax board at stop 3, alight at stop 5
#   Group D —  5 pax board at stop 5, alight at stop 6

tickets = pd.DataFrame({
    "boarding_stop_seq": [1, 2, 3, 5],
    "dest_stop_seq":     [4, 6, 5, 6],
    "passenger_count":   [15, 20, 10, 5],
})

CAPACITY  = 50
NUM_STOPS = 6

print("=" * 60)
print("BUS CROWD PREDICTION - Occupancy Engine Demo")
print("=" * 60)
print(f"\nRoute: {NUM_STOPS} stops | Capacity: {CAPACITY}")
print("\nTickets:")
print(tickets.to_string(index=False))

# ── Batch computation ────────────────────────────────────────────────────────
states = compute_segment_occupancy(tickets, num_stops=NUM_STOPS, capacity=CAPACITY)

print("\n-- Segment-by-segment occupancy (batch) --")
print(f"{'Seg':>4} {'Onboard':>8} {'Seats Free':>11} {'Load Ratio':>11} {'Band':<22}")
print("-" * 60)
for s in states:
    bar = "#" * int(s.load_ratio * 20)
    print(
        f"{s.segment:>4} {s.onboard:>8} {s.seats_free:>11} "
        f"{s.load_ratio:>11.2%}  {s.band.value:<22}  {bar}"
    )

# ── Incremental (streaming) computation ─────────────────────────────────────
print("\n-- Streaming tracker (same tickets ingested one-by-one) --")
tracker = IncrementalOccupancy(capacity=CAPACITY)
for _, row in tickets.iterrows():
    tracker.ingest_ticket(
        int(row.boarding_stop_seq),
        int(row.dest_stop_seq),
        int(row.passenger_count),
    )

print(f"Total tickets ingested: {tracker.ticket_count}")
seg3 = tracker.state_at_segment(3)
print(f"State at segment 3 -> onboard={seg3.onboard}, "
      f"seats_free={seg3.seats_free}, band='{seg3.band.value}'")

# ── Verify batch == streaming ────────────────────────────────────────────────
stream_states = tracker.snapshot(num_stops=NUM_STOPS)
all_match = all(b.onboard == s.onboard for b, s in zip(states, stream_states))
print(f"\nBatch == Streaming: {'MATCH' if all_match else 'MISMATCH'}")
print("=" * 60)
