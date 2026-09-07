package com.buscrowd.app.activities.passenger;

import android.os.Bundle;
import android.view.MenuItem;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import com.buscrowd.app.AppConfig;
import com.buscrowd.app.R;
import com.buscrowd.app.models.RecommendationResult;
import com.buscrowd.app.services.ApiClient;
import com.buscrowd.app.utils.CrowdUtils;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class AlertsActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_alerts);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setTitle("Crowd Alerts");
        }

        TextView tvAdvice    = findViewById(R.id.tv_alerts_advice);
        TextView tvBestTime  = findViewById(R.id.tv_alerts_best_time);
        TextView tvBestLoad  = findViewById(R.id.tv_alerts_best_load);
        ProgressBar pbLoad   = findViewById(R.id.pb_alerts_loading);

        pbLoad.setVisibility(View.VISIBLE);

        int stopSeq = 1; // default; can be enhanced with current location
        ApiClient.get(this).getRecommendation(AppConfig.ROUTE_ID, stopSeq, null)
                .enqueue(new Callback<RecommendationResult>() {
                    @Override
                    public void onResponse(@NonNull Call<RecommendationResult> call,
                                           @NonNull Response<RecommendationResult> response) {
                        pbLoad.setVisibility(View.GONE);
                        if (response.isSuccessful() && response.body() != null) {
                            RecommendationResult r = response.body();
                            runOnUiThread(() -> {
                                String band = r.getBestCrowdBandDisplay();
                                String time = r.getBestTimeDisplay();
                                String advice = r.getAdvice();
                                int loadPct = r.getBestLoadPercent();

                                tvAdvice.setText("💡 " + advice);
                                tvBestTime.setText("Best time to board: " + time);
                                tvBestLoad.setText(CrowdUtils.crowdLabel(band) + "  (" + loadPct + "% full)");
                                tvBestLoad.setTextColor(CrowdUtils.crowdColor(AlertsActivity.this, band));
                            });
                        }
                    }
                    @Override
                    public void onFailure(@NonNull Call<RecommendationResult> call,
                                          @NonNull Throwable t) {
                        runOnUiThread(() -> {
                            pbLoad.setVisibility(View.GONE);
                            tvAdvice.setText("⚠️ Could not load recommendations. Check server connection.");
                        });
                    }
                });
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        if (item.getItemId() == android.R.id.home) { onBackPressed(); return true; }
        return super.onOptionsItemSelected(item);
    }
}
