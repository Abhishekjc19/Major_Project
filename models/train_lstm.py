"""
train_lstm.py - Keras LSTM model training
==========================================
Trains an LSTM to predict next-segment occupancy from a sequence
of the last SEQ_LEN observations at the same stop_seq.

Architecture
------------
  Input  -> (SEQ_LEN, num_features)
  LSTM(64) -> Dropout(0.2) -> Dense(32, relu) -> Dense(1)

Two separate models:
  (a) Regression  -> predict segment_occupancy (pax count)
  (b) Classification -> predict crowd_band_encoded (softmax)

Uses the SAME chronological test period as XGBoost so metrics are comparable.
Saves models to models/lstm_reg.h5 and models/lstm_clf.h5.

Run:
    python models/train_lstm.py
"""

import pathlib, sys, warnings, os
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_absolute_error, mean_squared_error,
    classification_report,
)
from sklearn.preprocessing import StandardScaler

from features import load_features, get_train_val_test, FEATURE_COLS, TARGET_CLF, TARGET_REG, BAND_ORDER

MODELS_DIR = pathlib.Path(__file__).parent
PLOTS_DIR  = MODELS_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

SEQ_LEN    = 5      # look back 5 consecutive segments
EPOCHS     = 30
BATCH_SIZE = 64
BAND_NAMES = {v: k for k, v in BAND_ORDER.items()}
NUM_CLASSES = 4

# ── Load & split ─────────────────────────────────────────────────────────────
print("Loading features...")
df = load_features()
train_df, val_df, test_df = get_train_val_test(df)

# Scale features
scaler = StandardScaler()
X_train_raw = scaler.fit_transform(train_df[FEATURE_COLS])
X_val_raw   = scaler.transform(val_df[FEATURE_COLS])
X_test_raw  = scaler.transform(test_df[FEATURE_COLS])

y_reg_train = train_df[TARGET_REG].values
y_reg_val   = val_df[TARGET_REG].values
y_reg_test  = test_df[TARGET_REG].values

y_clf_train = train_df[TARGET_CLF].values
y_clf_val   = val_df[TARGET_CLF].values
y_clf_test  = test_df[TARGET_CLF].values

# ── Build sequences ───────────────────────────────────────────────────────────
def make_sequences(X, y, seq_len):
    Xs, ys = [], []
    for i in range(seq_len, len(X)):
        Xs.append(X[i-seq_len:i])
        ys.append(y[i])
    return np.array(Xs), np.array(ys)

print(f"Building sequences (SEQ_LEN={SEQ_LEN})...")
Xtr_reg, ytr_reg = make_sequences(X_train_raw, y_reg_train, SEQ_LEN)
Xvl_reg, yvl_reg = make_sequences(X_val_raw,   y_reg_val,   SEQ_LEN)
Xts_reg, yts_reg = make_sequences(X_test_raw,  y_reg_test,  SEQ_LEN)

Xtr_clf, ytr_clf = make_sequences(X_train_raw, y_clf_train, SEQ_LEN)
Xvl_clf, yvl_clf = make_sequences(X_val_raw,   y_clf_val,   SEQ_LEN)
Xts_clf, yts_clf = make_sequences(X_test_raw,  y_clf_test,  SEQ_LEN)

print(f"Train sequences: {len(Xtr_reg)} | Val: {len(Xvl_reg)} | Test: {len(Xts_reg)}")

# ── Import Keras (deferred so TF logs don't clutter output) ──────────────────
print("Loading TensorFlow/Keras...")
import tensorflow as tf
tf.random.set_seed(42)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

n_features = len(FEATURE_COLS)

# ═══════════════════════════════════════════════════════════════════════════════
# (a) LSTM REGRESSOR
# ═══════════════════════════════════════════════════════════════════════════════
print("\n--- Training LSTM Regressor ---")
lstm_reg = Sequential([
    LSTM(64, input_shape=(SEQ_LEN, n_features), return_sequences=False),
    Dropout(0.2),
    Dense(32, activation="relu"),
    Dense(1),
], name="lstm_regressor")

lstm_reg.compile(optimizer="adam", loss="mse", metrics=["mae"])

es = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)
hist_reg = lstm_reg.fit(
    Xtr_reg, ytr_reg,
    validation_data=(Xvl_reg, yvl_reg),
    epochs=EPOCHS, batch_size=BATCH_SIZE,
    callbacks=[es], verbose=0,
)
print(f"  Stopped at epoch {len(hist_reg.history['loss'])}")

y_reg_pred = lstm_reg.predict(Xts_reg, verbose=0).flatten()
y_reg_pred = np.clip(y_reg_pred, 0, None)

mae  = mean_absolute_error(yts_reg, y_reg_pred)
rmse = np.sqrt(mean_squared_error(yts_reg, y_reg_pred))
print(f"\n[LSTM Regressor — Test Set Metrics]")
print(f"  MAE  : {mae:.4f}")
print(f"  RMSE : {rmse:.4f}")

# Training curve
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(hist_reg.history["loss"], label="Train loss")
ax.plot(hist_reg.history["val_loss"], label="Val loss")
ax.set_xlabel("Epoch"); ax.set_ylabel("MSE Loss")
ax.set_title("LSTM Regressor — Training Curve")
ax.legend(); plt.tight_layout()
fig.savefig(PLOTS_DIR / "lstm_reg_training_curve.png", dpi=120)
plt.close()
print(f"  Training curve -> models/plots/lstm_reg_training_curve.png")

lstm_reg.save(str(MODELS_DIR / "lstm_reg.h5"))
print(f"  Model saved -> models/lstm_reg.h5")

# ═══════════════════════════════════════════════════════════════════════════════
# (b) LSTM CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════════
print("\n--- Training LSTM Classifier ---")
lstm_clf = Sequential([
    LSTM(64, input_shape=(SEQ_LEN, n_features), return_sequences=False),
    Dropout(0.2),
    Dense(32, activation="relu"),
    Dense(NUM_CLASSES, activation="softmax"),
], name="lstm_classifier")

lstm_clf.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

es2 = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)
hist_clf = lstm_clf.fit(
    Xtr_clf, ytr_clf,
    validation_data=(Xvl_clf, yvl_clf),
    epochs=EPOCHS, batch_size=BATCH_SIZE,
    callbacks=[es2], verbose=0,
)
print(f"  Stopped at epoch {len(hist_clf.history['loss'])}")

y_clf_pred_prob = lstm_clf.predict(Xts_clf, verbose=0)
y_clf_pred      = np.argmax(y_clf_pred_prob, axis=1)

acc  = accuracy_score(yts_clf, y_clf_pred)
prec = precision_score(yts_clf, y_clf_pred, average="weighted", zero_division=0)
rec  = recall_score(yts_clf, y_clf_pred, average="weighted", zero_division=0)
f1   = f1_score(yts_clf, y_clf_pred, average="weighted", zero_division=0)

print(f"\n[LSTM Classifier — Test Set Metrics]")
print(f"  Accuracy  : {acc:.4f}")
print(f"  Precision : {prec:.4f}")
print(f"  Recall    : {rec:.4f}")
print(f"  F1 Score  : {f1:.4f}")

present_labels = sorted(np.unique(yts_clf).tolist())
present_names  = [BAND_NAMES.get(l, str(l)) for l in present_labels]
print(f"\n  Classification Report:")
print(classification_report(
    yts_clf, y_clf_pred,
    labels=present_labels,
    target_names=present_names,
    zero_division=0,
))

lstm_clf.save(str(MODELS_DIR / "lstm_clf.h5"))
print(f"  Model saved -> models/lstm_clf.h5")

# ── Save metrics for compare_models.py ────────────────────────────────────────
metrics_path = MODELS_DIR / "lstm_metrics.txt"
with open(metrics_path, "w") as f:
    f.write(f"clf_accuracy={acc:.6f}\n")
    f.write(f"clf_precision={prec:.6f}\n")
    f.write(f"clf_recall={rec:.6f}\n")
    f.write(f"clf_f1={f1:.6f}\n")
    f.write(f"reg_mae={mae:.6f}\n")
    f.write(f"reg_rmse={rmse:.6f}\n")
print(f"\n  Metrics saved -> {metrics_path}")

print("\n" + "="*55)
print("LSTM Training Summary")
print("="*55)
print(f"  Classifier  Accuracy={acc:.4f}  F1={f1:.4f}")
print(f"  Regressor   MAE={mae:.4f}  RMSE={rmse:.4f}")
print("="*55)
