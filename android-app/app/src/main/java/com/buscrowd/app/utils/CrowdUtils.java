package com.buscrowd.app.utils;

import android.content.Context;
import android.graphics.Color;
import android.widget.ProgressBar;

import androidx.core.content.ContextCompat;

import com.buscrowd.app.R;

public class CrowdUtils {

    /**
     * Returns the color resource ID for a crowd band string.
     */
    public static int crowdColor(Context ctx, String crowdBand) {
        if (crowdBand == null) return ContextCompat.getColor(ctx, R.color.crowd_plenty);
        switch (crowdBand.toLowerCase()) {
            case "few seats": return ContextCompat.getColor(ctx, R.color.crowd_few);
            case "standing room": return ContextCompat.getColor(ctx, R.color.crowd_standing);
            case "full / no boarding": return ContextCompat.getColor(ctx, R.color.crowd_full);
            default: return ContextCompat.getColor(ctx, R.color.crowd_plenty); // "Plenty of seats"
        }
    }

    /**
     * Returns the background color resource ID for a crowd band badge.
     */
    public static int crowdBgColor(Context ctx, String crowdBand) {
        if (crowdBand == null) return ContextCompat.getColor(ctx, R.color.crowd_plenty_bg);
        switch (crowdBand.toLowerCase()) {
            case "few seats": return ContextCompat.getColor(ctx, R.color.crowd_few_bg);
            case "standing room": return ContextCompat.getColor(ctx, R.color.crowd_standing_bg);
            case "full / no boarding": return ContextCompat.getColor(ctx, R.color.crowd_full_bg);
            default: return ContextCompat.getColor(ctx, R.color.crowd_plenty_bg);
        }
    }

    /**
     * Returns an emoji + text label for a crowd band.
     */
    public static String crowdLabel(String crowdBand) {
        if (crowdBand == null) return "✅ Plenty of seats";
        switch (crowdBand.toLowerCase()) {
            case "few seats": return "🟡 Few seats";
            case "standing room": return "🟠 Standing room";
            case "full / no boarding": return "🔴 Full / No boarding";
            default: return "✅ Plenty of seats";
        }
    }

    /**
     * Sets the crowd meter ProgressBar progress and tint color.
     * loadRatio: 0.0 → 1.0
     */
    public static void applyCrowdMeter(Context ctx, ProgressBar bar, double loadRatio, String crowdBand) {
        int progress = (int) Math.round(loadRatio * 100);
        bar.setProgress(progress);
        bar.getProgressDrawable().setColorFilter(
                crowdColor(ctx, crowdBand),
                android.graphics.PorterDuff.Mode.SRC_IN
        );
    }

    /**
     * Calculates fare: base ₹1.50 + ₹0.50 per stop × passengers.
     */
    public static double calculateFare(int boardingSeq, int destSeq, int passengers) {
        int diff = Math.max(1, Math.abs(destSeq - boardingSeq));
        diff = Math.min(diff, 15);
        double perTicket = 1.50 + diff * 0.50;
        return Math.round(perTicket * passengers * 100.0) / 100.0;
    }

    /** Formats the current time as HH:MM for API queries. */
    public static String currentTimeHHMM() {
        java.util.Calendar cal = java.util.Calendar.getInstance();
        return String.format("%02d:%02d", cal.get(java.util.Calendar.HOUR_OF_DAY),
                cal.get(java.util.Calendar.MINUTE));
    }

    /** Returns a trip ID based on current hour. */
    public static String generateTripId() {
        java.util.Calendar cal = java.util.Calendar.getInstance();
        return "TRIP-LIVE-" + String.format("%02d00", cal.get(java.util.Calendar.HOUR_OF_DAY));
    }

    /** Returns an ISO-8601 timestamp. */
    public static String nowIso() {
        return new java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss",
                java.util.Locale.US).format(new java.util.Date());
    }
}
