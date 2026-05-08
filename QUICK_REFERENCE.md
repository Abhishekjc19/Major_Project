# OmniBus - Quick Reference

## Start/Stop Commands

### Start Everything (Recommended Order)

```bash
# Terminal 1: Start PostgreSQL
docker-compose up -d

# Terminal 2: Start Backend
cd backend
npm install  # First time only
npm run seed # First time only (creates demo data)
npm run dev

# Terminal 3: Start Frontend
npm install  # First time only
npm run dev
```

### Stop Everything

```bash
# Stop frontend & backend (Ctrl+C in terminals)
# Stop PostgreSQL
docker-compose down
```

## Common Commands

### Backend
```bash
npm run dev           # Start dev server (with hot reload)
npm run build         # Build TypeScript to JavaScript
npm start             # Run built JavaScript
npm run seed          # Populate demo data
npm run lint          # Check TypeScript syntax
npm run migrate       # Run database migrations
```

### Frontend
```bash
npm run dev           # Start dev server on port 5173
npm run build         # Build for production
npm run preview       # Preview production build
npm run lint          # Check TypeScript
```

### Database
```bash
# Access PostgreSQL CLI
psql -U postgres -d omnibus

# List tables
\dt

# View users
SELECT id, email, name, role FROM users;

# View buses
SELECT id, route_number, destination, current_occupancy FROM buses;

# Exit
\q
```

## Default Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend | 5173 | http://localhost:5173 |
| Backend | 3001 | http://localhost:3001 |
| PostgreSQL | 5432 | localhost:5432 |
| pgAdmin | 5050 | http://localhost:5050 |

## Debug Tips

### Check Backend Logs
- Look at terminal where `npm run dev` is running
- Log messages show socket connections and errors
- API calls are logged with method/path

### Check Frontend Logs
- Open browser DevTools: F12 or Cmd+Option+I
- Console tab shows JavaScript errors
- Network tab shows API calls to backend

### Check Database
```bash
# Connect to database
psql -U postgres -d omnibus

# Check tables exist
\dt

# Check users table
SELECT * FROM users LIMIT 5;
```

### Verify Socket.IO Connection
In browser DevTools Console:
```javascript
// Socket.IO connection status
io.socket  // Should show socket instance
```

## Common Error Fixes

| Error | Fix |
|-------|-----|
| "Port 3001 already in use" | Change PORT in `backend/.env` |
| "Cannot find module" | Run `npm install` in that directory |
| "Database doesn't exist" | Run `npm run seed` in backend |
| "No token provided" | Login again or check localStorage |
| "Socket won't connect" | Restart both frontend & backend |

## File Locations

| What | Location |
|------|----------|
| Backend config | `backend/.env` |
| Frontend config | `.env` |
| Database models | `backend/src/models/*.ts` |
| API routes | `backend/src/routes/*.ts` |
| Services | `backend/src/services/*.ts` |
| Frontend components | `src/components/*.tsx` |

## Testing the App

### 1. Login Test
- Go to http://localhost:5173
- Use `passenger@demo.com` / `demo123`

### 2. Bus Tracking Test
- Should see 3 buses in the list
- Click on any bus to see details
- Details show occupancy, stops, predictions

### 3. Real-Time Test (need 2 browsers)
- Open app in 2 browser windows
- In first window: Toggle to Conductor Mode
- In first window: Click + button to add passenger
- In second window: Watch occupancy update live

### 4. Chat Test
- Go to Safety tab
- Click "Lost & Found" item
- Type message and send
- Should see conductor response (simulated)

## Environment Variables Explained

### Backend `.env`
```
DATABASE_HOST          # PostgreSQL host
DATABASE_PORT          # PostgreSQL port
DATABASE_USER          # PostgreSQL username
DATABASE_PASSWORD      # PostgreSQL password
DATABASE_NAME          # Database name
NODE_ENV              # "development" or "production"
PORT                  # Server port (3001)
JWT_SECRET            # Secret for signing tokens (change in prod!)
JWT_EXPIRES_IN        # Token expiration time
FRONTEND_URL          # Frontend URL for CORS
SOCKET_IO_CORS_ORIGIN # Same as FRONTEND_URL
```

### Frontend `.env`
```
VITE_API_URL          # Backend API base URL
VITE_SOCKET_URL       # Backend Socket.IO URL
VITE_FRONTEND_URL     # Frontend URL
```

## API Examples

### Login
```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "passenger@demo.com",
    "password": "demo123"
  }'
```

Response:
```json
{
  "user": {
    "id": "...",
    "email": "passenger@demo.com",
    "name": "Demo Passenger",
    "role": "passenger"
  },
  "token": "..."
}
```

### Get Buses
```bash
# Use token from login response
curl http://localhost:3001/api/buses \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Response:
```json
[
  {
    "id": "...",
    "route_number": "42A",
    "destination": "Central Station",
    "current_occupancy": 12,
    "totalCapacity": 50,
    "status": "available",
    "stops": [...]
  }
]
```

## Socket.IO Events Cheat Sheet

### Client sends (Frontend → Backend)
```javascript
socket.emit('buses:request-update')          // Get bus data
socket.emit('ticket:sold', {busId, count})   // Add passenger
socket.emit('ticket:cancelled', {busId, count}) // Remove passenger
socket.emit('sos:activate', {description})   // Emergency alert
socket.emit('chat:message', {lostItemId, message}) // Send message
```

### Client receives (Backend → Frontend)
```javascript
socket.on('buses:init', buses)               // Initial data
socket.on('bus:update', bus)                 // Bus state changed
socket.on('bus:stop-reached', data)          // New stop reached
socket.on('chat:message', msg)               // New message
socket.on('sos:alert', alert)                // Emergency alert
```

## Performance Tips

1. **Reduce re-renders**: Use React.memo for bus cards
2. **Debounce search**: Add delay to search input
3. **Lazy load components**: Code split pages
4. **Cache API responses**: Store in localStorage
5. **Optimize images**: Use WebP format

## Security Notes

- 🔒 JWT tokens expire after 24 hours
- 🔒 Passwords hashed with bcrypt
- 🔒 CORS restricts to frontend URL
- ⚠️ Never commit `.env` with real secrets
- ⚠️ Always use HTTPS in production
- ⚠️ Change JWT_SECRET in production

## Useful Resources

- [Express.js Docs](https://expressjs.com)
- [TypeORM Docs](https://typeorm.io)
- [Socket.IO Docs](https://socket.io/docs)
- [React Docs](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)

## Feature Roadmap

- [ ] Implement ride history endpoints
- [ ] Add lost items management
- [ ] Integrate real map (Google Maps)
- [ ] Push notifications
- [ ] Payment integration
- [ ] Admin dashboard
- [ ] Mobile app (React Native)
- [ ] Predictions AI

---

**Need help?** Check `SETUP_GUIDE.md` or `BUILD_SUMMARY.md`
