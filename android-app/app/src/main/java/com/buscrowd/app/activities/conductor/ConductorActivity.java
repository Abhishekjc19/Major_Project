package com.buscrowd.app.activities.conductor;

import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ProgressBar;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import com.buscrowd.app.AppConfig;
import com.buscrowd.app.R;
import com.buscrowd.app.activities.passenger.PassengerHomeActivity;
import com.buscrowd.app.models.BusStop;
import com.buscrowd.app.models.ConductorTicket;
import com.buscrowd.app.models.LiveBusState;
import com.buscrowd.app.services.ApiClient;
import com.buscrowd.app.services.OfflineQueueService;
import com.buscrowd.app.services.StorageService;
import com.buscrowd.app.utils.CrowdUtils;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ConductorActivity extends AppCompatActivity {

    private static final String BUS_ID = "BUS-01";

    private List<BusStop> stops = BusStop.getDefaultStops();
    private List<ConductorTicket> recentTickets = new ArrayList<>();

    private Spinner spinnerBoarding, spinnerDest;
    private ArrayAdapter<BusStop> stopAdapter;

    private TextView tvOnboard, tvSeatsFree, tvCrowdBand, tvFare;
    private TextView tvOfflineBanner;
    private ProgressBar pbCrowd;
    private Button btnIssue, btnSync;
    private ImageButton btnMinus, btnPlus;
    private TextView tvPassengerCount;

    private int passengerCount = 1;
    private int liveOnboard = 0;
    private int busCapacity = AppConfig.DEFAULT_CAPACITY;
    private int seatsFree = AppConfig.DEFAULT_CAPACITY;
    private double loadRatio = 0.0;
    private String crowdBand = "Plenty of seats";
    private String tripId;
    private int offlineCount = 0;

    private final ExecutorService executor = Executors.newSingleThreadExecutor();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_conductor);

        tripId = CrowdUtils.generateTripId();

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle("Conductor Terminal");
            getSupportActionBar().setSubtitle(BUS_ID + " • " + AppConfig.ROUTE_ID);
        }

        // Views
        spinnerBoarding    = findViewById(R.id.spinner_boarding);
        spinnerDest        = findViewById(R.id.spinner_dest);
        tvOnboard          = findViewById(R.id.tv_conductor_onboard);
        tvSeatsFree        = findViewById(R.id.tv_conductor_seats_free);
        tvCrowdBand        = findViewById(R.id.tv_conductor_crowd_band);
        tvFare             = findViewById(R.id.tv_conductor_fare);
        tvPassengerCount   = findViewById(R.id.tv_passenger_count);
        tvOfflineBanner    = findViewById(R.id.tv_offline_banner);
        pbCrowd            = findViewById(R.id.pb_conductor_crowd);
        btnIssue           = findViewById(R.id.btn_issue_ticket);
        btnSync            = findViewById(R.id.btn_sync_offline);
        btnMinus           = findViewById(R.id.btn_minus);
        btnPlus            = findViewById(R.id.btn_plus);

        // Spinners
        stopAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, stops);
        stopAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerBoarding.setAdapter(stopAdapter);
        spinnerDest.setAdapter(stopAdapter);
        spinnerDest.setSelection(Math.min(4, stops.size() - 1));

        // Passenger stepper
        btnMinus.setOnClickListener(v -> {
            if (passengerCount > 1) { passengerCount--; updateFareDisplay(); }
        });
        btnPlus.setOnClickListener(v -> {
            if (passengerCount < 10) { passengerCount++; updateFareDisplay(); }
        });

        btnIssue.setOnClickListener(v -> issueTicket());
        btnSync.setOnClickListener(v -> syncOfflineQueue());

        // Spinner change → update fare
        spinnerBoarding.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(android.widget.AdapterView<?> parent, View view, int pos, long id) { updateFareDisplay(); }
            @Override public void onNothingSelected(android.widget.AdapterView<?> parent) {}
        });
        spinnerDest.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(android.widget.AdapterView<?> parent, View view, int pos, long id) { updateFareDisplay(); }
            @Override public void onNothingSelected(android.widget.AdapterView<?> parent) {}
        });

        initData();
        updateFareDisplay();
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_conductor, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        int id = item.getItemId();
        if (id == R.id.action_history) {
            Intent i = new Intent(this, ConductorHistoryActivity.class);
            i.putExtra("ticket_count", recentTickets.size());
            startActivity(i);
            return true;
        } else if (id == R.id.action_switch_passenger) {
            StorageService.setUserRole(this, "passenger");
            startActivity(new Intent(this, PassengerHomeActivity.class));
            finish();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    private void initData() {
        // Load stops
        ApiClient.get(this).getStops(AppConfig.ROUTE_ID).enqueue(new Callback<List<BusStop>>() {
            @Override
            public void onResponse(@NonNull Call<List<BusStop>> c, @NonNull Response<List<BusStop>> r) {
                if (r.isSuccessful() && r.body() != null && !r.body().isEmpty()) {
                    stops.clear();
                    stops.addAll(r.body());
                    runOnUiThread(() -> stopAdapter.notifyDataSetChanged());
                }
            }
            @Override public void onFailure(@NonNull Call<List<BusStop>> c, @NonNull Throwable t) {}
        });

        // Load live status
        ApiClient.get(this).getLiveStatus(BUS_ID).enqueue(new Callback<LiveBusState>() {
            @Override
            public void onResponse(@NonNull Call<LiveBusState> c, @NonNull Response<LiveBusState> r) {
                if (r.isSuccessful() && r.body() != null) {
                    LiveBusState s = r.body();
                    liveOnboard = s.onboard;
                    busCapacity = s.capacity;
                    seatsFree   = s.seatsFree;
                    loadRatio   = s.loadRatio;
                    crowdBand   = s.crowdBand;
                    runOnUiThread(() -> updateHud());
                }
            }
            @Override public void onFailure(@NonNull Call<LiveBusState> c, @NonNull Throwable t) {}
        });

        // Offline queue count
        offlineCount = StorageService.getOfflineTickets(this).size();
        updateOfflineBanner();
    }

    private void updateHud() {
        tvOnboard.setText(String.valueOf(liveOnboard));
        tvSeatsFree.setText(String.valueOf(seatsFree));
        tvCrowdBand.setText(CrowdUtils.crowdLabel(crowdBand));
        tvCrowdBand.setTextColor(CrowdUtils.crowdColor(this, crowdBand));
        CrowdUtils.applyCrowdMeter(this, pbCrowd, loadRatio, crowdBand);
    }

    private void updateFareDisplay() {
        BusStop boarding = (BusStop) spinnerBoarding.getSelectedItem();
        BusStop dest     = (BusStop) spinnerDest.getSelectedItem();
        tvPassengerCount.setText(String.valueOf(passengerCount));
        if (boarding != null && dest != null) {
            double fare = CrowdUtils.calculateFare(boarding.stopSeq, dest.stopSeq, passengerCount);
            tvFare.setText(String.format("$%.2f", fare));
            btnIssue.setText(String.format("ISSUE TICKET ($%.2f)", fare));
        }
    }

    private void updateOfflineBanner() {
        if (offlineCount > 0) {
            tvOfflineBanner.setVisibility(View.VISIBLE);
            tvOfflineBanner.setText("📦 " + offlineCount + " ticket(s) queued offline. Tap Sync to upload.");
        } else {
            tvOfflineBanner.setVisibility(View.GONE);
        }
    }

    private void issueTicket() {
        BusStop boarding = (BusStop) spinnerBoarding.getSelectedItem();
        BusStop dest     = (BusStop) spinnerDest.getSelectedItem();
        if (boarding == null || dest == null) return;
        if (boarding.stopSeq >= dest.stopSeq) {
            Toast.makeText(this, "Destination must be after boarding stop", Toast.LENGTH_SHORT).show();
            return;
        }

        btnIssue.setEnabled(false);
        btnIssue.setText("Recording Ticket...");

        String ticketId = "TKT-" + String.valueOf(System.currentTimeMillis()).substring(7);
        double fare     = CrowdUtils.calculateFare(boarding.stopSeq, dest.stopSeq, passengerCount);
        String now      = CrowdUtils.nowIso();

        ConductorTicket ticket = new ConductorTicket(
                ticketId, BUS_ID, AppConfig.ROUTE_ID, tripId,
                boarding.stopSeq, dest.stopSeq, now,
                passengerCount, fare, busCapacity, true
        );

        Map<String, Object> payload = new HashMap<>();
        payload.put("ticket_id",         ticketId);
        payload.put("bus_id",            BUS_ID);
        payload.put("route_id",          AppConfig.ROUTE_ID);
        payload.put("trip_id",           tripId);
        payload.put("boarding_stop_seq", boarding.stopSeq);
        payload.put("dest_stop_seq",     dest.stopSeq);
        payload.put("timestamp",         now);
        payload.put("passenger_count",   passengerCount);
        payload.put("fare",              fare);
        payload.put("bus_capacity",      busCapacity);

        ApiClient.get(this).postTicket(AppConfig.CONDUCTOR_API_KEY, payload)
                .enqueue(new Callback<Map<String, Object>>() {
                    @Override
                    public void onResponse(@NonNull Call<Map<String, Object>> c,
                                           @NonNull Response<Map<String, Object>> r) {
                        runOnUiThread(() -> {
                            btnIssue.setEnabled(true);
                            if (r.isSuccessful() && r.body() != null) {
                                Map<String, Object> res = r.body();
                                Object onboardVal = res.get("onboard_now");
                                liveOnboard = onboardVal instanceof Number
                                        ? ((Number) onboardVal).intValue()
                                        : liveOnboard + passengerCount;
                                seatsFree   = Math.max(0, busCapacity - liveOnboard);
                                loadRatio   = (double) liveOnboard / busCapacity;
                                Object band = res.get("crowd_band");
                                if (band != null) crowdBand = band.toString();
                                recentTickets.add(0, ticket);
                                updateHud();
                                updateFareDisplay();
                                Toast.makeText(ConductorActivity.this,
                                        "🎟️ Ticket #" + ticketId + " issued! Onboard: " + liveOnboard,
                                        Toast.LENGTH_SHORT).show();
                            } else {
                                handleOfflineFallback(ticket);
                            }
                        });
                    }

                    @Override
                    public void onFailure(@NonNull Call<Map<String, Object>> c, @NonNull Throwable t) {
                        runOnUiThread(() -> {
                            btnIssue.setEnabled(true);
                            handleOfflineFallback(ticket);
                        });
                    }
                });
    }

    private void handleOfflineFallback(ConductorTicket ticket) {
        ticket.isSynced = false;
        StorageService.saveOfflineTicket(this, ticket);
        recentTickets.add(0, ticket);
        liveOnboard += ticket.passengerCount;
        seatsFree    = Math.max(0, busCapacity - liveOnboard);
        loadRatio    = (double) liveOnboard / busCapacity;
        offlineCount = StorageService.getOfflineTickets(this).size();
        updateHud();
        updateOfflineBanner();
        updateFareDisplay();
        Toast.makeText(this,
                "📦 Offline: Ticket #" + ticket.ticketId + " queued (" + offlineCount + " pending)",
                Toast.LENGTH_LONG).show();
    }

    private void syncOfflineQueue() {
        btnSync.setEnabled(false);
        btnSync.setText("Syncing...");
        executor.execute(() -> {
            int synced = OfflineQueueService.syncPendingTickets(this);
            offlineCount = StorageService.getOfflineTickets(this).size();
            runOnUiThread(() -> {
                btnSync.setEnabled(true);
                btnSync.setText("Sync Offline Queue");
                updateOfflineBanner();
                String msg = synced > 0
                        ? "✅ Synced " + synced + " ticket(s)!"
                        : (offlineCount > 0 ? "❌ Server unreachable" : "All tickets in sync");
                Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
            });
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        executor.shutdown();
    }
}
