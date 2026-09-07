package com.buscrowd.app.services;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.location.Location;

import androidx.core.content.ContextCompat;

import com.buscrowd.app.models.BusStop;
import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.location.Priority;

import java.util.List;

public class LocationHelper {

    public interface NearestStopCallback {
        void onResult(BusStop nearest);  // null if no permission or no location
    }

    /**
     * Finds the nearest bus stop using the device's last known location.
     * Result delivered via callback on the main thread.
     */
    public static void findNearestStop(Context ctx, List<BusStop> stops, NearestStopCallback callback) {
        if (ContextCompat.checkSelfPermission(ctx, Manifest.permission.ACCESS_FINE_LOCATION)
                != PackageManager.PERMISSION_GRANTED) {
            callback.onResult(null);
            return;
        }

        FusedLocationProviderClient client = LocationServices.getFusedLocationProviderClient(ctx);
        client.getCurrentLocation(Priority.PRIORITY_HIGH_ACCURACY, null)
                .addOnSuccessListener(location -> {
                    if (location == null) {
                        callback.onResult(null);
                        return;
                    }
                    callback.onResult(pickNearest(location, stops));
                })
                .addOnFailureListener(e -> callback.onResult(null));
    }

    /** Haversine distance — picks the closest stop. */
    private static BusStop pickNearest(Location loc, List<BusStop> stops) {
        BusStop nearest = null;
        double minDist = Double.MAX_VALUE;
        for (BusStop stop : stops) {
            float[] result = new float[1];
            Location.distanceBetween(loc.getLatitude(), loc.getLongitude(),
                    stop.lat, stop.lng, result);
            if (result[0] < minDist) {
                minDist = result[0];
                nearest = stop;
            }
        }
        return nearest;
    }
}
