"""
Historical Standings Scraper
Scrapes final standings for each year to determine Super Bowl wins, playoff appearances, and spoons
"""
import requests
from bs4 import BeautifulSoup
import csv
import re
import os
from datetime import datetime
from typing import Dict, List, Optional
import time


class StandingsScraper:
    def __init__(self, league_id: str):
        self.league_id = league_id
        self.base_url = f"https://fantasy.nfl.com/league/{league_id}/history"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def fetch_standings_page(self, year: int, standings_type: str = 'final') -> Optional[BeautifulSoup]:
        """Fetch standings page for a specific year
        
        Args:
            year: The year to fetch
            standings_type: 'final' for final standings (champion), 'regular' for regular season
        """
        # Use final standings to get the actual champion (after playoffs)
        url = f"{self.base_url}/{year}/standings?historyStandingsType={standings_type}"
        try:
            print(f"  Fetching {year} standings ({standings_type})...")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"    Error: {e}")
            return None
    
    def parse_standings(self, soup: BeautifulSoup, year: int) -> List[Dict]:
        """Parse standings from the standings table"""
        standings = []
        
        if not soup:
            return standings
        
        # Find the standings table
        table = soup.find('table')
        if not table:
            # Fallback to old parsing method if table not found
            return self._parse_standings_legacy(soup, year)
        
        # Find all table rows
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 6:
                continue
            
            try:
                # Extract rank (first cell)
                rank_text = cells[0].get_text(strip=True)
                # Skip header row (contains "Rank" or non-numeric)
                if not rank_text or rank_text.lower() in ['rank', '']:
                    continue
                # Remove any non-numeric characters (like +1, -2 indicators)
                rank_match = re.search(r'(\d+)', rank_text)
                if not rank_match:
                    continue
                place = int(rank_match.group(1))
                
                # Extract team name (second cell, look for all links and get the last one with text)
                team_links = cells[1].find_all('a')
                team_name = None
                # Usually the team name is in the last link that has text
                for link in reversed(team_links):
                    link_text = link.get_text(strip=True)
                    if link_text:
                        team_name = link_text
                        break
                
                # Fallback: if no link with text, use cell text
                if not team_name:
                    team_name = cells[1].get_text(strip=True)
                
                if not team_name:
                    continue
                
                # Extract team logo/image URL
                team_logo = None
                team_img = cells[1].find('img')
                if team_img:
                    logo_src = team_img.get('src', '')
                    # Make sure it's a full URL
                    if logo_src.startswith('http'):
                        team_logo = logo_src
                    elif logo_src.startswith('/'):
                        team_logo = f"https://fantasy.nfl.com{logo_src}"
                    else:
                        team_logo = f"https://fantasy.nfl.com/{logo_src}"
                
                # Extract W-L-T (third cell)
                wlt_text = cells[2].get_text(strip=True)
                wlt_match = re.match(r'(\d+)-(\d+)-(\d+)', wlt_text)
                if not wlt_match:
                    continue
                wins = int(wlt_match.group(1))
                losses = int(wlt_match.group(2))
                ties = int(wlt_match.group(3))
                
                # Extract Win Percentage (fourth cell)
                pct_text = cells[3].get_text(strip=True)
                # Handle percentage format (e.g., ".786" means 0.786 or 78.6%)
                if pct_text.startswith('.'):
                    # Convert ".786" to 0.786
                    win_pct = float('0' + pct_text) if pct_text else 0.0
                else:
                    # If it's already a number, divide by 100 if > 1 (e.g., 78.6 -> 0.786)
                    win_pct = float(pct_text) if pct_text else 0.0
                    if win_pct > 1.0:
                        win_pct = win_pct / 100.0
                
                # Extract Points For (sixth cell, index 5)
                points_for_text = cells[5].get_text(strip=True)
                # Remove commas from numbers
                points_for_text = points_for_text.replace(',', '')
                points_for = float(points_for_text) if points_for_text else 0.0
                
                # Extract Points Against (seventh cell, index 6)
                points_against_text = cells[6].get_text(strip=True)
                # Remove commas from numbers
                points_against_text = points_against_text.replace(',', '')
                points_against = float(points_against_text) if points_against_text else 0.0
                
                standings.append({
                    'year': year,
                    'place': place,
                    'team_name': team_name,
                    'wins': wins,
                    'losses': losses,
                    'ties': ties,
                    'win_pct': win_pct,
                    'points_for': points_for,
                    'points_against': points_against,
                    'team_logo': team_logo,
                    'scraped_at': datetime.now().isoformat()
                })
            except (ValueError, IndexError) as e:
                print(f"    Warning: Error parsing row: {e}")
                continue
        
        # Sort by place
        standings.sort(key=lambda x: x['place'])
        
        return standings
    
    def _parse_standings_legacy(self, soup: BeautifulSoup, year: int) -> List[Dict]:
        """Legacy parsing method for pages without table structure"""
        standings = []
        
        # Pattern to find place numbers
        place_pattern = re.compile(r'(\d+)(st|nd|rd|th)\s+Place', re.I)
        
        # Find all list items
        list_items = soup.find_all('li')
        
        for li in list_items:
            text = li.get_text()
            place_match = place_pattern.search(text)
            
            if place_match:
                place = int(place_match.group(1))
                
                # Look for team name link with class 'teamName'
                team_link = li.find('a', class_=re.compile(r'teamName', re.I))
                
                # Fallback to any team link
                if not team_link:
                    team_link = li.find('a', href=re.compile(r'/team/'))
                
                if team_link:
                    team_name = team_link.get_text(strip=True)
                    standings.append({
                        'year': year,
                        'place': place,
                        'team_name': team_name,
                        'wins': 0,
                        'losses': 0,
                        'ties': 0,
                        'win_pct': 0.0,
                        'points_for': 0.0,
                        'points_against': 0.0,
                        'scraped_at': datetime.now().isoformat()
                    })
        
        # Sort by place
        standings.sort(key=lambda x: x['place'])
        
        return standings
    
    def scrape_year_standings(self, year: int, standings_type: str = 'final') -> List[Dict]:
        """Scrape standings for a specific year
        
        Args:
            year: The year to scrape
            standings_type: 'final' for final standings (after playoffs, determines champion)
                          'regular' for regular season standings only
        """
        soup = self.fetch_standings_page(year, standings_type)
        if not soup:
            return []
        
        standings = self.parse_standings(soup, year)
        return standings
    
    def scrape_all_standings(self, start_year: int = 2017, end_year: int = 2025) -> List[Dict]:
        """Scrape all historical standings"""
        all_standings = []
        
        for year in range(start_year, end_year + 1):
            standings = self.scrape_year_standings(year)
            all_standings.extend(standings)
            print(f"    {year}: {len(standings)} teams found")
            time.sleep(0.5)  # Be polite
        
        return all_standings


def save_standings_to_csv(standings: List[Dict], csv_file: str, standings_type: str = 'regular'):
    """Save standings to CSV file
    
    Args:
        standings: List of standing dictionaries
        csv_file: Path to CSV file
        standings_type: 'regular' or 'final' - determines which file to save to
    """
    if not standings:
        return
    
    # Use different files for regular vs final standings
    if standings_type == 'final':
        csv_file = csv_file.replace('.csv', '_final.csv')
    
    file_exists = os.path.exists(csv_file)
    
    fieldnames = ['year', 'place', 'team_name', 'wins', 'losses', 'ties', 'win_pct', 'points_for', 'points_against', 'team_logo', 'standings_type', 'scraped_at']
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for standing in standings:
            writer.writerow({
                'year': standing.get('year'),
                'place': standing.get('place'),
                'team_name': standing.get('team_name'),
                'wins': standing.get('wins', 0),
                'losses': standing.get('losses', 0),
                'ties': standing.get('ties', 0),
                'win_pct': standing.get('win_pct', 0.0),
                'points_for': standing.get('points_for', 0.0),
                'points_against': standing.get('points_against', 0.0),
                'team_logo': standing.get('team_logo', ''),
                'standings_type': standings_type,
                'scraped_at': standing.get('scraped_at', datetime.now().isoformat())
            })


def load_standings_from_csv(csv_file: str, standings_type: str = 'regular') -> List[Dict]:
    """Load standings from CSV file
    
    Args:
        csv_file: Path to CSV file (base path)
        standings_type: 'regular' or 'final' - determines which file to load
    """
    # Use different files for regular vs final standings
    if standings_type == 'final':
        csv_file = csv_file.replace('.csv', '_final.csv')
    
    if not os.path.exists(csv_file):
        return []
    
    standings = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            standing = {
                'year': int(row['year']),
                'place': int(row['place']),
                'team_name': row['team_name'],
                'scraped_at': row.get('scraped_at', ''),
                'standings_type': row.get('standings_type', standings_type)
            }
            
            # Handle optional fields (for backward compatibility)
            if 'wins' in row:
                standing['wins'] = int(row.get('wins', 0))
                standing['losses'] = int(row.get('losses', 0))
                standing['ties'] = int(row.get('ties', 0))
                standing['win_pct'] = float(row.get('win_pct', 0.0))
                standing['points_for'] = float(row.get('points_for', 0.0))
                standing['points_against'] = float(row.get('points_against', 0.0))
                standing['team_logo'] = row.get('team_logo', '')
            else:
                # Legacy data - set defaults
                standing['wins'] = 0
                standing['losses'] = 0
                standing['ties'] = 0
                standing['win_pct'] = 0.0
                standing['points_for'] = 0.0
                standing['points_against'] = 0.0
                standing['team_logo'] = ''
            
            standings.append(standing)
    
    return standings


if __name__ == '__main__':
    # Test scraper
    scraper = StandingsScraper('987449')
    
    print("Testing 2021 standings scrape...")
    standings = scraper.scrape_year_standings(2021)
    print(f"\nFound {len(standings)} teams:")
    for s in standings:
        print(f"  {s['place']}. {s['team_name']}")

