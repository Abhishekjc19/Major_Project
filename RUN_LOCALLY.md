# 🏃 RUN OMNIBUS LOCALLY - COMPLETE GUIDE

Test everything on **localhost** before deploying to production!

---

## 📋 PREREQUISITES

Make sure you have installed:

```bash
# Check Node.js (18+)
node --version
# Should show: v18.x.x or higher

# Check npm
npm --version
# Should show: 9.x.x or higher

# Check Docker (for PostgreSQL)
docker --version
# Should show: Docker version 20.x or higher

# Check Docker Compose
docker-compose --version
# Should show: docker-compose version 1.29.x or higher
```

**If missing anything:**
- Node.js: https://nodejs.org (download LTS)
- Docker: https://www.docker.com/products/docker-desktop

---

## 🚀 STEP 1: START DATABASE (PostgreSQL)

### Option A: Using Docker (Recommended)

```bash
# From project root directory
cd "c:/Major Project"

# Start PostgreSQL
docker-compose up -d

# Verify it's running
docker-compose ps
# Should show: postgres - Up

# Wait 10 seconds for database to be ready
echo "Waiting for database..."
sleep 10
```

### Option B: Manual PostgreSQL (If Docker not available)

```bash
# Create database
createdb omnibus

# Create user (if needed)
createuser postgres
```

---

## 🔧 STEP 2: START BACKEND SERVER

Open **NEW Terminal** and run:

```bash
# Navigate to backend
cd "c:/Major Project/backend"

# Install dependencies (first time only)
npm install

# Create demo data in database
npm run seed

# Start development server
npm run dev
```

**Expected output:**
```
🚌 OmniBus Backend running on http://localhost:3001
Frontend configured at: http://localhost:5173
```

✅ **Backend is running on http://localhost:3001**

**Keep this terminal open!**

---

## 💻 STEP 3: START FRONTEND

Open **ANOTHER NEW Terminal** and run:

```bash
# Navigate to frontend
cd "c:/Major Project/frontend"

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Expected output:**
```
  VITE v6.2.0  ready in 123 ms

  ➜  Local:   http://localhost:5173/
```

✅ **Frontend is running on http://localhost:5173**

**Keep this terminal open too!**

---

## 🌐 STEP 4: OPEN YOUR APP

Open your browser and go to:

```
http://localhost:5173
```

You should see:
- **OmniBus Login Page**
- Email input field
- Password input field
- "Sign In" button

---

## 👤 STEP 5: LOGIN WITH DEMO CREDENTIALS

### Option A: Passenger Account

```
Email:    passenger@demo.com
Password: demo123
```

Click "Sign In"

---

### Option B: Conductor Account

```
Email:    conductor@demo.com
Password: demo123
```

Click "Sign In"

---

## 📱 STEP 6: EXPLORE THE APP

### After logging in, you'll see:

**Tab 1: Buses** (Default)
- 3 live buses (routes 42A, 15C, 88)
- Real-time occupancy
- Click on a bus to see details
- Can see route, stops, occupancy predictions

**Tab 2: Map** (Coming soon)

**Tab 3: History**
- Your past rides
- Filter by date
- View fare history

**Tab 4: Safety**
- Emergency SOS button
- Lost & Found reports
- Chat with conductors

---

## 🧪 TESTING REAL-TIME FEATURES

### Test 1: Real-Time Bus Updates (Conductor Mode)

**Step 1: Open 2 Browser Tabs**
- Tab 1: http://localhost:5173 (login as conductor)
- Tab 2: http://localhost:5173 (login as passenger)

**Step 2: In Tab 1 (Conductor)**
- Click toggle icon (top-right) → "Conductor Mode" (becomes blue)
- You'll see + and - buttons on each bus

**Step 3: In Tab 1 (Conductor)**
- Click + button on first bus (Route 42A)
- Occupancy increases by 1

**Step 4: In Tab 2 (Passenger)**
- Watch the occupancy update LIVE on the same bus
- No page refresh needed!

✅ **Real-time Socket.IO is working!**

---

### Test 2: Lost & Found Chat

**Step 1: Go to Safety Tab**
- Click "Safety" tab at bottom
- See "Lost & Found" section
- See some sample lost items

**Step 2: Click a Lost Item**
- Example: "Blue Wallet" from Bus B101
- Chat modal opens

**Step 3: Send a Message**
- Type: "Have you found my wallet?"
- Click send button

**Step 4: Wait for Response**
- Conductor auto-responds after ~1.5 seconds
- Chat shows on screen

✅ **Real-time chat is working!**

---

### Test 3: Emergency SOS

**Step 1: Go to Safety Tab**
- See red "ACTIVATE SOS" button

**Step 2: Click SOS Button**
- Button turns black
- Shows countdown: "Cancel SOS (5s)"
- After 5 seconds: "SOS TRIGGERED"

**Step 3: Conductor Receives Alert**
- In another browser tab (conductor), check console
- Check network tab → Socket.IO events

✅ **Emergency system is working!**

---

### Test 4: Ride History

**Step 1: Go to History Tab**
- See list of past rides
- Shows route number, date, time, fare
- Filter by route or date

**Step 2: Click a Ride**
- Opens live tracking of that bus
- Shows map and route
- Can chat with conductor

✅ **Ride history is working!**

---

## 🔍 VERIFY EVERYTHING IS CONNECTED

### Check Backend

Open another terminal:

```bash
# Test API endpoint
curl http://localhost:3001/api/health

# Should return:
# {"status":"ok","timestamp":"2024-04-26T..."}
```

### Check Socket.IO Connection

In browser DevTools Console (F12):

```javascript
// Check if connected to Socket.IO
// Look for messages like:
// "Client connected" in browser console
```

### Check Database

```bash
# Connect to PostgreSQL
psql -U postgres -d omnibus

# List tables
\dt

# Check users
SELECT * FROM users;

# Exit
\q
```

---

## 📊 WHAT YOU SHOULD SEE

### Buses Tab

```
Route 42A → Central Station
├─ Status: Seats Available (green)
├─ Current: 12/50 passengers
├─ Next Stop: Oak Street
└─ Occupancy bar (visual)

Route 15C → North Harbor
├─ Status: Partially Full (yellow)
├─ Current: 38/50 passengers
└─ ...

Route 88 → Tech Park
├─ Status: Near Capacity (red)
├─ Current: 48/50 passengers
└─ ...
```

### Bus Details (Click on a bus)

```
Route: 42A
Destination: Central Station
Occupancy: 24% (with visual grid)
Next Stop: Oak Street

Route Timeline:
├─ Pine Avenue ✓ (passed)
├─ Oak Street ○ (next)
├─ Maple Road ○ (scheduled)
└─ Central Station ○ (scheduled)

Prediction Chart:
└─ Shows predicted occupancy for next 4 hours
```

---

## 🎬 DEMO DATA

### 3 Demo Users

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

### 3 Demo Buses

```
Route 42A:
  Destination: Central Station
  Capacity: 50
  Current: 12 passengers
  Status: Available

Route 15C:
  Destination: North Harbor
  Capacity: 50
  Current: 38 passengers
  Status: Partially Full

Route 88:
  Destination: Tech Park
  Capacity: 50
  Current: 48 passengers
  Status: Near Capacity
```

### 10 Demo Bus Stops

```
1. Pine Avenue
2. Oak Street
3. Maple Road
4. Central Station
5. West Gate
6. Market Square
7. Harbor View
8. City Center
9. Innovation Way
10. Tech Park
```

---

## 🆘 TROUBLESHOOTING

### "Cannot connect to backend"

```bash
# Check backend is running
# In backend terminal, should see:
# 🚌 OmniBus Backend running on http://localhost:3001

# If not, restart:
# 1. Stop backend (Ctrl+C)
# 2. npm run dev
```

### "Database connection error"

```bash
# Check PostgreSQL is running
docker-compose ps

# If not running:
docker-compose up -d

# Wait 10 seconds, then:
docker-compose ps
# Should show: postgres - Up
```

### "Cannot create database - already exists"

```bash
# This is OK! Just means seed already ran
# Data is already in database
# Proceed to test the app
```

### "Port 3001 or 5173 already in use"

```bash
# Stop other processes using these ports
# Option: Use different ports in .env files

# frontend/.env
VITE_SOCKET_URL=http://localhost:3001
# Change 3001 to 3002 if backend on different port

# OR kill the process
# Mac/Linux:
lsof -i :3001
kill -9 <PID>

# Windows:
netstat -ano | findstr :3001
taskkill /PID <PID> /F
```

### "Real-time updates not working"

```bash
# 1. Check WebSocket not blocked by firewall
# 2. Open DevTools (F12)
# 3. Go to Console
# 4. Check for errors
# 5. Look in Network tab → WS (WebSocket)
# 6. Restart backend if needed
```

### "Login fails"

```bash
# Make sure you ran seed:
cd backend
npm run seed

# Check users exist:
psql -U postgres -d omnibus
SELECT * FROM users;
\q
```

---

## 📚 WHAT TO TEST

After logging in:

- [ ] **Load buses** - See 3 buses listed
- [ ] **Click bus** - See details modal
- [ ] **Switch tabs** - Buses, Map, History, Safety work
- [ ] **Conductor mode** - Toggle works
- [ ] **Add passenger** - + button works (conductor)
- [ ] **Real-time update** - Other tab updates live
- [ ] **Remove passenger** - - button works
- [ ] **Chat** - Lost & Found chat works
- [ ] **SOS** - Emergency button works
- [ ] **Logout** - Logout works
- [ ] **Login again** - Can login multiple times

---

## 🎯 NEXT STEPS

### After Testing Locally:

1. ✅ Everything works on localhost?
   - Yes → Move to production deployment
   - No → Check troubleshooting above

2. **Deploy to Production:**
   - Open `GO_LIVE.md`
   - Follow `QUICK_DEPLOY.md`
   - Your app will be live in 30 minutes!

---

## 📝 TERMINAL OUTPUT EXAMPLES

### Backend Terminal (Should show)

```
$ npm run dev

> omnibus-backend@1.0.0 dev
> tsx src/index.ts

🚌 OmniBus Backend running on http://localhost:3001
Frontend configured at: http://localhost:5173
(You'll see socket connections as clients connect)
```

### Frontend Terminal (Should show)

```
$ npm run dev

  VITE v6.2.0  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

---

## ✅ FINAL CHECKLIST

- [ ] Docker running
- [ ] PostgreSQL started (`docker-compose up -d`)
- [ ] Backend installed and running (`npm run dev` in backend/)
- [ ] Backend seeded (`npm run seed`)
- [ ] Frontend installed and running (`npm run dev` in frontend/)
- [ ] Can open http://localhost:5173
- [ ] Can login with demo credentials
- [ ] Can see 3 buses on buses tab
- [ ] Real-time updates work (test in 2 tabs)
- [ ] Chat works (safety tab)
- [ ] SOS works (safety tab)
- [ ] All features accessible

**If all checked: Your app is working perfectly! 🎉**

---

## 🚀 YOU'RE READY!

Your OmniBus app is running locally at:

```
http://localhost:5173
```

Now you can:
1. Test all features
2. Make changes (auto-reload enabled)
3. Deploy to production when ready

**Next: Deploy to make it live for everyone!**

See: `GO_LIVE.md` and `QUICK_DEPLOY.md`
