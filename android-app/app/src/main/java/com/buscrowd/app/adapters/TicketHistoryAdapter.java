package com.buscrowd.app.adapters;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.buscrowd.app.R;
import com.buscrowd.app.models.ConductorTicket;
import com.buscrowd.app.utils.CrowdUtils;

import java.util.List;

public class TicketHistoryAdapter extends RecyclerView.Adapter<TicketHistoryAdapter.VH> {

    private final List<ConductorTicket> tickets;
    private final Context ctx;

    public TicketHistoryAdapter(Context ctx, List<ConductorTicket> tickets) {
        this.ctx     = ctx;
        this.tickets = tickets;
    }

    @NonNull @Override
    public VH onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(ctx).inflate(R.layout.item_ticket, parent, false);
        return new VH(v);
    }

    @Override
    public void onBindViewHolder(@NonNull VH h, int pos) {
        ConductorTicket t = tickets.get(pos);
        h.ticketId.setText(t.ticketId);
        h.route.setText("Stop " + t.boardingStopSeq + " → Stop " + t.destStopSeq
                + "  •  " + t.passengerCount + " pax");
        h.fare.setText(String.format("$%.2f", t.fare));
        h.time.setText(t.timestamp != null && t.timestamp.length() >= 16
                ? t.timestamp.substring(11, 16) : "—");
        h.status.setText(t.isSynced ? "✅ Synced" : "📦 Offline");
        h.status.setTextColor(ctx.getResources().getColor(
                t.isSynced ? R.color.crowd_plenty : R.color.crowd_few, null));
    }

    @Override public int getItemCount() { return tickets.size(); }

    static class VH extends RecyclerView.ViewHolder {
        TextView ticketId, route, fare, time, status;
        VH(@NonNull View v) {
            super(v);
            ticketId = v.findViewById(R.id.tv_ticket_id);
            route    = v.findViewById(R.id.tv_ticket_route);
            fare     = v.findViewById(R.id.tv_ticket_fare);
            time     = v.findViewById(R.id.tv_ticket_time);
            status   = v.findViewById(R.id.tv_ticket_status);
        }
    }
}
