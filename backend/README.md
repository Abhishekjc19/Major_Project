# OmniBus Backend

A production-ready Node.js + Express backend for the OmniBus real-time bus tracking application. Features real-time updates via Socket.IO, PostgreSQL persistence, JWT authentication, and role-based access control.

## Features

- ✅ **Real-time Updates** - Socket.IO integration for live bus tracking
- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **Role-Based Access** - Support for passenger, conductor, and admin roles
- ✅ **PostgreSQL** - Persistent data storage with TypeORM
- ✅ **REST API** - Complete API for buses, rides, lost items, and emergencies
- ✅ **Lost & Found Chat** - Real-time messaging between passengers and conductors
- ✅ **SOS Emergency Alerts** - Emergency reporting system
- ✅ **Conductor Mode** - Occupancy and location updates for bus staff

## Tech Stack

- **Runtime**: Node.js + TypeScript
- **Framework**: Express.js
- **Database**: PostgreSQL + TypeORM
- **Real-time**: Socket.IO
- **Authentication**: JWT + bcrypt
- **Validation**: class-validator
- **Dev Tools**: tsx, ts-node

## Prerequisites

- Node.js 18+ and npm
- PostgreSQL 12+
- Docker & Docker Compose (optional, for database setup)

## Getting Started

### 1. Install Dependencies

```bash
cd backend
npm install
```

### 2. Set Up Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Then edit `.env` with your configuration:

```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=omnibus
PORT=3001
JWT_SECRET=your_super_secret_key
FRONTEND_URL=http://localhost:5173
```

### 3. Option A: Using Docker Compose (Recommended)

Start PostgreSQL automatically:

```bash
docker-compose up -d
```

This starts PostgreSQL on port 5432 with the configured credentials.

### 3. Option B: Manual PostgreSQL Setup

Make sure PostgreSQL is running and create the database:

```sql
CREATE DATABASE omnibus;
```

### 4. Run Migrations

TypeORM will auto-sync the database schema in development mode. For production, use explicit migrations:

```bash
npm run migrate
```

### 5. Seed Sample Data (Optional)

Run this to create sample buses and stops (create this file if needed):

```bash
npm run seed
```

### 6. Start Development Server

```bash
npm run dev
```

Server will run at `http://localhost:3001`

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user (requires auth)

### Buses

- `GET /api/buses` - List all buses (supports filters: `status`, `route`)
- `GET /api/buses/:id` - Get bus details with route
- `POST /api/buses/:id/occupancy` - Update bus occupancy (conductor only)
- `POST /api/buses/:id/location` - Update bus location (conductor only)
- `POST /api/buses/:busId/stops/:stopId/mark-passed` - Mark stop as passed (conductor only)

### Health

- `GET /api/health` - Server health check

## Socket.IO Events

### Client → Server

**Buses:**
- `buses:request-update` - Request current buses data
- `ticket:sold` - Register ticket sale (conductor)
- `ticket:cancelled` - Register ticket cancellation (conductor)
- `bus:location-update` - Update bus GPS location (conductor)
- `bus:stop-passed` - Mark next stop as passed (conductor)

**Lost & Found:**
- `chat:message` - Send support message

**Emergency:**
- `sos:activate` - Activate emergency SOS
- `sos:update-status` - Update SOS status (conductor)

### Server → Client

- `buses:init` - Initial buses data
- `bus:update` - Bus status/occupancy changed
- `bus:stop-reached` - Bus reached a stop
- `chat:message` - New chat message
- `sos:alert` - Emergency alert
- `sos:status-updated` - SOS status updated
- `error` - Error notification

## Building for Production

```bash
npm run build
npm start
```

The compiled JavaScript will be in the `dist/` directory.

## Project Structure

```
backend/
├── src/
│   ├── config/         # Database configuration
│   ├── controllers/    # API route handlers
│   ├── middleware/     # Express middleware (auth, error handling)
│   ├── models/         # TypeORM entities
│   ├── routes/         # API routes
│   ├── services/       # Business logic
│   ├── sockets/        # Socket.IO handlers
│   ├── utils/          # Helper utilities
│   └── index.ts        # Application entry point
├── migrations/         # Database migrations
├── .env.example        # Environment template
├── tsconfig.json       # TypeScript config
└── package.json
```

## Database Schema

### Core Tables

- **users** - User accounts with roles (passenger, conductor, admin)
- **buses** - Active buses with occupancy info
- **bus_stops** - Physical bus stops with coordinates
- **route_stops** - Mapping of stops to bus routes
- **ride_history** - Historical record of rides
- **lost_items** - Lost & found reports
- **chat_messages** - Support conversations
- **sos_alerts** - Emergency alerts

## Authentication

The API uses JWT tokens for authentication. Include the token in request headers:

```
Authorization: Bearer <your_jwt_token>
```

Tokens are valid for 24 hours by default (configurable via `JWT_EXPIRES_IN`).

## Testing API Endpoints

### Register a User

```bash
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "passenger@example.com",
    "password": "password123",
    "name": "John Passenger"
  }'
```

### Login

```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "passenger@example.com",
    "password": "password123"
  }'
```

### Get Buses

```bash
curl http://localhost:3001/api/buses \
  -H "Authorization: Bearer <your_token>"
```

## Troubleshooting

### Database Connection Error

- Verify PostgreSQL is running: `psql -U postgres`
- Check DATABASE_* variables in `.env`
- Ensure database user has permissions

### Port Already in Use

Change the PORT in `.env` and restart.

### TypeORM Sync Issues

Clear the database and restart:

```bash
npm run dev
# TypeORM will recreate schema in development
```

## Next Steps

1. **Ride History Endpoints** - Add endpoints for recording and retrieving ride history
2. **Lost Items Management** - Complete CRUD for lost & found items
3. **Seat Predictions** - AI-powered occupancy forecasting
4. **Notifications** - Push notifications for arrivals
5. **Admin Dashboard** - Admin API for system management
6. **Logging** - Winston/pino integration for better monitoring

## License

MIT
