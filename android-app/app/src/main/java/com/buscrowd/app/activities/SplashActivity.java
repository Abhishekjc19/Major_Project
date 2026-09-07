package com.buscrowd.app.activities;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;

import androidx.appcompat.app.AppCompatActivity;

import com.buscrowd.app.services.StorageService;

public class SplashActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // No layout — pure brand-color screen from theme

        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            if (StorageService.isOnboardingSeen(this)) {
                startActivity(new Intent(this, RoleGateActivity.class));
            } else {
                startActivity(new Intent(this, OnboardingActivity.class));
            }
            finish();
        }, 1500);
    }
}
