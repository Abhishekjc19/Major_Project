# 🚀 OMNIBUS - PRODUCTION DEPLOYMENT GUIDE

Deploy your OmniBus application to the cloud and access it from anywhere!

## 📋 Deployment Overview

```
Your Domain (example.com)
         ↓
    Frontend (Netlify/Vercel)
         ↓ (API calls & WebSocket)
    Backend (Railway/Render)
         ↓
    Database (AWS RDS/DigitalOcean)
```

---

## 🔧 OPTION 1: EASIEST - Railway + Netlify (Recommended)

### Step 1: Deploy Backend to Railway

**1. Sign up at [railway.app](https://railway.app)**

**2. Create new project:**
- Click "New Project"
- Select "GitHub"
- Connect your repository

**3. Add PostgreSQL Database:**
- Click "Add Service"
- Select "PostgreSQL"
- Railway creates database automatically

**4. Deploy Backend:**
- Connect to your GitHub backend folder
- Railway auto-detects Node.js
- Set environment variables:

```env
DATABASE_HOST=<railway-db-host>
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=<railway-db-password>
DATABASE_NAME=omnibus
NODE_ENV=production
JWT_SECRET=<generate-random-secret>
FRONTEND_URL=https://yourdomain.com
PORT=3000
```

**5. Get Backend URL:**
- Railway provides: `https://backend-xxxxx.up.railway.app`
- Use this in frontend configuration

---

### Step 2: Deploy Frontend to Netlify

**1. Sign up at [netlify.com](https://netlify.com)**

**2. Build frontend:**
```bash
cd frontend
npm run build
# Creates dist/ folder
```

**3. Connect to GitHub:**
- Click "New site from Git"
- Select your repository
- Set build command: `npm run build` (from frontend folder)
- Set publish directory: `frontend/dist`

**4. Environment Variables:**
In Netlify dashboard → Settings → Build & Deploy → Environment:

```
VITE_API_URL=https://backend-xxxxx.up.railway.app/api
VITE_SOCKET_URL=https://backend-xxxxx.up.railway.app
VITE_FRONTEND_URL=https://yourdomain.com
```

**5. Deploy:**
- Click "Deploy site"
- Netlify auto-deploys on every push

**6. Get Frontend URL:**
- Netlify provides: `https://your-site.netlify.app`

---

### Step 3: Connect Custom Domain

**1. In Netlify:**
- Settings → Domain Management
- Add custom domain

**2. Update DNS:**
- Add CNAME record pointing to Netlify
- DNS provider: GoDaddy, Namecheap, etc.

---

## 🔧 OPTION 2: Vercel + Render (Also Easy)

### Deploy Frontend to Vercel

**1. Sign up at [vercel.com](https://vercel.com)**

**2. Import GitHub Project:**
- Click "New Project"
- Select your repository
- Configure:
  - Root directory: `frontend`
  - Build command: `npm run build`
  - Output directory: `.next` or `dist`

**3. Add Environment Variables:**
```
VITE_API_URL=https://backend-render-url/api
VITE_SOCKET_URL=https://backend-render-url
VITE_FRONTEND_URL=https://yourdomain.com
```

**4. Deploy:** Click "Deploy" - Done!

---

### Deploy Backend to Render

**1. Sign up at [render.com](https://render.com)**

**2. Create New Service:**
- Click "New +"
- Select "Web Service"
- Connect GitHub

**3. Configure:**
- Root directory: `backend`
- Build command: `npm install && npm run build`
- Start command: `npm start`
- Runtime: Node

**4. Add Environment Variables:**
```
DATABASE_URL=postgresql://user:password@host:5432/omnibus
NODE_ENV=production
JWT_SECRET=<random-secret>
FRONTEND_URL=https://yourdomain.com
```

**5. Create Database:**
- Click "Database"
- Select PostgreSQL
- Render provides connection string

**6. Deploy:** Auto-deploys from GitHub

---

## 💾 OPTION 3: Full Cloud - AWS

### Deploy Everything to AWS

#### A. Database (AWS RDS)

```bash
# 1. AWS Console → RDS → Create Database
# - Engine: PostgreSQL
# - Instance class: db.t3.micro (free tier)
# - Storage: 20 GB
# - Multi-AZ: No (saves cost)

# 2. Get connection string:
# postgresql://username:password@rds-host:5432/omnibus

# 3. Security Group: Allow inbound on port 5432
```

#### B. Backend (AWS EC2 or Elastic Beanstalk)

**Option B1: Elastic Beanstalk (Easier)**
```bash
# 1. Install EB CLI
brew install awsebcli

# 2. Initialize in backend folder
cd backend
eb init -p node.js omnibus-backend

# 3. Create environment
eb create omnibus-prod

# 4. Set environment variables
eb setenv \
  DATABASE_URL=postgresql://user:pass@rds-host/omnibus \
  NODE_ENV=production \
  JWT_SECRET=your-secret \
  FRONTEND_URL=https://yourdomain.com

# 5. Deploy
git push && eb deploy

# 6. Get URL
eb open
```

**Option B2: EC2 (More control)**
```bash
# 1. Launch Ubuntu EC2 instance
# 2. SSH into instance
ssh -i key.pem ec2-user@instance-ip

# 3. Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 4. Clone repository
git clone your-repo
cd backend

# 5. Install dependencies
npm install

# 6. Set environment
cat > .env << EOF
DATABASE_URL=postgresql://user:pass@rds-host/omnibus
NODE_ENV=production
PORT=3000
EOF

# 7. Run with PM2 (process manager)
npm install -g pm2
pm2 start npm --name "omnibus" -- start

# 8. Setup reverse proxy with Nginx
# (See Nginx setup below)
```

#### C. Frontend (AWS S3 + CloudFront)

```bash
# 1. Build frontend
cd frontend
npm run build

# 2. Create S3 bucket
aws s3 mb s3://omnibus-frontend

# 3. Upload build files
aws s3 sync dist/ s3://omnibus-frontend --delete

# 4. Create CloudFront distribution
# - Origin: S3 bucket
# - Add SSL certificate
# - Point custom domain

# 5. Update frontend environment
VITE_API_URL=https://backend-url/api
VITE_SOCKET_URL=https://backend-url
```

---

## 🌐 OPTION 4: Docker Deployment (Any Server)

### Build Docker Images

**1. Backend Dockerfile:**
```dockerfile
# backend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

**2. Frontend Dockerfile:**
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
```

**3. Docker Compose (Production):**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://postgres:secure_password@postgres:5432/omnibus
      NODE_ENV: production
      JWT_SECRET: your-secret-key
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

**4. Deploy on any server:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔐 Production Environment Setup

### Backend `.env` (Production)

```env
# Database
DATABASE_HOST=prod-db-host
DATABASE_PORT=5432
DATABASE_USER=postgres_prod
DATABASE_PASSWORD=<VERY-SECURE-PASSWORD>
DATABASE_NAME=omnibus_prod

# Server
NODE_ENV=production
PORT=3000

# JWT
JWT_SECRET=<GENERATE-WITH: node -e "console.log(require('crypto').randomBytes(32).toString('hex'))">
JWT_EXPIRES_IN=24h

# Frontend
FRONTEND_URL=https://yourdomain.com

# Socket.IO
SOCKET_IO_CORS_ORIGIN=https://yourdomain.com

# Logging (Optional)
LOG_LEVEL=info
```

### Frontend Environment (Production)

```env
VITE_API_URL=https://api.yourdomain.com/api
VITE_SOCKET_URL=https://api.yourdomain.com
VITE_FRONTEND_URL=https://yourdomain.com
```

---

## 🔗 Nginx Configuration (If using EC2)

Create `/etc/nginx/sites-available/omnibus`:

```nginx
# Frontend
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/omnibus-frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}

# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable with:
```bash
sudo ln -s /etc/nginx/sites-available/omnibus /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 SSL/HTTPS Setup

### Option 1: Let's Encrypt (Free)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com

# Auto-renew
sudo systemctl enable certbot.timer
```

### Option 2: AWS Certificate Manager (Free on AWS)
- Automatic renewal
- Works with CloudFront, ALB, NLB

### Option 3: Commercial SSL
- DigiCert, Let's Encrypt, Sectigo
- Cost: $10-200/year

---

## 📊 Deployment Checklist

### Pre-Deployment
- [ ] Change all `localhost` to production URLs
- [ ] Generate secure JWT secret
- [ ] Set strong database password
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS correctly
- [ ] Set environment variables in cloud provider

### After Deployment
- [ ] Test login functionality
- [ ] Test real-time updates
- [ ] Test file uploads (if any)
- [ ] Monitor error logs
- [ ] Setup error tracking (Sentry)
- [ ] Setup performance monitoring (New Relic)
- [ ] Setup database backups
- [ ] Configure auto-scaling

### Security
- [ ] Enable HTTPS only
- [ ] Set secure cookies
- [ ] Configure CORS properly
- [ ] Rate limit API endpoints
- [ ] Monitor for suspicious activity
- [ ] Regular security updates

---

## 🚀 Step-by-Step: Railway + Netlify (Fastest)

### For Backend (Railway)

```bash
# 1. Push to GitHub
git add .
git commit -m "Production ready"
git push origin main

# 2. Go to railway.app
# - Sign up with GitHub
# - New Project
# - Select backend folder
# - Connect GitHub repo

# 3. Add PostgreSQL
# - Add Service → PostgreSQL
# - Railway auto-creates

# 4. Set Environment Variables (in Railway dashboard)
DATABASE_HOST=<railway-host>
DATABASE_PASSWORD=<railway-password>
NODE_ENV=production
JWT_SECRET=<generate-secure-key>
FRONTEND_URL=https://yourdomain.com
PORT=3000

# 5. Deploy
# - Railway auto-deploys
# - Get URL: https://backend-xxxxx.up.railway.app

# 6. Run migrations
# In Railway: Shell → npm run seed
```

### For Frontend (Netlify)

```bash
# 1. Build
cd frontend
npm run build

# 2. Go to netlify.com
# - Sign up with GitHub
# - New site from Git
# - Select repository
# - Set root: frontend
# - Build cmd: npm run build
# - Publish: dist

# 3. Set Environment Variables
VITE_API_URL=https://backend-xxxxx.up.railway.app/api
VITE_SOCKET_URL=https://backend-xxxxx.up.railway.app
VITE_FRONTEND_URL=https://yourdomain.com

# 4. Deploy
# - Click Deploy
# - Auto-deployed on every push

# 5. Add custom domain
# - Domain settings
# - Add custom domain
# - Update DNS at registrar
```

---

## 📱 Domain Setup

### 1. Buy Domain
- GoDaddy, Namecheap, Google Domains
- Cost: $10-15/year

### 2. Update DNS Records

For **Netlify Frontend:**
```
Type: CNAME
Name: yourdomain.com
Value: your-site.netlify.app
```

For **Railway Backend API:**
```
Type: CNAME
Name: api.yourdomain.com
Value: <railway-provided-url>
```

---

## 🔍 Monitoring & Logs

### View Backend Logs (Railway)
```bash
# In Railway dashboard
# Deployments → Select deployment → Logs
```

### View Frontend Logs (Netlify)
```bash
# In Netlify dashboard
# Deploys → Select deploy → Logs
```

### Error Tracking (Optional)
```bash
# Add Sentry for error tracking
npm install @sentry/node

# In backend/src/index.ts
import * as Sentry from "@sentry/node";
Sentry.init({ dsn: "your-sentry-dsn" });
```

---

## 💰 Estimated Monthly Costs

| Service | Cost | Notes |
|---------|------|-------|
| Railway Backend | $5-20 | Free tier available |
| Netlify Frontend | $0 | Free tier (sufficient) |
| Domain | $1 | NameCheap, ~$12/year |
| Database | $5-15 | Railway or AWS free tier |
| Total | $10-50 | Budget-friendly |

**Free Options:**
- Frontend: Netlify (free)
- Backend: Railway free tier
- Database: Railway free tier
- Domain: .tk (free, not recommended)

---

## ✅ Verification Checklist

After deployment:

```bash
# 1. Test login
curl https://yourdomain.com
# Should show login page

# 2. Test API
curl https://api.yourdomain.com/api/health
# Should show: {"status": "ok"}

# 3. Test Socket.IO
# Open browser console on https://yourdomain.com
# Should see: Connected to backend

# 4. Test real-time updates
# Open in 2 browsers
# One: add passenger (conductor)
# Two: occupancy updates live
```

---

## 🆘 Troubleshooting

### "Cannot connect to backend"
- Check CORS settings
- Verify backend URL in frontend .env
- Check firewall rules

### "Database connection error"
- Verify DATABASE_URL is correct
- Check database is running
- Verify credentials

### "Real-time updates not working"
- Check WebSocket not blocked
- Verify Socket.IO URL
- Check authentication token

### "Blank page / 404"
- Check build output (dist/)
- Verify build command
- Check root directory setting

---

## 📚 Additional Resources

- **Railway Docs:** https://docs.railway.app
- **Netlify Docs:** https://docs.netlify.com
- **AWS Docs:** https://docs.aws.amazon.com
- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs

---

## 🎯 Next Steps

1. **Choose deployment option** (Railway + Netlify recommended)
2. **Sign up** for chosen services
3. **Push code to GitHub**
4. **Deploy backend** following your option
5. **Deploy frontend** following your option
6. **Setup custom domain**
7. **Test production**
8. **Setup monitoring**

---

**Your OmniBus app will now be live on the web! 🌍**

Access it at: `https://yourdomain.com`
