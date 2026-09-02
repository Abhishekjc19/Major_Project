"""
simulate_live_stream.py - Interactive Live Ticket Streamer
===========================================================
Simulates tickets streaming in real time every few seconds.
Prints a terminal display of buses moving along the route,
updating live seat counts, and showing the ML predictions.

Run:
    python simulate_live_stream.py
"""

import time, random, urllib.request, json
from datetime import datetime

BACKEND_URL = "http://localhost:8000"
ROUTE_ID    = "ROUTE-1"
NUM_STOPS   = 15

STOP_NAMES = [
    "Central Stn", "Market Sq", "Univ Gate", "Hospital", "Tech Park",
    "Old Town", "River Brg", "Sports Cmplx", "Shop Mall", "Res Colony",
    "Ind Area", "Sub North", "Sub East", "Airport Rd", "Airport Term"
]

BUS_IDS = ["BUS-101", "BUS-102", "BUS-103"]

def post_ticket(bus_id, board, dest, count):
    payload = {
        "ticket_id": f"TKT-{int(time.time()*1000)%1000000}",
        "bus_id": bus_id,
        "route_id": ROUTE_ID,
        "trip_id": f"LIVE-TRIP-{datetime.now().strftime('%H%M')}",
        "boarding_stop_seq": board,
        "dest_stop_seq": dest,
        "timestamp": datetime.now().isoformat(),
        "passenger_count": count,
        "fare": round(1.5 + (dest - board) * 0.5, 2),
        "bus_capacity": 50
    }
    req = urllib.request.Request(
        f"{BACKEND_URL}/tickets",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode())
    except Exception as e:
        return None

def get_live(bus_id):
    try:
        with urllib.request.urlopen(f"{BACKEND_URL}/live?bus_id={bus_id}") as res:
            return json.loads(res.read().decode())
    except Exception:
        return None

def get_recommend(stop_seq):
    try:
        with urllib.request.urlopen(f"{BACKEND_URL}/recommend?route_id={ROUTE_ID}&stop_seq={stop_seq}") as res:
            return json.loads(res.read().decode())
    except Exception:
        return None

print("\n" + "="*70)
print("🚌 LIVE TICKET STREAMING SIMULATOR (Press Ctrl+C to stop)")
print("="*70)
print("Connecting to backend at", BACKEND_URL)

try:
    step = 0
    while True:
        step += 1
        bus_id = random.choice(BUS_IDS)
        board  = random.randint(1, NUM_STOPS - 2)
        dest   = random.randint(board + 1, min(NUM_STOPS, board + random.randint(2, 6)))
        count  = random.choices([1, 2, 3, 4], weights=[0.6, 0.25, 0.1, 0.05])[0]

        # Ingest ticket
        res = post_ticket(bus_id, board, dest, count)
        live = get_live(bus_id)

        now_str = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{now_str}] 🎫 Ingested Ticket for {bus_id}:")
        print(f"   Route: {ROUTE_ID} | {board}. {STOP_NAMES[board-1]} -> {dest}. {STOP_NAMES[dest-1]} (+{count} pax)")

        if live:
            onboard = live["onboard"]
            cap = live["capacity"]
            rho = live["load_ratio"]
            band = live["crowd_band"]
            bar_len = int(min(rho, 1.5) * 20)
            bar = "#" * bar_len + "-" * max(0, 20 - bar_len)
            print(f"   📊 Live Occupancy: [{bar}] {onboard}/{cap} pax ({rho*100:.0f}%) -> {band}")

        # Every 3 steps, print a passenger decision recommendation
        if step % 3 == 0:
            rec_stop = random.choice([3, 5, 8])
            rec = get_recommend(rec_stop)
            if rec:
                print(f"   💡 Recommendation @ Stop {rec_stop} ({STOP_NAMES[rec_stop-1]}): {rec['recommendation']}")

        time.sleep(2.5)

except KeyboardInterrupt:
    print("\n\nStream stopped by user. All backend states preserved.")
