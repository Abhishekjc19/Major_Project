import { Bus, RideHistory, LostItemReport } from './types';

export const MOCK_HISTORY: RideHistory[] = [
  {
    id: 'h1',
    date: '2023-10-24',
    time: '08:30 AM',
    from: 'Pine Avenue',
    to: 'Central Station',
    routeNumber: '42A',
    fare: '$2.50'
  },
  {
    id: 'h2',
    date: '2023-10-23',
    time: '05:15 PM',
    from: 'Central Station',
    to: 'Pine Avenue',
    routeNumber: '42A',
    fare: '$2.50'
  },
  {
    id: 'h3',
    date: '2023-10-22',
    time: '09:00 AM',
    from: 'West Gate',
    to: 'Market Square',
    routeNumber: '15C',
    fare: '$3.00'
  },
  {
    id: 'h4',
    date: '2023-10-20',
    time: '02:45 PM',
    from: 'City Center',
    to: 'Tech Park',
    routeNumber: '88',
    fare: '$4.50'
  }
];

export const MOCK_REPORTS: LostItemReport[] = [
  {
    id: 'r1',
    itemName: 'Blue Wallet',
    busId: 'B101',
    date: 'Oct 24, 2023',
    status: 'searching',
    description: 'Left on the back seat of 42A'
  },
  {
    id: 'r2',
    itemName: 'iPhone 13',
    busId: 'B102',
    date: 'Oct 23, 2023',
    status: 'found',
    description: 'Silver color, black case'
  }
];

export const MOCK_BUSES: Bus[] = [
  {
    id: 'B101',
    routeNumber: '42A',
    destination: 'Central Station',
    currentOccupancy: 12,
    totalCapacity: 50,
    status: 'available',
    nextStop: 'Oak Street',
    lastUpdated: '2 mins ago',
    stops: [
      { id: 's1', name: 'Pine Avenue', estimatedArrival: '10:15 AM', isPassed: true },
      { id: 's2', name: 'Oak Street', estimatedArrival: '10:22 AM', isPassed: false },
      { id: 's3', name: 'Maple Road', estimatedArrival: '10:30 AM', isPassed: false },
      { id: 's4', name: 'Central Station', estimatedArrival: '10:45 AM', isPassed: false },
    ],
    predictedOccupancy: [
      { time: '10:00', level: 10 },
      { time: '11:00', level: 45 },
      { time: '12:00', level: 85 },
      { time: '13:00', level: 60 },
      { time: '14:00', level: 30 },
    ]
  },
  {
    id: 'B102',
    routeNumber: '15C',
    destination: 'North Harbor',
    currentOccupancy: 38,
    totalCapacity: 50,
    status: 'partial',
    nextStop: 'Market Square',
    lastUpdated: 'Just now',
    stops: [
      { id: 's5', name: 'West Gate', estimatedArrival: '10:18 AM', isPassed: true },
      { id: 's6', name: 'Market Square', estimatedArrival: '10:25 AM', isPassed: false },
      { id: 's7', name: 'Harbor View', estimatedArrival: '10:35 AM', isPassed: false },
    ],
    predictedOccupancy: [
      { time: '10:00', level: 30 },
      { time: '11:00', level: 70 },
      { time: '12:00', level: 90 },
      { time: '13:00', level: 80 },
      { time: '14:00', level: 50 },
    ]
  },
  {
    id: 'B103',
    routeNumber: '88',
    destination: 'Tech Park',
    currentOccupancy: 48,
    totalCapacity: 50,
    status: 'full',
    nextStop: 'Innovation Way',
    lastUpdated: '5 mins ago',
    stops: [
      { id: 's8', name: 'City Center', estimatedArrival: '10:10 AM', isPassed: true },
      { id: 's9', name: 'Innovation Way', estimatedArrival: '10:28 AM', isPassed: false },
      { id: 's10', name: 'Tech Park', estimatedArrival: '10:40 AM', isPassed: false },
    ],
    predictedOccupancy: [
      { time: '10:00', level: 80 },
      { time: '11:00', level: 95 },
      { time: '12:00', level: 100 },
      { time: '13:00', level: 90 },
      { time: '14:00', level: 85 },
    ]
  }
];
