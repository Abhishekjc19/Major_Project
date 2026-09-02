# AI-Based Real-Time Bus Crowd Prediction & Passenger Decision Support System

> Final-year engineering project — built incrementally, phase by phase.

---

## What This Is

A system that tells passengers **how crowded a bus is right now** and **predicts how crowded it will be** — using only ticket data (no cameras, no sensors).

**Key insight:** A bus ticket records a boarding stop and a destination stop. From the stream of tickets on a trip we can compute *exactly* how many passengers are on board at any point using pure arithmetic. We call this the **Occupancy Engine**. Machine learning is used *only* to predict future crowd levels — it can never corrupt live seat counts.

---

## Architecture

```
Ticket stream ──► Occupancy Engine (deterministic) ──► Live status API
                                │
                                ▼
                    Training data (occupancy_history.csv)
                                │
                                ▼
                    ML Models (XGBoost / LSTM) ──► Prediction API
                                                         │
                              ┌──────────────────────────┤
                              ▼                          ▼
                    Flutter Mobile App         Streamlit Dashboard
                    (passenger-facing)         (authority-facing)
```

---

## Crowd Bands

Load ratio ρ = onboard / capacity:

| Band | ρ Range | GTFS Status |
|------|---------|-------------|
| 🟢 Plenty of seats | ρ ≤ 0.6 | MANY_SEATS_AVAILABLE |
| 🟡 Few seats left | 0.6 < ρ ≤ 1.0 | FEW_SEATS_AVAILABLE |
| 🟠 Standing only | 1.0 < ρ ≤ 1.3 | STANDING_ROOM_ONLY |
| 🔴 Packed / full | ρ > 1.3 | CRUSHED_SRO |

---

## Repo Structure

```
bus-crowd-prediction/
├── backend/        # FastAPI app: occupancy engine, prediction API, recommend
├── datasets/       # GTFS data + ticket simulator + generated CSVs
├── models/         # training scripts, saved models, notebooks
├── app/            # Flutter mobile app
├── dashboard/      # Streamlit authority dashboard
├── tests/          # pytest tests
├── docs/           # diagrams, API docs
├── demo_occupancy.py
└── README.md
```

---

## Canonical Ticket Schema

```
ticket_id, bus_id, route_id, trip_id, boarding_stop_seq (int),
dest_stop_seq (int), timestamp (ISO datetime), passenger_count (int),
fare (float), bus_capacity (int)
```

Derived (computed, never stored as input): `segment_occupancy`, `crowd_band`

---

## How to Run Each Part

### Phase 1 — Occupancy Engine

```powershell
# From project root
.\venv\Scripts\activate

# Run tests
pytest tests/test_occupancy.py -v

# Run demo
python demo_occupancy.py
```

### Phase 2 — Dataset Generation *(coming soon)*

```powershell
python datasets/simulate_tickets.py
python datasets/build_training_table.py
```

### Phase 3 — Model Training *(coming soon)*

```powershell
python models/train_xgboost.py
python models/train_lstm.py
python models/compare_models.py
```

### Phase 4 — Backend API *(coming soon)*

```powershell
uvicorn backend.main:app --reload --port 8000
# Docs at: http://localhost:8000/docs
```

### Phase 5 — Flutter App *(coming soon)*

```bash
cd app
flutter run
```

### Phase 6 — Streamlit Dashboard *(coming soon)*

```powershell
streamlit run dashboard/app.py
```

---

## Dataset Note

The dataset is **semi-synthetic**: generated from realistic GTFS route/stop structures with demand shaped by time-of-day peaks, day-of-week patterns, and configurable noise. All occupancy labels are computed deterministically by the Occupancy Engine — they are never guessed or approximated.

---

## Results

*(To be filled in after Phase 3 training — real metrics only, no invented numbers.)*

| Model | Accuracy | F1 | MAE | RMSE |
|-------|----------|----|-----|------|
| XGBoost | — | — | — | — |
| LSTM | — | — | — | — |

---

## Tech Stack

- **Backend/API:** Python 3.12 + FastAPI + uvicorn
- **ML:** pandas · scikit-learn · XGBoost · TensorFlow/Keras (LSTM)
- **Database:** SQLite (local dev) / PostgreSQL (production)
- **Real-time:** Firebase Firestore (Phase 5)
- **Mobile:** Flutter (Dart)
- **Dashboard:** Streamlit
- **Version control:** Git + GitHub
