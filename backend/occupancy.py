"""
occupancy.py — Deterministic Occupancy Engine
=============================================
This module is the SINGLE SOURCE OF TRUTH for live seat counts.
It uses pure arithmetic — NO machine-learning — so a model bug can
never corrupt real passenger figures.

Core formula
------------
For a bus trip with `num_stops` stops (numbered 1..num_stops):

    onboard(j) = Σ passenger_count
                 for all tickets where
                 boarding_stop_seq <= j < dest_stop_seq

A passenger boards at stop `boarding_stop_seq` and is on the bus for
every segment up to (but NOT including) `dest_stop_seq`.

Crowd bands (load ratio ρ = onboard / capacity):
    ρ ≤ 0.6         → "Plenty of seats"   (MANY_SEATS_AVAILABLE)
    0.6 < ρ ≤ 1.0   → "Few seats left"    (FEW_SEATS_AVAILABLE)
    1.0 < ρ ≤ 1.3   → "Standing only"     (STANDING_ROOM_ONLY)
    ρ > 1.3         → "Packed / full"     (CRUSHED_SRO)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Crowd band definitions
# ---------------------------------------------------------------------------

class CrowdBand(str, Enum):
    MANY_SEATS   = "Plenty of seats"
    FEW_SEATS    = "Few seats left"
    STANDING     = "Standing only"
    PACKED       = "Packed / full"


def crowd_band(rho: float) -> CrowdBand:
    """Return the GTFS-aligned crowd band for load ratio ρ = onboard / capacity."""
    if rho <= 0.6:
        return CrowdBand.MANY_SEATS
    elif rho <= 1.0:
        return CrowdBand.FEW_SEATS
    elif rho <= 1.3:
        return CrowdBand.STANDING
    else:
        return CrowdBand.PACKED


# ---------------------------------------------------------------------------
# Segment-level result container
# ---------------------------------------------------------------------------

@dataclass
class SegmentState:
    """Occupancy state for one between-stop segment."""
    segment: int          # segment j means "between stop j and stop j+1"
    onboard: int          # number of passengers on the bus
    capacity: int
    seats_free: int       # max(0, capacity - onboard)
    load_ratio: float     # onboard / capacity
    band: CrowdBand


# ---------------------------------------------------------------------------
# Batch (full-trip) computation
# ---------------------------------------------------------------------------

def compute_segment_occupancy(
    tickets: pd.DataFrame,
    num_stops: int,
    capacity: int,
) -> List[SegmentState]:
    """
    Compute occupancy for every segment of a trip from a batch of tickets.

    Parameters
    ----------
    tickets   : DataFrame with at least columns
                  boarding_stop_seq (int), dest_stop_seq (int),
                  passenger_count (int).
    num_stops : Total number of stops on the route (stops are 1..num_stops).
    capacity  : Declared seating + standing capacity of the bus.

    Returns
    -------
    List of SegmentState, one per segment j in 1..(num_stops-1).
    Segment j represents the leg between stop j and stop j+1.
    """
    if tickets.empty:
        # Return zero-occupancy states for all segments
        return [
            _make_state(j, 0, capacity)
            for j in range(1, num_stops)
        ]

    results: List[SegmentState] = []
    for j in range(1, num_stops):          # segment j: stop j → stop j+1
        mask = (
            (tickets["boarding_stop_seq"] <= j) &
            (j < tickets["dest_stop_seq"])
        )
        onboard = int(tickets.loc[mask, "passenger_count"].sum())
        results.append(_make_state(j, onboard, capacity))

    return results


def _make_state(segment: int, onboard: int, capacity: int) -> SegmentState:
    seats_free = max(0, capacity - onboard)
    rho = onboard / capacity if capacity > 0 else 0.0
    return SegmentState(
        segment=segment,
        onboard=onboard,
        capacity=capacity,
        seats_free=seats_free,
        load_ratio=round(rho, 4),
        band=crowd_band(rho),
    )


# ---------------------------------------------------------------------------
# Incremental (streaming) computation — for real-time ingest
# ---------------------------------------------------------------------------

@dataclass
class IncrementalOccupancy:
    """
    Streaming occupancy tracker.

    Usage
    -----
    tracker = IncrementalOccupancy(capacity=50)
    tracker.ingest_ticket(boarding_stop_seq=1, dest_stop_seq=4, passenger_count=3)
    tracker.ingest_ticket(boarding_stop_seq=2, dest_stop_seq=5, passenger_count=2)
    state = tracker.state_at_stop(3)  # how many on-board AT/AFTER stop 3
    """

    capacity: int
    # Internal storage: list of (boarding, dest, count) tuples
    _tickets: List[tuple] = field(default_factory=list, repr=False)

    def ingest_ticket(
        self,
        boarding_stop_seq: int,
        dest_stop_seq: int,
        passenger_count: int = 1,
    ) -> None:
        """Record a single ticket event."""
        if boarding_stop_seq >= dest_stop_seq:
            raise ValueError(
                f"boarding_stop_seq ({boarding_stop_seq}) must be < "
                f"dest_stop_seq ({dest_stop_seq})"
            )
        self._tickets.append((boarding_stop_seq, dest_stop_seq, passenger_count))

    def state_at_segment(self, segment: int) -> SegmentState:
        """
        Return the occupancy state for segment j (between stop j and stop j+1).
        Uses the same formula as compute_segment_occupancy.
        """
        onboard = sum(
            count
            for (board, dest, count) in self._tickets
            if board <= segment < dest
        )
        return _make_state(segment, onboard, self.capacity)

    def snapshot(self, num_stops: int) -> List[SegmentState]:
        """Return SegmentState for all segments 1..(num_stops-1)."""
        return [self.state_at_segment(j) for j in range(1, num_stops)]

    def reset(self) -> None:
        """Clear all ticket data (start a new trip)."""
        self._tickets.clear()

    @property
    def ticket_count(self) -> int:
        return len(self._tickets)


# ---------------------------------------------------------------------------
# Convenience helper used by the API / dashboard
# ---------------------------------------------------------------------------

def occupancy_summary(
    tickets: pd.DataFrame,
    num_stops: int,
    capacity: int,
) -> pd.DataFrame:
    """
    Thin wrapper that returns a tidy DataFrame instead of a list of dataclasses.

    Columns: segment, onboard, seats_free, load_ratio, band
    """
    states = compute_segment_occupancy(tickets, num_stops, capacity)
    return pd.DataFrame(
        [
            {
                "segment":    s.segment,
                "onboard":    s.onboard,
                "seats_free": s.seats_free,
                "load_ratio": s.load_ratio,
                "band":       s.band.value,
            }
            for s in states
        ]
    )
