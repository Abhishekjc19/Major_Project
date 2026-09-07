package com.buscrowd.app.models;

import com.google.gson.annotations.SerializedName;

import java.util.ArrayList;
import java.util.List;

public class BusStop {

    @SerializedName("stop_seq")
    public int stopSeq;

    @SerializedName("stop_name")
    public String stopName;

    @SerializedName("lat")
    public double lat;

    @SerializedName("lng")
    public double lng;

    public BusStop() {}

    public BusStop(int stopSeq, String stopName, double lat, double lng) {
        this.stopSeq  = stopSeq;
        this.stopName = stopName;
        this.lat      = lat;
        this.lng      = lng;
    }

    @Override
    public String toString() {
        return stopSeq + ". " + stopName;
    }

    /** Default 15-stop list shown when the API is unreachable. */
    public static List<BusStop> getDefaultStops() {
        List<BusStop> stops = new ArrayList<>();
        stops.add(new BusStop(1,  "City Centre Terminal",   12.9716, 77.5946));
        stops.add(new BusStop(2,  "Market Square",          12.9726, 77.5956));
        stops.add(new BusStop(3,  "Central Park",           12.9740, 77.5970));
        stops.add(new BusStop(4,  "University Gate",        12.9755, 77.5985));
        stops.add(new BusStop(5,  "Hospital Junction",      12.9770, 77.6000));
        stops.add(new BusStop(6,  "Tech Hub",               12.9785, 77.6015));
        stops.add(new BusStop(7,  "Industrial Zone",        12.9800, 77.6030));
        stops.add(new BusStop(8,  "Residential Area",       12.9815, 77.6045));
        stops.add(new BusStop(9,  "Shopping Mall",          12.9830, 77.6060));
        stops.add(new BusStop(10, "Sports Complex",         12.9845, 77.6075));
        stops.add(new BusStop(11, "Outer Ring Road",        12.9860, 77.6090));
        stops.add(new BusStop(12, "Satellite Town",         12.9875, 77.6105));
        stops.add(new BusStop(13, "Airport Road Junction",  12.9890, 77.6120));
        stops.add(new BusStop(14, "Airport Check-In",       12.9905, 77.6135));
        stops.add(new BusStop(15, "Airport Terminal",       12.9920, 77.6150));
        return stops;
    }
}
