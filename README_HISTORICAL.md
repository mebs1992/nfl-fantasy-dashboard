# Historical Data Import Guide

This guide explains how to import historical matchup data from 2017-2024 to enable head-to-head statistics in your dashboard.

## What Gets Imported

The historical scraper will collect:
- **Standings** for each year (2017-2024)
- **All weekly matchups** with scores and winners
- **Team records** across all seasons

This data is then used to calculate:
- All-time head-to-head win percentages
- Team vs team records
- Historical performance statistics

## How to Import Historical Data

### Option 1: Using the Script (Recommended)

Run the import script from the project root:

```bash
cd nfl-fantasy-dashboard
./import_history.sh
```

This will:
1. Prompt you to confirm
2. Scrape data from 2017-2024 (takes 10-20 minutes)
3. Import all matchups into the dashboard
4. Save the data to `data/historical_data.json`

### Option 2: Using Python Directly

```bash
cd nfl-fantasy-dashboard/backend
python3 import_historical.py
```

### Option 3: Via API (After Backend is Running)

```bash
curl -X POST http://localhost:5000/api/import-historical \
  -H "Content-Type: application/json" \
  -d '{"start_year": 2017, "end_year": 2024}'
```

## What to Expect

The scraper will:
- Visit each year's schedule page (2017-2024)
- Extract matchup data for each week
- Parse team names, scores, and winners
- Store everything in the historical data file

**Note:** The scraper includes delays between requests to be respectful to NFL.com's servers. The full import may take 10-20 minutes.

## Troubleshooting

### Scraper Can't Find Matchups

If the scraper reports 0 matchups for a year:
- The HTML structure may have changed
- Check the actual schedule page in your browser
- You may need to update the parsing logic in `backend/historical_scraper.py`

### Partial Data Imported

If some years have data but others don't:
- Check your internet connection
- The scraper will continue even if one year fails
- You can re-run the import - it will add new matchups without duplicating

### Authentication Required

If pages require login:
- You may need to add authentication cookies to the scraper
- Check `backend/historical_scraper.py` and add session cookies if needed

## After Import

Once the import is complete:
1. Refresh your dashboard at `http://localhost:3010`
2. Go to the **Head-to-Head** tab
3. Select any two teams to see their all-time record
4. View win percentages and matchup history

The data is stored in `data/historical_data.json` and persists between dashboard restarts.

## Manual Data Entry

If scraping doesn't work, you can manually add matchup data to `data/historical_data.json`:

```json
{
  "matchups": [
    {
      "year": 2017,
      "week": 1,
      "team1_name": "Team A",
      "team2_name": "Team B",
      "team1_score": 120.5,
      "team2_score": 115.2,
      "winner": "Team A"
    }
  ]
}
```

Then restart the backend to load the new data.

