# Vercel Deployment Guide for OmniBus

## 🚀 Quick Deployment Steps

### Step 1: Deploy Backend to Render (Free tier)

1. Go to https://render.com
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `npm install && npm run build`
   - **Start Command:** `npm start`
   - **Root Directory:** `backend`
   - **Environment:** Node
5. Add Environment Variables:
   ```
   NODE_ENV=production
   DATABASE_TYPE=sqlite
   JWT_SECRET=your-secret-key-here
   PORT=3000
   FRONTEND_URL=https://your-frontend.vercel.app
   SUPABASE_URL=https://vwflvallvgoaknjdqehj.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```
6. Click **Create Web Service** and wait for deployment

### Step 2: Deploy Frontend to Vercel

1. Go to https://vercel.com
2. Click **Add New** → **Project**
3. Import your GitHub repository
4. Configure:
   - **Framework:** Vite
   - **Build Command:** `cd frontend && npm run build`
   - **Output Directory:** `frontend/dist`
   - **Root Directory:** `.` (or leave default)
5. Add Environment Variables:
   ```
   VITE_BACKEND_URL=https://your-backend-on-render.onrender.com
   VITE_SOCKET_URL=https://your-backend-on-render.onrender.com
   ```
6. Click **Deploy**

### Step 3: Update Your Frontend Code

Update `frontend/src/constants.ts` or wherever you define the API URLs:

```typescript
export const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3001';
export const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:3001';
```

### Backend Deployment Alternatives:

- **Railway.app** - Free tier, easy PostgreSQL setup
- **Fly.io** - Good for Docker
- **Heroku** - Paid but reliable
- **AWS Lambda** - Serverless option

## 📝 Environment Variables Checklist

**Frontend (.env.production):**
```
VITE_BACKEND_URL=your-backend-url
VITE_SOCKET_URL=your-backend-url
```

**Backend (Render/wherever):**
```
NODE_ENV=production
JWT_SECRET=generate-a-strong-secret
DATABASE_TYPE=sqlite
SUPABASE_URL=https://vwflvallvgoaknjdqehj.supabase.co
SUPABASE_ANON_KEY=your-key
SUPABASE_SERVICE_ROLE_KEY=your-key
```

## ⚠️ Important Notes

1. **Socket.io on Vercel**: Vercel doesn't support WebSockets directly. Deploy backend on Render/Railway/Fly.io instead.
2. **Database**: SQLite works for now. For production, upgrade to PostgreSQL.
3. **CORS**: Update FRONTEND_URL in backend env vars when deploying.
4. **API Keys**: Never commit `.env` files. Set them in deployment platform's environment variables.

## 🔗 Useful Links

- [Vercel Docs](https://vercel.com/docs)
- [Render.com Docs](https://render.com/docs)
- [Supabase PostgreSQL](https://supabase.com)
