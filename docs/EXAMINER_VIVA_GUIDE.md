# Final-Year Project Viva & Examiner Q&A Guide

Use this cheat sheet to confidently answer questions from project reviewers, professors, and external examiners.

---

### Q1: Why not use cameras, OpenCV, or YOLO on the bus?
> **Answer:** "Cameras and computer vision systems require expensive edge hardware on every bus, suffer from camera occlusions during rush hours, have lens dirt/lighting issues, consume high power, and raise severe passenger privacy/GDPR concerns. Our approach uses the **existing ticketing infrastructure** with zero added hardware cost, zero maintenance, and 100% mathematical precision for live occupancy."

---

### Q2: How does the Occupancy Engine work without machine learning?
> **Answer:** "Every ticket explicitly specifies the **origin stop** and **destination stop**. For any segment $j$ along the route, a passenger is physically on board if and only if their $\text{boarding\_stop} \le j < \text{dest\_stop}$. We simply take the sum of active passengers. This is a deterministic closed-form calculation, ensuring a model hallucination or prediction error can never corrupt the real-time seat availability."

---

### Q3: Where does Machine Learning come in?
> **Answer:** "Machine learning is used **strictly for predicting future crowd levels** before a bus arrives (e.g. predicting if the 8:30 bus will have seats at stop 7). We trained both **XGBoost** and a sequential **Keras LSTM** using cyclical time features (sine/cosine of hour and day) and historical lag features. LSTM achieved **75.18% accuracy** in crowd band classification."

---

### Q4: How did you prevent data leakage during model training?
> **Answer:** "We implemented a strict **chronological split** (Train $\to$ Validation $\to$ Test across successive time periods) without random shuffling across dates. This ensures the model only learns from the past and is tested on unseen future days, exactly as in production."

---

### Q5: What if a passenger buys a ticket but gets off early or late?
> **Answer:** "In public bus systems, destination compliance is high due to fare verification. However, for edge cases, transit authorities apply periodic calibration constants (turnover rates), which our `IncrementalOccupancy` engine supports seamlessly."

---

### Q6: How does the Recommendation feature work?
> **Answer:** "When a user queries `/recommend?route_id=...&stop_seq=...`, the backend queries the ML model for all upcoming departures in a 90-minute window, ranks them by predicted occupancy, and delivers actionable guidance — such as recommending skipping a packed bus if an empty bus arrives 15 minutes later."

---

### Q7: What are the GTFS-aligned crowd bands?
> **Answer:** "We aligned our crowd categories with the official General Transit Feed Specification (GTFS-Realtime) occupancy standard:
> 1. $\rho \le 0.60$: *Plenty of seats* (`MANY_SEATS_AVAILABLE`)
> 2. $0.60 < \rho \le 1.00$: *Few seats left* (`FEW_SEATS_AVAILABLE`)
> 3. $1.00 < \rho \le 1.30$: *Standing only* (`STANDING_ROOM_ONLY`)
> 4. $\rho > 1.30$: *Packed / full* (`CRUSHED_SRO` / `FULL`)"

---

### Q8: What is the system's response latency?
> **Answer:** "Our automated benchmark measured an average latency of **8.76 ms** for live bus state queries, **17.19 ms** for ticket ingestion, and **144.62 ms** for real-time ML inference."
