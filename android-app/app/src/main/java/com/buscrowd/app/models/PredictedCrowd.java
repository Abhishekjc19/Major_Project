package com.buscrowd.app.models;

import com.google.gson.annotations.SerializedName;

public class PredictedCrowd {

    @SerializedName("route_id")
    public String routeId;

    @SerializedName("stop_seq")
    public int stopSeq;

    @SerializedName("predicted_load")
    public double predictedLoad;

    @SerializedName("crowd_band")
    public String crowdBand;

    /** Label for display e.g. "08:30" — set by client from the request time */
    public String timeLabel;

    public PredictedCrowd() {}
}
