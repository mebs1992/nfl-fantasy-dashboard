# Troubleshooting Network Error

## Quick Checks:

1. **Check Browser Console** (F12 → Console tab):
   - What's the exact error message?
   - Is it trying to connect to `localhost:5000` or the Render URL?

2. **Verify Vercel Environment Variable**:
   - Go to Vercel → Your Project → Settings → Environment Variables
   - Make sure `VITE_API_BASE_URL` is set to: `https://nfl-fantasy-dashboard-9ckz.onrender.com/api`
   - Make sure it's enabled for **Production** environment
   - **Redeploy** after setting it

3. **Check if Backend is Awake**:
   - Visit: https://nfl-fantasy-dashboard-9ckz.onrender.com/api/health
   - If it takes 30+ seconds, the backend is "sleeping" (normal for free tier)
   - First request after sleep takes ~30 seconds

4. **Common Issues**:
   - Environment variable not set → Frontend uses `localhost:5000` (won't work)
   - Backend sleeping → First request is slow
   - CORS error → Backend needs to be redeployed with new CORS settings

## Quick Fix:

1. **In Vercel**: Settings → Environment Variables
   - Add/Update: `VITE_API_BASE_URL` = `https://nfl-fantasy-dashboard-9ckz.onrender.com/api`
   - **Important**: Make sure "Production" is checked
   - Save and **Redeploy**

2. **Wait for backend to wake up** (if sleeping):
   - Visit the backend health endpoint first
   - Then try the frontend

Let me know what error you see in the browser console!

