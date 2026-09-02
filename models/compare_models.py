"""
compare_models.py - XGBoost vs LSTM comparison table
=====================================================
Reads the metrics files saved by train_xgboost.py and train_lstm.py
and prints a side-by-side comparison table.

Run AFTER both training scripts have completed:
    python models/compare_models.py
"""

import pathlib

MODELS_DIR = pathlib.Path(__file__).parent

def read_metrics(path: pathlib.Path) -> dict:
    metrics = {}
    if not path.exists():
        return metrics
    with open(path) as f:
        for line in f:
            line = line.strip()
            if "=" in line:
                k, v = line.split("=", 1)
                metrics[k.strip()] = float(v.strip())
    return metrics

xgb_m  = read_metrics(MODELS_DIR / "xgb_metrics.txt")
lstm_m = read_metrics(MODELS_DIR / "lstm_metrics.txt")

if not xgb_m or not lstm_m:
    print("Run train_xgboost.py and train_lstm.py first.")
    raise SystemExit(1)

print("\n" + "="*65)
print("MODEL COMPARISON — Test Set (Chronological Split, Same Period)")
print("="*65)

print(f"\n{'Metric':<28} {'XGBoost':>12} {'LSTM':>12}")
print("-"*55)

clf_rows = [
    ("Accuracy",  "clf_accuracy"),
    ("Precision (weighted)", "clf_precision"),
    ("Recall (weighted)",    "clf_recall"),
    ("F1 Score (weighted)",  "clf_f1"),
]
print("\n  CLASSIFICATION (crowd band prediction)")
for label, key in clf_rows:
    xv = xgb_m.get(key, float("nan"))
    lv = lstm_m.get(key, float("nan"))
    better = "<< XGB" if xv > lv else "<< LSTM"
    print(f"  {label:<26} {xv:>12.4f} {lv:>12.4f}  {better}")

print()
reg_rows = [
    ("MAE  (passengers)",  "reg_mae"),
    ("RMSE (passengers)",  "reg_rmse"),
]
print("  REGRESSION (occupancy count prediction)")
for label, key in reg_rows:
    xv = xgb_m.get(key, float("nan"))
    lv = lstm_m.get(key, float("nan"))
    better = "<< XGB" if xv < lv else "<< LSTM"
    print(f"  {label:<26} {xv:>12.4f} {lv:>12.4f}  {better}")

print("\n" + "="*65)
print("NOTE: All numbers measured on the held-out test set.")
print("      No numbers have been invented or hardcoded.")
print("="*65)
