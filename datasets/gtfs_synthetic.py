"""
gtfs_synthetic.py - Synthetic GTFS generator
============================================
Generates a realistic GTFS-like route structure (15 stops, ~20 trips/day)
so Phase 2 can proceed without downloading an external feed.

Output files (written to datasets/gtfs_raw/):
  routes.csv, stops.csv, trips.csv, stop_times.csv

Run:
    python datasets/gtfs_synthetic.py
"""

import os, random, pathlib
import pandas as pd

# ── Config ───────────────────────────────────────────────────────────────────
SEED        = 42
ROUTE_ID    = "ROUTE-1"
ROUTE_NAME  = "City Centre - Airport Express"
NUM_STOPS   = 15
BUS_CAPACITY= 30
TRIPS_PER_DAY = 20          # round trips; we model a single direction
FIRST_TRIP_HOUR = 6         # 06:00
LAST_TRIP_HOUR  = 22        # last trip departs at ~22:00
SERVICE_DATE    = "2026-01-06"   # a Monday (service_id = weekday)
OUT_DIR = pathlib.Path(__file__).parent / "gtfs_raw"

random.seed(SEED)

# ── Stops ────────────────────────────────────────────────────────────────────
STOP_NAMES = [
    "Central Station", "Market Square", "University Gate",
    "Hospital Junction", "Tech Park", "Old Town",
    "River Bridge", "Sports Complex", "Shopping Mall",
    "Residential Colony", "Industrial Area", "Suburb North",
    "Suburb East", "Airport Road", "Airport Terminal",
]
assert len(STOP_NAMES) == NUM_STOPS

# Approximate lat/lon along a corridor
BASE_LAT, BASE_LON = 12.9716, 77.5946   # Bangalore-ish
stops_df = pd.DataFrame({
    "stop_id":   [f"S{i+1:02d}" for i in range(NUM_STOPS)],
    "stop_name": STOP_NAMES,
    "stop_lat":  [round(BASE_LAT + i * 0.018, 6) for i in range(NUM_STOPS)],
    "stop_lon":  [round(BASE_LON + i * 0.015, 6) for i in range(NUM_STOPS)],
    "stop_seq":  list(range(1, NUM_STOPS + 1)),
})

# ── Routes ───────────────────────────────────────────────────────────────────
routes_df = pd.DataFrame([{
    "route_id":         ROUTE_ID,
    "route_short_name": "R1",
    "route_long_name":  ROUTE_NAME,
    "route_type":       3,   # bus
}])

# ── Trips & stop times ───────────────────────────────────────────────────────
# Spread trips evenly between first and last departure hour
trip_rows    = []
stoptime_rows= []

interval_minutes = int((LAST_TRIP_HOUR - FIRST_TRIP_HOUR) * 60 / TRIPS_PER_DAY)
travel_per_stop  = 4   # minutes between consecutive stops

for t_idx in range(TRIPS_PER_DAY):
    trip_id = f"TRIP-{t_idx+1:03d}"
    depart_min = FIRST_TRIP_HOUR * 60 + t_idx * interval_minutes

    trip_rows.append({
        "route_id":   ROUTE_ID,
        "service_id": "weekday",
        "trip_id":    trip_id,
        "direction_id": 0,
        "bus_capacity": BUS_CAPACITY,
    })

    for s_idx, row in stops_df.iterrows():
        arr_min = depart_min + s_idx * travel_per_stop
        arr_h, arr_m = divmod(arr_min, 60)
        time_str = f"{arr_h:02d}:{arr_m:02d}:00"
        stoptime_rows.append({
            "trip_id":        trip_id,
            "stop_id":        row["stop_id"],
            "stop_sequence":  row["stop_seq"],
            "arrival_time":   time_str,
            "departure_time": time_str,
        })

trips_df      = pd.DataFrame(trip_rows)
stoptimes_df  = pd.DataFrame(stoptime_rows)

# ── Write output ─────────────────────────────────────────────────────────────
OUT_DIR.mkdir(parents=True, exist_ok=True)
stops_df.to_csv(OUT_DIR / "stops.csv", index=False)
routes_df.to_csv(OUT_DIR / "routes.csv", index=False)
trips_df.to_csv(OUT_DIR / "trips.csv", index=False)
stoptimes_df.to_csv(OUT_DIR / "stop_times.csv", index=False)

print(f"Synthetic GTFS written to {OUT_DIR}/")
print(f"  Stops   : {len(stops_df)}")
print(f"  Trips   : {len(trips_df)}")
print(f"  Records : {len(stoptimes_df)} stop-time entries")
print(f"\nStop sequence:")
for _, r in stops_df.iterrows():
    print(f"  {r['stop_seq']:>2}. {r['stop_name']}")
