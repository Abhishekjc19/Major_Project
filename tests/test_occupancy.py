"""
test_occupancy.py — pytest suite for the deterministic occupancy engine
=======================================================================
Covers every scenario specified in Phase 1:
  1. Simple hand-computed trip
  2. Simultaneous boarding at one stop
  3. Full turnover at a stop (everyone alights, new passengers board)
  4. Over-capacity case
  5. IncrementalOccupancy streaming tracker
  6. Edge cases: empty ticket list, single-segment route
"""

import pandas as pd
import pytest

# Make sure the backend package is importable when running from project root
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))

from occupancy import (
    CrowdBand,
    IncrementalOccupancy,
    SegmentState,
    compute_segment_occupancy,
    crowd_band,
    occupancy_summary,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_tickets(**kwargs) -> pd.DataFrame:
    """
    Quick factory.  Pass lists for boarding_stop_seq, dest_stop_seq,
    passenger_count.  All three must be the same length.
    """
    return pd.DataFrame(kwargs)


# ---------------------------------------------------------------------------
# Unit tests for crowd_band()
# ---------------------------------------------------------------------------

class TestCrowdBand:
    def test_boundary_many_seats(self):
        assert crowd_band(0.0) == CrowdBand.MANY_SEATS
        assert crowd_band(0.6) == CrowdBand.MANY_SEATS

    def test_boundary_few_seats(self):
        assert crowd_band(0.601) == CrowdBand.FEW_SEATS
        assert crowd_band(1.0)   == CrowdBand.FEW_SEATS

    def test_boundary_standing(self):
        assert crowd_band(1.001) == CrowdBand.STANDING
        assert crowd_band(1.3)   == CrowdBand.STANDING

    def test_boundary_packed(self):
        assert crowd_band(1.301) == CrowdBand.PACKED
        assert crowd_band(2.0)   == CrowdBand.PACKED


# ---------------------------------------------------------------------------
# 1. Simple hand-computed trip
# ---------------------------------------------------------------------------

class TestSimpleTrip:
    """
    Route has 5 stops → 4 segments (1,2,3,4).
    Tickets:
      A: boards stop 1, alights stop 4  → on board for segments 1,2,3
      B: boards stop 2, alights stop 5  → on board for segments 2,3,4
      C: boards stop 3, alights stop 5  → on board for segments 3,4
    capacity = 50

    Expected onboard per segment:
      seg 1 → 2 (A)
      seg 2 → 4 (A+B)
      seg 3 → 6 (A+B+C)
      seg 4 → 4 (B+C)
    """

    @pytest.fixture
    def tickets(self):
        return make_tickets(
            boarding_stop_seq=[1, 2, 3],
            dest_stop_seq    =[4, 5, 5],
            passenger_count  =[2, 2, 2],
        )

    def test_onboard_counts(self, tickets):
        states = compute_segment_occupancy(tickets, num_stops=5, capacity=50)
        onboard = [s.onboard for s in states]
        assert onboard == [2, 4, 6, 4], f"Got {onboard}"

    def test_seats_free(self, tickets):
        states = compute_segment_occupancy(tickets, num_stops=5, capacity=50)
        assert states[2].seats_free == 44   # segment 3: 50 - 6 = 44

    def test_bands(self, tickets):
        states = compute_segment_occupancy(tickets, num_stops=5, capacity=50)
        for s in states:
            # max 6 pax / 50 capacity = 0.12 → all MANY_SEATS
            assert s.band == CrowdBand.MANY_SEATS

    def test_segment_count(self, tickets):
        states = compute_segment_occupancy(tickets, num_stops=5, capacity=50)
        assert len(states) == 4  # num_stops - 1


# ---------------------------------------------------------------------------
# 2. Simultaneous boarding at one stop
# ---------------------------------------------------------------------------

class TestSimultaneousBoarding:
    """
    All 30 passengers board at stop 1, alight at stop 3.
    capacity = 50 → seg 1 & 2 have 30 pax, seg 3+ has 0.
    """

    @pytest.fixture
    def tickets(self):
        return make_tickets(
            boarding_stop_seq=[1] * 10,   # 10 tickets × 3 pax = 30
            dest_stop_seq    =[3] * 10,
            passenger_count  =[3] * 10,
        )

    def test_onboard_segment_1(self, tickets):
        states = compute_segment_occupancy(tickets, num_stops=4, capacity=50)
        assert states[0].onboard == 30   # segment 1

    def test_onboard_segment_2(self, tickets):
        states = compute_segment_occupancy(tickets, num_stops=4, capacity=50)
        assert states[1].onboard == 30   # segment 2

    def test_onboard_segment_3_empty(self, tickets):
        states = compute_segment_occupancy(tickets, num_stops=4, capacity=50)
        assert states[2].onboard == 0    # everyone alighted at stop 3

    def test_load_ratio(self, tickets):
        states = compute_segment_occupancy(tickets, num_stops=4, capacity=50)
        assert states[0].load_ratio == pytest.approx(0.6, abs=1e-4)
        assert states[0].band == CrowdBand.MANY_SEATS   # exactly 0.6 → MANY


# ---------------------------------------------------------------------------
# 3. Full turnover at a stop
# ---------------------------------------------------------------------------

class TestFullTurnover:
    """
    40 passengers board at stop 1, alight at stop 3 (full turnover).
    40 fresh passengers board at stop 3, alight at stop 5.
    capacity = 50.

    Expected:
      seg 1 → 40, seg 2 → 40, seg 3 → 40, seg 4 → 40
      (onboard same but different passengers)
    """

    @pytest.fixture
    def tickets(self):
        return make_tickets(
            boarding_stop_seq=[1, 3],
            dest_stop_seq    =[3, 5],
            passenger_count  =[40, 40],
        )

    def test_all_segments_onboard(self, tickets):
        states = compute_segment_occupancy(tickets, num_stops=5, capacity=50)
        onboard = [s.onboard for s in states]
        assert onboard == [40, 40, 40, 40]

    def test_seg2_empty_before_reboard(self, tickets):
        """Segment 2 (between stops 2-3) has only the first group."""
        states = compute_segment_occupancy(tickets, num_stops=5, capacity=50)
        assert states[1].onboard == 40   # first group still on, second not yet boarded

    def test_bands_few_seats(self, tickets):
        """40/50 = 0.80 → FEW_SEATS_AVAILABLE for all segments."""
        states = compute_segment_occupancy(tickets, num_stops=5, capacity=50)
        for s in states:
            assert s.band == CrowdBand.FEW_SEATS

    def test_seats_free(self, tickets):
        states = compute_segment_occupancy(tickets, num_stops=5, capacity=50)
        for s in states:
            assert s.seats_free == 10


# ---------------------------------------------------------------------------
# 4. Over-capacity case
# ---------------------------------------------------------------------------

class TestOverCapacity:
    """
    70 passengers on a 50-seat bus → ρ = 1.4 → PACKED.
    seats_free must be clamped to 0 (never negative).
    """

    @pytest.fixture
    def tickets(self):
        return make_tickets(
            boarding_stop_seq=[1],
            dest_stop_seq    =[4],
            passenger_count  =[70],
        )

    def test_onboard_exceeds_capacity(self, tickets):
        states = compute_segment_occupancy(tickets, num_stops=4, capacity=50)
        assert states[0].onboard == 70

    def test_seats_free_clamped_to_zero(self, tickets):
        states = compute_segment_occupancy(tickets, num_stops=4, capacity=50)
        for s in states[:2]:   # segments 1 and 2 (70 pax on board)
            assert s.seats_free == 0

    def test_band_packed(self, tickets):
        states = compute_segment_occupancy(tickets, num_stops=4, capacity=50)
        assert states[0].band == CrowdBand.PACKED

    def test_load_ratio_over_one(self, tickets):
        states = compute_segment_occupancy(tickets, num_stops=4, capacity=50)
        assert states[0].load_ratio == pytest.approx(1.4, abs=1e-4)


# ---------------------------------------------------------------------------
# 5. IncrementalOccupancy streaming tracker
# ---------------------------------------------------------------------------

class TestIncrementalOccupancy:
    def test_ingest_and_query(self):
        tracker = IncrementalOccupancy(capacity=50)
        tracker.ingest_ticket(1, 4, 10)
        tracker.ingest_ticket(2, 5, 15)
        # segment 2 → both tickets active → 25
        s = tracker.state_at_segment(2)
        assert s.onboard == 25
        assert s.seats_free == 25

    def test_matches_batch(self):
        """Incremental and batch must return identical results."""
        df = make_tickets(
            boarding_stop_seq=[1, 2, 1, 3],
            dest_stop_seq    =[3, 5, 5, 4],
            passenger_count  =[5, 3, 7, 2],
        )
        tracker = IncrementalOccupancy(capacity=60)
        for _, row in df.iterrows():
            tracker.ingest_ticket(
                int(row.boarding_stop_seq),
                int(row.dest_stop_seq),
                int(row.passenger_count),
            )
        batch_states  = compute_segment_occupancy(df, num_stops=6, capacity=60)
        stream_states = tracker.snapshot(num_stops=6)
        for b, s in zip(batch_states, stream_states):
            assert b.onboard == s.onboard, f"Mismatch at segment {b.segment}"

    def test_invalid_ticket_raises(self):
        tracker = IncrementalOccupancy(capacity=50)
        with pytest.raises(ValueError):
            tracker.ingest_ticket(3, 3, 5)   # board == dest → invalid

    def test_reset(self):
        tracker = IncrementalOccupancy(capacity=50)
        tracker.ingest_ticket(1, 4, 10)
        tracker.reset()
        s = tracker.state_at_segment(1)
        assert s.onboard == 0
        assert tracker.ticket_count == 0


# ---------------------------------------------------------------------------
# 6. Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_ticket_list(self):
        df = make_tickets(
            boarding_stop_seq=[], dest_stop_seq=[], passenger_count=[]
        )
        states = compute_segment_occupancy(df, num_stops=5, capacity=50)
        assert all(s.onboard == 0 for s in states)
        assert all(s.band == CrowdBand.MANY_SEATS for s in states)

    def test_single_segment_route(self):
        df = make_tickets(
            boarding_stop_seq=[1], dest_stop_seq=[2], passenger_count=[10]
        )
        states = compute_segment_occupancy(df, num_stops=2, capacity=50)
        assert len(states) == 1
        assert states[0].onboard == 10

    def test_occupancy_summary_dataframe(self):
        df = make_tickets(
            boarding_stop_seq=[1, 2],
            dest_stop_seq    =[4, 5],
            passenger_count  =[20, 15],
        )
        summary = occupancy_summary(df, num_stops=5, capacity=50)
        assert list(summary.columns) == [
            "segment", "onboard", "seats_free", "load_ratio", "band"
        ]
        assert len(summary) == 4  # 5 stops → 4 segments
