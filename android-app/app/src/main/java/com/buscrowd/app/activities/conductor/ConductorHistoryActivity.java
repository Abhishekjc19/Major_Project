package com.buscrowd.app.activities.conductor;

import android.os.Bundle;
import android.view.MenuItem;
import android.widget.Button;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.buscrowd.app.R;
import com.buscrowd.app.adapters.TicketHistoryAdapter;
import com.buscrowd.app.models.ConductorTicket;
import com.buscrowd.app.services.OfflineQueueService;
import com.buscrowd.app.services.StorageService;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ConductorHistoryActivity extends AppCompatActivity {

    private final ExecutorService executor = Executors.newSingleThreadExecutor();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_conductor_history);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setTitle("Ticket History");
        }

        List<ConductorTicket> tickets = StorageService.getOfflineTickets(this);

        RecyclerView rv = findViewById(R.id.rv_ticket_history);
        rv.setLayoutManager(new LinearLayoutManager(this));
        rv.setAdapter(new TicketHistoryAdapter(this, tickets));

        Button btnSyncAll = findViewById(R.id.btn_sync_all);
        btnSyncAll.setOnClickListener(v -> {
            btnSyncAll.setEnabled(false);
            btnSyncAll.setText("Syncing...");
            executor.execute(() -> {
                int synced = OfflineQueueService.syncPendingTickets(this);
                runOnUiThread(() -> {
                    btnSyncAll.setEnabled(true);
                    btnSyncAll.setText("Sync All");
                    String msg = synced > 0
                            ? "✅ Synced " + synced + " ticket(s)"
                            : "❌ Server unreachable or queue empty";
                    Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
                    // Refresh list
                    tickets.clear();
                    tickets.addAll(StorageService.getOfflineTickets(this));
                    rv.getAdapter().notifyDataSetChanged();
                });
            });
        });
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        if (item.getItemId() == android.R.id.home) { onBackPressed(); return true; }
        return super.onOptionsItemSelected(item);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        executor.shutdown();
    }
}
