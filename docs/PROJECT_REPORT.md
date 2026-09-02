# Comprehensive Project Report: AI-Based Real-Time Bus Crowd Prediction & Decision Support System

## 1. Abstract
Public transportation systems frequently suffer from crowded buses and passenger uncertainty. Existing solutions rely heavily on expensive hardware like infrared passenger counters or CCTV camera networks, which face high deployment costs, occlusions, privacy concerns, and sensor failures. This project proposes a hardware-free, zero-sensor solution: leveraging electronic ticketing transactions (origin-destination ticketing stream) to deterministically compute live onboard bus crowd with zero error, while utilizing temporal machine learning (XGBoost & Keras LSTM) to forecast future crowd levels and provide proactive decision support to waiting passengers.

---

## 2. Problem Statement & Mathematical Formulation

### 2.1 The Occupancy Engine (Deterministic Formulation)
Let a bus route consist of $N$ ordered stops $S = \{s_1, s_2, \dots, s_N\}$.
A trip comprises a stream of electronic tickets $T = \{t_1, t_2, \dots, t_K\}$.
Each ticket $t_i$ contains:
- $b_i$: Boarding stop sequence index ($1 \le b_i < N$)
- $d_i$: Destination stop sequence index ($b_i < d_i \le N$)
- $c_i$: Passenger count associated with ticket $t_i$

The exact number of passengers on board during segment $j$ (the transit corridor between stop $s_j$ and stop $s_{j+1}$) is given by:

$$\text{onboard}(j) = \sum_{i=1}^{K} c_i \cdot \mathbb{I}(b_i \le j < d_i)$$

Where $\mathbb{I}(\cdot)$ is the indicator function.

### 2.2 Free Seats & Load Ratio
Given declared bus capacity $C$:
$$\text{seats\_free}(j) = \max(0, C - \text{onboard}(j))$$
$$\rho(j) = \frac{\text{onboard}(j)}{C}$$

### 2.3 Crowd Bands (GTFS-Realtime Specification)
- $\rho \le 0.60 \implies \text{Plenty of seats}$ (`MANY_SEATS_AVAILABLE`)
- $0.60 < \rho \le 1.00 \implies \text{Few seats left}$ (`FEW_SEATS_AVAILABLE`)
- $1.00 < \rho \le 1.30 \implies \text{Standing only}$ (`STANDING_ROOM_ONLY`)
- $\rho > 1.30 \implies \text{Packed / full}$ (`CRUSHED_SRO` / `FULL`)

---

## 3. Machine Learning Methodology

### 3.1 Feature Engineering
To capture periodic transit demand patterns without temporal leakage:
1. **Cyclic Time Encodings**:
   $$\text{hour\_sin} = \sin\left(\frac{2\pi \cdot \text{hour}}{24}\right), \quad \text{hour\_cos} = \cos\left(\frac{2\pi \cdot \text{hour}}{24}\right)$$
   $$\text{dow\_sin} = \sin\left(\frac{2\pi \cdot \text{dow}}{7}\right), \quad \text{dow\_cos} = \cos\left(\frac{2\pi \cdot \text{dow}}{7}\right)$$
2. **Binary Domain Indicators**: $\text{is\_peak}$ (7–9h & 17–19h), $\text{is\_weekend}$.
3. **Lag & Trend Features**: $\text{lag}_1, \text{lag}_2$, and 3-trip rolling mean for the same stop slot.

### 3.2 Chronological Validation
Data is strictly split chronologically (70% Train, 15% Validation, 15% Test) without time shuffling to mirror real-world deployment.

---

## 4. Experimental Results & Discussion

### 4.1 Comparative Model Performance

| Metric | XGBoost | LSTM (Keras) | Remarks |
|---|---|---|---|
| **Classification Accuracy** | 70.88% | **75.18%** | LSTM captures multi-step sequential dependencies better |
| **Weighted F1 Score** | 0.6700 | **0.7007** | Superior performance across rare extreme classes |
| **Regression MAE** | **3.352 pax** | 3.356 pax | Both models predict within ~3.3 passengers of true count |
| **Regression RMSE** | **4.713 pax** | 4.911 pax | XGBoost achieves slightly lower variance in extreme residuals |

### 4.2 API Latency & Engineering Benchmarks
- Live Bus State Retrieval: **8.76 ms** (p95: 15.20 ms)
- Ticket Ingestion & Validation: **17.19 ms** (p95: 35.82 ms)
- Real-time ML Prediction: **144.62 ms** (p95: 336.06 ms)
- Automated Trip Recommendation: **336.35 ms** (p95: 561.20 ms)

---

## 5. Conclusion & Future Scope
The system proves that electronic ticketing data is sufficient to operate a real-time crowd tracking and prediction engine without hardware instrumentation. Future work includes integrating GTFS-RT GPS feeds for dynamic delay adjustments and multi-modal transit graph routing.
