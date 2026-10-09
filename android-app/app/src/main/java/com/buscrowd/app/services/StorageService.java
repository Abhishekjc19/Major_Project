package com.buscrowd.app.services;

import android.content.Context;
import android.content.SharedPreferences;

import com.buscrowd.app.AppConfig;
import com.buscrowd.app.models.ConductorTicket;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class StorageService {

    private static SharedPreferences prefs(Context ctx) {
        return ctx.getSharedPreferences(AppConfig.PREFS_NAME, Context.MODE_PRIVATE);
    }

    // ── User Role ──────────────────────────────────────────────────────────────

    public static String getUserRole(Context ctx) {
        return prefs(ctx).getString(AppConfig.KEY_USER_ROLE, "passenger");
    }

    public static void setUserRole(Context ctx, String role) {
        prefs(ctx).edit().putString(AppConfig.KEY_USER_ROLE, role).apply();
    }

    // ── Onboarding ─────────────────────────────────────────────────────────────

    public static boolean isOnboardingSeen(Context ctx) {
        return prefs(ctx).getBoolean(AppConfig.KEY_ONBOARDING_SEEN, false);
    }

    public static void setOnboardingSeen(Context ctx) {
        prefs(ctx).edit().putBoolean(AppConfig.KEY_ONBOARDING_SEEN, true).apply();
    }

    // ── Home Stop ──────────────────────────────────────────────────────────────

    public static int getHomeStop(Context ctx) {
        return prefs(ctx).getInt(AppConfig.KEY_HOME_STOP, 1);
    }

    public static void setHomeStop(Context ctx, int stopSeq) {
        prefs(ctx).edit().putInt(AppConfig.KEY_HOME_STOP, stopSeq).apply();
    }

    // ── Saved Routes ───────────────────────────────────────────────────────────

    public static List<String> getSavedRoutes(Context ctx) {
        String json = prefs(ctx).getString(AppConfig.KEY_SAVED_ROUTES, null);
        if (json == null) return new ArrayList<>(Arrays.asList("BMTC-500D"));
        Type type = new TypeToken<List<String>>() {}.getType();
        return new Gson().fromJson(json, type);
    }

    public static void setSavedRoutes(Context ctx, List<String> routes) {
        prefs(ctx).edit().putString(AppConfig.KEY_SAVED_ROUTES, new Gson().toJson(routes)).apply();
    }

    // ── Shared Live Bus State (Syncs Passenger & Conductor Screens) ────────────

    public static int getLiveOnboard(Context ctx, String busId) {
        return prefs(ctx).getInt("live_onboard_" + busId, 0);
    }

    public static void setLiveOnboard(Context ctx, String busId, int onboard) {
        prefs(ctx).edit().putInt("live_onboard_" + busId, Math.max(0, onboard)).apply();
    }

    // ── Offline Ticket Queue ───────────────────────────────────────────────────

    public static List<ConductorTicket> getOfflineTickets(Context ctx) {
        String json = prefs(ctx).getString(AppConfig.KEY_OFFLINE_QUEUE, null);
        if (json == null) return new ArrayList<>();
        Type type = new TypeToken<List<ConductorTicket>>() {}.getType();
        return new Gson().fromJson(json, type);
    }

    public static void saveOfflineTicket(Context ctx, ConductorTicket ticket) {
        List<ConductorTicket> queue = getOfflineTickets(ctx);
        queue.add(ticket);
        prefs(ctx).edit().putString(AppConfig.KEY_OFFLINE_QUEUE, new Gson().toJson(queue)).apply();
    }

    public static void removeOfflineTicket(Context ctx, String ticketId) {
        List<ConductorTicket> queue = getOfflineTickets(ctx);
        queue.removeIf(t -> t.ticketId.equals(ticketId));
        prefs(ctx).edit().putString(AppConfig.KEY_OFFLINE_QUEUE, new Gson().toJson(queue)).apply();
    }

    public static void clearOfflineQueue(Context ctx) {
        prefs(ctx).edit().remove(AppConfig.KEY_OFFLINE_QUEUE).apply();
    }
}
