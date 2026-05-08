# OmniBus - Complete Project Structure

Complete, production-ready full-stack bus tracking application.

## 📂 Directory Structure

```
Major Project/
│
├── 📁 frontend/                    # React frontend application
│   ├── src/
│   │   ├── components/
│   │   │   ├── BusCard.tsx        # Bus card component
│   │   │   └── BusDetails.tsx     # Bus details modal
│   │   ├── lib/
│   │   │   └── utils.ts           # Utility functions
│   │   ├── App.tsx                # Main app with auth
│   │   ├── main.tsx               # React entry point
│   │   ├── types.ts               # TypeScript types
│   │   ├── constants.ts           # Mock data
│   │   └── index.css              # Global styles
│   ├── package.json               # Frontend dependencies
│   ├── tsconfig.json              # TypeScript config
│   ├── vite.config.ts             # Vite configuration
│   ├── index.html                 # HTML entry point
│   ├── .env                       # Frontend environment
│   ├── .gitignore
│   └── README.md                  # Frontend documentation
│
├── 📁 backend/                     # Express backend server
│   ├── src/
│   │   ├── config/
│   │   │   └── database.ts        # TypeORM configuration
│   │   ├── models/                # Database entities
│   │   │   ├── User.ts
│   │   │   ├── Bus.ts
│   │   │   ├── BusStop.ts
│   │   │   ├── RouteStop.ts
│   │   │   ├── RideHistory.ts
│   │   │   ├── LostItem.ts
│   │   │   ├── ChatMessage.ts
│   │   │   └── SOSAlert.ts
│   │   ├── services/              # Business logic
│   │   │   ├── AuthService.ts
│   │   │   └── BusService.ts
│   │   ├── controllers/           # API handlers
│   │   │   ├── authController.ts
│   │   │   └── busController.ts
│   │   ├── routes/                # Express routes
│   │   │   ├── auth.ts
│   │   │   └── buses.ts
│   │   ├── middleware/
│   │   │   └── auth.ts            # JWT & error handling
│   │   ├── sockets/
│   │   │   └── handlers.ts        # Socket.IO events
│   │   ├── utils/
│   │   │   └── auth.ts            # Auth utilities
│   │   └── index.ts               # Server entry point
│   ├── migrations/                # Database migrations
│   ├── seed.ts                    # Demo data seeding
│   ├── package.json               # Backend dependencies
│   ├── tsconfig.json              # TypeScript config
│   ├── .env.example               # Environment template
│   ├── .gitignore
│   └── README.md                  # Backend documentation
│
├── 📄 docker-compose.yml          # PostgreSQL setup
├── 📄 SETUP_GUIDE.md              # Installation guide
├── 📄 BUILD_SUMMARY.md            # Architecture overview
├── 📄 QUICK_REFERENCE.md          # Commands & examples
├── 📄 IMPLEMENTATION_SUMMARY.txt   # Build summary
├── 📄 .env                        # Root environment
├── 📄 .gitignore
└── 📄 README.md                   # Project README

```

## 🚀 Quick Start

### 1. Start PostgreSQL
```bash
docker-compose up -d
```

### 2. Start Backend
```bash
cd backend
npm install
npm run seed
npm run dev
```

Backend runs on `http://localhost:3001`

### 3. Start Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

### 4. Login
- Email: `passenger@demo.com`
- Password: `demo123`

## 📋 Available Commands

### Frontend Commands
```bash
cd frontend

npm run dev        # Start dev server (HMR enabled)
npm run build      # Build for production
npm run preview    # Preview production build
npm run lint       # Check TypeScript
npm run clean      # Remove dist folder
```

### Backend Commands
```bash
cd backend

npm run dev        # Start dev server (HMR enabled)
npm run build      # Build TypeScript
npm start          # Run production build
npm run seed       # Seed demo data
npm run lint       # Check TypeScript
npm run migrate    # Run database migrations
```

## 🔗 Services & Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend (Vite) | 5173 | http://localhost:5173 |
| Backend (Express) | 3001 | http://localhost:3001 |
| PostgreSQL | 5432 | localhost:5432 |
| pgAdmin | 5050 | http://localhost:5050 |

## 📚 Documentation

Read in this order:

1. **SETUP_GUIDE.md** - Step-by-step setup & troubleshooting
2. **QUICK_REFERENCE.md** - Common commands & API examples
3. **BUILD_SUMMARY.md** - Architecture & tech stack
4. **frontend/README.md** - Frontend-specific details
5. **backend/README.md** - Backend-specific details

## 🎯 Key Features

✅ **Real-Time Bus Tracking**
- Live occupancy updates
- GPS location tracking
- Status: available/partial/full

✅ **Authentication & Authorization**
- JWT tokens (24hr expiry)
- Role-based access (passenger, conductor, admin)
- Secure password hashing

✅ **Conductor Mode**
- Manage passenger count
- Update bus location
- Mark stops as passed

✅ **Lost & Found**
- Report lost items
- Real-time chat with conductors
- Status tracking

✅ **Emergency SOS**
- Quick emergency alerts
- Notifies conductors
- Resolution tracking

✅ **Ride History**
- Track past journeys
- Filter by date/route
- Fare information

## 💾 Database

- **PostgreSQL** 12+
- **8 Tables**: Users, Buses, Stops, Routes, History, Lost Items, Chat, SOS
- **3 Demo Users**: Passenger, Conductor, Admin
- **3 Demo Buses**: Routes with full stop information

## 🔐 Security

- JWT authentication
- bcrypt password hashing
- Role-based access control
- CORS configured
- Socket.IO token validation

## 🛠 Tech Stack

### Frontend
- React 19.0
- TypeScript 5.8
- Vite 6.2
- Tailwind CSS 4.1
- Socket.IO Client 4.8

### Backend
- Node.js 18+
- Express.js 4.21
- PostgreSQL 12+
- TypeORM 0.3.19
- Socket.IO 4.8

## 📝 Demo Credentials

**Passenger**
- Email: passenger@demo.com
- Password: demo123

**Conductor**
- Email: conductor@demo.com
- Password: demo123

**Admin**
- Email: admin@demo.com
- Password: demo123

## 🚢 Deployment

### Build Frontend
```bash
cd frontend
npm run build
# Output: dist/ folder
```

### Build Backend
```bash
cd backend
npm run build
npm start
# Output: dist/ folder
```

Deploy:
- Frontend to: Netlify, Vercel, AWS S3, etc.
- Backend to: Railway, Render, AWS EC2, etc.
- Database: AWS RDS, DigitalOcean, etc.

## 📞 Need Help?

1. **Setup Issues?** → See SETUP_GUIDE.md
2. **Command Questions?** → See QUICK_REFERENCE.md
3. **Architecture?** → See BUILD_SUMMARY.md
4. **Frontend Specific?** → See frontend/README.md
5. **Backend Specific?** → See backend/README.md

## 📈 What's Included

- ✅ 19 TypeScript backend files
- ✅ 8 database entities/models
- ✅ 21 API endpoints
- ✅ 12+ Socket.IO events
- ✅ 500+ lines of documentation
- ✅ Docker setup
- ✅ Seed script
- ✅ Production-ready code

## 🎓 Next Steps

1. ✅ Run the application (see Quick Start)
2. ✅ Explore the features
3. ✅ Test with demo credentials
4. ✅ Customize as needed
5. ✅ Deploy to production

## 📄 License

MIT

---

**Ready to run?** Start with the Quick Start section above! 🚌
