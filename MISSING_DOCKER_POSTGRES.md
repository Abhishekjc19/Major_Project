# ⚠️ MISSING: Docker or PostgreSQL

Your system doesn't have Docker or PostgreSQL installed.

---

## 🚀 QUICKEST FIX: Install Docker Desktop

### Step 1: Download Docker Desktop
- Go to: **https://www.docker.com/products/docker-desktop**
- Download for Windows
- Install it
- Open Docker Desktop
- Wait until it says "Docker is running"

### Step 2: Then run:
```bash
cd "c:/Major Project"
docker-compose up -d
```

**Time needed: 5 minutes**

---

## 🗄️ ALTERNATIVE: Install PostgreSQL Locally

### Step 1: Download PostgreSQL
- Go to: **https://www.postgresql.org/download/windows/**
- Download PostgreSQL 16
- Install with:
  - Username: `postgres`
  - Password: `postgres`
  - Port: 5432

### Step 2: Create Database
```bash
psql -U postgres -c "CREATE DATABASE omnibus;"
```

### Step 3: Update backend/.env
```
DATABASE_HOST=localhost
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=omnibus
```

### Step 4: Run backend
```bash
cd backend
npm install
npm run seed
npm run dev
```

**Time needed: 10 minutes**

---

## ✅ AFTER EITHER OPTION

Once you have Docker running OR PostgreSQL installed:

```bash
# Terminal 1: Database (if using Docker)
cd "c:/Major Project"
docker-compose up -d

# Terminal 2: Backend
cd "c:/Major Project/backend"
npm install
npm run seed
npm run dev

# Terminal 3: Frontend
cd "c:/Major Project/frontend"
npm install
npm run dev
```

Then open: **http://localhost:5173**

---

## 📦 WHICH OPTION?

| Option | Time | Difficulty | Setup |
|--------|------|-----------|-------|
| **Docker** ⭐ | 5 min | Easy | Download & install Docker Desktop |
| **PostgreSQL** | 10 min | Medium | Download & install PostgreSQL |

**Recommended: Docker** (it handles everything automatically)

---

## 🎯 NEXT STEPS

1. **Choose one option above**
2. **Install Docker OR PostgreSQL**
3. **Come back and tell me when done**
4. **I'll run all the commands for you**

---

**Don't worry! Once you have one of these, everything else works automatically!**
