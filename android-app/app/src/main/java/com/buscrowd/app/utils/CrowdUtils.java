package com.buscrowd.app.utils;

import android.content.Context;
import android.graphics.PorterDuff;
import android.widget.ProgressBar;

import androidx.core.content.ContextCompat;

import com.buscrowd.app.R;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

public class CrowdUtils {

    /**
     * Returns the text color resource ID for a crowd band string.
     */
    public static int crowdColor(Context ctx, String crowdBand) {
        if (crowdBand == null) return ContextCompat.getColor(ctx, R.color.crowd_plenty);
        String band = crowdBand.toLowerCase();
        if (band.contains("few")) {
            return ContextCompat.getColor(ctx, R.color.crowd_few);
        } else if (band.contains("standing")) {
            return ContextCompat.getColor(ctx, R.color.crowd_standing);
        } else if (band.contains("packed") || band.contains("full") || band.contains("crushed")) {
            return ContextCompat.getColor(ctx, R.color.crowd_full);
        } else {
            return ContextCompat.getColor(ctx, R.color.crowd_plenty);
        }
    }

    /**
     * Returns the background color resource ID for a crowd band badge.
     */
    public static int crowdBgColor(Context ctx, String crowdBand) {
        if (crowdBand == null) return ContextCompat.getColor(ctx, R.color.crowd_plenty_bg);
        String band = crowdBand.toLowerCase();
        if (band.contains("few")) {
            return ContextCompat.getColor(ctx, R.color.crowd_few_bg);
        } else if (band.contains("standing")) {
            return ContextCompat.getColor(ctx, R.color.crowd_standing_bg);
        } else if (band.contains("packed") || band.contains("full") || band.contains("crushed")) {
            return ContextCompat.getColor(ctx, R.color.crowd_full_bg);
        } else {
            return ContextCompat.getColor(ctx, R.color.crowd_plenty_bg);
        }
    }

    /**
     * Returns an emoji + text label for a crowd band.
     */
    public static String crowdLabel(String crowdBand) {
        if (crowdBand == null) return "✅ Plenty of seats";
        String band = crowdBand.toLowerCase();
        if (band.contains("few")) {
            return "🟡 Few seats left";
        } else if (band.contains("standing")) {
            return "🟠 Standing room only";
        } else if (band.contains("packed") || band.contains("full") || band.contains("crushed")) {
            return "🔴 Packed / Full";
        } else {
            return "✅ Plenty of seats";
        }
    }

    /**
     * Sets the crowd meter ProgressBar progress and tint color.
     * loadRatio: 0.0 → 1.0+
     */
    public static void applyCrowdMeter(Context ctx, ProgressBar bar, double loadRatio, String crowdBand) {
        int progress = (int) Math.round(Math.min(1.0, loadRatio) * 100);
        bar.setProgress(progress);
        bar.getProgressDrawable().setColorFilter(
                crowdColor(ctx, crowdBand),
                PorterDuff.Mode.SRC_IN
        );
    }

    /**
     * Calculates BMTC fare: ₹5 base + ₹2.50 per stop × passengers.
     */
    public static double calculateFare(int boardingSeq, int destSeq, int passengers) {
        int diff = Math.max(1, Math.abs(destSeq - boardingSeq));
        diff = Math.min(diff, 15);
        double perTicket = 5.0 + diff * 2.50;
        return Math.round(perTicket * passengers * 100.0) / 100.0;
    }

    /** Formats the current time as HH:MM for API queries. */
    public static String currentTimeHHMM() {
        Calendar cal = Calendar.getInstance();
        return String.format("%02d:%02d", cal.get(Calendar.HOUR_OF_DAY),
                cal.get(Calendar.MINUTE));
    }

    /** Returns a trip ID based on current hour. */
    public static String generateTripId() {
        Calendar cal = Calendar.getInstance();
        return "TRIP-LIVE-" + String.format("%02d00", cal.get(Calendar.HOUR_OF_DAY));
    }

    /** Returns an ISO-8601 timestamp. */
    public static String nowIso() {
        return new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss",
                Locale.US).format(new Date());
    }
}
