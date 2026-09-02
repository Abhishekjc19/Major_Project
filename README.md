# AI-Based Real-Time Bus Crowd Prediction & Passenger Decision Support System

> Final-year engineering project — deterministic occupancy engine + machine learning crowd predictions with passenger mobile app and authority dashboard.

---

## 📌 System Architecture

```
                                  ┌───────────────────────────────┐
                                  │      TICKET GENERATION /      │
                                  │       VALIDATION STREAM       │
                                  └───────────────┬───────────────┘
                                                  │ (ticket_id, bus_id, route_id, boarding_stop, dest_stop)
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │       OCCUPANCY ENGINE        │
                                  │    (Deterministic Core)       │
                                  │   onboard(j) = Σ passengers   │
                                  └───────┬───────────────┬───────┘
                                          │               │
                     (Live seat counts)   ▼               ▼ (Historical training data)
            ┌───────────────────────────────┐   ┌───────────────────────────────┐
            │       FASTAPI BACKEND         │   │   ML MODELS (XGBoost & LSTM)  │
            │   - Ingestion (/tickets)      │   │   - Crowd Band Classification │
            │   - Real-time (/live)         │◄──┤   - Occupancy Regression      │
            │   - Decision (/recommend)     │   │   - Cyclic & Lag Features     │
            │   - Authority (/analytics)    │   └───────────────────────────────┘
            └───────────────┬───────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│    FLUTTER MOBILE APP     │   │    STREAMLIT DASHBOARD    │
│    (Passenger-Facing)     │   │    (Authority-Facing)     │
│  - Live & Predicted Crowd │   │  - Demand by Hour Heatmap │
│  - Color-Coded Badges     │   │  - Peak/Off-Peak Metrics  │
│  - Smart Trip Advice      │   │  - Critical Stop Alerts   │
└───────────────────────────┘   └───────────────────────────┘
```

---

## 🚌 GTFS-Aligned Crowd Bands

Load ratio: $\rho = \frac{\text{onboard}}{\text{capacity}}$

| Crowd Band | Load Ratio Range ($\rho$) | GTFS Realtime Status | Visual Indicator |
|---|---|---|---|
| **Plenty of seats** | $\rho \le 0.60$ | `MANY_SEATS_AVAILABLE` | 🟢 Green |
| **Few seats left** | $0.60 < \rho \le 1.00$ | `FEW_SEATS_AVAILABLE` | 🟡 Amber |
| **Standing only** | $1.00 < \rho \le 1.30$ | `STANDING_ROOM_ONLY` | 🟠 Orange |
| **Packed / full** | $\rho > 1.30$ | `CRUSHED_SRO` / `FULL` | 🔴 Red |

---

## 📊 Real Measured Experimental Results

> **Note:** All figures are reproducible and evaluated strictly on the chronological held-out test split (972 test segments, 0 temporal data leakage).

### 1. Model Performance (Test Set Comparison)

| Task | Metric | XGBoost | LSTM (Keras) | Winner |
|---|---|---|---|---|
| **Crowd Band Classification** | **Accuracy** | 70.88% | **75.18%** | 🏆 **LSTM (+4.3%)** |
| | **Weighted Precision** | 66.42% | **72.01%** | 🏆 **LSTM** |
| | **Weighted Recall** | 70.88% | **75.18%** | 🏆 **LSTM** |
| | **Weighted F1 Score** | 0.6700 | **0.7007** | 🏆 **LSTM** |
| **Occupancy Regression** | **MAE (Passengers)** | **3.352 pax** | 3.356 pax | 🏆 **XGBoost** |
| | **RMSE (Passengers)** | **4.713 pax** | 4.911 pax | 🏆 **XGBoost** |

### 2. API Response Time & Latency Benchmarks (50 requests/endpoint)

| Endpoint | Purpose | Average Latency | p95 Latency | Min Latency | Max Latency |
|---|---|---|---|---|---|
| `POST /tickets` | Ingest ticket & update live state | **17.19 ms** | 35.82 ms | 11.77 ms | 37.32 ms |
| `GET /live` | Query deterministic live bus count | **8.76 ms** | 15.20 ms | 5.59 ms | 15.44 ms |
| `GET /predict` | ML inference for future stop/time | **144.62 ms** | 336.06 ms | 44.81 ms | 341.95 ms |
| `GET /recommend` | Multi-trip ranking & decision filter | **336.35 ms** | 561.20 ms | 77.05 ms | 574.13 ms |
| `GET /analytics` | Aggregated demand for operators | **13.43 ms** | 25.49 ms | 6.08 ms | 45.67 ms |

---

## 📁 Repository Structure

```
bus-crowd-prediction/
├── backend/
│   ├── main.py             # FastAPI REST endpoints (/tickets, /live, /predict, /recommend, /analytics)
│   ├── occupancy.py        # Deterministic Occupancy Engine (Batch & Streaming)
│   ├── database.py         # SQLAlchemy models + SQLite/Postgres connection
│   ├── schemas.py          # Pydantic data schemas & request validators
│   ├── predictor.py        # ML Model loading & inference wrapper
│   └── requirements.txt    # Production dependencies
├── datasets/
│   ├── gtfs_synthetic.py   # GTFS schedule generator (15 stops, 20 trips/day)
│   ├── simulate_tickets.py # Ticket stream simulator with morning/evening peaks
│   ├── build_training_table.py # Computes segment occupancy history
│   └── inject_extreme_bands.py # Extreme peak & event records for balanced ML training
├── models/
│   ├── features.py         # Cyclic time encoding (sin/cos) & lag feature matrix
│   ├── train_xgboost.py    # XGBoost classifier + regressor training
│   ├── train_lstm.py       # Sequential Keras LSTM network training
│   ├── compare_models.py   # Comparative evaluation table generator
│   └── plots/              # Confusion matrix, scatter & training curve plots
├── app/
│   ├── pubspec.yaml        # Flutter configuration
│   └── lib/
│       ├── main.dart       # App entry & Material 3 theme
│       ├── config.dart     # Backend connection host config
│       ├── api_service.dart# HTTP REST API connector
│       └── screens/
│           ├── home_screen.dart       # Stop selection & route overview
│           └── route_view_screen.dart # Live crowd badges & smart recommendation banner
├── dashboard/
│   └── app.py              # Streamlit authority analytics dashboard
├── tests/
│   ├── test_occupancy.py   # 27 unit tests for the deterministic occupancy engine
│   └── test_api.py         # 17 unit & integration tests for FastAPI endpoints
├── benchmark_api.py        # API latency measurement script
├── demo_occupancy.py       # CLI interactive occupancy engine demo
├── Dockerfile              # Container definition for cloud deployment
└── README.md
```

---

## 🚀 How to Run the Project (Step-by-Step)

### 1. Environment Setup
```powershell
cd "C:\Major Project\bus-crowd-prediction"
.\venv\Scripts\activate
```

### 2. Run Test Suite (All 44 Tests)
```powershell
pytest tests/ -v
```

### 3. Run the CLI Occupancy Demo
```powershell
python demo_occupancy.py
```

### 4. Start the FastAPI Backend
```powershell
uvicorn backend.main:app --reload --port 8000
```
- Interactive Swagger API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Interactive Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 5. Launch the Streamlit Authority Dashboard
In a new terminal window:
```powershell
streamlit run dashboard/app.py
```
- Opens automatically in your browser at `http://localhost:8501`.

### 6. Run the Flutter Mobile Passenger App
```bash
cd app
flutter pub get
flutter run
```
*(Configure `app/lib/config.dart` with your backend IP or `10.0.2.2:8000` for Android Emulator).*

---

## ☁️ Free Cloud Deployment Guide (Render / Railway)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deployable bus crowd prediction system"
   git push origin main
   ```
2. **Deploy on Render (Free Web Service)**:
   - Go to [render.com](https://render.com) and create a **New Web Service**.
   - Connect your GitHub repository.
   - Set **Environment** to `Docker` (Render will detect the `Dockerfile` automatically).
   - Click **Deploy**.
3. **Connect the App**:
   - Copy your deployed HTTPS URL (e.g. `https://bus-crowd-api.onrender.com`).
   - Paste it into `app/lib/config.dart`:
     ```dart
     static const String BASE_URL = 'https://bus-crowd-api.onrender.com';
     ```

---

## 🎬 Live Examiner Demo Script

When presenting to examiners/evaluators:
1. **Show Deterministic Core**: Run `python demo_occupancy.py` and explain the arithmetic formula `onboard(j) = sum(passenger_count)` where `boarding <= j < dest`. Highlight that ML is **not** in the live seat calculation path.
2. **Show Tests**: Run `pytest tests/ -v` showing all 44 unit and edge-case tests passing in ~4 seconds.
3. **Show ML Comparison**: Run `python models/compare_models.py` showing that LSTM achieves **75.18% classification accuracy** while XGBoost achieves **3.35 MAE regression**.
4. **Show Live API**: Open `http://localhost:8000/docs`, execute `POST /tickets`, then `GET /live` to show instantaneous state tracking.
5. **Show Authority View**: Open Streamlit dashboard (`http://localhost:8501`) highlighting peak hour demand spikes and the stop $\times$ hour heatmap.
6. **Show Passenger Experience**: Demonstrate the Flutter UI showing color-coded crowd levels and the "Skip this bus / Board this bus" decision advice banner.
