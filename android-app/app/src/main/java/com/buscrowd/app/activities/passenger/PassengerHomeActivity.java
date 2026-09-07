package com.buscrowd.app.activities.passenger;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.buscrowd.app.AppConfig;
import com.buscrowd.app.R;
import com.buscrowd.app.activities.RoleGateActivity;
import com.buscrowd.app.activities.conductor.ConductorAuthActivity;
import com.buscrowd.app.models.BusStop;
import com.buscrowd.app.services.ApiClient;
import com.buscrowd.app.services.LocationHelper;
import com.buscrowd.app.services.StorageService;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class PassengerHomeActivity extends AppCompatActivity {

    private static final int LOC_PERM_REQUEST = 1001;

    private List<BusStop> stops;
    private Spinner spinnerFrom, spinnerTo;
    private ArrayAdapter<BusStop> stopAdapter;
    private TextView tvRouteBadge, tvRouteName;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_passenger_home);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        spinnerFrom   = findViewById(R.id.spinner_from);
        spinnerTo     = findViewById(R.id.spinner_to);
        tvRouteBadge  = findViewById(R.id.tv_route_badge);
        tvRouteName   = findViewById(R.id.tv_route_name);

        tvRouteBadge.setText(AppConfig.ROUTE_ID);
        tvRouteName.setText(AppConfig.ROUTE_NAME);

        // Load stops with default fallback
        stops = BusStop.getDefaultStops();
        setupSpinners();
        loadStopsFromApi();

        // Swap button
        ImageButton btnSwap = findViewById(R.id.btn_swap);
        btnSwap.setOnClickListener(v -> {
            int fromPos = spinnerFrom.getSelectedItemPosition();
            spinnerFrom.setSelection(spinnerTo.getSelectedItemPosition());
            spinnerTo.setSelection(fromPos);
        });

        // Near Me
        Button btnNearMe = findViewById(R.id.btn_near_me);
        btnNearMe.setOnClickListener(v -> detectNearestStop());

        // Find Buses
        Button btnFind = findViewById(R.id.btn_find_buses);
        btnFind.setOnClickListener(v -> searchBuses());
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_passenger_home, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        int id = item.getItemId();
        if (id == R.id.action_alerts) {
            startActivity(new Intent(this, AlertsActivity.class));
            return true;
        } else if (id == R.id.action_settings) {
            startActivity(new Intent(this, SettingsActivity.class));
            return true;
        } else if (id == R.id.action_conductor) {
            StorageService.setUserRole(this, "conductor");
            startActivity(new Intent(this, ConductorAuthActivity.class));
            finish();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    private void setupSpinners() {
        stopAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, stops);
        stopAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerFrom.setAdapter(stopAdapter);
        spinnerTo.setAdapter(stopAdapter);

        // Default: home stop → stop 5
        int homeSeq = StorageService.getHomeStop(this);
        for (int i = 0; i < stops.size(); i++) {
            if (stops.get(i).stopSeq == homeSeq) { spinnerFrom.setSelection(i); break; }
        }
        spinnerTo.setSelection(Math.min(5, stops.size() - 1));
    }

    private void loadStopsFromApi() {
        ApiClient.get(this).getStops(AppConfig.ROUTE_ID).enqueue(new Callback<List<BusStop>>() {
            @Override
            public void onResponse(@NonNull Call<List<BusStop>> call,
                                   @NonNull Response<List<BusStop>> response) {
                if (response.isSuccessful() && response.body() != null && !response.body().isEmpty()) {
                    stops.clear();
                    stops.addAll(response.body());
                    runOnUiThread(() -> stopAdapter.notifyDataSetChanged());
                }
            }
            @Override public void onFailure(@NonNull Call<List<BusStop>> call, @NonNull Throwable t) {
                // keep defaults
            }
        });
    }

    private void detectNearestStop() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.ACCESS_FINE_LOCATION}, LOC_PERM_REQUEST);
            return;
        }
        LocationHelper.findNearestStop(this, stops, nearest -> {
            if (nearest != null) {
                int idx = stopAdapter.getPosition(nearest);
                if (idx >= 0) spinnerFrom.setSelection(idx);
                Toast.makeText(this,
                        "📍 Nearest stop: " + nearest.stopName + " (Stop " + nearest.stopSeq + ")",
                        Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(this, "Could not detect location", Toast.LENGTH_SHORT).show();
            }
        });
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] perms,
                                           @NonNull int[] results) {
        super.onRequestPermissionsResult(requestCode, perms, results);
        if (requestCode == LOC_PERM_REQUEST && results.length > 0
                && results[0] == PackageManager.PERMISSION_GRANTED) {
            detectNearestStop();
        }
    }

    private void searchBuses() {
        BusStop from = (BusStop) spinnerFrom.getSelectedItem();
        BusStop to   = (BusStop) spinnerTo.getSelectedItem();
        if (from == null || to == null) return;
        if (from.stopSeq >= to.stopSeq) {
            Toast.makeText(this, "Destination must be after boarding stop", Toast.LENGTH_SHORT).show();
            return;
        }
        Intent intent = new Intent(this, RouteResultsActivity.class);
        intent.putExtra("from_seq",  from.stopSeq);
        intent.putExtra("from_name", from.stopName);
        intent.putExtra("to_seq",    to.stopSeq);
        intent.putExtra("to_name",   to.stopName);
        intent.putExtra("route_id",  AppConfig.ROUTE_ID);
        startActivity(intent);
    }
}
