package com.buscrowd.app.activities;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.RecyclerView;
import androidx.viewpager2.widget.ViewPager2;

import com.buscrowd.app.R;
import com.buscrowd.app.services.StorageService;
import com.google.android.material.tabs.TabLayout;
import com.google.android.material.tabs.TabLayoutMediator;

public class OnboardingActivity extends AppCompatActivity {

    private static final String[][] PAGES = {
            {"Real-Time Crowd Data",
             "See exactly how crowded every bus is — calculated from real conductor tickets, not sensors.",
             "🚌"},
            {"Plan Smarter Trips",
             "Pick the best time to travel. Get crowd forecasts up to 2 hours ahead.",
             "📊"},
            {"Conductor Terminal",
             "Conductors can issue tickets and update live crowd data even when offline.",
             "🎟️"},
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_onboarding);

        ViewPager2 pager = findViewById(R.id.vp_onboarding);
        TabLayout dots  = findViewById(R.id.tab_dots);
        Button btnNext  = findViewById(R.id.btn_onboarding_next);

        pager.setAdapter(new OnboardingAdapter());
        new TabLayoutMediator(dots, pager, (tab, pos) -> {}).attach();

        pager.registerOnPageChangeCallback(new ViewPager2.OnPageChangeCallback() {
            @Override
            public void onPageSelected(int position) {
                btnNext.setText(position == PAGES.length - 1
                        ? getString(R.string.get_started) : getString(R.string.next));
            }
        });

        btnNext.setOnClickListener(v -> {
            int current = pager.getCurrentItem();
            if (current < PAGES.length - 1) {
                pager.setCurrentItem(current + 1);
            } else {
                finish_onboarding();
            }
        });
    }

    private void finish_onboarding() {
        StorageService.setOnboardingSeen(this);
        startActivity(new Intent(this, RoleGateActivity.class));
        finish();
    }

    // ── Inline adapter ────────────────────────────────────────────────────────
    class OnboardingAdapter extends RecyclerView.Adapter<OnboardingAdapter.VH> {
        @NonNull @Override
        public VH onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            View v = LayoutInflater.from(parent.getContext())
                    .inflate(R.layout.item_onboarding_page, parent, false);
            return new VH(v);
        }

        @Override
        public void onBindViewHolder(@NonNull VH h, int pos) {
            h.emoji.setText(PAGES[pos][2]);
            h.title.setText(PAGES[pos][0]);
            h.desc.setText(PAGES[pos][1]);
        }

        @Override public int getItemCount() { return PAGES.length; }

        class VH extends RecyclerView.ViewHolder {
            TextView emoji, title, desc;
            VH(@NonNull View v) {
                super(v);
                emoji = v.findViewById(R.id.tv_onboarding_emoji);
                title = v.findViewById(R.id.tv_onboarding_title);
                desc  = v.findViewById(R.id.tv_onboarding_desc);
            }
        }
    }
}
