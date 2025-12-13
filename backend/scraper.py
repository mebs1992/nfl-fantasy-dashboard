"""
NFL Fantasy League Data Scraper
Scrapes league data from NFL.com Fantasy pages
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime
from typing import Dict, List, Optional
import time


class NFLFantasyScraper:
    def __init__(self, league_id: str):
        self.league_id = league_id
        self.base_url = f"https://fantasy.nfl.com/league/{league_id}"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def parse_standings(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse league standings from the page"""
        standings = []
        
        # Try multiple strategies to find standings
        # Strategy 1: Look for tables with standings data
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
            
            # Check if this looks like a standings table
            first_row_text = ' '.join([cell.get_text(strip=True) for cell in rows[0].find_all(['th', 'td'])])
            if any(keyword in first_row_text.lower() for keyword in ['team', 'w-l-t', 'rank', 'points']):
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        try:
                            team_data = {}
                            
                            # Extract team name (usually in a link)
                            team_link = row.find('a', href=re.compile(r'/team/'))
                            if team_link:
                                team_data['name'] = team_link.get_text(strip=True)
                                team_id_match = re.search(r'/team/(\d+)', team_link.get('href', ''))
                                if team_id_match:
                                    team_data['id'] = team_id_match.group(1)
                            else:
                                # Try to find team name in cells
                                for cell in cells:
                                    cell_text = cell.get_text(strip=True)
                                    if cell_text and not re.match(r'^\d+\.?\d*$', cell_text) and '-' not in cell_text:
                                        team_data['name'] = cell_text
                                        break
                            
                            # Extract record (W-L-T format) - look for pattern like "9-5-0"
                            for cell in cells:
                                cell_text = cell.get_text(strip=True)
                                if re.match(r'^\d+-\d+-\d+$', cell_text):
                                    parts = cell_text.split('-')
                                    team_data['wins'] = int(parts[0])
                                    team_data['losses'] = int(parts[1])
                                    team_data['ties'] = int(parts[2]) if len(parts) > 2 else 0
                                    break
                            
                            # Extract points - look for decimal numbers
                            for cell in cells:
                                cell_text = cell.get_text(strip=True)
                                # Match numbers with decimals (points)
                                if re.match(r'^\d+\.\d+$', cell_text):
                                    points = float(cell_text)
                                    if 'points_for' not in team_data or points > team_data.get('points_for', 0):
                                        team_data['points_for'] = points
                            
                            if team_data.get('name'):
                                standings.append(team_data)
                        except Exception as e:
                            print(f"Error parsing row: {e}")
                            continue
                if standings:
                    break
        
        # Strategy 2: Look for div-based standings (if table parsing fails)
        if not standings:
            # Try to find standings in div structures
            standings_sections = soup.find_all(['div', 'section'], class_=re.compile(r'standings|ranking', re.I))
            for section in standings_sections:
                # This would need to be customized based on actual HTML structure
                pass
        
        return standings
    
    def parse_matchups(self, soup: BeautifulSoup, week: int) -> List[Dict]:
        """Parse weekly matchups"""
        matchups = []
        
        # Look for matchup data in the scoreboard section
        scoreboard_section = soup.find('div', class_=re.compile(r'scoreboard|matchup', re.I))
        if not scoreboard_section:
            # Try to find any div containing team names and scores
            scoreboard_section = soup
        
        # Look for patterns like "Team1 Score Team2 Score"
        team_links = soup.find_all('a', href=re.compile(r'/team/'))
        scores = soup.find_all(text=re.compile(r'\d+\.\d+'))
        
        # This is a simplified parser - may need refinement based on actual HTML structure
        # For now, return empty list and we'll enhance based on actual page structure
        return matchups
    
    def get_standings(self) -> List[Dict]:
        """Get current league standings"""
        soup = self.fetch_page(self.base_url)
        if not soup:
            return []
        
        return self.parse_standings(soup)
    
    def get_historical_data(self) -> Dict:
        """Get historical matchup data (requires navigating through weeks)"""
        # This would need to iterate through all weeks/seasons
        # For now, return structure for future implementation
        return {
            'seasons': [],
            'matchups': []
        }


def scrape_league_data(league_id: str) -> Dict:
    """Main function to scrape all league data"""
    scraper = NFLFantasyScraper(league_id)
    
    standings = scraper.get_standings()
    
    # If scraping returns empty, try to load sample data as fallback
    if not standings:
        try:
            sample_file = os.path.join('data', 'sample_data.json')
            if os.path.exists(sample_file):
                with open(sample_file, 'r') as f:
                    sample_data = json.load(f)
                    print("Scraping returned no data, using sample data")
                    return {
                        'league_id': league_id,
                        'scraped_at': datetime.now().isoformat(),
                        'standings': sample_data.get('standings', []),
                        'current_week': sample_data.get('current_week', 15),
                        'matchups': sample_data.get('matchups', []),
                        'transactions': sample_data.get('transactions', [])
                    }
        except Exception as e:
            print(f"Error loading sample data: {e}")
    
    data = {
        'league_id': league_id,
        'scraped_at': datetime.now().isoformat(),
        'standings': standings,
        'current_week': 15,  # This would need to be determined dynamically
        'matchups': [],
        'transactions': []
    }
    
    return data

