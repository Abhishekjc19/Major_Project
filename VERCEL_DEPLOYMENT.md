# Vercel Deployment Guide

## Step 1: Prepare Your Project

✅ Already done:
- Vercel configuration files created
- Build scripts updated
- Environment variables configured

## Step 2: Push to GitHub

Your project needs to be on GitHub to deploy to Vercel.

```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

## Step 3: Create Vercel Account

1. Go to https://vercel.com
2. Click "Sign Up"
3. Sign up with GitHub account
4. Authorize Vercel to access your repositories

## Step 4: Import Project to Vercel

1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Select your repository from GitHub
4. Click "Import"

## Step 5: Configure Environment Variables

On the Vercel dashboard, go to **Settings → Environment Variables** and add:

```
SUPABASE_URL=https://vwflvallvgoaknjdqehj.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ3Zmx2YWxsdmdvYWtuamRxZWhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgxNjc2MzQsImV4cCI6MjA5Mzc0MzYzNH0.0ujY9JXhb_HNc2Q_3pMNAD-ghxRByMwHBBz66VUhu1s
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ3Zmx2YWxzdmdvYWtuamRxZWhqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODE2NzYzNCwiZXhwIjoyMDkzNzQzNjM0fQ.fvAPyrRQxGlZp4hVlWxSTgQw-PFWxegYeIPc-prXQf8
DATABASE_TYPE=sqlite
JWT_SECRET=your_super_secret_jwt_key_change_this_in_production
NODE_ENV=production
VITE_BACKEND_URL=https://your-vercel-url.vercel.app/api
VITE_SOCKET_URL=https://your-vercel-url.vercel.app
```

Replace `your-vercel-url` with your actual Vercel domain.

## Step 6: Deploy

1. Click "Deploy"
2. Wait for build to complete
3. Your app will be live at `https://your-project.vercel.app`

## Step 7: Verify Deployment

Test your API:
```bash
curl https://your-project.vercel.app/api/health
```

## Project Structure for Vercel

```
/
├── api/                  # Backend API routes
├── backend/             # Node.js backend
├── frontend/            # React frontend
├── vercel.json          # Vercel config
└── package.json         # Root package.json
```

## Troubleshooting

### Build Fails
- Check that both `frontend/` and `backend/` have package.json
- Run `npm install` in both directories locally

### API Not Working
- Check environment variables are set correctly
- Verify SUPABASE_URL and keys are correct
- Check Vercel logs in Dashboard → Deployments → Logs

### Frontend Can't Reach Backend
- Update VITE_BACKEND_URL to your Vercel URL
- Make sure CORS is enabled in backend

## Production Database

⚠️ Important: Your current setup uses SQLite which doesn't persist on Vercel.

**To use persistent database in production:**
- Set `DATABASE_TYPE=postgres` (keep Supabase credentials)
- Or configure a managed PostgreSQL database

## Next Steps

After successful deployment:
1. Test signup/login at https://your-project.vercel.app
2. Test API endpoints
3. Monitor Vercel dashboard for errors
