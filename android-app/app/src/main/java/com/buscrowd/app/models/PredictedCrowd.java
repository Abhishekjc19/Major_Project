package com.buscrowd.app.models;

import com.google.gson.annotations.SerializedName;

public class PredictedCrowd {

    @SerializedName("route_id")
    public String routeId;

    @SerializedName("stop_seq")
    public int stopSeq;

    @SerializedName("occupancy")
    public double occupancy;

    @SerializedName("predicted_load")
    public double predictedLoad;

    @SerializedName("crowd_band")
    public String crowdBand;

    @SerializedName("seats_free")
    public double seatsFree;

    /** Label for display e.g. "08:30" — set by client from the request time */
    public String timeLabel;

    public PredictedCrowd() {}

    public double getLoadRatio() {
        if (occupancy > 0) {
            return Math.min(1.5, occupancy / 50.0);
        }
        if (predictedLoad > 0) {
            return Math.min(1.5, predictedLoad);
        }
        return 0.25;
    }
}
