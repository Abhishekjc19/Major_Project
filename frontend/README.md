# OmniBus Frontend

React + TypeScript frontend for the OmniBus real-time bus tracking application.

## Features

- ✅ Real-time bus tracking with Socket.IO
- ✅ User authentication with JWT
- ✅ Live occupancy management (conductor mode)
- ✅ Lost & Found reporting system
- ✅ Emergency SOS alerts
- ✅ Ride history tracking
- ✅ Responsive design with Tailwind CSS
- ✅ Smooth animations with Framer Motion

## Tech Stack

- **React** 19.0
- **TypeScript** 5.8
- **Vite** 6.2 (build tool)
- **Tailwind CSS** 4.1
- **Socket.IO Client** 4.8
- **Recharts** 3.8 (charts)
- **Motion** 12.23 (animations)
- **Lucide React** (icons)

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy `.env` file (already configured with defaults):

```bash
VITE_API_URL=http://localhost:3001/api
VITE_SOCKET_URL=http://localhost:3001
VITE_FRONTEND_URL=http://localhost:5173
```

### 3. Start Development Server

```bash
npm run dev
```

Server will run at http://localhost:5173

## Scripts

```bash
npm run dev        # Start development server with hot reload
npm run build      # Build for production
npm run preview    # Preview production build locally
npm run clean      # Remove dist folder
npm run lint       # Check TypeScript syntax
```

## Project Structure

```
src/
├── components/          # Reusable React components
│   ├── BusCard.tsx     # Bus card display
│   └── BusDetails.tsx  # Bus details modal
├── App.tsx             # Main app component with routing
├── main.tsx            # React app entry point
├── types.ts            # TypeScript type definitions
├── constants.ts        # App constants & mock data
├── index.css           # Global styles
└── lib/
    └── utils.ts        # Utility functions (cn, etc)
```

## Authentication

### Login Credentials (Demo)

```
Passenger:
  Email: passenger@demo.com
  Password: demo123

Conductor:
  Email: conductor@demo.com
  Password: demo123

Admin:
  Email: admin@demo.com
  Password: demo123
```

The frontend automatically:
- Stores JWT token in localStorage
- Connects to backend via Socket.IO with token
- Maintains session on page reload
- Handles token refresh

## Component Overview

### BusCard
- Displays bus information
- Shows real-time occupancy
- Click to view details

### BusDetails
- Full bus information modal
- Route timeline
- Occupancy predictions
- Live stop tracking

### App Component
- Main application shell
- Tab navigation (Buses, Map, History, Safety)
- Real-time bus updates via Socket.IO
- Conductor mode toggle
- Authentication handling

## Real-Time Features

Socket.IO connects to backend and receives:

```javascript
// Incoming events
socket.on('buses:init', buses)      // Initial bus list
socket.on('bus:update', bus)        // Bus state changed
socket.on('bus:stop-reached', data) // New stop reached
socket.on('chat:message', msg)      // New message
socket.on('sos:alert', alert)       // Emergency alert
```

Emitted events:

```javascript
socket.emit('buses:request-update')            // Get bus data
socket.emit('ticket:sold', {busId, count})    // Add passenger
socket.emit('ticket:cancelled', {busId, count}) // Remove passenger
socket.emit('sos:activate')                    // Emergency alert
socket.emit('chat:message', {lostItemId, msg}) // Send message
```

## Styling

Uses **Tailwind CSS** with custom theme:

- Primary color: `#3B82F6` (brand-primary)
- Success: `#10B981`
- Warning: `#F59E0B`
- Danger: `#EF4444`

Global styles in `src/index.css`

## Building for Production

```bash
npm run build
```

Creates optimized build in `dist/` folder. Ready to deploy to any static hosting service.

### Deploy with Vite

```bash
npm run build      # Build
npm run preview    # Test build locally
# Upload dist/ to hosting
```

## Debugging

### Check Console Logs
```javascript
// In browser DevTools console
// Socket.IO connection status
console.log(socket)

// View stored token
console.log(localStorage.getItem('authToken'))

// View stored user
console.log(localStorage.getItem('authUser'))
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Cannot connect to backend" | Ensure backend running on 3001, check VITE_SOCKET_URL |
| "Login fails" | Ensure backend database is seeded with demo users |
| "Real-time updates not working" | Check Socket.IO connection in browser console |
| "Hot reload not working" | Restart dev server, check DISABLE_HMR env var |

## Performance Tips

1. Use React.memo for expensive components (BusCard)
2. Debounce search input
3. Use lazy loading for route components
4. Cache API responses in localStorage
5. Monitor bundle size with Vite

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Environment Variables

| Variable | Description | Default |
|----------|-----------|---------|
| VITE_API_URL | Backend API URL | http://localhost:3001/api |
| VITE_SOCKET_URL | Socket.IO server URL | http://localhost:3001 |
| VITE_FRONTEND_URL | Frontend URL | http://localhost:5173 |
| GEMINI_API_KEY | Google Gemini API key | (optional) |

## Contributing

1. Create a component in `src/components/`
2. Use TypeScript types from `src/types.ts`
3. Follow existing code style
4. Test in dev server before committing

## Learn More

- [React Docs](https://react.dev)
- [Vite Docs](https://vitejs.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Socket.IO Client](https://socket.io/docs/v4/client-api/)

## License

MIT
