package com.buscrowd.app.services;

import android.content.Context;

import com.buscrowd.app.AppConfig;
import com.buscrowd.app.models.ConductorTicket;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import retrofit2.Response;

public class OfflineQueueService {

    /**
     * Tries to sync all pending offline tickets to the backend.
     * Returns the number of tickets successfully synced.
     */
    public static int syncPendingTickets(Context ctx) {
        List<ConductorTicket> queue = StorageService.getOfflineTickets(ctx);
        if (queue.isEmpty()) return 0;

        int synced = 0;
        ApiInterface api = ApiClient.get(ctx);

        for (ConductorTicket ticket : queue) {
            try {
                Map<String, Object> payload = buildPayload(ticket);
                Response<Map<String, Object>> response = api.postTicket(
                        AppConfig.CONDUCTOR_API_KEY, payload
                ).execute();  // synchronous — call from background thread

                if (response.isSuccessful()) {
                    StorageService.removeOfflineTicket(ctx, ticket.ticketId);
                    synced++;
                }
            } catch (Exception e) {
                // Server still unreachable — leave in queue
                break;
            }
        }
        return synced;
    }

    private static Map<String, Object> buildPayload(ConductorTicket ticket) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("ticket_id",        ticket.ticketId);
        payload.put("bus_id",           ticket.busId);
        payload.put("route_id",         ticket.routeId);
        payload.put("trip_id",          ticket.tripId);
        payload.put("boarding_stop_seq", ticket.boardingStopSeq);
        payload.put("dest_stop_seq",    ticket.destStopSeq);
        payload.put("timestamp",        ticket.timestamp);
        payload.put("passenger_count",  ticket.passengerCount);
        payload.put("fare",             ticket.fare);
        payload.put("bus_capacity",     ticket.busCapacity);
        return payload;
    }
}
