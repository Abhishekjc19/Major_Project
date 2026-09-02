"""
simulate_tickets.py - Realistic ticket stream generator
=======================================================
Reads the synthetic GTFS (or a real GTFS feed) and generates a
ticket record for every passenger boarding on every trip over a
configurable number of days.

Demand model
------------
- Base demand per trip:  Poisson-sampled around a route-level mean.
- Stop popularity:       Higher near city centre and airport (stops 1,2,3 and 13,14,15).
- Time-of-day peaks:     Morning 7-9 h and evening 17-19 h have 2x demand.
- Day-of-week:           Weekdays 1.0x, Saturday 0.8x, Sunday 0.55x.
- Noise:                 Uniform ±20 % jitter per origin-destination pair.
- Over-capacity:         Allowed up to 130 % at peak (mild crush load).

Output
------
  datasets/tickets.csv   (canonical ticket schema)

Run:
    python datasets/simulate_tickets.py
"""

import pathlib, random
import numpy as np
import pandas as pd
from datetime import date, timedelta

# ── Config ───────────────────────────────────────────────────────────────────
SEED            = 42
NUM_DAYS        = 21        # 3 weeks
START_DATE      = date(2026, 1, 5)   # Monday
GTFS_DIR        = pathlib.Path(__file__).parent / "gtfs_raw"
OUT_PATH        = pathlib.Path(__file__).parent / "tickets.csv"
BUS_CAPACITY    = 30        # smaller bus so same demand creates crush loads
MAX_LOAD_RATIO  = 1.5       # allow up to 150 % at crush-peak
BASE_DEMAND_PER_TRIP = 120  # high enough that peak trips fill and exceed capacity

rng = np.random.default_rng(SEED)
random.seed(SEED)

# ── Load GTFS ────────────────────────────────────────────────────────────────
stops_df    = pd.read_csv(GTFS_DIR / "stops.csv")
trips_df    = pd.read_csv(GTFS_DIR / "trips.csv")
st_df       = pd.read_csv(GTFS_DIR / "stop_times.csv")

NUM_STOPS   = len(stops_df)
STOP_SEQS   = stops_df["stop_seq"].tolist()   # [1..15]

# ── Stop popularity weights ───────────────────────────────────────────────────
# Peaks at both ends (city centre + airport) and at stop 7 (midpoint hub)
raw_weights = np.array([
    5, 4, 3, 2, 2, 1, 3, 2, 2, 1, 1, 2, 3, 4, 5
], dtype=float)
board_weights = raw_weights / raw_weights.sum()

# Destination weights: opposite skew (people travelling TO the other end)
dest_raw = raw_weights[::-1]
dest_weights = dest_raw / dest_raw.sum()

# ── Time-of-day multiplier ────────────────────────────────────────────────────
def tod_multiplier(hour: int) -> float:
    if 7 <= hour < 9:   return 3.0    # morning peak — very high demand
    if 17 <= hour < 19: return 3.0    # evening peak
    if 9 <= hour < 12:  return 1.4
    if 16 <= hour < 17: return 1.6
    if 6 <= hour < 7:   return 0.7
    if 21 <= hour < 23: return 0.6
    return 1.2

# ── Day-of-week multiplier ────────────────────────────────────────────────────
DOW_MULT = {0:1.0, 1:1.0, 2:1.0, 3:1.0, 4:1.0, 5:0.8, 6:0.55}

# ── Build trip schedule lookup ────────────────────────────────────────────────
# Map trip_id -> departure hour (hour of first stop)
first_stop = st_df[st_df["stop_sequence"] == 1][["trip_id","departure_time"]].copy()
first_stop["hour"] = first_stop["departure_time"].str[:2].astype(int)
trip_hour  = dict(zip(first_stop["trip_id"], first_stop["hour"]))

# ── Generate tickets ──────────────────────────────────────────────────────────
records = []
ticket_counter = 1

for day_offset in range(NUM_DAYS):
    sim_date = START_DATE + timedelta(days=day_offset)
    dow      = sim_date.weekday()    # 0=Mon … 6=Sun
    dow_mult = DOW_MULT[dow]

    for _, trip in trips_df.iterrows():
        trip_id  = trip["trip_id"]
        route_id = trip["route_id"]
        capacity = int(trip["bus_capacity"])
        hour     = trip_hour.get(trip_id, 12)
        tod_mult = tod_multiplier(hour)

        # Expected total boardings for this trip
        expected_demand = BASE_DEMAND_PER_TRIP * tod_mult * dow_mult
        # Jitter ±20 %
        jitter  = rng.uniform(0.8, 1.2)
        total_board = max(1, int(rng.poisson(expected_demand * jitter)))

        # Cap: never exceed MAX_LOAD_RATIO * capacity (mild over-capacity ok)
        total_board = min(total_board, int(MAX_LOAD_RATIO * capacity))

        # Build a realistic OD distribution for this trip
        # Allocate passengers to boarding stops probabilistically
        board_counts = rng.multinomial(total_board, board_weights)

        for b_idx, b_count in enumerate(board_counts):
            if b_count == 0:
                continue
            board_seq = STOP_SEQS[b_idx]
            # Remaining stops after boarding
            remaining = [s for s in STOP_SEQS if s > board_seq]
            if not remaining:
                continue

            # Allocate b_count passengers to destination stops
            rem_weights = dest_weights[b_idx+1:]
            if rem_weights.sum() == 0:
                continue
            rem_weights = rem_weights / rem_weights.sum()
            dest_counts = rng.multinomial(b_count, rem_weights)

            for d_idx, d_count in enumerate(dest_counts):
                if d_count == 0:
                    continue
                dest_seq = remaining[d_idx]

                # Build timestamp: trip depart time + (board_stop-1)*4 min
                arr_minutes = hour * 60 + (board_seq - 1) * 4
                h, m = divmod(arr_minutes, 60)
                ts_str = f"{sim_date.isoformat()}T{h:02d}:{m:02d}:00"

                records.append({
                    "ticket_id":          ticket_counter,
                    "bus_id":             f"BUS-{(ticket_counter % 5) + 1:02d}",
                    "route_id":           route_id,
                    "trip_id":            f"{sim_date.isoformat()}_{trip_id}",
                    "boarding_stop_seq":  board_seq,
                    "dest_stop_seq":      dest_seq,
                    "timestamp":          ts_str,
                    "passenger_count":    int(d_count),
                    "fare":               round(1.5 + (dest_seq - board_seq) * 0.5, 2),
                    "bus_capacity":       capacity,
                })
                ticket_counter += 1

tickets_df = pd.DataFrame(records)
tickets_df.to_csv(OUT_PATH, index=False)

# ── Summary stats ─────────────────────────────────────────────────────────────
print(f"\nTicket simulation complete")
print(f"  Total tickets : {len(tickets_df):,}")
print(f"  Days simulated: {NUM_DAYS}")
print(f"  Trips covered : {tickets_df['trip_id'].nunique():,}")
print(f"  Date range    : {tickets_df['timestamp'].min()[:10]}  ->  {tickets_df['timestamp'].max()[:10]}")
print(f"\nPassenger count summary (per ticket record):")
print(tickets_df["passenger_count"].describe().to_string())
print(f"\nFare summary:")
print(tickets_df["fare"].describe().to_string())
print(f"\nOutput -> {OUT_PATH}")
