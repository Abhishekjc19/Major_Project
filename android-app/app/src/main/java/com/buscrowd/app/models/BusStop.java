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

    /** Default BMTC Bengaluru stops list shown when the API is offline. */
    public static List<BusStop> getDefaultStops() {
        List<BusStop> stops = new ArrayList<>();
        stops.add(new BusStop(1,  "Central Silk Board Junction",      12.9172, 77.6228));
        stops.add(new BusStop(2,  "HSR Layout BDA Complex",          12.9116, 77.6389));
        stops.add(new BusStop(3,  "Agara Junction",                  12.9257, 77.6483));
        stops.add(new BusStop(4,  "Iblur Bus Stop",                  12.9238, 77.6625));
        stops.add(new BusStop(5,  "Bellandur EcoSpace",              12.9282, 77.6821));
        stops.add(new BusStop(6,  "Kadubeesanahalli",                12.9372, 77.6934));
        stops.add(new BusStop(7,  "Marathahalli Bridge",             12.9569, 77.7011));
        stops.add(new BusStop(8,  "ISRO Junction",                   12.9642, 77.6965));
        stops.add(new BusStop(9,  "Mahadevapura",                    12.9881, 77.6983));
        stops.add(new BusStop(10, "Tin Factory",                     12.9964, 77.6698));
        stops.add(new BusStop(11, "Kasturi Nagar",                   13.0083, 77.6534));
        stops.add(new BusStop(12, "Kalyan Nagar HRBR Layout",        13.0234, 77.6412));
        stops.add(new BusStop(13, "Nagawara Junction",               13.0418, 77.6189));
        stops.add(new BusStop(14, "Hebbal Flyover Bus Stop",         13.0359, 77.5970));
        stops.add(new BusStop(15, "Kempegowda Int. Airport (KIAS)", 13.1986, 77.7066));
        return stops;
    }
}
