package com.buscrowd.app.adapters;

import android.content.Context;
import android.graphics.drawable.GradientDrawable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ProgressBar;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.buscrowd.app.R;
import com.buscrowd.app.models.PredictedCrowd;
import com.buscrowd.app.utils.CrowdUtils;

import java.util.List;

public class CrowdForecastAdapter extends RecyclerView.Adapter<CrowdForecastAdapter.VH> {

    private final List<PredictedCrowd> items;
    private final Context ctx;

    public CrowdForecastAdapter(Context ctx, List<PredictedCrowd> items) {
        this.ctx   = ctx;
        this.items = items;
    }

    @NonNull @Override
    public VH onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(ctx).inflate(R.layout.item_crowd_forecast, parent, false);
        return new VH(v);
    }

    @Override
    public void onBindViewHolder(@NonNull VH h, int pos) {
        PredictedCrowd p = items.get(pos);
        h.time.setText(p.timeLabel != null ? p.timeLabel : "—");
        h.crowdLabel.setText(CrowdUtils.crowdLabel(p.crowdBand));
        h.crowdLabel.setTextColor(CrowdUtils.crowdColor(ctx, p.crowdBand));
        CrowdUtils.applyCrowdMeter(ctx, h.meter, p.predictedLoad, p.crowdBand);
        h.percent.setText(String.format("%d%%", (int) Math.round(p.predictedLoad * 100)));
    }

    @Override public int getItemCount() { return items.size(); }

    static class VH extends RecyclerView.ViewHolder {
        TextView time, crowdLabel, percent;
        ProgressBar meter;
        VH(@NonNull View v) {
            super(v);
            time       = v.findViewById(R.id.tv_forecast_time);
            crowdLabel = v.findViewById(R.id.tv_forecast_label);
            meter      = v.findViewById(R.id.pb_forecast_meter);
            percent    = v.findViewById(R.id.tv_forecast_percent);
        }
    }
}
