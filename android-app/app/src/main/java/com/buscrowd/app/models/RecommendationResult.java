package com.buscrowd.app.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class RecommendationResult {

    @SerializedName("route_id")
    public String routeId;

    @SerializedName("stop_seq")
    public int stopSeq;

    @SerializedName("recommendation")
    public String recommendation;

    @SerializedName("advice")
    public String advice;

    @SerializedName("best_hour")
    public Integer bestHour;

    @SerializedName("best_load")
    public Double bestLoad;

    @SerializedName("crowd_band")
    public String crowdBand;

    @SerializedName("options")
    public List<TripOption> options;

    public static class TripOption {
        @SerializedName("trip_id")
        public String tripId;

        @SerializedName("departure_time")
        public String departureTime;

        @SerializedName("predicted_band")
        public String predictedBand;

        @SerializedName("predicted_load")
        public double predictedLoad;

        @SerializedName("seats_free")
        public double seatsFree;
    }

    public String getAdvice() {
        if (recommendation != null && !recommendation.trim().isEmpty()) {
            return recommendation;
        }
        if (advice != null && !advice.trim().isEmpty()) {
            return advice;
        }
        return "Board the next bus — plenty of seats available.";
    }

    public TripOption getBestOption() {
        if (options != null && !options.isEmpty()) {
            TripOption best = options.get(0);
            for (TripOption o : options) {
                if (o.predictedLoad < best.predictedLoad) {
                    best = o;
                }
            }
            return best;
        }
        return null;
    }

    public String getBestTimeDisplay() {
        TripOption best = getBestOption();
        if (best != null && best.departureTime != null) {
            return best.departureTime;
        }
        if (bestHour != null) {
            return String.format("%02d:00", bestHour);
        }
        return "Next Bus";
    }

    public String getBestCrowdBandDisplay() {
        TripOption best = getBestOption();
        if (best != null && best.predictedBand != null) {
            return best.predictedBand;
        }
        if (crowdBand != null) {
            return crowdBand;
        }
        return "Plenty of seats";
    }

    public int getBestLoadPercent() {
        TripOption best = getBestOption();
        if (best != null) {
            // capacity is 50
            return (int) Math.round((best.predictedLoad / 50.0) * 100.0);
        }
        if (bestLoad != null) {
            return (int) Math.round(bestLoad * 100.0);
        }
        return 25;
    }
}
