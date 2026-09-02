"""
benchmark_api.py - Measure API response times and latency
==========================================================
"""

import time, uuid, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "backend"))
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import create_tables

create_tables()
client = TestClient(app)

def benchmark_endpoint(name, method, url, **kwargs):
    latencies = []
    # Measure 30 iterations
    N = 30
    for i in range(N):
        t0 = time.perf_counter()
        if method == "GET":
            res = client.get(url, **kwargs)
        else:
            payload = kwargs.get("json", {}).copy()
            payload["ticket_id"] = f"BENCH_{uuid.uuid4().hex[:8]}"
            res = client.post(url, json=payload)
        t1 = time.perf_counter()
        if res.status_code not in [200, 201]:
            print(f"Error on {name}: {res.status_code} {res.text}", flush=True)
        latencies.append((t1 - t0) * 1000) # ms
        
    avg = sum(latencies) / len(latencies)
    p95 = sorted(latencies)[int(0.95 * len(latencies))]
    min_lat = min(latencies)
    max_lat = max(latencies)
    
    print(f"| {name:<24} | {avg:>8.2f} ms | {p95:>8.2f} ms | {min_lat:>8.2f} ms | {max_lat:>8.2f} ms |", flush=True)
    return avg, p95

print("\n" + "="*72, flush=True)
print("API LATENCY BENCHMARK (30 sequential requests per endpoint)", flush=True)
print("="*72, flush=True)
print(f"| {'Endpoint':<24} | {'Avg Lat':>11} | {'p95 Lat':>11} | {'Min Lat':>11} | {'Max Lat':>11} |", flush=True)
print("|" + "-"*26 + "|" + "-"*13 + "|" + "-"*13 + "|" + "-"*13 + "|" + "-"*13 + "|", flush=True)

benchmark_endpoint(
    "POST /tickets (Ingest)", "POST", "/tickets",
    json={
        "ticket_id": "BENCH_TKT", "bus_id": "BUS-01", "route_id": "ROUTE-1", "trip_id": "TRIP-01",
        "boarding_stop_seq": 1, "dest_stop_seq": 5, "timestamp": "2026-01-05T08:00:00",
        "passenger_count": 1, "fare": 3.5, "bus_capacity": 50
    }
)

benchmark_endpoint("GET /live (Live Status)", "GET", "/live", params={"bus_id": "BUS-01"})
benchmark_endpoint("GET /predict (ML Infer)", "GET", "/predict", params={"route_id": "ROUTE-1", "stop_seq": 4, "time": "08:30"})
benchmark_endpoint("GET /recommend (Rank)", "GET", "/recommend", params={"route_id": "ROUTE-1", "stop_seq": 4})
benchmark_endpoint("GET /analytics (Agg)", "GET", "/analytics", params={"route_id": "ROUTE-1"})
print("="*72 + "\n", flush=True)
