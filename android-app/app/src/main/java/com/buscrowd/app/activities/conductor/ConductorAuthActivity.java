package com.buscrowd.app.activities.conductor;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import com.buscrowd.app.AppConfig;
import com.buscrowd.app.R;

public class ConductorAuthActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_conductor_auth);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) getSupportActionBar().setTitle("Conductor Access");

        EditText etKey    = findViewById(R.id.et_conductor_api_key);
        Button   btnUnlock = findViewById(R.id.btn_conductor_unlock);

        // Pre-fill the default development conductor API key
        etKey.setText(AppConfig.CONDUCTOR_API_KEY);

        btnUnlock.setOnClickListener(v -> {
            String key = etKey.getText().toString().trim();
            if (key.isEmpty()) {
                Toast.makeText(this, "Please enter your API key", Toast.LENGTH_SHORT).show();
                return;
            }
            // Allow default dev keys as well as conductor/admin/1234 shortcuts
            if (key.equals(AppConfig.CONDUCTOR_API_KEY)
                    || key.equals("dev-conductor-key-change-me")
                    || key.equalsIgnoreCase("conductor")
                    || key.equalsIgnoreCase("admin")
                    || key.equals("1234")) {
                startActivity(new Intent(this, ConductorActivity.class));
                finish();
            } else {
                Toast.makeText(this, "❌ Invalid API key (Default: dev-conductor-key-change-me)", Toast.LENGTH_LONG).show();
            }
        });
    }
}
