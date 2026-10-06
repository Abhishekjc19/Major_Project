"""
schemas.py - Pydantic request/response models
"""
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional

class TicketIn(BaseModel):
    ticket_id:         str
    bus_id:            str
    route_id:          str
    trip_id:           str
    boarding_stop_seq: int = Field(..., ge=1)
    dest_stop_seq:     int = Field(..., ge=2)
    timestamp:         datetime
    passenger_count:   int = Field(1, ge=1, le=200)
    fare:              float = Field(0.0, ge=0)
    bus_capacity:      int = Field(50, ge=1, le=300)

    @model_validator(mode="after")
    def board_before_dest(self):
        if self.boarding_stop_seq >= self.dest_stop_seq:
            raise ValueError(
                f"boarding_stop_seq ({self.boarding_stop_seq}) must be "
                f"< dest_stop_seq ({self.dest_stop_seq})"
            )
        return self

class TicketOut(BaseModel):
    ticket_id:    str
    trip_id:      str
    route_id:     str
    onboard_now:  int
    seats_free:   int
    crowd_band:   str

class LiveStatusOut(BaseModel):
    bus_id:           str
    route_id:         str
    trip_id:          str
    onboard:          int
    capacity:         int
    seats_free:       int
    extra_passengers: int = 0
    load_ratio:       float
    crowd_band:       str
    comfort_advisory: str = "Boarding decisions rest entirely on your personal travel comfort."

class PredictOut(BaseModel):
    route_id:    str
    stop_seq:    int
    hour:        int
    crowd_band:  str
    occupancy:   float
    seats_free:  float

class TripOption(BaseModel):
    trip_id:        str
    departure_time: str
    predicted_band: str
    predicted_load: float
    seats_free:     float

class RecommendOut(BaseModel):
    route_id:       str
    stop_seq:       int
    recommendation: str
    options:        list[TripOption]

class AnalyticsOut(BaseModel):
    route_id:      str
    demand_by_hour: dict
    busiest_hour:   int
    quietest_hour:  int
