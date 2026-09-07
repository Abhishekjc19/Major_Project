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

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setTitle(fromName + " → " + toName);
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
        ApiClient.get(this).getLiveStatus("BUS-01").enqueue(new Callback<LiveBusState>() {
            @Override
            public void onResponse(@NonNull Call<LiveBusState> call,
                                   @NonNull Response<LiveBusState> resp) {
                if (resp.isSuccessful() && resp.body() != null) {
                    LiveBusState s = resp.body();
                    runOnUiThread(() -> {
                        tvLiveOnboard.setText(String.valueOf(s.onboard));
                        tvLiveSeats.setText(String.valueOf(s.seatsFree));
                        tvLiveBand.setText(CrowdUtils.crowdLabel(s.crowdBand));
                        tvLiveBand.setTextColor(CrowdUtils.crowdColor(RouteResultsActivity.this, s.crowdBand));
                        tvLiveStatus.setVisibility(View.GONE);
                        CrowdUtils.applyCrowdMeter(RouteResultsActivity.this, pbLive, s.loadRatio, s.crowdBand);
                    });
                }
            }
            @Override public void onFailure(@NonNull Call<LiveBusState> c, @NonNull Throwable t) {
                runOnUiThread(() -> tvLiveStatus.setText("⚠️ Live data unavailable"));
            }
        });
    }

    private void loadForecast() {
        pbLoading.setVisibility(View.VISIBLE);
        Calendar cal = Calendar.getInstance();
        int startHour = cal.get(Calendar.HOUR_OF_DAY);
        int pending[] = {4};  // fetch next 4 half-hour slots

        for (int i = 0; i < 4; i++) {
            int offsetMins = i * 30;
            int totalMins = startHour * 60 + cal.get(Calendar.MINUTE) + offsetMins;
            int hh = (totalMins / 60) % 24;
            int mm = totalMins % 60;
            String timeStr = String.format("%02d:%02d", hh, mm);
            final String timeLabel = timeStr;

            ApiClient.get(this).getPrediction(routeId, fromSeq, timeStr)
                    .enqueue(new Callback<PredictedCrowd>() {
                        @Override
                        public void onResponse(@NonNull Call<PredictedCrowd> call,
                                               @NonNull Response<PredictedCrowd> resp) {
                            pending[0]--;
                            if (resp.isSuccessful() && resp.body() != null) {
                                resp.body().timeLabel = timeLabel;
                                forecastList.add(resp.body());
                            }
                            if (pending[0] == 0) {
                                runOnUiThread(() -> {
                                    pbLoading.setVisibility(View.GONE);
                                    forecastAdapter.notifyDataSetChanged();
                                });
                            }
                        }
                        @Override public void onFailure(@NonNull Call<PredictedCrowd> c,
                                                        @NonNull Throwable t) {
                            pending[0]--;
                            if (pending[0] == 0) runOnUiThread(() -> pbLoading.setVisibility(View.GONE));
                        }
                    });
        }
    }

    private void loadRecommendation() {
        int currentHour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
        ApiClient.get(this).getRecommendation(routeId, fromSeq, currentHour)
                .enqueue(new Callback<RecommendationResult>() {
                    @Override
                    public void onResponse(@NonNull Call<RecommendationResult> call,
                                           @NonNull Response<RecommendationResult> resp) {
                        if (resp.isSuccessful() && resp.body() != null && resp.body().advice != null) {
                            final String adviceText = resp.body().advice;
                            runOnUiThread(() -> tvRecommendationAdvice.setText(adviceText));
                        }
                    }

                    @Override
                    public void onFailure(@NonNull Call<RecommendationResult> call, @NonNull Throwable t) {
                        runOnUiThread(() -> tvRecommendationAdvice.setText("💡 Smart Travel Advice: Recommended departure during off-peak hours for maximum comfort and seat availability."));
                    }
                });
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        if (item.getItemId() == android.R.id.home) { onBackPressed(); return true; }
        return super.onOptionsItemSelected(item);
    }
}
