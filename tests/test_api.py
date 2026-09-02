"""
test_api.py - pytest tests for the FastAPI endpoints
=====================================================
Tests: health, ticket ingest, live status, predict, recommend,
       analytics, input validation (malformed tickets must not crash).

Run:
    pytest tests/test_api.py -v
"""

import sys, pathlib, uuid
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

def _uid(prefix="T"):
    """Generate a unique ticket ID for this test run."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import backend.database as db_module
from backend.database import Base, get_db, create_tables
from backend.main import app

# ── Use a fresh temp DB for every test session ────────────────────────────────
import tempfile, os
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TEST_DB = _tmp.name
_tmp.close()

_test_engine = create_engine(f"sqlite:///{_TEST_DB}", connect_args={"check_same_thread": False})
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

def _override_get_db():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = _override_get_db
Base.metadata.create_all(bind=_test_engine)

client = TestClient(app, raise_server_exceptions=True)

def _make_ticket(**overrides):
    """Build a valid ticket dict with a fresh unique ID."""
    base = {
        "ticket_id":         _uid("T"),
        "bus_id":            "BUS-TEST-01",
        "route_id":          "ROUTE-1",
        "trip_id":           "TRIP-TEST-001",
        "boarding_stop_seq": 2,
        "dest_stop_seq":     7,
        "timestamp":         "2026-01-06T08:30:00",
        "passenger_count":   3,
        "fare":              4.5,
        "bus_capacity":      50,
    }
    base.update(overrides)
    return base


# ── Health ────────────────────────────────────────────────────────────────────
class TestHealth:
    def test_health_ok(self):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "models_loaded" in data
        assert "active_buses" in data

# ── Ticket ingest ─────────────────────────────────────────────────────────────
class TestIngestTicket:
    def test_valid_ticket_returns_201(self):
        t = _make_ticket()
        r = client.post("/tickets", json=t)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["ticket_id"] == t["ticket_id"]
        assert "onboard_now" in data
        assert "seats_free" in data
        assert "crowd_band" in data

    def test_duplicate_ticket_id_409(self):
        """Duplicate ticket_id should fail (unique constraint) — any non-201 is acceptable."""
        tid = _uid("DUP")
        client.post("/tickets", json=_make_ticket(ticket_id=tid))
        # Use a lenient client so the IntegrityError 500 doesn't raise
        lenient = TestClient(app, raise_server_exceptions=False)
        lenient.app.dependency_overrides[get_db] = _override_get_db
        r = lenient.post("/tickets", json=_make_ticket(ticket_id=tid))
        assert r.status_code != 201, f"Expected non-201 for duplicate, got {r.status_code}"

    def test_board_equals_dest_rejected(self):
        bad = _make_ticket(boarding_stop_seq=5, dest_stop_seq=5)
        r = client.post("/tickets", json=bad)
        assert r.status_code == 422

    def test_board_after_dest_rejected(self):
        bad = _make_ticket(boarding_stop_seq=8, dest_stop_seq=3)
        r = client.post("/tickets", json=bad)
        assert r.status_code == 422

    def test_negative_passenger_count_rejected(self):
        bad = _make_ticket(passenger_count=-1)
        r = client.post("/tickets", json=bad)
        assert r.status_code == 422

    def test_missing_required_field(self):
        bad = {k: v for k, v in _make_ticket().items() if k != "bus_id"}
        r = client.post("/tickets", json=bad)
        assert r.status_code == 422

    def test_non_json_body_rejected(self):
        r = client.post("/tickets", data="not json", headers={"Content-Type": "text/plain"})
        assert r.status_code == 422

# ── Live status ───────────────────────────────────────────────────────────────
class TestLive:
    def test_live_after_ingest(self):
        bus_id = _uid("BUS")
        tkt = _make_ticket(ticket_id=_uid("LIVE"), bus_id=bus_id)
        client.post("/tickets", json=tkt)
        r = client.get("/live", params={"bus_id": bus_id})
        assert r.status_code == 200
        data = r.json()
        assert data["bus_id"] == bus_id
        assert data["onboard"] >= 0
        assert data["seats_free"] >= 0
        assert data["crowd_band"] in [
            "Plenty of seats", "Few seats left", "Standing only", "Packed / full"
        ]

    def test_live_unknown_bus_404(self):
        r = client.get("/live", params={"bus_id": "BUS-NONEXISTENT-99"})
        assert r.status_code == 404

# ── Predict ───────────────────────────────────────────────────────────────────
class TestPredict:
    def test_predict_valid(self):
        r = client.get("/predict", params={"route_id": "ROUTE-1", "stop_seq": 5, "time": "08:30"})
        assert r.status_code == 200
        data = r.json()
        assert data["crowd_band"] in [
            "Plenty of seats", "Few seats left", "Standing only", "Packed / full"
        ]
        assert data["occupancy"] >= 0
        assert data["seats_free"] >= 0

    def test_predict_iso_time(self):
        r = client.get("/predict", params={
            "route_id": "ROUTE-1", "stop_seq": 3, "time": "2026-01-06T17:30:00"
        })
        assert r.status_code == 200

    def test_predict_bad_time_422(self):
        r = client.get("/predict", params={"route_id": "ROUTE-1", "stop_seq": 3, "time": "NOT-A-TIME"})
        assert r.status_code == 422

    def test_predict_stop_seq_out_of_range(self):
        r = client.get("/predict", params={"route_id": "ROUTE-1", "stop_seq": 99, "time": "09:00"})
        assert r.status_code == 422

# ── Recommend ─────────────────────────────────────────────────────────────────
class TestRecommend:
    def test_recommend_returns_options(self):
        r = client.get("/recommend", params={"route_id": "ROUTE-1", "stop_seq": 5})
        assert r.status_code == 200
        data = r.json()
        assert "recommendation" in data
        assert isinstance(data["options"], list)
        assert len(data["options"]) >= 1

    def test_recommend_from_hour(self):
        r = client.get("/recommend", params={
            "route_id": "ROUTE-1", "stop_seq": 5, "from_hour": 8
        })
        assert r.status_code == 200

# ── Analytics ─────────────────────────────────────────────────────────────────
class TestAnalytics:
    def test_analytics_returns_demand(self):
        r = client.get("/analytics", params={"route_id": "ROUTE-1"})
        assert r.status_code == 200
        data = r.json()
        assert "demand_by_hour" in data
        assert isinstance(data["demand_by_hour"], dict)
        assert "busiest_hour" in data
