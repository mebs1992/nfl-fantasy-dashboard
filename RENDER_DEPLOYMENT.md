# Step 2: Deploy Backend to Render

## 🎯 Goal: Get your Flask backend running on Render (free)

### Step-by-Step:

1. **Go to Render**: https://render.com
2. **Sign up** (or sign in if you have an account)
   - You can sign up with GitHub (easiest!)
3. **Create a New Web Service**:
   - Click "New +" → "Web Service"
   - Click "Connect account" next to GitHub (if not already connected)
   - Select your repository: `mebs1992/nfl-fantasy-dashboard`
4. **Configure the Service**:
   - **Name**: `nfl-fantasy-backend` (or whatever you want)
   - **Region**: Choose closest to you (e.g., Oregon)
   - **Branch**: `main`
   - **Root Directory**: Leave blank (we'll handle this)
   - **Runtime**: `Python 3`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && python3 app.py`
   - **Plan**: Select **Free** (this is fine for now)

5. **Environment Variables** (click "Advanced" → "Add Environment Variable"):
   - `FLASK_ENV` = `production`
   - `PORT` = `5000` (Render will set this automatically, but good to have)
   - `FRONTEND_URL` = We'll set this later after deploying frontend (for now, leave it or set to `http://localhost:3010`)

6. **Click "Create Web Service"**

7. **Wait for deployment** (takes 2-5 minutes)

8. **Note your Render URL**: It will be something like `https://nfl-fantasy-backend.onrender.com`

---

## ⚠️ Important Notes:

- **Free tier spins down** after 15 min of inactivity (takes ~30 seconds to wake up)
- **First deployment** might take a few minutes
- **Data files**: Your CSV files are in the repo, so they'll be available!

---

## ✅ Once deployed, you'll have:
- Backend API running at: `https://your-app.onrender.com`
- API endpoints at: `https://your-app.onrender.com/api/...`

**Next**: Step 3 - Deploy Frontend to Vercel!

