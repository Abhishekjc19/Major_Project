export type OccupancyStatus = 'available' | 'partial' | 'full';

export interface BusStop {
  id: string;
  name: string;
  estimatedArrival: string;
  isPassed: boolean;
}

export interface RideHistory {
  id: string;
  date: string;
  time: string;
  from: string;
  to: string;
  routeNumber: string;
  fare: string;
}

export interface LostItemReport {
  id: string;
  itemName: string;
  busId: string;
  date: string;
  status: 'searching' | 'found' | 'returned';
  description: string;
}

export interface Bus {
  id: string;
  routeNumber: string;
  destination: string;
  currentOccupancy: number; // 0 to 100
  totalCapacity: number;
  status: OccupancyStatus;
  nextStop: string;
  stops: BusStop[];
  lastUpdated: string;
  predictedOccupancy: { time: string; level: number }[];
}
