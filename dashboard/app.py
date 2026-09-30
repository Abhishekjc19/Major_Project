"""
dashboard/app.py - Streamlit Authority Dashboard
=================================================
Shows demand analytics for bus operators.

Features:
  - Demand by hour bar chart
  - Crowd level heatmap (stop x hour)
  - Peak-hour summary
  - Busiest segments table

Run:
    streamlit run dashboard/app.py
"""

import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import requests

# ── Config ────────────────────────────────────────────────────────────────────
BACKEND_URL  = "http://localhost:8000"
HIST_PATH    = pathlib.Path(__file__).parent.parent / "datasets" / "occupancy_history.csv"

BAND_COLORS  = {
    "Plenty of seats": "#2ecc71",
    "Few seats left":  "#f39c12",
    "Standing only":   "#e67e22",
    "Packed / full":   "#e74c3c",
}

st.set_page_config(
    page_title="Bus Crowd Dashboard",
    page_icon="🚌",
    layout="wide",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .metric-card {
    background: #1e1e2e; border-radius: 12px; padding: 18px 24px;
    color: white; margin-bottom: 10px;
  }
  .metric-value { font-size: 2.2rem; font-weight: 700; }
  .metric-label { font-size: 0.85rem; color: #aaa; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🚌 Bus Crowd Authority Dashboard")
st.caption("Real-time and historical demand analytics for transport operators")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    route_id = st.selectbox("Route", ["BMTC-500D", "BMTC-335E", "BMTC-356CW", "BMTC-KIAS9"], index=0)
    data_src  = st.radio("Data source", ["Local CSV (offline)", "Backend API (live)"])
    st.divider()
    st.caption("BMTC Bengaluru Route Analytics & Real-Time Passenger Flow.")

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_history() -> pd.DataFrame:
    if HIST_PATH.exists():
        return pd.read_csv(HIST_PATH)
    return pd.DataFrame()

@st.cache_data(ttl=30)
def load_analytics_api(route: str):
    try:
        r = requests.get(f"{BACKEND_URL}/analytics", params={"route_id": route}, timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

df = load_history()

if df.empty:
    st.warning("occupancy_history.csv not found. Run `python datasets/build_training_table.py` first.")
    st.stop()

df_route = df[df["route_id"] == route_id] if "route_id" in df.columns else df

# ── KPI Cards ─────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
avg_onboard  = df_route["onboard"].mean()
peak_df      = df_route[df_route["hour"].between(7, 9) | df_route["hour"].between(17, 19)]
offpeak_df   = df_route[~(df_route["hour"].between(7, 9) | df_route["hour"].between(17, 19))]
max_onboard  = df_route["onboard"].max()
busiest_stop = df_route.groupby("stop_seq")["onboard"].mean().idxmax()

with col1:
    st.metric("Avg Onboard", f"{avg_onboard:.1f} pax")
with col2:
    st.metric("Peak Avg Onboard", f"{peak_df['onboard'].mean():.1f} pax" if not peak_df.empty else "N/A")
with col3:
    st.metric("Off-Peak Avg", f"{offpeak_df['onboard'].mean():.1f} pax" if not offpeak_df.empty else "N/A")
with col4:
    st.metric("Max Onboard Recorded", f"{int(max_onboard)} pax")

st.divider()

# ── Row 1: Demand by Hour ─────────────────────────────────────────────────────
st.subheader("Average Onboard Passengers by Hour of Day")

hour_agg = df_route.groupby("hour")["onboard"].mean().reset_index()
hour_agg.columns = ["Hour", "Avg Onboard"]

fig, ax = plt.subplots(figsize=(12, 4))
colors = ["#e74c3c" if (7 <= h <= 9 or 17 <= h <= 19) else "#3498db"
          for h in hour_agg["Hour"]]
ax.bar(hour_agg["Hour"], hour_agg["Avg Onboard"], color=colors, width=0.7, edgecolor="none")
ax.set_xlabel("Hour of Day", fontsize=11)
ax.set_ylabel("Avg Passengers Onboard", fontsize=11)
ax.set_title("Demand by Hour (red = peak hours)", fontsize=13)
ax.set_xticks(hour_agg["Hour"])
ax.spines[["top","right"]].set_visible(False)
plt.tight_layout()
st.pyplot(fig)
plt.close()

# ── Row 2: Heatmap (stop x hour) ─────────────────────────────────────────────
st.subheader("Crowd Level Heatmap — Stop × Hour")

pivot = df_route.pivot_table(
    index="stop_seq", columns="hour", values="load_ratio", aggfunc="mean"
).fillna(0)

fig2, ax2 = plt.subplots(figsize=(14, 6))
cmap = sns.color_palette("YlOrRd", as_cmap=True)
sns.heatmap(
    pivot, cmap=cmap, linewidths=0.3, linecolor="white",
    annot=False, fmt=".2f", ax=ax2,
    cbar_kws={"label": "Load Ratio (0=empty, 1=full, >1=crush)"}
)
ax2.set_xlabel("Hour of Day")
ax2.set_ylabel("Stop Sequence")
ax2.set_title("Average Load Ratio per Stop per Hour")
plt.tight_layout()
st.pyplot(fig2)
plt.close()

# ── Row 3: Busiest Segments ───────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Top 5 Busiest Stops (avg onboard)")
    stop_avg = (
        df_route.groupby("stop_seq")["onboard"]
        .mean().reset_index()
        .sort_values("onboard", ascending=False)
        .head(5)
    )
    stop_avg.columns = ["Stop Seq", "Avg Onboard"]
    st.dataframe(stop_avg.reset_index(drop=True), use_container_width=True)

with col_b:
    st.subheader("Band Distribution")
    band_counts = df_route["crowd_band"].value_counts().reset_index()
    band_counts.columns = ["Band", "Count"]

    fig3, ax3 = plt.subplots(figsize=(6, 4))
    colors3 = [BAND_COLORS.get(b, "#888") for b in band_counts["Band"]]
    ax3.barh(band_counts["Band"], band_counts["Count"], color=colors3)
    ax3.set_xlabel("Count")
    ax3.set_title("Records per Crowd Band")
    ax3.spines[["top","right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

# ── Row 4: Raw sample ─────────────────────────────────────────────────────────
with st.expander("Show raw occupancy sample (first 50 rows)"):
    st.dataframe(df_route.head(50), use_container_width=True)

st.caption(
    "Dataset is semi-synthetic — generated from a GTFS-like route structure "
    "with demand shaped by time-of-day peaks and day-of-week patterns. "
    "All occupancy labels are computed deterministically by the Occupancy Engine."
)
