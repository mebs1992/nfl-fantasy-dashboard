"""
Data Manager for storing and processing league data
Handles historical data, head-to-head calculations, etc.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class DataManager:
    def __init__(self, data_dir='data'):
        # Use provided data_dir or find it relative to current location
        if not os.path.isabs(data_dir):
            # Handle both running from backend/ and root directory
            if os.path.exists('data'):
                self.data_dir = os.path.abspath('data')
            elif os.path.exists('../data'):
                self.data_dir = os.path.abspath('../data')
            else:
                self.data_dir = os.path.abspath(data_dir)
        else:
            self.data_dir = data_dir
        
        self.data_file = os.path.join(self.data_dir, 'league_data.json')
        self.historical_file = os.path.join(self.data_dir, 'historical_data.json')
        self.current_data = {}
        self.historical_data = {}
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_data(self):
        """Load data from JSON files"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    loaded_data = json.load(f)
                    # Only use if it has actual standings data
                    if loaded_data.get('standings') and len(loaded_data.get('standings', [])) > 0:
                        self.current_data = loaded_data
                    else:
                        raise ValueError("No standings data in file")
            except Exception as e:
                print(f"Error loading data: {e}, trying sample data...")
                self.current_data = {}
        
        # If no valid data loaded, try sample data
        if not self.current_data.get('standings'):
            sample_file = os.path.join(self.data_dir, 'sample_data.json')
            if os.path.exists(sample_file):
                try:
                    with open(sample_file, 'r') as f:
                        self.current_data = json.load(f)
                        # Save it as the main data file
                        self.save_data()
                        print("Loaded sample data. Click 'Refresh Data' to fetch real data from NFL.com")
                except Exception as e:
                    print(f"Error loading sample data: {e}")
                    self.current_data = {}
            else:
                self.current_data = {}
        
        if os.path.exists(self.historical_file):
            try:
                with open(self.historical_file, 'r') as f:
                    self.historical_data = json.load(f)
            except Exception as e:
                print(f"Error loading historical data: {e}")
                self.historical_data = {
                    'seasons': [],
                    'matchups': [],
                    'teams': {}
                }
        else:
            self.historical_data = {
                'seasons': [],
                'matchups': [],
                'teams': {}
            }
    
    def save_data(self):
        """Save data to JSON files"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.current_data, f, indent=2)
            
            with open(self.historical_file, 'w') as f:
                json.dump(self.historical_data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def update_data(self, new_data: Dict):
        """Update current data and merge into historical"""
        self.current_data = new_data
        self.current_data['last_updated'] = datetime.now().isoformat()
        
        # Merge matchups into historical data
        if 'matchups' in new_data:
            for matchup in new_data['matchups']:
                self._add_matchup_to_history(matchup)
        
        # Update team information
        if 'standings' in new_data:
            for team in new_data['standings']:
                team_name = team.get('name')
                if team_name:
                    if team_name not in self.historical_data['teams']:
                        self.historical_data['teams'][team_name] = {
                            'id': team.get('id'),
                            'total_wins': 0,
                            'total_losses': 0,
                            'total_ties': 0,
                            'total_points': 0,
                            'seasons': []
                        }
                    
                    # Update totals
                    team_data = self.historical_data['teams'][team_name]
                    team_data['total_wins'] += team.get('wins', 0)
                    team_data['total_losses'] += team.get('losses', 0)
                    team_data['total_ties'] += team.get('ties', 0)
                    team_data['total_points'] += team.get('points_for', 0)
        
        self.save_data()
    
    def _add_matchup_to_history(self, matchup: Dict):
        """Add a matchup to historical data"""
        if 'matchups' not in self.historical_data:
            self.historical_data['matchups'] = []
        
        # Check if matchup already exists
        matchup_id = matchup.get('id') or f"{matchup.get('week')}_{matchup.get('team1')}_{matchup.get('team2')}"
        existing = [m for m in self.historical_data['matchups'] if m.get('id') == matchup_id]
        
        if not existing:
            matchup['id'] = matchup_id
            self.historical_data['matchups'].append(matchup)
    
    def get_standings(self) -> List[Dict]:
        """Get current standings"""
        standings = self.current_data.get('standings', [])
        # Filter out any invalid entries (like header rows)
        return [s for s in standings if s.get('name') and s.get('name') != 'Rank' and isinstance(s.get('wins'), int)]
    
    def get_head_to_head(self, team1: str, team2: str) -> Dict:
        """Get head-to-head record between two teams"""
        # Import team mapper
        try:
            from team_mapper import normalize_team_name
        except ImportError:
            # Fallback if mapper not available
            def normalize_team_name(name):
                return name
        
        # Normalize input team names
        team1_normalized = normalize_team_name(team1)
        team2_normalized = normalize_team_name(team2)
        
        # Load matchups from CSV first (faster and more complete)
        matchups = self.get_matchups()
        
        # Fallback to historical_data if CSV not available
        if not matchups:
            matchups = self.historical_data.get('matchups', [])
        
        team1_wins = 0
        team2_wins = 0
        ties = 0
        games = []
        
        for matchup in matchups:
            # Normalize team names in matchup
            t1 = normalize_team_name(matchup.get('team1_name') or matchup.get('team1'))
            t2 = normalize_team_name(matchup.get('team2_name') or matchup.get('team2'))
            
            # Check if this matchup involves our two teams (in either order)
            if (t1 == team1_normalized and t2 == team2_normalized) or (t1 == team2_normalized and t2 == team1_normalized):
                games.append(matchup)
                winner = matchup.get('winner')
                if winner:
                    winner_normalized = normalize_team_name(winner)
                    if winner_normalized == team1_normalized:
                        team1_wins += 1
                    elif winner_normalized == team2_normalized:
                        team2_wins += 1
                    elif winner == 'Tie' or winner == 'tie':
                        ties += 1
        
        total_games = team1_wins + team2_wins + ties
        team1_win_pct = (team1_wins / total_games * 100) if total_games > 0 else 0
        team2_win_pct = (team2_wins / total_games * 100) if total_games > 0 else 0
        
        return {
            'team1': team1,
            'team2': team2,
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'ties': ties,
            'total_games': total_games,
            'team1_win_pct': round(team1_win_pct, 2),
            'team2_win_pct': round(team2_win_pct, 2),
            'games': games
        }
    
    def get_all_head_to_head(self) -> Dict:
        """Get all head-to-head records for all team pairs"""
        teams = list(self.historical_data.get('teams', {}).keys())
        if not teams:
            # Fallback to current standings teams
            standings = self.get_standings()
            teams = [t.get('name') for t in standings if t.get('name')]
        
        h2h_matrix = {}
        
        for i, team1 in enumerate(teams):
            for team2 in teams[i+1:]:
                h2h = self.get_head_to_head(team1, team2)
                key = f"{team1} vs {team2}"
                h2h_matrix[key] = h2h
        
        return h2h_matrix
    
    def get_team_stats(self, team_id: Optional[str] = None, team_name: Optional[str] = None) -> Dict:
        """Get comprehensive stats for a team"""
        # Find team in current standings
        standings = self.get_standings()
        team_data = None
        
        if team_id:
            team_data = next((t for t in standings if t.get('id') == team_id), None)
        elif team_name:
            team_data = next((t for t in standings if t.get('name') == team_name), None)
        
        if not team_data:
            return {}
        
        team_name = team_name or team_data.get('name')
        historical = self.historical_data.get('teams', {}).get(team_name, {})
        
        # Get all matchups involving this team
        matchups = self.historical_data.get('matchups', [])
        team_matchups = [
            m for m in matchups
            if m.get('team1_name') == team_name or m.get('team2_name') == team_name
            or m.get('team1') == team_name or m.get('team2') == team_name
        ]
        
        # Calculate win percentage vs each opponent
        opponent_records = defaultdict(lambda: {'wins': 0, 'losses': 0, 'ties': 0})
        
        for matchup in team_matchups:
            opponent = None
            if matchup.get('team1_name') == team_name or matchup.get('team1') == team_name:
                opponent = matchup.get('team2_name') or matchup.get('team2')
            else:
                opponent = matchup.get('team1_name') or matchup.get('team1')
            
            if opponent:
                winner = matchup.get('winner')
                if winner == team_name:
                    opponent_records[opponent]['wins'] += 1
                elif winner == opponent:
                    opponent_records[opponent]['losses'] += 1
                else:
                    opponent_records[opponent]['ties'] += 1
        
        # Convert to list with win percentages
        opponent_stats = []
        for opponent, record in opponent_records.items():
            total = record['wins'] + record['losses'] + record['ties']
            win_pct = (record['wins'] / total * 100) if total > 0 else 0
            opponent_stats.append({
                'opponent': opponent,
                **record,
                'win_pct': round(win_pct, 2)
            })
        
        return {
            'current': team_data,
            'historical': historical,
            'matchups': team_matchups,
            'opponent_records': sorted(opponent_stats, key=lambda x: x['win_pct'], reverse=True)
        }
    
    def get_matchups(self, week: Optional[int] = None, year: Optional[int] = None) -> List[Dict]:
        """Get matchups for a specific week or all weeks"""
        # Import team mapper for normalization
        try:
            from team_mapper import normalize_matchup
        except ImportError:
            def normalize_matchup(m):
                return m
        
        # Try to load from CSV first (faster)
        csv_file = os.path.join(self.data_dir, 'matchups.csv')
        if os.path.exists(csv_file):
            try:
                from historical_scraper import load_from_csv
                matchups = load_from_csv(csv_file)
                
                # Normalize team names in all matchups
                matchups = [normalize_matchup(m) for m in matchups]
                
                # Filter by week/year if specified
                if week:
                    matchups = [m for m in matchups if m.get('week') == week]
                if year:
                    matchups = [m for m in matchups if m.get('year') == year]
                
                return matchups
            except Exception as e:
                print(f"Error loading from CSV: {e}, falling back to JSON")
        
        # Fallback to JSON
        matchups = self.historical_data.get('matchups', [])
        
        # Normalize team names
        matchups = [normalize_matchup(m) for m in matchups]
        
        if week:
            matchups = [m for m in matchups if m.get('week') == week]
        if year:
            matchups = [m for m in matchups if m.get('year') == year]
        
        return matchups
    
    def get_transactions(self, limit: int = 50) -> List[Dict]:
        """Get recent transactions"""
        transactions = self.current_data.get('transactions', [])
        return transactions[:limit]
    
    def get_league_info(self) -> Dict:
        """Get general league information"""
        return {
            'league_id': self.current_data.get('league_id'),
            'name': 'The Greatest League',
            'current_week': self.current_data.get('current_week'),
            'last_updated': self.get_last_update(),
            'total_teams': len(self.get_standings()),
            'total_seasons': len(self.historical_data.get('seasons', []))
        }
    
    def get_last_update(self) -> str:
        """Get timestamp of last update"""
        return self.current_data.get('last_updated', datetime.now().isoformat())

