"""
Script to import historical data into the dashboard using CSV storage
Scrapes historical matchup data and saves to CSV for fast access
"""
import os
import sys
from datetime import datetime

# Get project root
if os.path.basename(os.getcwd()) == 'backend':
    project_root = os.path.dirname(os.getcwd())
else:
    project_root = os.getcwd()

# Add backend to path
backend_dir = os.path.join(project_root, 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from historical_scraper import (
    HistoricalScraper, 
    save_to_csv, 
    load_from_csv, 
    get_scraped_weeks
)
from data_manager import DataManager


def import_historical_data(league_id: str = "987449", start_year: int = 2017, end_year: int = 2024, force: bool = False):
    """Scrape and import historical data to CSV"""
    csv_file = os.path.join(project_root, 'data', 'matchups.csv')
    
    print("="*60)
    print("NFL Fantasy Historical Data Importer")
    print("="*60)
    print(f"League ID: {league_id}")
    print(f"Years: {start_year} - {end_year}")
    print(f"CSV File: {csv_file}")
    print("="*60)
    print()
    
    scraper = HistoricalScraper(league_id)
    
    # Get already scraped weeks if not forcing
    scraped_weeks = {} if force else get_scraped_weeks(csv_file)
    
    total_new_matchups = 0
    
    # Scrape historical years (2017-2024)
    for year in range(start_year, end_year + 1):
        print(f"\n{'='*60}")
        print(f"Processing {year}")
        print(f"{'='*60}")
        
        if year in scraped_weeks:
            print(f"  Already scraped weeks: {sorted(scraped_weeks[year])}")
        
        # Scrape weeks 1-17 for each year
        for week in range(1, 18):
            # Skip if already scraped (unless forcing)
            if not force and year in scraped_weeks and week in scraped_weeks[year]:
                continue
            
            matchups = scraper.scrape_week(year, week)
            
            if matchups:
                save_to_csv(matchups, csv_file)
                total_new_matchups += len(matchups)
                print(f"    Week {week}: {len(matchups)} matchups saved ({matchups[0].get('week_type', 'unknown')})")
            else:
                # If no matchups found, might be end of season
                print(f"    Week {week}: No matchups (may be end of season)")
                # Don't break, continue to next week in case there are gaps
    
    print("\n" + "="*60)
    print("Historical Import Complete!")
    print("="*60)
    print(f"Total new matchups added: {total_new_matchups}")
    print(f"Data saved to: {csv_file}")
    print("="*60)


def import_current_season(league_id: str = "987449", year: int = 2025, max_week: int = 17, force: bool = False):
    """Import current season, only scraping new weeks"""
    csv_file = os.path.join(project_root, 'data', 'matchups.csv')
    
    print("="*60)
    print("NFL Fantasy Current Season Importer")
    print("="*60)
    print(f"Year: {year}")
    print(f"Max Week: {max_week}")
    print(f"CSV File: {csv_file}")
    print("="*60)
    print()
    
    scraper = HistoricalScraper(league_id)
    
    # Get already scraped weeks
    scraped_weeks = get_scraped_weeks(csv_file)
    year_scraped = scraped_weeks.get(year, set())
    
    if year_scraped:
        print(f"Already scraped weeks for {year}: {sorted(year_scraped)}")
        print(f"Will only scrape new weeks...")
    else:
        print(f"No data found for {year}, will scrape all weeks 1-{max_week}")
    
    total_new_matchups = 0
    
    # Scrape only new weeks
    for week in range(1, max_week + 1):
        # Skip if already scraped (unless forcing)
        if not force and week in year_scraped:
            print(f"  Week {week}: Already scraped, skipping")
            continue
        
        print(f"\n  Scraping Week {week}...")
        matchups = scraper.scrape_week(year, week)
        
        if matchups:
            save_to_csv(matchups, csv_file)
            total_new_matchups += len(matchups)
            print(f"    ✓ {len(matchups)} matchups saved ({matchups[0].get('week_type', 'unknown')})")
        else:
            print(f"    ✗ No matchups found (may not be played yet)")
    
    print("\n" + "="*60)
    print("Current Season Import Complete!")
    print("="*60)
    print(f"Total new matchups added: {total_new_matchups}")
    print(f"Data saved to: {csv_file}")
    print("="*60)


def sync_csv_to_data_manager():
    """Sync CSV data to data manager for API access"""
    csv_file = os.path.join(project_root, 'data', 'matchups.csv')
    
    if not os.path.exists(csv_file):
        print("No CSV file found. Run import first.")
        return
    
    print("Syncing CSV data to data manager...")
    
    # Load matchups from CSV
    matchups = load_from_csv(csv_file)
    print(f"Loaded {len(matchups)} matchups from CSV")
    
    # Initialize data manager
    data_manager = DataManager(data_dir=os.path.join(project_root, 'data'))
    data_manager.load_data()
    
    # Add all matchups to historical data
    for matchup in matchups:
        matchup['id'] = f"{matchup['year']}_week{matchup['week']}_{matchup['team1_name']}_{matchup['team2_name']}"
        data_manager._add_matchup_to_history(matchup)
    
    # Save to JSON (for API compatibility)
    data_manager.save_data()
    
    print("✓ CSV data synced to data manager")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Import NFL Fantasy historical data')
    parser.add_argument('--historical', action='store_true', help='Import historical data (2017-2024)')
    parser.add_argument('--current', action='store_true', help='Import current season (2025)')
    parser.add_argument('--sync', action='store_true', help='Sync CSV to data manager')
    parser.add_argument('--force', action='store_true', help='Force re-scrape of all weeks')
    parser.add_argument('--year', type=int, default=2025, help='Year for current season (default: 2025)')
    parser.add_argument('--max-week', type=int, default=17, help='Max week to scrape (default: 17)')
    
    args = parser.parse_args()
    
    if args.historical:
        import_historical_data(force=args.force)
    elif args.current:
        import_current_season(year=args.year, max_week=args.max_week, force=args.force)
    elif args.sync:
        sync_csv_to_data_manager()
    else:
        # Default: do both historical and current, then sync
        print("Running full import (historical + current season)...")
        import_historical_data(force=args.force)
        import_current_season(year=args.year, max_week=args.max_week, force=args.force)
        sync_csv_to_data_manager()
