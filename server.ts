import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const MOCK_BUSES = [
  {
    id: 'B101',
    routeNumber: '42A',
    destination: 'Central Station',
    currentOccupancy: 12,
    totalCapacity: 50,
    status: 'available',
    nextStop: 'Oak Street',
    lastUpdated: 'Just now',
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
    lastUpdated: 'Just now',
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

let buses = [...MOCK_BUSES];

async function startServer() {
  const app = express();
  const httpServer = createServer(app);
  const io = new Server(httpServer);

  const PORT = 3000;

  io.on('connection', (socket) => {
    console.log('Client connected:', socket.id);
    
    // Send initial data
    socket.emit('buses:init', buses);

    // Handle ticket sales (from conductor)
    socket.on('ticket:sold', ({ busId, count }) => {
      const bus = buses.find(b => b.id === busId);
      if (bus) {
        bus.currentOccupancy = Math.min(bus.totalCapacity, bus.currentOccupancy + count);
        bus.lastUpdated = 'Just now';
        
        // Update status
        const ratio = bus.currentOccupancy / bus.totalCapacity;
        if (ratio < 0.5) bus.status = 'available';
        else if (ratio < 0.9) bus.status = 'partial';
        else bus.status = 'full';

        io.emit('bus:update', bus);
      }
    });

    // Handle ticket cancellations
    socket.on('ticket:cancelled', ({ busId, count }) => {
      const bus = buses.find(b => b.id === busId);
      if (bus) {
        bus.currentOccupancy = Math.max(0, bus.currentOccupancy - count);
        bus.lastUpdated = 'Just now';
        
        // Update status
        const ratio = bus.currentOccupancy / bus.totalCapacity;
        if (ratio < 0.5) bus.status = 'available';
        else if (ratio < 0.9) bus.status = 'partial';
        else bus.status = 'full';

        io.emit('bus:update', bus);
      }
    });

    socket.on('disconnect', () => {
      console.log('Client disconnected');
    });
  });

  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  httpServer.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
