package com.buscrowd.app.services;

import com.buscrowd.app.models.BusStop;
import com.buscrowd.app.models.LiveBusState;
import com.buscrowd.app.models.PredictedCrowd;
import com.buscrowd.app.models.RecommendationResult;

import java.util.List;
import java.util.Map;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.GET;
import retrofit2.http.Header;
import retrofit2.http.POST;
import retrofit2.http.Query;

public interface ApiInterface {

    // 1. Health check
    @GET("/health")
    Call<Map<String, Object>> checkHealth();

    // 2. GET /stops
    @GET("/stops")
    Call<List<BusStop>> getStops(@Query("route_id") String routeId);

    // 3. GET /live
    @GET("/live")
    Call<LiveBusState> getLiveStatus(@Query("bus_id") String busId);

    // 4. POST /tickets
    @POST("/tickets")
    Call<Map<String, Object>> postTicket(
            @Header("X-Conductor-Api-Key") String apiKey,
            @Body Map<String, Object> body
    );

    // 5. GET /predict
    @GET("/predict")
    Call<PredictedCrowd> getPrediction(
            @Query("route_id") String routeId,
            @Query("stop_seq") int stopSeq,
            @Query("time") String time
    );

    // 6. GET /recommend
    @GET("/recommend")
    Call<RecommendationResult> getRecommendation(
            @Query("route_id") String routeId,
            @Query("stop_seq") int stopSeq,
            @Query("from_hour") Integer fromHour
    );

    // 7. GET /analytics
    @GET("/analytics")
    Call<Map<String, Object>> getAnalytics(@Query("route_id") String routeId);
}
