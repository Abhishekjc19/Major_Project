import React from 'react';
import { motion } from 'motion/react';
import { Users, MapPin, Clock, ChevronRight } from 'lucide-react';
import { Bus } from '../types';
import { cn } from '../lib/utils';

interface BusCardProps {
  bus: Bus;
  onClick: (bus: Bus) => void;
}

export const BusCard: React.FC<BusCardProps> = ({ bus, onClick }) => {
  const statusColors = {
    available: 'text-brand-success bg-brand-success/10',
    partial: 'text-brand-warning bg-brand-warning/10',
    full: 'text-brand-danger bg-brand-danger/10',
  };

  const statusLabels = {
    available: 'Seats Available',
    partial: 'Partially Full',
    full: 'Near Capacity',
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onClick(bus)}
      className="glass-card p-5 rounded-3xl cursor-pointer group relative overflow-hidden"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1 block">Route</span>
          <h3 className="text-3xl font-display font-bold text-slate-900">{bus.routeNumber}</h3>
        </div>
        <div className={cn("px-3 py-1 rounded-full text-xs font-bold uppercase tracking-tighter", statusColors[bus.status])}>
          {statusLabels[bus.status]}
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center text-slate-600">
          <MapPin className="w-4 h-4 mr-2 text-brand-primary" />
          <span className="text-sm font-medium truncate">To {bus.destination}</span>
        </div>
        <div className="flex items-center text-slate-600">
          <Clock className="w-4 h-4 mr-2 text-brand-primary" />
          <span className="text-sm">Next: <span className="font-bold">{bus.nextStop}</span></span>
        </div>
      </div>

      <div className="mt-6">
        <div className="flex justify-between items-end mb-2">
          <div className="flex items-center text-slate-500 text-xs">
            <Users className="w-3 h-3 mr-1" />
            <span>{bus.currentOccupancy}/{bus.totalCapacity} Passengers</span>
          </div>
          <span className="text-xs font-bold text-slate-400">Updated {bus.lastUpdated}</span>
        </div>
        <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${(bus.currentOccupancy / bus.totalCapacity) * 100}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className={cn(
              "h-full rounded-full",
              bus.status === 'available' ? 'bg-brand-success' :
              bus.status === 'partial' ? 'bg-brand-warning' : 'bg-brand-danger'
            )}
          />
        </div>
      </div>

      <div className="absolute right-4 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
        <ChevronRight className="w-6 h-6 text-slate-300" />
      </div>
    </motion.div>
  );
};
