"""
main.py - FastAPI application
==============================
Endpoints:
  POST /tickets                         - ingest a ticket
  GET  /live?bus_id=...                 - live occupancy for a bus
  GET  /predict?route_id=&stop_seq=&time= - ML crowd prediction
  GET  /recommend?route_id=&stop_seq=   - best upcoming trip
  GET  /analytics?route_id=            - demand by hour (authority view)
  GET  /health                          - health check

Run:
  uvicorn backend.main:app --reload --port 8000
"""

from __future__ import annotations
import json
import os
import pathlib, sys
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Depends, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import pandas as pd

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except Exception:
    firebase_admin = None
    credentials = None
    firestore = None

# Make local imports work
sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from database  import create_tables, get_db, TicketDB
from schemas   import (TicketIn, TicketOut, LiveStatusOut,
                        PredictOut, RecommendOut, TripOption, AnalyticsOut)
from occupancy import IncrementalOccupancy, crowd_band
from predictor import predict_band_and_occupancy, models_loaded

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Bus Crowd Prediction API",
    description=(
        "Real-time bus occupancy engine + ML crowd predictions. "
        "Occupancy is computed deterministically (no ML). "
        "Predictions come from trained XGBoost models."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_tables()
    _init_firestore()

# ── In-memory live state ──────────────────────────────────────────────────────
# Maps bus_id -> IncrementalOccupancy tracker
# Also keeps track of route_id / trip_id / capacity per bus
_bus_state: dict[str, IncrementalOccupancy] = {}
_bus_meta:  dict[str, dict] = {}   # bus_id -> {route_id, trip_id, capacity}
_firestore_client = None


def _get_or_create_tracker(bus_id: str, capacity: int = 50) -> IncrementalOccupancy:
    if bus_id not in _bus_state:
        _bus_state[bus_id] = IncrementalOccupancy(capacity=capacity)
    return _bus_state[bus_id]


def _init_firestore() -> None:
    """Enable Firestore publishing when Firebase Admin credentials are present."""
    global _firestore_client
    if firebase_admin is None:
        return
    if firebase_admin._apps:
        _firestore_client = firestore.client()
        return

    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    project_id = os.getenv("FIREBASE_PROJECT_ID")

    try:
        if service_account_json:
            cred = credentials.Certificate(json.loads(service_account_json))
            firebase_admin.initialize_app(cred)
        elif service_account_path:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        elif project_id:
            firebase_admin.initialize_app(options={"projectId": project_id})
        else:
            return
        _firestore_client = firestore.client()
    except Exception as exc:
        print(f"Firestore disabled: {exc}")
        _firestore_client = None


def verify_conductor_api_key(
    x_conductor_api_key: Optional[str] = Header(default=None),
) -> None:
    """Protect conductor writes when CONDUCTOR_API_KEY is configured."""
    expected = os.getenv("CONDUCTOR_API_KEY")
    if expected and x_conductor_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid conductor API key")


def _rebuild_tracker_from_db(bus_id: str, db: Session) -> bool:
    """Rehydrate live state after a server restart using persisted tickets."""
    rows = (
        db.query(TicketDB)
        .filter(TicketDB.bus_id == bus_id)
        .order_by(TicketDB.timestamp.asc(), TicketDB.id.asc())
        .all()
    )
    if not rows:
        return False

    latest = rows[-1]
    tracker = IncrementalOccupancy(capacity=latest.bus_capacity or 50)
    for row in rows:
        tracker.ingest_ticket(
            row.boarding_stop_seq,
            row.dest_stop_seq,
            row.passenger_count or 1,
        )

    _bus_state[bus_id] = tracker
    _bus_meta[bus_id] = {
        "route_id": latest.route_id,
        "trip_id": latest.trip_id,
        "capacity": latest.bus_capacity or 50,
        "current_stop": latest.boarding_stop_seq,
    }
    return True


def _publish_live_to_firestore(bus_id: str, payload: dict) -> None:
    """Publish live state for passenger apps. No-op until Firebase is configured."""
    if _firestore_client is None:
        return
    try:
        _firestore_client.collection("live_buses").document(bus_id).set(payload, merge=True)
    except Exception as exc:
        print(f"Firestore live publish failed for {bus_id}: {exc}")


# ══════════════════════════════════════════════════════════════════════════════
# POST /tickets
# ══════════════════════════════════════════════════════════════════════════════
@app.post("/tickets", response_model=TicketOut, status_code=201, tags=["Ingest"])
def ingest_ticket(
    ticket: TicketIn,
    _: None = Depends(verify_conductor_api_key),
    db: Session = Depends(get_db),
):
    """
    Ingest a single ticket.  Updates the live occupancy state for the bus
    and persists the ticket to the database.
    """
    # Persist to DB
    db_ticket = TicketDB(
        ticket_id         = ticket.ticket_id,
        bus_id            = ticket.bus_id,
        route_id          = ticket.route_id,
        trip_id           = ticket.trip_id,
        boarding_stop_seq = ticket.boarding_stop_seq,
        dest_stop_seq     = ticket.dest_stop_seq,
        timestamp         = ticket.timestamp,
        passenger_count   = ticket.passenger_count,
        fare              = ticket.fare,
        bus_capacity      = ticket.bus_capacity,
    )
    try:
        db.add(db_ticket)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Duplicate ticket_id")

    # Update live state
    tracker = _get_or_create_tracker(ticket.bus_id, ticket.bus_capacity)
    tracker.ingest_ticket(
        ticket.boarding_stop_seq,
        ticket.dest_stop_seq,
        ticket.passenger_count,
    )
    _bus_meta[ticket.bus_id] = {
        "route_id": ticket.route_id,
        "trip_id":  ticket.trip_id,
        "capacity": ticket.bus_capacity,
        "current_stop": ticket.boarding_stop_seq,
    }

    state = tracker.state_at_segment(ticket.boarding_stop_seq)
    _publish_live_to_firestore(
        ticket.bus_id,
        {
            "bus_id": ticket.bus_id,
            "route_id": ticket.route_id,
            "trip_id": ticket.trip_id,
            "onboard": state.onboard,
            "capacity": ticket.bus_capacity,
            "seats_free": state.seats_free,
            "load_ratio": state.load_ratio,
            "crowd_band": state.band.value,
            "current_stop": ticket.boarding_stop_seq,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    return TicketOut(
        ticket_id   = ticket.ticket_id,
        trip_id     = ticket.trip_id,
        route_id    = ticket.route_id,
        onboard_now = state.onboard,
        seats_free  = state.seats_free,
        crowd_band  = state.band.value,
    )


# ══════════════════════════════════════════════════════════════════════════════
# GET /live
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/live", response_model=LiveStatusOut, tags=["Live"])
def get_live_status(
    bus_id: str = Query(..., description="Bus identifier"),
    db: Session = Depends(get_db),
):
    """Return current occupancy for a bus (from in-memory state)."""
    if bus_id not in _bus_state:
        restored = _rebuild_tracker_from_db(bus_id, db)
        if not restored:
            raise HTTPException(404, detail=f"No live data for bus '{bus_id}'. Ingest a ticket first.")

    meta     = _bus_meta[bus_id]
    tracker  = _bus_state[bus_id]
    stop     = meta.get("current_stop", 1)
    capacity = meta.get("capacity", 50)
    state    = tracker.state_at_segment(stop)

    return LiveStatusOut(
        bus_id     = bus_id,
        route_id   = meta["route_id"],
        trip_id    = meta["trip_id"],
        onboard    = state.onboard,
        capacity   = capacity,
        seats_free = state.seats_free,
        load_ratio = state.load_ratio,
        crowd_band = state.band.value,
    )


# ══════════════════════════════════════════════════════════════════════════════
# GET /predict
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/predict", response_model=PredictOut, tags=["Prediction"])
def predict_crowd(
    route_id: str = Query(...),
    stop_seq: int = Query(..., ge=1, le=15),
    time:     str = Query(..., description="ISO datetime or HH:MM"),
):
    """Predict crowd band + occupancy at a future stop using the trained model."""
    try:
        if "T" in time or " " in time:
            dt = datetime.fromisoformat(time.replace(" ", "T"))
        else:
            dt = datetime.strptime(time, "%H:%M")
        hour = dt.hour
        dow  = dt.weekday() if hasattr(dt, "date") else 0
    except Exception:
        raise HTTPException(422, detail="time must be ISO datetime or HH:MM format")

    result = predict_band_and_occupancy(stop_seq=stop_seq, hour=hour, day_of_week=dow)
    return PredictOut(
        route_id   = route_id,
        stop_seq   = stop_seq,
        hour       = hour,
        crowd_band = result["crowd_band"],
        occupancy  = result["occupancy"],
        seats_free = result["seats_free"],
    )


# ══════════════════════════════════════════════════════════════════════════════
# GET /recommend
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/recommend", response_model=RecommendOut, tags=["Recommendation"])
def recommend_trip(
    route_id: str = Query(...),
    stop_seq: int = Query(..., ge=1, le=15),
    from_hour: int = Query(None, ge=0, le=23, description="Current hour (default: now)"),
):
    """
    Rank the next 4 upcoming trips by predicted occupancy.
    Returns the least-crowded trip within a 90-min window.
    """
    now_hour = from_hour if from_hour is not None else datetime.now().hour
    dow      = datetime.now().weekday()

    # Synthetic trip schedule: one trip per hour from 6:00 to 21:00.
    trip_hours = list(range(6, 22))  # one trip per hour for simplicity
    upcoming   = [h for h in trip_hours if h >= now_hour][:4]
    if not upcoming:
        upcoming = trip_hours[:4]

    options = []
    for h in upcoming:
        result = predict_band_and_occupancy(stop_seq=stop_seq, hour=h, day_of_week=dow)
        options.append(TripOption(
            trip_id        = f"TRIP-H{h:02d}",
            departure_time = f"{h:02d}:00",
            predicted_band = result["crowd_band"],
            predicted_load = result["occupancy"],
            seats_free     = result["seats_free"],
        ))

    best = min(options, key=lambda x: x.predicted_load)
    if best.departure_time == (f"{upcoming[0]:02d}:00" if upcoming else ""):
        msg = "Board the next bus — it looks comfortable."
    else:
        msg = (
            f"Skip the next bus. The {best.departure_time} departure "
            f"has more seats ({best.seats_free:.0f} free)."
        )

    return RecommendOut(
        route_id       = route_id,
        stop_seq       = stop_seq,
        recommendation = msg,
        options        = options,
    )


# ══════════════════════════════════════════════════════════════════════════════
# GET /analytics
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/analytics", response_model=AnalyticsOut, tags=["Analytics"])
def get_analytics(
    route_id: str = Query(...),
    db: Session = Depends(get_db),
):
    """Aggregate demand by hour for the authority dashboard."""
    rows = db.query(TicketDB).filter(TicketDB.route_id == route_id).all()

    if not rows:
        # Return synthetic analytics from the occupancy_history CSV
        hist_path = pathlib.Path(__file__).parent.parent / "datasets" / "occupancy_history.csv"
        if hist_path.exists():
            hist = pd.read_csv(hist_path)
            by_hour = hist.groupby("hour")["onboard"].mean().round(1).to_dict()
            by_hour = {int(k): float(v) for k, v in by_hour.items()}
        else:
            by_hour = {h: 0.0 for h in range(6, 23)}
    else:
        by_hour: dict[int, float] = defaultdict(float)
        for r in rows:
            h = r.timestamp.hour if r.timestamp else 0
            by_hour[h] += r.passenger_count
        by_hour = {int(k): round(float(v), 1) for k, v in sorted(by_hour.items())}

    if by_hour:
        busiest  = max(by_hour, key=by_hour.get)
        quietest = min(by_hour, key=by_hour.get)
    else:
        busiest = quietest = 0

    return AnalyticsOut(
        route_id       = route_id,
        demand_by_hour = by_hour,
        busiest_hour   = busiest,
        quietest_hour  = quietest,
    )


# ══════════════════════════════════════════════════════════════════════════════
# GET /stops
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/stops", tags=["Transit"])
def get_stops(route_id: str = Query("ROUTE-1")):
    """Return ordered list of bus stops for the route with coordinates and sequence numbers."""
    stops_csv = pathlib.Path(__file__).parent.parent / "datasets" / "gtfs_raw" / "stops.csv"
    if stops_csv.exists():
        df_stops = pd.read_csv(stops_csv)
        return df_stops.to_dict(orient="records")
    # Fallback if csv not present
    return [
        {"stop_id": f"S{i+1:02d}", "stop_seq": i+1, "stop_name": name, "stop_lat": 12.9716 + i*0.018, "stop_lon": 77.5946 + i*0.015}
        for i, name in enumerate([
            "Central Station", "Market Square", "University Gate", "Hospital Junction",
            "Tech Park", "Old Town", "River Bridge", "Sports Complex", "Shopping Mall",
            "Residential Colony", "Industrial Area", "Suburb North", "Suburb East",
            "Airport Road", "Airport Terminal"
        ])
    ]


# ══════════════════════════════════════════════════════════════════════════════
# GET /health
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/health", tags=["System"])
def health():
    return {
        "status":        "ok",
        "models_loaded": models_loaded(),
        "active_buses":  len(_bus_state),
        "timestamp":     datetime.now(timezone.utc).isoformat(),
    }
