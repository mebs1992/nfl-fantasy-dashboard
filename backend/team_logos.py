"""
Team Logo Mapper
Maps team names to their logo URLs from NFL.com
"""
import csv
import os
from typing import Dict, Optional

def load_team_logos(data_dir: str = 'data') -> Dict[str, str]:
    """
    Load team logos from standings CSV files.
    Returns a dictionary mapping normalized team names to logo URLs.
    Uses the most recent logo URL for each team.
    """
    from team_mapper import normalize_team_name
    
    logos = {}
    csv_file = os.path.join(data_dir, 'standings.csv')
    
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                team_name = normalize_team_name(row.get('team_name', ''))
                logo_url = row.get('team_logo', '')
                if team_name and logo_url:
                    # Use the most recent logo (later years override earlier ones)
                    logos[team_name] = logo_url
    
    return logos


def get_team_logo_url(team_name: str, data_dir: str = 'data') -> Optional[str]:
    """
    Get the logo URL for a team.
    
    Args:
        team_name: The team name (will be normalized)
        data_dir: Directory containing the standings CSV
        
    Returns:
        Logo URL string or None if not found
    """
    from team_mapper import normalize_team_name
    
    normalized_name = normalize_team_name(team_name)
    logos = load_team_logos(data_dir)
    return logos.get(normalized_name)

