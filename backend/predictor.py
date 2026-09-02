"""
predictor.py - Model loader + inference wrapper
===============================================
Loads saved XGBoost (primary) or LSTM models at startup.
Falls back gracefully if models haven't been trained yet.
"""
import pathlib, pickle, warnings
import numpy as np

warnings.filterwarnings("ignore")

MODELS_DIR = pathlib.Path(__file__).parent.parent / "models"

BAND_NAMES = {
    0: "Plenty of seats",
    1: "Few seats left",
    2: "Standing only",
    3: "Packed / full",
}
CAPACITY = 50

_clf = None
_reg = None

def _load_models():
    global _clf, _reg
    clf_path = MODELS_DIR / "xgb_clf.pkl"
    reg_path = MODELS_DIR / "xgb_reg.pkl"
    if clf_path.exists():
        with open(clf_path, "rb") as f:
            _clf = pickle.load(f)
    if reg_path.exists():
        with open(reg_path, "rb") as f:
            _reg = pickle.load(f)

_load_models()


def _make_feature_vector(
    stop_seq: int,
    hour: int,
    day_of_week: int,
    lag1: float = 0.2,
    lag2: float = 0.2,
    rolling3: float = 0.2,
) -> np.ndarray:
    """Build a single-row feature vector matching features.FEATURE_COLS."""
    import math
    hour_sin = math.sin(2 * math.pi * hour / 24)
    hour_cos = math.cos(2 * math.pi * hour / 24)
    dow_sin  = math.sin(2 * math.pi * day_of_week / 7)
    dow_cos  = math.cos(2 * math.pi * day_of_week / 7)
    is_peak    = int((7 <= hour <= 9) or (17 <= hour <= 19))
    is_weekend = int(day_of_week >= 5)
    return np.array([[
        stop_seq, hour_sin, hour_cos, dow_sin, dow_cos,
        is_peak, is_weekend, lag1, lag2, rolling3,
    ]])


def predict_band_and_occupancy(
    stop_seq: int,
    hour: int,
    day_of_week: int = 0,
    lag1: float = 0.2,
    lag2: float = 0.2,
    rolling3: float = 0.2,
    capacity: int = CAPACITY,
) -> dict:
    """
    Returns predicted crowd_band and occupancy count.
    If models aren't loaded, returns a rule-based fallback.
    """
    X = _make_feature_vector(stop_seq, hour, day_of_week, lag1, lag2, rolling3)

    if _clf is not None:
        band_code = int(_clf.predict(X)[0])
        band_name = BAND_NAMES.get(band_code, "Unknown")
    else:
        # Fallback: heuristic based on hour
        is_peak = (7 <= hour <= 9) or (17 <= hour <= 19)
        band_name = "Few seats left" if is_peak else "Plenty of seats"
        band_code = 1 if is_peak else 0

    if _reg is not None:
        occ = float(np.clip(_reg.predict(X)[0], 0, capacity * 1.3))
    else:
        occ = capacity * (0.7 if band_code == 1 else 0.3)

    seats_free = max(0.0, float(capacity - occ))
    return {
        "crowd_band": band_name,
        "occupancy":  round(occ, 1),
        "seats_free": round(seats_free, 1),
    }


def models_loaded() -> bool:
    return _clf is not None and _reg is not None
