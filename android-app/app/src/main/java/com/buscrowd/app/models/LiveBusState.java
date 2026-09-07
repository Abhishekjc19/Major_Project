package com.buscrowd.app.models;

import com.google.gson.annotations.SerializedName;

public class LiveBusState {

    @SerializedName("bus_id")
    public String busId;

    @SerializedName("route_id")
    public String routeId;

    @SerializedName("trip_id")
    public String tripId;

    @SerializedName("onboard")
    public int onboard;

    @SerializedName("capacity")
    public int capacity;

    @SerializedName("seats_free")
    public int seatsFree;

    @SerializedName("load_ratio")
    public double loadRatio;

    @SerializedName("crowd_band")
    public String crowdBand;

    public LiveBusState() {}
}
