"""
train_xgboost.py - XGBoost model training
==========================================
Trains two models on occupancy_history.csv:
  (a) Classifier  -> predict crowd_band  (4-class)
  (b) Regressor   -> predict segment_occupancy (numeric)

Uses a strict chronological train/val/test split.
Reports REAL metrics on the held-out test set.
Saves models to models/xgb_clf.pkl and models/xgb_reg.pkl.
Saves plots to models/plots/.

Run:
    python models/train_xgboost.py
"""

import pathlib, sys, pickle, warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBClassifier, XGBRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, mean_absolute_error, mean_squared_error,
    classification_report,
)

from features import load_features, get_train_val_test, FEATURE_COLS, TARGET_CLF, TARGET_REG, BAND_ORDER

MODELS_DIR = pathlib.Path(__file__).parent
PLOTS_DIR  = MODELS_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

BAND_NAMES = {v: k for k, v in BAND_ORDER.items()}

# ── Load & split ─────────────────────────────────────────────────────────────
print("Loading features...")
df = load_features()
train, val, test = get_train_val_test(df)

X_train = train[FEATURE_COLS]
X_val   = val[FEATURE_COLS]
X_test  = test[FEATURE_COLS]

y_clf_train = train[TARGET_CLF];  y_clf_val = val[TARGET_CLF];  y_clf_test = test[TARGET_CLF]
y_reg_train = train[TARGET_REG];  y_reg_val = val[TARGET_REG];  y_reg_test = test[TARGET_REG]

print(f"Train: {len(train)} | Val: {len(val)} | Test: {len(test)}")

# ═══════════════════════════════════════════════════════════════════════════════
# (a) CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════════
print("\n--- Training XGBoost Classifier ---")
clf = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    num_class=4,
    objective="multi:softmax",
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1,
    verbosity=0,
)
clf.fit(
    X_train, y_clf_train,
    eval_set=[(X_val, y_clf_val)],
    verbose=False,
)

y_clf_pred = clf.predict(X_test)

acc  = accuracy_score(y_clf_test, y_clf_pred)
prec = precision_score(y_clf_test, y_clf_pred, average="weighted", zero_division=0)
rec  = recall_score(y_clf_test, y_clf_pred, average="weighted", zero_division=0)
f1   = f1_score(y_clf_test, y_clf_pred, average="weighted", zero_division=0)

print(f"\n[XGBoost Classifier — Test Set Metrics]")
print(f"  Accuracy  : {acc:.4f}")
print(f"  Precision : {prec:.4f}")
print(f"  Recall    : {rec:.4f}")
print(f"  F1 Score  : {f1:.4f}")

present_labels = sorted(y_clf_test.unique())
present_names  = [BAND_NAMES.get(l, str(l)) for l in present_labels]
print(f"\n  Classification Report:")
print(classification_report(
    y_clf_test, y_clf_pred,
    labels=present_labels,
    target_names=present_names,
    zero_division=0
))

# Confusion matrix plot
cm = confusion_matrix(y_clf_test, y_clf_pred, labels=present_labels)
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=present_names, yticklabels=present_names, ax=ax)
ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
ax.set_title("XGBoost Classifier — Confusion Matrix (Test Set)")
plt.tight_layout()
fig.savefig(PLOTS_DIR / "xgb_confusion_matrix.png", dpi=120)
plt.close()
print(f"  Confusion matrix saved -> models/plots/xgb_confusion_matrix.png")

# Feature importance
fi = pd.Series(clf.feature_importances_, index=FEATURE_COLS).sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(7, 5))
fi.plot(kind="barh", ax=ax, color="steelblue")
ax.set_title("XGBoost Classifier — Feature Importance")
ax.set_xlabel("Importance Score")
plt.tight_layout()
fig.savefig(PLOTS_DIR / "xgb_feature_importance.png", dpi=120)
plt.close()
print(f"  Feature importance saved -> models/plots/xgb_feature_importance.png")

# Save classifier
clf_path = MODELS_DIR / "xgb_clf.pkl"
with open(clf_path, "wb") as f:
    pickle.dump(clf, f)
print(f"  Model saved -> {clf_path}")

# ═══════════════════════════════════════════════════════════════════════════════
# (b) REGRESSOR
# ═══════════════════════════════════════════════════════════════════════════════
print("\n--- Training XGBoost Regressor ---")
reg = XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    verbosity=0,
)
reg.fit(
    X_train, y_reg_train,
    eval_set=[(X_val, y_reg_val)],
    verbose=False,
)

y_reg_pred = reg.predict(X_test)
y_reg_pred = np.clip(y_reg_pred, 0, None)  # no negative passengers

mae  = mean_absolute_error(y_reg_test, y_reg_pred)
rmse = np.sqrt(mean_squared_error(y_reg_test, y_reg_pred))

print(f"\n[XGBoost Regressor — Test Set Metrics]")
print(f"  MAE  : {mae:.4f}")
print(f"  RMSE : {rmse:.4f}")

# Actual vs predicted scatter
fig, ax = plt.subplots(figsize=(6, 5))
ax.scatter(y_reg_test, y_reg_pred, alpha=0.3, s=10, color="steelblue")
lims = [min(y_reg_test.min(), y_reg_pred.min()), max(y_reg_test.max(), y_reg_pred.max())]
ax.plot(lims, lims, "r--", lw=1.5, label="Perfect prediction")
ax.set_xlabel("Actual onboard"); ax.set_ylabel("Predicted onboard")
ax.set_title(f"XGBoost Regressor — Actual vs Predicted\nMAE={mae:.2f}  RMSE={rmse:.2f}")
ax.legend()
plt.tight_layout()
fig.savefig(PLOTS_DIR / "xgb_actual_vs_predicted.png", dpi=120)
plt.close()
print(f"  Scatter plot saved -> models/plots/xgb_actual_vs_predicted.png")

# Save regressor
reg_path = MODELS_DIR / "xgb_reg.pkl"
with open(reg_path, "wb") as f:
    pickle.dump(reg, f)
print(f"  Model saved -> {reg_path}")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "="*55)
print("XGBoost Training Summary")
print("="*55)
print(f"  Classifier  Accuracy={acc:.4f}  F1={f1:.4f}")
print(f"  Regressor   MAE={mae:.4f}  RMSE={rmse:.4f}")
print("="*55)

# Save metrics for compare_models.py
metrics_path = MODELS_DIR / "xgb_metrics.txt"
with open(metrics_path, "w") as f:
    f.write(f"clf_accuracy={acc:.6f}\n")
    f.write(f"clf_precision={prec:.6f}\n")
    f.write(f"clf_recall={rec:.6f}\n")
    f.write(f"clf_f1={f1:.6f}\n")
    f.write(f"reg_mae={mae:.6f}\n")
    f.write(f"reg_rmse={rmse:.6f}\n")
print(f"  Metrics saved -> {metrics_path}")
