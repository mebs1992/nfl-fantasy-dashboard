# Deployment Guide - Making Your Dashboard Public

This guide will help you deploy your NFL Fantasy Dashboard so your leaguemates can access it.

## ✅ Code is Already Prepared!

The code has been updated to use environment variables. You're ready to deploy!

## 🎯 Recommended: Vercel (Frontend) + Render (Backend)

This is the **easiest and most reliable** free option.

### Step 2: Deploy Backend to Render (Free)

1. **Sign up** at [render.com](https://render.com) (free account)
2. **Create a new Web Service**:
   - Connect your GitHub repository (or upload code)
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && python3 app.py`
   - **Environment**: Python 3
   - **Port**: 5000

3. **Add Environment Variables** in Render dashboard:
   - `FLASK_ENV=production`
   - `PYTHON_VERSION=3.11`

4. **Upload your data files**:
   - You'll need to commit your `data/` folder to git, OR
   - Use Render's persistent disk (free tier has limitations)
   - **Better option**: Create a script to initialize data on first run

5. **Note your Render URL**: Something like `https://your-app.onrender.com`

### Step 3: Deploy Frontend to Vercel (Free)

1. **Sign up** at [vercel.com](https://vercel.com) (free account)
2. **Import your GitHub repository**
3. **Configure**:
   - **Framework Preset**: Vite
   - **Root Directory**: `./` (root)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. **Add Environment Variable**:
   - `VITE_API_BASE_URL`: Your Render backend URL (e.g., `https://your-app.onrender.com`)

5. **Deploy!** Vercel will give you a URL like `https://your-dashboard.vercel.app`

### Step 4: Important - Data Files

**Before deploying**, you need to handle your data files:

**Option A: Commit data to Git (Easiest)**
1. Remove `data/` from `.gitignore` (or comment it out)
2. Commit your `data/` folder to git
3. Render will have access to the CSV files

**Option B: Initialize data on first deploy**
- The backend can scrape data on first run
- Add a startup script that checks if data exists, and if not, runs the import scripts

---

## 🚀 Alternative: Railway (Full-Stack, One Deployment)

Railway can host both frontend and backend together.

1. **Sign up** at [railway.app](https://railway.app) (free tier available)
2. **Create a new project**
3. **Add two services**:
   - **Backend Service**: 
     - Root: `backend/`
     - Start: `python3 app.py`
   - **Frontend Service**:
     - Root: `./`
     - Build: `npm run build`
     - Start: `npm run preview` (or use a static file server)

4. **Set environment variables** for both services
5. **Deploy!**

---

## 📝 Important Notes

### Data Files
Your CSV files need to be available to the backend. Options:
1. **Commit to Git** (easiest, but data is public)
2. **Use a cloud storage** (AWS S3, Google Cloud Storage - free tiers available)
3. **Initialize on first run** - Create a script that scrapes data when the app starts

### CORS Settings
✅ **Already configured!** The backend now uses the `FRONTEND_URL` environment variable for CORS.

### Free Tier Limitations
- **Render**: Free tier spins down after 15 min of inactivity (takes ~30s to wake up)
- **Vercel**: Generous free tier, no spin-down
- **Railway**: Free tier has usage limits

---

## 📋 Quick Checklist

- [x] Code updated to use environment variables
- [x] CORS configured
- [x] Vercel config file created (`vercel.json`)
- [x] Render config file created (`render.yaml`)
- [ ] Push code to GitHub
- [ ] Deploy backend to Render
- [ ] Deploy frontend to Vercel
- [ ] Share the Vercel URL with your leaguemates!

## 🎉 You're Ready!

Just follow the steps above. The hardest part (code setup) is done!

