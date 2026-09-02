"""
inject_extreme_bands.py - Inject Standing/Packed records for ML training
=========================================================================
The organic simulation rarely reaches crush loads because demand distributes
across 14 segments. This script injects realistic extreme records for the
"Standing only" and "Packed / full" bands to ensure the classifier has
training examples for all 4 classes.

These records represent real-world scenarios:
  - Special events (match days, festivals) at peak stops
  - School rush hours
  - Reduced fleet days

The injection is clearly flagged in the dataset with trip_id prefixes.
Run ONCE after build_training_table.py:
    python datasets/inject_extreme_bands.py
"""
import pathlib, sys
import pandas as pd
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))
from occupancy import crowd_band as compute_band

HIST_PATH = pathlib.Path(__file__).parent / "occupancy_history.csv"
SEED = 42
rng = np.random.default_rng(SEED)

df = pd.read_csv(HIST_PATH)
capacity = int(df["capacity"].iloc[0])

# ── Generate Standing only records (rho 1.01 - 1.29) ─────────────────────────
n_standing = 400
standing_records = []
for i in range(n_standing):
    stop_seq   = int(rng.integers(3, 13))
    hour       = int(rng.choice([7, 8, 17, 18]))  # peak hours
    dow        = int(rng.integers(0, 5))           # weekday
    rho        = float(rng.uniform(1.01, 1.29))
    onboard    = int(rho * capacity)
    seats_free = 0
    standing_records.append({
        "trip_id":           f"EVENT-STANDING-{i:04d}",
        "route_id":          "ROUTE-1",
        "date":              f"2026-01-{(i % 21)+5:02d}",
        "day_of_week":       dow,
        "hour":              hour,
        "stop_seq":          stop_seq,
        "onboard":           onboard,
        "capacity":          capacity,
        "seats_free":        seats_free,
        "load_ratio":        round(rho, 4),
        "segment_occupancy": onboard,
        "crowd_band":        "Standing only",
    })

# ── Generate Packed / full records (rho > 1.3) ───────────────────────────────
n_packed = 200
packed_records = []
for i in range(n_packed):
    stop_seq   = int(rng.integers(3, 10))
    hour       = int(rng.choice([7, 8, 17, 18]))
    dow        = int(rng.integers(0, 5))
    rho        = float(rng.uniform(1.31, 1.50))
    onboard    = int(rho * capacity)
    seats_free = 0
    packed_records.append({
        "trip_id":           f"EVENT-PACKED-{i:04d}",
        "route_id":          "ROUTE-1",
        "date":              f"2026-01-{(i % 21)+5:02d}",
        "day_of_week":       dow,
        "hour":              hour,
        "stop_seq":          stop_seq,
        "onboard":           onboard,
        "capacity":          capacity,
        "seats_free":        seats_free,
        "load_ratio":        round(rho, 4),
        "segment_occupancy": onboard,
        "crowd_band":        "Packed / full",
    })

injected = pd.DataFrame(standing_records + packed_records)
df_full  = pd.concat([df, injected], ignore_index=True)
# Re-sort chronologically
df_full["date"] = pd.to_datetime(df_full["date"])
df_full = df_full.sort_values(["date", "hour", "trip_id", "stop_seq"]).reset_index(drop=True)
df_full["date"] = df_full["date"].dt.strftime("%Y-%m-%d")

df_full.to_csv(HIST_PATH, index=False)

print(f"Injection complete:")
print(df_full["crowd_band"].value_counts().to_string())
print(f"\nTotal rows: {len(df_full):,}")
print(f"Output -> {HIST_PATH}")
