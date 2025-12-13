"""
Historical Data Scraper for NFL Fantasy League
Scrapes historical matchup data from 2017-2025 using exact URL pattern
"""
import requests
from bs4 import BeautifulSoup
import csv
import re
import os
from datetime import datetime
from typing import Dict, List, Optional
import time


class HistoricalScraper:
    def __init__(self, league_id: str):
        self.league_id = league_id
        self.base_url = f"https://fantasy.nfl.com/league/{league_id}/history"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def fetch_week_page(self, year: int, week: int) -> Optional[BeautifulSoup]:
        """Fetch schedule page for a specific year and week"""
        url = f"{self.base_url}/{year}/schedule?gameSeason={year}&leagueId={self.league_id}&scheduleDetail={week}&scheduleType=week&standingsTab=schedule"
        try:
            print(f"  Fetching {year} Week {week}...")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"    Error: {e}")
            return None
    
    def parse_matchups_from_page(self, soup: BeautifulSoup, year: int, week: int) -> List[Dict]:
        """Parse matchups from the schedule page HTML"""
        matchups = []
        
        if not soup:
            return matchups
        
        # Find all matchup list items (each <li class="matchup"> contains both teams)
        matchup_lis = soup.find_all('li', class_=re.compile(r'matchup', re.I))
        
        for matchup_li in matchup_lis:
            # Find both team name links in this matchup
            team_links = matchup_li.find_all('a', class_=re.compile(r'teamName', re.I))
            
            if len(team_links) >= 2:
                team1_name = team_links[0].get_text(strip=True)
                team2_name = team_links[1].get_text(strip=True)
                
                # Extract scores from HTML directly (avoid text concatenation issues)
                # Scores appear as standalone numbers like >128.62< in the HTML
                html = str(matchup_li)
                score_pattern = re.compile(r'>(\d+\.\d+)<')
                scores = [float(m) for m in score_pattern.findall(html)]
                
                # If we found scores in HTML, use those
                if len(scores) >= 2:
                    # Take first two scores (should be the team scores)
                    team1_score = scores[0]
                    team2_score = scores[1]
                else:
                    # Fallback: try to extract from teamWrap divs
                    team_wraps = matchup_li.find_all('div', class_=re.compile(r'teamWrap', re.I))
                    scores = []
                    for wrap in team_wraps[:2]:  # Only first two wraps
                        wrap_html = str(wrap)
                        wrap_scores = score_pattern.findall(wrap_html)
                        if wrap_scores:
                            scores.append(float(wrap_scores[0]))
                    
                    if len(scores) >= 2:
                        team1_score = scores[0]
                        team2_score = scores[1]
                    else:
                        continue  # Skip this matchup if we can't find scores
                
                matchup = {
                    'year': year,
                    'week': week,
                    'team1_name': team1_name,
                    'team1_score': team1_score,
                    'team2_name': team2_name,
                    'team2_score': team2_score,
                    'winner': team1_name if team1_score > team2_score else (team2_name if team2_score > team1_score else 'Tie'),
                    'scraped_at': datetime.now().isoformat()
                }
                matchups.append(matchup)
        
        # Remove duplicates (same teams in same week)
        seen = set()
        unique_matchups = []
        for m in matchups:
            key = (m['team1_name'], m['team2_name'], m['week'])
            if key not in seen:
                seen.add(key)
                unique_matchups.append(m)
        
        return unique_matchups
    
    def _parse_structured_matchups(self, soup: BeautifulSoup, year: int, week: int) -> List[Dict]:
        """Parse matchups using the known HTML structure"""
        matchups = []
        score_pattern = re.compile(r'^\d+\.\d+$')
        
        # Find all list items (matchups are typically in <li> tags)
        list_items = soup.find_all('li')
        
        current_teams = []
        current_scores = []
        
        for li in list_items:
            text = li.get_text(separator='\n')
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Look for team names (usually first line with capitalized words)
            # Look for scores (decimal numbers)
            team_name = None
            score = None
            
            for line in lines:
                # Check if line is a score
                if score_pattern.match(line):
                    score = float(line)
                    continue
                
                # Check if line looks like a team name (has capitalized words, not a record)
                if not re.search(r'\d+-\d+-\d+', line) and not line.lower().startswith(('waiver', 'streak', 'view')):
                    words = line.split()
                    if words and words[0][0].isupper() and len(words[0]) > 2:
                        # Might be a team name
                        potential_name = ' '.join([w for w in words if w[0].isupper() or w.isdigit()])
                        if len(potential_name) > 3:
                            team_name = potential_name
            
            if team_name and score is not None:
                current_teams.append(team_name)
                current_scores.append(score)
                
                # When we have 2 teams and 2 scores, we have a matchup
                if len(current_teams) == 2 and len(current_scores) == 2:
                    matchup = {
                        'year': year,
                        'week': week,
                        'team1_name': current_teams[0],
                        'team1_score': current_scores[0],
                        'team2_name': current_teams[1],
                        'team2_score': current_scores[1],
                        'winner': current_teams[0] if current_scores[0] > current_scores[1] else (current_teams[1] if current_scores[1] > current_scores[0] else 'Tie'),
                        'scraped_at': datetime.now().isoformat()
                    }
                    matchups.append(matchup)
                    current_teams = []
                    current_scores = []
        
        return matchups
    
    def determine_week_type(self, matchup_count: int) -> str:
        """Determine week type based on number of matchups"""
        if matchup_count == 6:
            return 'regular'
        elif matchup_count == 4:
            return 'playoff'
        elif matchup_count == 2:
            return 'superbowl'
        else:
            return 'unknown'
    
    def scrape_week(self, year: int, week: int) -> List[Dict]:
        """Scrape a specific week"""
        soup = self.fetch_week_page(year, week)
        if not soup:
            return []
        
        matchups = self.parse_matchups_from_page(soup, year, week)
        
        # Determine week type
        week_type = self.determine_week_type(len(matchups))
        
        # Add week type to each matchup
        for matchup in matchups:
            matchup['week_type'] = week_type
        
        return matchups
    
    def scrape_year(self, year: int, start_week: int = 1, end_week: int = 17) -> List[Dict]:
        """Scrape all weeks for a year"""
        all_matchups = []
        
        print(f"\nScraping {year}...")
        
        for week in range(start_week, end_week + 1):
            matchups = self.scrape_week(year, week)
            
            if matchups:
                all_matchups.extend(matchups)
                print(f"    Week {week}: {len(matchups)} matchups ({matchups[0].get('week_type', 'unknown')})")
            else:
                print(f"    Week {week}: No matchups found")
            
            # Rate limiting
            time.sleep(0.5)
        
        return all_matchups
    
    def scrape_all_historical(self, start_year: int = 2017, end_year: int = 2024) -> List[Dict]:
        """Scrape all historical data"""
        all_matchups = []
        
        for year in range(start_year, end_year + 1):
            matchups = self.scrape_year(year)
            all_matchups.extend(matchups)
            time.sleep(1)  # Be polite between years
        
        return all_matchups
    
    def scrape_current_season(self, year: int = 2025, max_week: int = 17) -> List[Dict]:
        """Scrape current season up to specified week"""
        return self.scrape_year(year, start_week=1, end_week=max_week)


def save_to_csv(matchups: List[Dict], csv_file: str):
    """Save matchups to CSV file"""
    if not matchups:
        return
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(csv_file)
    
    fieldnames = ['year', 'week', 'week_type', 'team1_name', 'team1_score', 
                  'team2_name', 'team2_score', 'winner', 'scraped_at']
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for matchup in matchups:
            writer.writerow({
                'year': matchup.get('year'),
                'week': matchup.get('week'),
                'week_type': matchup.get('week_type', 'unknown'),
                'team1_name': matchup.get('team1_name'),
                'team1_score': matchup.get('team1_score'),
                'team2_name': matchup.get('team2_name'),
                'team2_score': matchup.get('team2_score'),
                'winner': matchup.get('winner'),
                'scraped_at': matchup.get('scraped_at', datetime.now().isoformat())
            })


def load_from_csv(csv_file: str) -> List[Dict]:
    """Load matchups from CSV file"""
    if not os.path.exists(csv_file):
        return []
    
    matchups = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            matchups.append({
                'year': int(row['year']),
                'week': int(row['week']),
                'week_type': row['week_type'],
                'team1_name': row['team1_name'],
                'team1_score': float(row['team1_score']),
                'team2_name': row['team2_name'],
                'team2_score': float(row['team2_score']),
                'winner': row['winner'],
                'scraped_at': row.get('scraped_at', '')
            })
    
    return matchups


def get_scraped_weeks(csv_file: str) -> Dict:
    """Get dictionary of already scraped year/week combinations"""
    if not os.path.exists(csv_file):
        return {}
    
    scraped = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = int(row['year'])
            week = int(row['week'])
            if year not in scraped:
                scraped[year] = set()
            scraped[year].add(week)
    
    return scraped


if __name__ == '__main__':
    # Test scraper
    scraper = HistoricalScraper('987449')
    
    # Test single week
    print("Testing Week 1, 2017...")
    matchups = scraper.scrape_week(2017, 1)
    print(f"Found {len(matchups)} matchups")
    for m in matchups:
        print(f"  {m['team1_name']} ({m['team1_score']}) vs {m['team2_name']} ({m['team2_score']}) - Winner: {m['winner']}")
