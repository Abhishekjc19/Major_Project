package com.buscrowd.app;

import android.content.Context;
import android.content.SharedPreferences;

public class AppConfig {

    // Default backend URLs
    public static final String DEFAULT_LOCAL_URL      = "http://10.0.2.2:8000";    // Android emulator → PC localhost
    public static final String DEFAULT_PHYSICAL_URL   = "http://192.168.1.100:8000"; // Physical device on LAN
    public static final String DEFAULT_PRODUCTION_URL = "https://bus-crowd-prediction.onrender.com";

    // Conductor API key (change for production)
    public static final String CONDUCTOR_API_KEY = "dev-conductor-key-change-me";

    // Route info (BMTC Bengaluru)
    public static final String ROUTE_ID      = "BMTC-500D";
    public static final String ROUTE_NAME    = "BMTC Silk Board ↔ Hebbal Express";
    public static final int    TOTAL_STOPS   = 15;
    public static final int    DEFAULT_CAPACITY = 50;

    // SharedPreferences keys
    public static final String PREFS_NAME              = "BusCrowdPrefs";
    public static final String KEY_BASE_URL            = "custom_base_url";
    public static final String KEY_USER_ROLE           = "active_user_role";
    public static final String KEY_ONBOARDING_SEEN     = "onboarding_seen";
    public static final String KEY_SAVED_ROUTES        = "saved_routes_list";
    public static final String KEY_OFFLINE_QUEUE       = "conductor_offline_queue";
    public static final String KEY_HOME_STOP           = "user_home_stop_seq";

    /** Returns the currently configured base URL (from prefs or default). */
    public static String getBaseUrl(Context ctx) {
        SharedPreferences prefs = ctx.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        String saved = prefs.getString(KEY_BASE_URL, null);
        return (saved != null && !saved.trim().isEmpty()) ? saved.trim() : DEFAULT_LOCAL_URL;
    }

    /** Persists a new base URL. */
    public static void setBaseUrl(Context ctx, String url) {
        ctx.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                .edit().putString(KEY_BASE_URL, url.trim()).apply();
    }
}
