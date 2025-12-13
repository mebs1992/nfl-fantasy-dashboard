# Quick Start Guide

Get your NFL Fantasy Dashboard up and running in minutes!

## Option 1: Using the Startup Script (Easiest)

```bash
cd nfl-fantasy-dashboard
./start.sh
```

This will:
- Check prerequisites
- Install dependencies
- Start both backend and frontend servers

Then open your browser to `http://localhost:3010`

## Option 2: Manual Setup

### Step 1: Install Dependencies

**Python dependencies:**
```bash
pip install -r requirements.txt
```

**Node.js dependencies:**
```bash
npm install
```

### Step 2: Start Backend Server

In Terminal 1:
```bash
cd backend
python app.py
```

You should see: `Starting NFL Fantasy Dashboard API server...`

### Step 3: Start Frontend Server

In Terminal 2:
```bash
npm run dev
```

### Step 4: Open Dashboard

Open your browser to: `http://localhost:3010`

## First Time Setup

1. **Initial Data**: The dashboard comes with sample data so you can see how it works immediately.

2. **Fetch Real Data**: Click the "🔄 Refresh Data" button in the dashboard header to fetch real data from your NFL Fantasy league.

3. **Note**: The scraper may need adjustments based on NFL.com's current HTML structure. If data doesn't load, check the browser console and backend logs for errors.

## Troubleshooting

**Backend won't start?**
- Make sure port 5000 is available
- Check that all Python packages are installed: `pip install -r requirements.txt`

**Frontend won't start?**
- Make sure port 3010 is available  
- Try: `rm -rf node_modules && npm install`

**No data showing?**
- Click "Refresh Data" button
- Check that backend is running on port 5000
- Sample data should load automatically on first run

## Next Steps

- Explore the **Head-to-Head** tab to see all-time records
- Check **Team Stats** for detailed opponent breakdowns
- View **Matchups** to see weekly results
- Review **Transactions** for recent activity

Enjoy your dashboard! 🏈

