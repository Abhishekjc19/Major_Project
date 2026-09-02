"""
build_training_table.py - Occupancy history builder
====================================================
Runs the deterministic occupancy engine over every trip in tickets.csv
and produces occupancy_history.csv with one row per
(trip_id, stop_seq) plus rich feature columns and the LABEL.

Schema of occupancy_history.csv
--------------------------------
trip_id, route_id, date, day_of_week, hour, stop_seq,
boarding_stop_seq_mode, onboard, capacity,
seats_free, load_ratio, segment_occupancy, crowd_band

Run:
    python datasets/build_training_table.py
"""

import pathlib, sys
import pandas as pd

# Make backend importable
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))
from occupancy import compute_segment_occupancy

TICKETS_PATH  = pathlib.Path(__file__).parent / "tickets.csv"
GTFS_DIR      = pathlib.Path(__file__).parent / "gtfs_raw"
OUT_PATH      = pathlib.Path(__file__).parent / "occupancy_history.csv"

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading tickets...")
tickets = pd.read_csv(TICKETS_PATH)
tickets["timestamp"] = pd.to_datetime(tickets["timestamp"])
tickets["date"]      = tickets["timestamp"].dt.date
tickets["hour"]      = tickets["timestamp"].dt.hour
tickets["dow"]       = tickets["timestamp"].dt.dayofweek  # 0=Mon

stops_df = pd.read_csv(GTFS_DIR / "stops.csv")
NUM_STOPS = len(stops_df)

CAPACITY = int(tickets["bus_capacity"].iloc[0])

# ── Build occupancy history ────────────────────────────────────────────────────
print(f"Processing {tickets['trip_id'].nunique():,} trips...")
rows = []

for trip_id, group in tickets.groupby("trip_id"):
    # Metadata from the group
    meta_row   = group.iloc[0]
    route_id   = meta_row["route_id"]
    date_val   = meta_row["date"]
    hour_val   = meta_row["hour"]
    dow_val    = meta_row["dow"]
    capacity   = int(meta_row["bus_capacity"])

    # Run occupancy engine (batch mode)
    states = compute_segment_occupancy(group, num_stops=NUM_STOPS, capacity=capacity)

    for state in states:
        rows.append({
            "trip_id":           trip_id,
            "route_id":          route_id,
            "date":              str(date_val),
            "day_of_week":       dow_val,
            "hour":              hour_val,
            "stop_seq":          state.segment,
            "onboard":           state.onboard,
            "capacity":          capacity,
            "seats_free":        state.seats_free,
            "load_ratio":        state.load_ratio,
            "segment_occupancy": state.onboard,       # alias for ML clarity
            "crowd_band":        state.band.value,    # <-- THE LABEL
        })

history = pd.DataFrame(rows)
history.to_csv(OUT_PATH, index=False)

# ── Summary stats ─────────────────────────────────────────────────────────────
print(f"\nOccupancy history built")
print(f"  Rows      : {len(history):,}")
print(f"  Trips     : {history['trip_id'].nunique():,}")
print(f"  Columns   : {list(history.columns)}")

print(f"\n-- Band distribution --")
print(history["crowd_band"].value_counts().to_string())

peak_mask   = history["hour"].between(7, 9) | history["hour"].between(17, 19)
off_mask    = ~peak_mask

print(f"\n-- Avg onboard: peak hours vs off-peak --")
print(f"  Peak   (7-9h, 17-19h) : {history.loc[peak_mask,'onboard'].mean():.1f} pax")
print(f"  Off-peak               : {history.loc[off_mask,'onboard'].mean():.1f} pax")

print(f"\n-- Load ratio percentiles --")
pcts = history["load_ratio"].quantile([0.25, 0.5, 0.75, 0.9, 0.99])
for p, v in pcts.items():
    print(f"  p{int(p*100):>2} = {v:.2f}")

print(f"\nOutput -> {OUT_PATH}")
