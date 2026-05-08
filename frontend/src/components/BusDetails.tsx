import React from 'react';
import { motion } from 'motion/react';
import { X, MapPin, TrendingUp, Info } from 'lucide-react';
import { Bus } from '../types';
import { cn } from '../lib/utils';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface BusDetailsProps {
  bus: Bus;
  onClose: () => void;
}

export const BusDetails: React.FC<BusDetailsProps> = ({ bus, onClose }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: '100%' }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: '100%' }}
      className="fixed inset-0 z-50 flex flex-col bg-slate-50 md:inset-auto md:right-0 md:top-0 md:bottom-0 md:w-[450px] md:shadow-2xl"
    >
      <div className="p-6 flex items-center justify-between border-b border-slate-200 bg-white">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 rounded-2xl bg-brand-primary flex items-center justify-center text-white font-display font-bold text-xl">
            {bus.routeNumber}
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">{bus.destination}</h2>
            <p className="text-sm text-slate-500">Bus ID: {bus.id}</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-slate-100 rounded-full transition-colors"
        >
          <X className="w-6 h-6 text-slate-400" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        {/* Occupancy Visualization */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center">
              <Info className="w-4 h-4 mr-2" />
              Live Occupancy
            </h3>
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1 bg-brand-success/10 px-2 py-1 rounded-md">
                <div className="w-1.5 h-1.5 bg-brand-success rounded-full animate-pulse" />
                <span className="text-[10px] font-bold text-brand-success uppercase">Live</span>
              </div>
              <span className={cn(
                "px-3 py-1 rounded-full text-xs font-bold uppercase",
                bus.status === 'available' ? 'text-brand-success bg-brand-success/10' :
                bus.status === 'partial' ? 'text-brand-warning bg-brand-warning/10' : 'text-brand-danger bg-brand-danger/10'
              )}>
                {Math.round((bus.currentOccupancy / bus.totalCapacity) * 100)}% Full
              </span>
            </div>
          </div>

          <div className="bg-white p-6 rounded-[2.5rem] border border-slate-100 shadow-inner">
            <div className="grid grid-cols-4 gap-3 max-w-[200px] mx-auto">
              {/* Bus Front */}
              <div className="col-span-4 h-8 bg-slate-100 rounded-t-3xl mb-4 flex items-center justify-center">
                <div className="w-12 h-1 bg-slate-200 rounded-full" />
              </div>
              
              {Array.from({ length: 20 }).map((_, i) => {
                const isOccupied = i < (bus.currentOccupancy / bus.totalCapacity) * 20;
                return (
                  <motion.div
                    key={i}
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: i * 0.02 }}
                    className={cn(
                      "aspect-square rounded-lg flex items-center justify-center transition-all duration-500",
                      isOccupied
                        ? bus.status === 'available' ? 'bg-brand-success shadow-lg shadow-brand-success/20' :
                          bus.status === 'partial' ? 'bg-brand-warning shadow-lg shadow-brand-warning/20' : 'bg-brand-danger shadow-lg shadow-brand-danger/20'
                        : 'bg-slate-100'
                    )}
                  >
                    {isOccupied && <div className="w-1.5 h-1.5 bg-white/40 rounded-full" />}
                  </motion.div>
                );
              })}
            </div>
          </div>
          <p className="mt-4 text-sm text-slate-500 text-center italic">
            "Based on real-time ticket sales data"
          </p>
        </section>

        {/* Prediction Chart */}
        <section className="bg-white p-5 rounded-3xl border border-slate-200">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4 flex items-center">
            <TrendingUp className="w-4 h-4 mr-2" />
            AI Crowd Prediction
          </h3>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={bus.predictedOccupancy}>
                <defs>
                  <linearGradient id="colorLevel" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fontSize: 10, fill: '#94a3b8'}} />
                <YAxis hide domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                  labelStyle={{ fontWeight: 'bold', marginBottom: '4px' }}
                />
                <Area
                  type="monotone"
                  dataKey="level"
                  stroke="#3B82F6"
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#colorLevel)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-400 mt-2 text-center">Predicted occupancy for the next 4 hours</p>
        </section>

        {/* Route Timeline */}
        <section>
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-6 flex items-center">
            <MapPin className="w-4 h-4 mr-2" />
            Route Timeline
          </h3>
          <div className="space-y-0 relative">
            <div className="absolute left-[11px] top-2 bottom-2 w-0.5 bg-slate-200" />
            {bus.stops.map((stop, idx) => (
              <div key={stop.id} className="relative pl-10 pb-8 last:pb-0">
                <div className={cn(
                  "absolute left-0 top-1 w-6 h-6 rounded-full border-4 border-slate-50 z-10 flex items-center justify-center",
                  stop.isPassed ? "bg-brand-primary" : "bg-slate-300"
                )}>
                  {stop.isPassed && <div className="w-2 h-2 bg-white rounded-full" />}
                </div>
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className={cn("font-bold text-sm", stop.isPassed ? "text-slate-400" : "text-slate-900")}>
                      {stop.name}
                    </h4>
                    {idx === 0 && <span className="text-[10px] font-bold text-brand-primary uppercase">Starting Point</span>}
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold text-slate-500">{stop.estimatedArrival}</span>
                    <p className="text-[10px] text-slate-400">{stop.isPassed ? 'Passed' : 'Scheduled'}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <div className="p-6 bg-white border-t border-slate-200">
        <button className="w-full py-4 bg-slate-900 text-white rounded-2xl font-bold hover:bg-slate-800 transition-colors shadow-lg shadow-slate-200">
          Set Arrival Notification
        </button>
      </div>
    </motion.div>
  );
};
