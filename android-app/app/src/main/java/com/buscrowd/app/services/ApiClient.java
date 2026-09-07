package com.buscrowd.app.services;

import android.content.Context;

import com.buscrowd.app.AppConfig;

import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class ApiClient {

    private static ApiInterface instance;
    private static String lastBaseUrl;

    /**
     * Returns a Retrofit ApiInterface. Re-creates it if the base URL changed.
     */
    public static ApiInterface get(Context ctx) {
        String baseUrl = AppConfig.getBaseUrl(ctx);
        // Ensure trailing slash for Retrofit
        if (!baseUrl.endsWith("/")) baseUrl = baseUrl + "/";

        if (instance == null || !baseUrl.equals(lastBaseUrl)) {
            lastBaseUrl = baseUrl;

            HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
            logging.setLevel(HttpLoggingInterceptor.Level.BODY);

            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(5, TimeUnit.SECONDS)
                    .readTimeout(5, TimeUnit.SECONDS)
                    .writeTimeout(5, TimeUnit.SECONDS)
                    .addInterceptor(logging)
                    .build();

            instance = new Retrofit.Builder()
                    .baseUrl(lastBaseUrl)
                    .client(client)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build()
                    .create(ApiInterface.class);
        }
        return instance;
    }

    /** Call this after changing the base URL so the next call rebuilds the client. */
    public static void reset() {
        instance = null;
        lastBaseUrl = null;
    }
}
