"""
features.py - Feature engineering for crowd prediction
=======================================================
Turns occupancy_history.csv into a model-ready feature matrix.

Features
--------
- stop_seq            : stop index (1-15)
- hour_sin / hour_cos : cyclic encoding of hour-of-day
- dow_sin  / dow_cos  : cyclic encoding of day-of-week
- is_peak             : 1 if morning (7-9h) or evening (17-19h) peak
- is_weekend          : 1 if Saturday or Sunday
- load_ratio_lag1     : same route+stop, previous trip (chronological)
- load_ratio_lag2     : two trips back
- rolling_mean3       : rolling mean of last 3 trips at same stop+hour slot

Target columns (returned separately)
--------------------------------------
- segment_occupancy   : numeric regression target
- crowd_band_encoded  : ordinal label for classification
                        0=Plenty, 1=Few, 2=Standing, 3=Packed
"""

import pathlib
import numpy as np
import pandas as pd

DATA_PATH = pathlib.Path(__file__).parent.parent / "datasets" / "occupancy_history.csv"

BAND_ORDER = {
    "Plenty of seats": 0,
    "Few seats left":  1,
    "Standing only":   2,
    "Packed / full":   3,
}


def load_features(path: pathlib.Path = DATA_PATH) -> pd.DataFrame:
    """
    Load occupancy_history.csv and return a fully-featured DataFrame
    sorted chronologically, ready for train/val/test splitting.
    """
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "hour", "trip_id", "stop_seq"]).reset_index(drop=True)

    # ── Cyclic time encodings ────────────────────────────────────────────────
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["dow_sin"]  = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"]  = np.cos(2 * np.pi * df["day_of_week"] / 7)

    # ── Binary flags ─────────────────────────────────────────────────────────
    df["is_peak"]    = ((df["hour"].between(7, 9)) | (df["hour"].between(17, 19))).astype(int)
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # ── Lag features per (stop_seq) across trips (chronological) ─────────────
    # Sort and compute lag within each stop_seq group
    df = df.sort_values(["stop_seq", "date", "hour"]).reset_index(drop=True)
    df["load_ratio_lag1"] = (
        df.groupby("stop_seq")["load_ratio"].shift(1).fillna(df["load_ratio"].mean())
    )
    df["load_ratio_lag2"] = (
        df.groupby("stop_seq")["load_ratio"].shift(2).fillna(df["load_ratio"].mean())
    )
    df["rolling_mean3"] = (
        df.groupby("stop_seq")["load_ratio"]
          .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
          .fillna(df["load_ratio"].mean())
    )

    # ── Ordinal label ────────────────────────────────────────────────────────
    df["crowd_band_encoded"] = df["crowd_band"].map(BAND_ORDER)

    # Back to chronological order for splitting
    df = df.sort_values(["date", "hour", "trip_id", "stop_seq"]).reset_index(drop=True)

    return df


FEATURE_COLS = [
    "stop_seq",
    "hour_sin", "hour_cos",
    "dow_sin", "dow_cos",
    "is_peak", "is_weekend",
    "load_ratio_lag1", "load_ratio_lag2", "rolling_mean3",
]

TARGET_CLF  = "crowd_band_encoded"
TARGET_REG  = "segment_occupancy"


def get_train_val_test(df: pd.DataFrame, val_frac: float = 0.15, test_frac: float = 0.15):
    """
    Chronological split — never shuffle across time.
    Returns (train, val, test) DataFrames.
    """
    n = len(df)
    val_start  = int(n * (1 - val_frac - test_frac))
    test_start = int(n * (1 - test_frac))
    return df.iloc[:val_start], df.iloc[val_start:test_start], df.iloc[test_start:]


if __name__ == "__main__":
    df = load_features()
    train, val, test = get_train_val_test(df)
    print(f"Feature matrix: {df.shape}")
    print(f"Train / Val / Test : {len(train)} / {len(val)} / {len(test)}")
    print(f"\nFeature columns: {FEATURE_COLS}")
    print(f"\nLabel distribution (crowd_band_encoded):")
    print(df["crowd_band_encoded"].value_counts().to_string())
    print(f"\nLoad ratio stats:")
    print(df["load_ratio"].describe().to_string())
