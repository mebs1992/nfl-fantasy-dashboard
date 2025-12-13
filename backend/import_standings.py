"""
Script to import historical standings data
"""
import os
import sys

# Get project root
if os.path.basename(os.getcwd()) == 'backend':
    project_root = os.path.dirname(os.getcwd())
else:
    project_root = os.getcwd()

# Add backend to path
backend_dir = os.path.join(project_root, 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from standings_scraper import StandingsScraper, save_standings_to_csv, load_standings_from_csv
from team_mapper import normalize_team_name


def import_standings(start_year: int = 2017, end_year: int = 2025, force: bool = False):
    """Import historical standings"""
    csv_file = os.path.join(project_root, 'data', 'standings.csv')
    
    print("="*60)
    print("NFL Fantasy Historical Standings Importer")
    print("="*60)
    print(f"Years: {start_year} - {end_year}")
    print(f"CSV File: {csv_file}")
    print("="*60)
    print()
    
    scraper = StandingsScraper('987449')
    
    # Get already scraped years (check both regular and final)
    scraped_years = set()
    if not force:
        regular_file = csv_file
        final_file = csv_file.replace('.csv', '_final.csv')
        if os.path.exists(regular_file):
            existing = load_standings_from_csv(regular_file, 'regular')
            scraped_years.update({s['year'] for s in existing})
        if os.path.exists(final_file):
            existing = load_standings_from_csv(final_file, 'final')
            scraped_years.update({s['year'] for s in existing})
        if scraped_years:
            print(f"Already scraped years: {sorted(scraped_years)}")
            print()
    
    total_new_regular = 0
    total_new_final = 0
    
    for year in range(start_year, end_year + 1):
        if not force and year in scraped_years:
            print(f"  {year}: Already scraped, skipping")
            continue
        
        print(f"  Scraping {year}...")
        
        # Scrape regular season standings (for stats)
        print(f"    Regular season...")
        regular_standings = scraper.scrape_year_standings(year, 'regular')
        if regular_standings:
            # Normalize team names
            for s in regular_standings:
                s['team_name'] = normalize_team_name(s['team_name'])
            save_standings_to_csv(regular_standings, csv_file, 'regular')
            total_new_regular += len(regular_standings)
            print(f"      ✓ {len(regular_standings)} teams saved (regular)")
        
        # Scrape final standings (for championships/spoons)
        print(f"    Final standings...")
        final_standings = scraper.scrape_year_standings(year, 'final')
        if final_standings:
            # Normalize team names
            for s in final_standings:
                s['team_name'] = normalize_team_name(s['team_name'])
            save_standings_to_csv(final_standings, csv_file, 'final')
            total_new_final += len(final_standings)
            print(f"      ✓ {len(final_standings)} teams saved (final)")
        
        if not regular_standings and not final_standings:
            print(f"    ✗ No standings found")
    
    print("\n" + "="*60)
    print("Import Complete!")
    print("="*60)
    print(f"Regular season standings: {total_new_regular}")
    print(f"Final standings: {total_new_final}")
    print(f"Data saved to: {csv_file} and {csv_file.replace('.csv', '_final.csv')}")
    print("="*60)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Import historical standings')
    parser.add_argument('--force', action='store_true', help='Force re-scrape of all years')
    parser.add_argument('--start-year', type=int, default=2017, help='Start year')
    parser.add_argument('--end-year', type=int, default=2025, help='End year')
    
    args = parser.parse_args()
    import_standings(args.start_year, args.end_year, args.force)

