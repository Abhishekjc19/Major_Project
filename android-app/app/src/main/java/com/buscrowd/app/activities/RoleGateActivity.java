package com.buscrowd.app.activities;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;

import androidx.appcompat.app.AppCompatActivity;

import com.buscrowd.app.R;
import com.buscrowd.app.activities.conductor.ConductorAuthActivity;
import com.buscrowd.app.activities.passenger.PassengerHomeActivity;
import com.buscrowd.app.services.StorageService;

public class RoleGateActivity extends AppCompatActivity {

    private String selectedRole = "passenger";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_role_gate);

        // Restore previously saved role
        selectedRole = StorageService.getUserRole(this);

        LinearLayout cardPassenger = findViewById(R.id.card_passenger);
        LinearLayout cardConductor = findViewById(R.id.card_conductor);
        Button btnContinue         = findViewById(R.id.btn_role_continue);

        updateSelection(cardPassenger, cardConductor, btnContinue);

        cardPassenger.setOnClickListener(v -> {
            selectedRole = "passenger";
            updateSelection(cardPassenger, cardConductor, btnContinue);
        });

        cardConductor.setOnClickListener(v -> {
            selectedRole = "conductor";
            updateSelection(cardPassenger, cardConductor, btnContinue);
        });

        btnContinue.setOnClickListener(v -> {
            StorageService.setUserRole(this, selectedRole);
            if ("conductor".equals(selectedRole)) {
                startActivity(new Intent(this, ConductorAuthActivity.class));
            } else {
                startActivity(new Intent(this, PassengerHomeActivity.class));
            }
            finish();
        });
    }

    private void updateSelection(LinearLayout cardP, LinearLayout cardC, Button btn) {
        boolean isPassenger = "passenger".equals(selectedRole);

        cardP.setBackground(getDrawable(isPassenger
                ? R.drawable.bg_card_selected : R.drawable.bg_card));
        cardC.setBackground(getDrawable(!isPassenger
                ? R.drawable.bg_card_selected : R.drawable.bg_card));

        btn.setText(isPassenger
                ? getString(R.string.start_commuting)
                : getString(R.string.open_conductor_portal));
    }
}
