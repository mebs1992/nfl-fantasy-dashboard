"""
Historical Data Scraper using Selenium for JavaScript-rendered pages
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
import re
import time
from typing import Dict, List, Optional
from datetime import datetime


class HistoricalScraperSelenium:
    def __init__(self, league_id: str, headless: bool = True):
        self.league_id = league_id
        self.base_url = f"https://fantasy.nfl.com/league/{league_id}/history"
        self.headless = headless
        self.driver = None
    
    def _get_driver(self):
        """Initialize Selenium WebDriver"""
        if self.driver is None:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                print(f"Error initializing Chrome driver: {e}")
                print("Make sure ChromeDriver is installed and in PATH")
                raise
        return self.driver
    
    def _close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def get_matchups_for_week(self, year: int, week: int) -> List[Dict]:
        """Get matchups for a specific week using Selenium"""
        driver = self._get_driver()
        url = f"{self.base_url}/{year}/schedule"
        
        try:
            driver.get(url)
            # Wait for page to load
            time.sleep(3)
            
            # Try to click on the week if there's a week selector
            try:
                week_element = driver.find_element(By.XPATH, f"//a[contains(text(), 'Week {week}')] | //li[contains(text(), 'Week {week}')]")
                week_element.click()
                time.sleep(2)  # Wait for content to load
            except:
                # Week selector not found or already on that week
                pass
            
            # Get page source after JavaScript rendering
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            matchups = self._parse_matchups_from_rendered_page(soup, year, week)
            return matchups
            
        except Exception as e:
            print(f"Error fetching week {week} for {year}: {e}")
            return []
    
    def _parse_matchups_from_rendered_page(self, soup: BeautifulSoup, year: int, week: int) -> List[Dict]:
        """Parse matchups from rendered HTML"""
        matchups = []
        
        # Look for matchup containers - NFL.com uses specific classes
        # Try multiple selectors
        selectors = [
            ('div', {'class': re.compile(r'matchup|gameRow', re.I)}),
            ('li', {'class': re.compile(r'matchup|game', re.I)}),
            ('tr', {'class': re.compile(r'matchup|game', re.I)}),
        ]
        
        for tag, attrs in selectors:
            containers = soup.find_all(tag, attrs)
            for container in containers:
                matchup = self._parse_matchup_element(container, year, week)
                if matchup:
                    matchups.append(matchup)
            
            if matchups:
                break
        
        # If no matchups found with classes, try finding by structure
        if not matchups:
            # Look for elements containing team names and scores
            all_elements = soup.find_all(['div', 'li', 'tr'])
            for elem in all_elements:
                text = elem.get_text()
                # Check if it looks like a matchup (has 2 scores)
                scores = re.findall(r'\d+\.\d+', text)
                if len(scores) >= 2:
                    # Check if it has team-like text
                    words = text.split()
                    if len(words) > 4:  # Likely has team names
                        matchup = self._parse_matchup_element(elem, year, week)
                        if matchup:
                            matchups.append(matchup)
        
        return matchups
    
    def _parse_matchup_element(self, element, year: int, week: int) -> Optional[Dict]:
        """Parse a single matchup element"""
        try:
            text = element.get_text()
            
            # Extract scores
            score_pattern = re.compile(r'\d+\.\d+')
            scores = [float(m) for m in score_pattern.findall(text)]
            
            if len(scores) < 2:
                return None
            
            matchup = {
                'year': year,
                'week': week,
                'team1_score': scores[0],
                'team2_score': scores[1]
            }
            
            # Extract team names
            # Look for links first
            team_links = element.find_all('a', href=re.compile(r'/team/'))
            if len(team_links) >= 2:
                matchup['team1_name'] = team_links[0].get_text(strip=True)
                matchup['team2_name'] = team_links[1].get_text(strip=True)
            else:
                # Try to extract from text
                # Split text and look for capitalized words that might be team names
                words = text.split()
                team_names = []
                for word in words:
                    # Skip scores, week numbers, common words
                    if (len(word) > 3 and word[0].isupper() and 
                        not re.match(r'^\d+\.?\d*$', word) and
                        word not in ['Week', 'Matchup', 'Results', 'By', 'Team', 'Schedule', 'Win', 'Loss']):
                        team_names.append(word)
                        if len(team_names) >= 2:
                            break
                
                if len(team_names) >= 2:
                    matchup['team1_name'] = team_names[0]
                    matchup['team2_name'] = team_names[1]
                else:
                    return None
            
            # Determine winner
            if scores[0] > scores[1]:
                matchup['winner'] = matchup['team1_name']
            elif scores[1] > scores[0]:
                matchup['winner'] = matchup['team2_name']
            else:
                matchup['winner'] = 'Tie'
            
            return matchup
            
        except Exception as e:
            return None
    
    def scrape_year(self, year: int) -> Dict:
        """Scrape all data for a year"""
        driver = self._get_driver()
        url = f"{self.base_url}/{year}/schedule"
        
        print(f"Scraping {year}...")
        
        all_matchups = []
        
        try:
            driver.get(url)
            time.sleep(4)  # Wait for JavaScript to render
            
            # Get all weeks available
            week_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'week')] | //li[contains(text(), 'Week')]")
            week_numbers = set()
            
            for elem in week_elements:
                text = elem.text
                week_match = re.search(r'week\s*(\d+)', text, re.I)
                if week_match:
                    week_numbers.add(int(week_match.group(1)))
            
            # If no weeks found in links, try weeks 1-17
            if not week_numbers:
                week_numbers = set(range(1, 18))
            
            print(f"Found {len(week_numbers)} weeks")
            
            # Fetch each week
            for week in sorted(week_numbers):
                print(f"  Fetching Week {week}...")
                week_matchups = self.get_matchups_for_week(year, week)
                all_matchups.extend(week_matchups)
                print(f"    Found {len(week_matchups)} matchups")
                time.sleep(1)  # Be polite
            
        except Exception as e:
            print(f"Error scraping {year}: {e}")
        finally:
            self._close_driver()
        
        return {
            'year': year,
            'matchups': all_matchups
        }


def scrape_2017_test():
    """Test function to scrape just 2017"""
    scraper = HistoricalScraperSelenium('987449', headless=True)
    try:
        data = scraper.scrape_year(2017)
        return data
    finally:
        scraper._close_driver()


if __name__ == '__main__':
    print("Testing 2017 scrape with Selenium...")
    data = scrape_2017_test()
    
    output_file = '../data/test_2017_selenium.json'
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nScrape complete!")
    print(f"Found {len(data['matchups'])} matchups")
    print(f"Data saved to: {output_file}")

