import 'reflect-metadata';
import express, { Express } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { createServer } from 'http';
import { Server as SocketIOServer, Socket } from 'socket.io';
import { AppDataSource } from './config/database';
import { errorHandler, AuthRequest } from './middleware/auth';
import { authUtils } from './utils/auth';
import authRoutes from './routes/auth';
import busRoutes from './routes/buses';
import { setupSocketHandlers } from './sockets/handlers';
import { config } from 'dotenv';

config();

const app: Express = express();
const httpServer = createServer(app);

const PORT = parseInt(process.env.PORT || '3001', 10);
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5173';

// Initialize Socket.IO
const io = new SocketIOServer(httpServer, {
  cors: {
    origin: FRONTEND_URL,
    methods: ['GET', 'POST'],
    credentials: true,
  },
});

// Middleware
app.use(helmet());
app.use(cors({
  origin: FRONTEND_URL,
  credentials: true,
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/buses', busRoutes);

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Error handling
app.use(errorHandler);

// Socket.IO middleware for authentication
io.use((socket, next) => {
  try {
    const token = socket.handshake.auth.token;
    if (!token) {
      return next(new Error('Authentication failed'));
    }

    const decoded = authUtils.verifyToken(token);
    socket.data.userId = decoded.userId;
    socket.data.userRole = decoded.role;
    next();
  } catch (error) {
    next(new Error('Authentication failed'));
  }
});

// Socket.IO connection handling
io.on('connection', (socket: Socket) => {
  console.log(`Client connected: ${socket.id} (User: ${socket.data.userId})`);

  // Setup Socket.IO event handlers
  setupSocketHandlers(socket, io);

  socket.on('disconnect', () => {
    console.log(`Client disconnected: ${socket.id}`);
  });

  socket.on('error', (error) => {
    console.error(`Socket error for ${socket.id}:`, error);
  });
});

// Database initialization and server start
async function startServer() {
  try {
    // Initialize database
    console.log('Initializing database...');
    await AppDataSource.initialize();
    console.log('Database initialized successfully');

    // Start HTTP server
    httpServer.listen(PORT, '0.0.0.0', () => {
      console.log(`🚌 OmniBus Backend running on http://localhost:${PORT}`);
      console.log(`Frontend configured at: ${FRONTEND_URL}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\nShutting down gracefully...');
  io.close();
  httpServer.close();
  await AppDataSource.destroy();
  console.log('Server closed');
  process.exit(0);
});

startServer();

export { app, io };
