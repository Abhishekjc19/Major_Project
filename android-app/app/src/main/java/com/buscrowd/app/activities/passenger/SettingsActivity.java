package com.buscrowd.app.activities.passenger;

import android.content.Intent;
import android.os.Bundle;
import android.view.MenuItem;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import com.buscrowd.app.AppConfig;
import com.buscrowd.app.R;
import com.buscrowd.app.activities.RoleGateActivity;
import com.buscrowd.app.models.BusStop;
import com.buscrowd.app.services.ApiClient;
import com.buscrowd.app.services.StorageService;

import java.util.List;

public class SettingsActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setTitle("Settings");
        }

        EditText etUrl        = findViewById(R.id.et_settings_url);
        Button   btnSaveUrl   = findViewById(R.id.btn_settings_save_url);
        Button   btnSwitchRole = findViewById(R.id.btn_settings_switch_role);

        // Populate current URL
        etUrl.setText(AppConfig.getBaseUrl(this));

        btnSaveUrl.setOnClickListener(v -> {
            String url = etUrl.getText().toString().trim();
            if (url.isEmpty()) {
                Toast.makeText(this, "URL cannot be empty", Toast.LENGTH_SHORT).show();
                return;
            }
            AppConfig.setBaseUrl(this, url);
            ApiClient.reset();
            Toast.makeText(this, "Server URL saved!", Toast.LENGTH_SHORT).show();
        });

        btnSwitchRole.setOnClickListener(v -> {
            startActivity(new Intent(this, RoleGateActivity.class)
                    .setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK));
        });
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        if (item.getItemId() == android.R.id.home) { onBackPressed(); return true; }
        return super.onOptionsItemSelected(item);
    }
}
