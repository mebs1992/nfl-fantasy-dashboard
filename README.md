# NFL Fantasy League Dashboard

A comprehensive, locally-hosted dashboard for your NFL Fantasy league with advanced analytics including all-time head-to-head statistics, team performance tracking, and more.

## Features

### 🏆 Current Standings
- Real-time league standings with win-loss records
- Points for/against tracking
- Win percentage calculations
- Visual charts comparing team performance

### 📊 All-Time Head-to-Head Stats
- **Win percentages** between any two teams over the entire league history
- Interactive search to compare specific team matchups
- Visual pie charts showing head-to-head records
- Complete matrix of all team vs team records

### 📈 Team Statistics
- Current season performance
- All-time historical stats (total wins, losses, points)
- Win percentage vs each opponent
- Detailed opponent-by-opponent breakdowns
- Visual charts for opponent win rates

### 🎮 Weekly Matchups
- View matchups by week
- Historical matchup results
- Score tracking

### 📝 Transactions
- Recent adds, drops, and trades
- Transaction history tracking

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd nfl-fantasy-dashboard
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

### Running the Dashboard

You'll need to run both the backend API server and the frontend development server.

#### Terminal 1 - Backend API Server:
```bash
cd backend
python app.py
```

The API server will start on `http://localhost:5000`

#### Terminal 2 - Frontend Development Server:
```bash
npm run dev
```

The dashboard will be available at `http://localhost:3010`

### Initial Data Collection

The dashboard needs to collect data from your NFL Fantasy league. The scraper is configured for league ID `987449` (The Greatest League).

**To refresh data manually:**
1. Click the "🔄 Refresh Data" button in the dashboard header
2. Or make a POST request to `http://localhost:5000/api/refresh`

**Note:** The initial scraper implementation provides a foundation. You may need to enhance it based on the actual HTML structure of NFL.com Fantasy pages, as they may require authentication or have dynamic content loading.

## Project Structure

```
nfl-fantasy-dashboard/
├── backend/
│   ├── app.py              # Flask API server
│   ├── scraper.py          # NFL.com data scraper
│   └── data_manager.py     # Data storage and processing
├── src/
│   ├── components/         # React components
│   │   ├── Standings.jsx
│   │   ├── HeadToHead.jsx
│   │   ├── TeamStats.jsx
│   │   ├── Matchups.jsx
│   │   └── Transactions.jsx
│   ├── App.jsx             # Main app component
│   └── main.jsx            # Entry point
├── data/                   # Data storage (created automatically)
│   ├── league_data.json
│   └── historical_data.json
├── requirements.txt        # Python dependencies
├── package.json           # Node.js dependencies
└── README.md
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/standings` - Get current standings
- `GET /api/head-to-head?team1=X&team2=Y` - Get head-to-head between two teams
- `GET /api/head-to-head` - Get all head-to-head records
- `GET /api/team-stats?team_name=X` - Get comprehensive team stats
- `GET /api/matchups?week=X` - Get matchups (optionally filtered by week)
- `GET /api/transactions?limit=X` - Get recent transactions
- `GET /api/league-info` - Get league information
- `POST /api/refresh` - Manually refresh data from NFL.com

## Data Storage

The dashboard stores data locally in JSON files:
- `data/league_data.json` - Current season data
- `data/historical_data.json` - Historical matchups and team records

Data is automatically saved when refreshed and persists between sessions.

## Customization

### Changing League ID

Edit `backend/app.py` and update the `LEAGUE_ID` variable:
```python
LEAGUE_ID = "987449"  # Your league ID
```

### Enhancing the Scraper

The scraper in `backend/scraper.py` may need adjustments based on:
- NFL.com's HTML structure (which may change)
- Authentication requirements
- Dynamic content loading (may require Selenium)

For more robust scraping, consider:
- Using Selenium for JavaScript-rendered content
- Implementing authentication handling
- Adding error handling and retry logic

## Troubleshooting

### Backend won't start
- Ensure Python dependencies are installed: `pip install -r requirements.txt`
- Check that port 5000 is not in use
- Verify you're in the `backend` directory when running `python app.py`

### Frontend won't start
- Ensure Node.js dependencies are installed: `npm install`
- Check that port 3010 is not in use
- Try deleting `node_modules` and running `npm install` again

### No data showing
- Click "Refresh Data" to fetch initial data
- Check browser console for API errors
- Verify backend is running on port 5000
- Check `data/` directory for JSON files

### Scraper not working
- NFL.com may require authentication or have changed their HTML structure
- Check `backend/scraper.py` and adjust parsing logic as needed
- Consider using browser developer tools to inspect the actual page structure

## Future Enhancements

Potential features to add:
- Automatic scheduled data refreshes
- Email notifications for important events
- Player performance tracking
- Draft analysis
- Trade analyzer
- Playoff predictions
- Mobile-responsive improvements

## License

This project is for personal use. Please respect NFL.com's terms of service when scraping data.

## Contributing

Feel free to enhance the scraper, add features, or improve the UI!

