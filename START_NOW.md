# ▶️ COPY-PASTE: START YOUR APP NOW

**Follow these commands exactly - copy and paste them!**

---

## 🔧 TERMINAL 1: START DATABASE

```bash
cd "c:/Major Project"
docker-compose up -d
docker-compose ps
```

**Wait for output showing:**
```
postgres  ...  Up
```

✅ **Database is running**

---

## 🔌 TERMINAL 2: START BACKEND

**Open a NEW terminal/command prompt**

```bash
cd "c:/Major Project/backend"
npm install
npm run seed
npm run dev
```

**Wait for output showing:**
```
🚌 OmniBus Backend running on http://localhost:3001
```

✅ **Backend is running on http://localhost:3001**

**Keep this terminal open!**

---

## 🎨 TERMINAL 3: START FRONTEND

**Open ANOTHER NEW terminal/command prompt**

```bash
cd "c:/Major Project/frontend"
npm install
npm run dev
```

**Wait for output showing:**
```
➜  Local:   http://localhost:5173/
```

✅ **Frontend is running on http://localhost:5173**

**Keep this terminal open!**

---

## 🌐 STEP 4: OPEN IN BROWSER

### Click this link or copy to browser:

```
http://localhost:5173
```

---

## 👤 STEP 5: LOGIN

### Use either account:

**Passenger:**
```
Email:    passenger@demo.com
Password: demo123
```

**OR Conductor:**
```
Email:    conductor@demo.com
Password: demo123
```

Click "Sign In"

---

## ✅ YOU SHOULD SEE

After login:
- ✅ 3 buses listed (routes 42A, 15C, 88)
- ✅ Real-time occupancy percentages
- ✅ Bus status (available/partial/full)
- ✅ Navigation tabs at bottom (Buses, Map, History, Safety)

---

## 🧪 QUICK TEST

### Test 1: Open 2 Tabs

**Tab 1:** http://localhost:5173 → Login as Conductor  
**Tab 2:** http://localhost:5173 → Login as Passenger

### Test 2: Add Passenger (Tab 1, Conductor)

- Click toggle at top-right → "Conductor Mode" (turns blue)
- Click **+** button on first bus (Route 42A)
- Occupancy increases

### Test 3: Watch Real-Time Update (Tab 2, Passenger)

- Look at Route 42A in Tab 2
- Occupancy **updates automatically** (no refresh!)

✅ **Real-time Socket.IO working!**

---

## 📋 QUICK TROUBLESHOOTING

### "Cannot connect to backend"
```bash
# Check backend terminal
# Should show: 🚌 OmniBus Backend running on http://localhost:3001
# If not, restart it (Ctrl+C, then npm run dev)
```

### "Blank page or 404"
```bash
# Check frontend terminal
# Should show: ➜  Local:   http://localhost:5173/
# If not, restart it (Ctrl+C, then npm run dev)
```

### "Database error"
```bash
# Check PostgreSQL is running
docker-compose ps
# Should show: postgres ... Up

# If not:
docker-compose up -d
```

### "Cannot login - wrong credentials"
```bash
# Make sure you ran seed in backend terminal:
# It should have shown: "✅ Database seeded successfully!"

# If not, run:
cd backend
npm run seed
```

---

## 🎯 WHAT TO DO NEXT

### When everything is working:

1. **Explore the app**
   - Switch between tabs
   - Try conductor mode
   - Test real-time updates
   - Try Lost & Found
   - Try Emergency SOS

2. **Make code changes**
   - Edit files in frontend/ or backend/
   - Changes auto-reload (Vite HMR)
   - No need to restart

3. **When ready to deploy:**
   - See `GO_LIVE.md`
   - See `QUICK_DEPLOY.md`
   - Deploy in 30 minutes!

---

## ⚠️ IMPORTANT NOTES

**Terminal 1 (Database):**
- Can minimize, don't close
- Keep running in background

**Terminal 2 (Backend):**
- Must stay open
- Shows errors/logs
- Press Ctrl+C to stop

**Terminal 3 (Frontend):**
- Must stay open
- Auto-reloads on code changes
- Press Ctrl+C to stop

---

## 🚨 IF SOMETHING GOES WRONG

### Restart Everything:

```bash
# 1. Close all terminals (Ctrl+C)

# 2. Stop database
docker-compose down

# 3. In new terminal, start fresh
cd "c:/Major Project"
docker-compose up -d

# 4. In new terminal, backend
cd backend
npm run dev

# 5. In new terminal, frontend
cd frontend
npm run dev

# 6. Open http://localhost:5173
```

---

## 🎉 SUCCESS INDICATORS

You'll know it's working when:

✅ 3 buses appear on screen  
✅ Buses have different occupancy levels  
✅ Status shows: "Available", "Partially Full", "Near Capacity"  
✅ Clicking a bus shows details modal  
✅ Can switch tabs (Buses, History, Safety)  
✅ Real-time updates work (tested above)  
✅ Can login/logout  

---

## 📍 URLS TO USE

```
Frontend:    http://localhost:5173
Backend API: http://localhost:3001/api
Health:      http://localhost:3001/api/health
```

---

**START NOW:**

1. Copy first command block (Terminal 1)
2. Copy second command block (Terminal 2)  
3. Copy third command block (Terminal 3)
4. Open http://localhost:5173
5. Login with credentials above
6. See your app work! 🚀

