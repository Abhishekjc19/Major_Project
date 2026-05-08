# OmniBus - Complete Setup Guide

Welcome! This guide will help you set up and run the complete OmniBus application (Frontend + Backend).

## Architecture Overview

```
OmniBus Application
├── Frontend (React + Vite)
│   ├── Real-time bus tracking
│   ├── Lost & Found reports
│   ├── Emergency SOS
│   └── Conductor management mode
│
├── Backend (Node.js + Express)
│   ├── PostgreSQL database
│   ├── JWT authentication
│   ├── REST API
│   └── Socket.IO real-time updates
│
└── Database (PostgreSQL)
    ├── Users, Buses, Stops
    ├── Ride history, Lost items
    └── Chat messages, SOS alerts
```

## Prerequisites

- **Node.js** 18+ ([download](https://nodejs.org))
- **PostgreSQL** 12+ ([download](https://www.postgresql.org/download/) or use Docker)
- **Docker & Docker Compose** (optional, for easy database setup)
- **npm** (comes with Node.js)

## Quick Start (Recommended: 5-10 minutes)

### Option 1: With Docker (Easiest)

```bash
# 1. Start PostgreSQL with Docker
docker-compose up -d

# Wait 10 seconds for PostgreSQL to start...

# 2. Install backend dependencies
cd backend
npm install

# 3. Seed demo data
npm run seed

# 4. Start backend (keep running)
npm run dev

# In a new terminal:
# 5. Install frontend dependencies
cd ..
npm install

# 6. Start frontend (keep running)
npm run dev
```

Your app will be available at: **http://localhost:5173**

### Option 2: Without Docker (Manual PostgreSQL)

```bash
# 1. Create PostgreSQL database
createdb omnibus

# 2. Update backend/.env with your PostgreSQL credentials
# Edit backend/.env:
# DATABASE_HOST=localhost
# DATABASE_USER=your_postgres_user
# DATABASE_PASSWORD=your_postgres_password

# 3-6. Same as Option 1 steps 2-6
```

## Detailed Installation

### Backend Setup

```bash
cd backend

# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 3. Seed demo data (creates users and buses)
npm run seed

# 4. Start development server
npm run dev
```

**Expected output:**
```
🚌 OmniBus Backend running on http://localhost:3001
Frontend configured at: http://localhost:5173
```

### Frontend Setup

```bash
# From project root
npm install

# Start development server
npm run dev
```

**Expected output:**
```
  VITE v5.0.0  ready in 123 ms

  ➜  Local:   http://localhost:5173/
```

## Demo Credentials

After running the seed script, you can login with:

### Passenger Account
- **Email:** passenger@demo.com
- **Password:** demo123
- **Can:** View buses, Track rides, Report lost items, Use SOS

### Conductor Account
- **Email:** conductor@demo.com
- **Password:** demo123
- **Can:** Update occupancy, Change locations, Mark stops, Chat with passengers

### Admin Account
- **Email:** admin@demo.com
- **Password:** demo123
- **Can:** All conductor actions + system management

## Features Walkthrough

### 1. View Live Buses
- Go to the "Buses" tab
- See all available buses with real-time occupancy
- Filter by status: Available, Partially Full, Near Capacity
- Search by route number or destination

### 2. Conductor Mode
- Toggle Conductor Mode in the top-right (UserCheck icon)
- Click + or - buttons to update passenger count
- Changes sync in real-time to all connected passengers

### 3. Ride History
- Click the "History" tab
- See your past journeys
- Filter by date or route

### 4. Safety Features
- Click "Safety" tab to access Emergency SOS
- Report lost items and chat with conductors
- Real-time notifications for support responses

## Troubleshooting

### Port Already in Use

If port 3001 (backend) or 5173 (frontend) is already in use:

**Backend:** Edit `backend/.env` and change PORT
```
PORT=3002
```

**Frontend:** Edit `vite.config.ts` or run:
```bash
npm run dev -- --port 5174
```

### Database Connection Error

```
error: connect ECONNREFUSED 127.0.0.1:5432
```

**Solutions:**
1. Ensure PostgreSQL is running:
   ```bash
   # macOS
   brew services start postgresql
   
   # Windows: Start PostgreSQL service
   # Linux
   sudo service postgresql start
   ```

2. Check `.env` database credentials match your setup

3. Verify database exists:
   ```bash
   psql -U postgres -c "CREATE DATABASE omnibus;"
   ```

### Socket.IO Connection Failed

If real-time updates aren't working:

1. Ensure backend is running on port 3001
2. Check `VITE_SOCKET_URL` in `.env`
3. Verify frontend `.env` is loaded:
   ```bash
   # Restart frontend dev server
   npm run dev
   ```

### TypeORM Synchronization Issue

```
error: relation "buses" does not exist
```

**Solution:** Delete database and reseed:
```bash
dropdb omnibus
createdb omnibus
cd backend
npm run seed
```

## File Structure

```
Major Project/
├── backend/                    # Express backend
│   ├── src/
│   │   ├── config/            # Database config
│   │   ├── controllers/       # API handlers
│   │   ├── models/            # TypeORM entities
│   │   ├── routes/            # Express routes
│   │   ├── services/          # Business logic
│   │   ├── sockets/           # Socket.IO handlers
│   │   ├── middleware/        # Auth, error handling
│   │   ├── utils/             # Helpers
│   │   └── index.ts           # Entry point
│   ├── .env                   # Configuration
│   ├── seed.ts                # Demo data script
│   └── package.json
│
├── src/                        # React frontend
│   ├── components/            # React components
│   ├── pages/                 # Page components
│   ├── types.ts               # TypeScript types
│   ├── constants.ts           # Constants
│   ├── App.tsx                # Main component
│   └── main.tsx               # Entry point
│
├── .env                        # Frontend environment
├── package.json
├── vite.config.ts
└── docker-compose.yml         # PostgreSQL config
```

## API Documentation

### Authentication
```bash
# Register
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe"
  }'

# Login
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Buses
```bash
# Get all buses
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:3001/api/buses

# Get specific bus
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:3001/api/buses/<BUS_ID>

# Update occupancy (conductor only)
curl -X POST http://localhost:3001/api/buses/<BUS_ID>/occupancy \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{ "change": 1 }'
```

## Production Deployment

### Build Frontend
```bash
npm run build
# Creates optimized build in dist/
```

### Build Backend
```bash
cd backend
npm run build
npm start
```

### Environment Variables for Production

**backend/.env:**
```
NODE_ENV=production
DATABASE_HOST=your-postgres-host
DATABASE_NAME=omnibus
JWT_SECRET=your-very-secret-key-change-this
FRONTEND_URL=https://yourdomain.com
```

## Next Steps

- **Customize branding** - Update colors in tailwind.config
- **Add more routes** - Extend API endpoints for new features
- **Implement payments** - Add fare payment integration
- **Add map integration** - Use Google Maps or Mapbox
- **Setup CI/CD** - Deploy with GitHub Actions or GitLab CI

## Support & Debugging

### View Backend Logs
```bash
# Backend logs are displayed in terminal
# Look for socket connections and API calls
```

### View Frontend Errors
```bash
# Open browser DevTools (F12)
# Check Console tab for JavaScript errors
# Check Network tab for API calls
```

### Enable Verbose Logging
Edit `backend/src/index.ts` to enable TypeORM logging:
```typescript
logging: process.env.NODE_ENV === 'development'  // Set to true
```

## Performance Tips

1. **Database Indexing** - Add indexes on frequently queried fields
2. **Caching** - Use Redis for session storage
3. **Connection Pooling** - Configure TypeORM pool size
4. **API Rate Limiting** - Implement with express-rate-limit

## Security Considerations

- ✅ JWT tokens (24hr expiry)
- ✅ Password hashing (bcrypt)
- ✅ CORS configured
- ✅ Role-based access control
- ⚠️ Use HTTPS in production
- ⚠️ Rotate JWT_SECRET regularly
- ⚠️ Never commit `.env` files

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Port 3001 in use | Change PORT in backend/.env |
| Database exists error | Run `dropdb omnibus` then reseed |
| Socket.IO won't connect | Ensure backend is running, check VITE_SOCKET_URL |
| Login fails | Check DB is seeded with `npm run seed` |
| TypeScript errors | Run `npm run lint` to check for issues |

## Contributing

Feel free to extend the application with:
- Additional API endpoints
- More real-time features
- Enhanced UI components
- Payment integration
- Mobile app (React Native)

## License

MIT

---

**Happy transit tracking! 🚌**

For more details, see:
- Frontend: `README.md` (root)
- Backend: `backend/README.md`
- Architecture: `plans/cozy-skipping-eich.md`
