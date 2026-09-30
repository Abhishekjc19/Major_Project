package com.buscrowd.app.activities.passenger;

import android.os.Bundle;
import android.view.MenuItem;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.buscrowd.app.R;
import com.buscrowd.app.adapters.CrowdForecastAdapter;
import com.buscrowd.app.models.LiveBusState;
import com.buscrowd.app.models.PredictedCrowd;
import com.buscrowd.app.models.RecommendationResult;
import com.buscrowd.app.services.ApiClient;
import com.buscrowd.app.utils.CrowdUtils;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class RouteResultsActivity extends AppCompatActivity {

    private int fromSeq, toSeq;
    private String routeId, fromName, toName;

    private TextView tvLiveOnboard, tvLiveSeats, tvLiveBand, tvLiveStatus, tvRecommendationAdvice;
    private ProgressBar pbLive, pbLoading;
    private RecyclerView rvForecast;
    private final List<PredictedCrowd> forecastList = new ArrayList<>();
    private CrowdForecastAdapter forecastAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_route_results);

        fromSeq  = getIntent().getIntExtra("from_seq", 1);
        toSeq    = getIntent().getIntExtra("to_seq", 5);
        fromName = getIntent().getStringExtra("from_name");
        toName   = getIntent().getStringExtra("to_name");
        routeId  = getIntent().getStringExtra("route_id");
        if (routeId == null || routeId.trim().isEmpty()) {
            routeId = "BMTC-500D";
        }

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setTitle((fromName != null ? fromName : "Origin") + " → " + (toName != null ? toName : "Destination"));
        }

        tvLiveOnboard         = findViewById(R.id.tv_live_onboard);
        tvLiveSeats           = findViewById(R.id.tv_live_seats);
        tvLiveBand            = findViewById(R.id.tv_live_band);
        tvLiveStatus          = findViewById(R.id.tv_live_status);
        tvRecommendationAdvice= findViewById(R.id.tv_recommendation_advice);
        pbLive                = findViewById(R.id.pb_live_meter);
        pbLoading             = findViewById(R.id.pb_loading);

        rvForecast = findViewById(R.id.rv_forecast);
        rvForecast.setLayoutManager(new LinearLayoutManager(this));
        forecastAdapter = new CrowdForecastAdapter(this, forecastList);
        rvForecast.setAdapter(forecastAdapter);

        loadLiveStatus();
        loadForecast();
        loadRecommendation();
    }

    private void loadLiveStatus() {
        tvLiveStatus.setText("Fetching live status...");
        tvLiveStatus.setVisibility(View.VISIBLE);

        ApiClient.get(this).getLiveStatus("BUS-01").enqueue(new Callback<LiveBusState>() {
            @Override
            public void onResponse(@NonNull Call<LiveBusState> call,
                                   @NonNull Response<LiveBusState> resp) {
                if (resp.isSuccessful() && resp.body() != null) {
                    LiveBusState s = resp.body();
                    runOnUiThread(() -> updateLiveUi(s.onboard, s.seatsFree, s.loadRatio, s.crowdBand, true));
                } else {
                    runOnUiThread(() -> showFallbackLiveStatus());
                }
            }
            @Override public void onFailure(@NonNull Call<LiveBusState> c, @NonNull Throwable t) {
                runOnUiThread(() -> showFallbackLiveStatus());
            }
        });
    }

    private void updateLiveUi(int onboard, int seatsFree, double loadRatio, String crowdBand, boolean isLive) {
        int loadPct = (int) Math.round(loadRatio * 100);
        tvLiveOnboard.setText(String.valueOf(onboard));
        tvLiveSeats.setText(String.valueOf(seatsFree));
        tvLiveBand.setText(CrowdUtils.crowdLabel(crowdBand) + " (" + loadPct + "% full)");
        tvLiveBand.setTextColor(CrowdUtils.crowdColor(this, crowdBand));
        if (isLive) {
            tvLiveStatus.setVisibility(View.GONE);
        } else {
            tvLiveStatus.setText("📡 Estimated Live Status (Offline Mode)");
            tvLiveStatus.setVisibility(View.VISIBLE);
        }
        CrowdUtils.applyCrowdMeter(this, pbLive, loadRatio, crowdBand);
    }

    private void showFallbackLiveStatus() {
        int hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
        boolean isPeak = (hour >= 8 && hour <= 10) || (hour >= 17 && hour <= 19);
        int onboard = isPeak ? 34 : 12;
        int capacity = 50;
        int seatsFree = Math.max(0, capacity - onboard);
        double loadRatio = (double) onboard / capacity;
        String crowdBand = isPeak ? "Few seats left" : "Plenty of seats";

        updateLiveUi(onboard, seatsFree, loadRatio, crowdBand, false);
    }

    private void loadForecast() {
        pbLoading.setVisibility(View.VISIBLE);
        forecastList.clear();

        Calendar cal = Calendar.getInstance();
        int startHour = cal.get(Calendar.HOUR_OF_DAY);
        int startMin  = cal.get(Calendar.MINUTE);
        int[] pending = {4};

        for (int i = 0; i < 4; i++) {
            int offsetMins = i * 30;
            int totalMins = startHour * 60 + startMin + offsetMins;
            int hh = (totalMins / 60) % 24;
            int mm = totalMins % 60;
            String timeStr = String.format("%02d:%02d", hh, mm);
            final String timeLabel = timeStr;
            final int targetHour = hh;

            ApiClient.get(this).getPrediction(routeId, fromSeq, timeStr)
                    .enqueue(new Callback<PredictedCrowd>() {
                        @Override
                        public void onResponse(@NonNull Call<PredictedCrowd> call,
                                               @NonNull Response<PredictedCrowd> resp) {
                            PredictedCrowd item;
                            if (resp.isSuccessful() && resp.body() != null) {
                                item = resp.body();
                            } else {
                                item = generateFallbackPrediction(targetHour);
                            }
                            item.timeLabel = timeLabel;
                            addAndNotifyForecast(item, pending);
                        }

                        @Override public void onFailure(@NonNull Call<PredictedCrowd> c,
                                                        @NonNull Throwable t) {
                            PredictedCrowd item = generateFallbackPrediction(targetHour);
                            item.timeLabel = timeLabel;
                            addAndNotifyForecast(item, pending);
                        }
                    });
        }
    }

    private synchronized void addAndNotifyForecast(PredictedCrowd item, int[] pending) {
        forecastList.add(item);
        pending[0]--;
        if (pending[0] <= 0) {
            runOnUiThread(() -> {
                pbLoading.setVisibility(View.GONE);
                forecastAdapter.notifyDataSetChanged();
            });
        }
    }

    private PredictedCrowd generateFallbackPrediction(int hour) {
        PredictedCrowd p = new PredictedCrowd();
        p.routeId = routeId;
        p.stopSeq = fromSeq;

        boolean isPeak = (hour >= 8 && hour <= 10) || (hour >= 17 && hour <= 19);
        if (isPeak) {
            p.occupancy = 38.0;
            p.predictedLoad = 0.76;
            p.crowdBand = "Few seats left";
            p.seatsFree = 12.0;
        } else {
            p.occupancy = 14.0;
            p.predictedLoad = 0.28;
            p.crowdBand = "Plenty of seats";
            p.seatsFree = 36.0;
        }
        return p;
    }

    private void loadRecommendation() {
        int currentHour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
        ApiClient.get(this).getRecommendation(routeId, fromSeq, currentHour)
                .enqueue(new Callback<RecommendationResult>() {
                    @Override
                    public void onResponse(@NonNull Call<RecommendationResult> call,
                                           @NonNull Response<RecommendationResult> resp) {
                        if (resp.isSuccessful() && resp.body() != null) {
                            RecommendationResult r = resp.body();
                            String adviceText = r.getAdvice();
                            runOnUiThread(() -> tvRecommendationAdvice.setText("💡 " + adviceText));
                        } else {
                            showFallbackRecommendation(currentHour);
                        }
                    }

                    @Override
                    public void onFailure(@NonNull Call<RecommendationResult> call, @NonNull Throwable t) {
                        showFallbackRecommendation(currentHour);
                    }
                });
    }

    private void showFallbackRecommendation(int hour) {
        boolean isPeak = (hour >= 8 && hour <= 10) || (hour >= 17 && hour <= 19);
        String advice;
        if (isPeak) {
            int offPeakHour = (hour + 2) % 24;
            advice = String.format("Smart Travel Advice: High demand expected during peak hours. Departure at %02d:00 recommended for maximum comfort and free seats.", offPeakHour);
        } else {
            advice = "Smart Travel Advice: Off-peak hours detected. Current bus departures on this route have plenty of free seats available.";
        }
        runOnUiThread(() -> tvRecommendationAdvice.setText("💡 " + advice));
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        if (item.getItemId() == android.R.id.home) { onBackPressed(); return true; }
        return super.onOptionsItemSelected(item);
    }
}
