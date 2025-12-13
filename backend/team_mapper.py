"""
Team Name Mapper
Maps historical team name variations to canonical names for accurate head-to-head tracking
"""

# Team name mappings: {old_name: canonical_name}
TEAM_NAME_MAPPINGS = {
    # Wolfpack variations (all the same team)
    'Make Wolfpack Great Again': 'Wolfpack',
    'Wolfpack is Problematic': 'Wolfpack',
    'Covid Caged Wolfpack': 'Wolfpack',
    'Neutered Wolfpack': 'Wolfpack',
    'Impeached Wolfpack': 'Wolfpack',
    'Unidentifiable Wolfpack': 'Wolfpack',
    
    # Scrubs variations
    'Handycuffs': 'Scrubs',
    'PMQ Scrubs': 'Scrubs',
    'Captain Phillips': 'Scrubs',
    'Part-Time Battlers': 'Scrubs',
    
    # The Brotherhood variations
    'Hood': 'The Brotherhood',
    'Smitten on Witten': 'The Brotherhood',
    'The Arian Brother Hood': 'The Brotherhood',
    
    # Killer Cam variations (case normalization)
    'killer cam': 'Killer Cam',
    
    # Woody variations
    'Cowboys Ware94': 'Woody',
    
    # MEGATRON variations
    'TeamBreezy': 'MEGATRON',
    "Breezes' Transformers": 'MEGATRON',
    'MegatroN': 'MEGATRON',
    
    # The Generous variations
    'Generous Brady': 'The Generous',
    'Ball So Hard Wolfpak': 'The Generous',
    'Wolfpak': 'The Generous',
    'Boston Tea Party': 'The Generous',
    
    # Pelicans variations
    'Palm Beach Pelicans': 'Pels',
    
    # Mebs Militia variations
    'Mebs Militia owns the Hood': 'Mebs Militia',
    
    # Rats variations
    'Rats': 'The Ratpack',
    
    # Keep these as-is (no changes detected)
    # 'DirtyBirds': 'DirtyBirds',
    # 'Killer Cam': 'Killer Cam',
    # "Maggi's Mighty Ducks": "Maggi's Mighty Ducks",
    # 'Scrubs': 'Scrubs',
    # 'The Brotherhood': 'The Brotherhood',
    # 'Woody': 'Woody',
    # 'cheeseheads': 'cheeseheads',
    # 'Freshie Vice': 'Freshie Vice',
    # 'MEGATRON': 'MEGATRON',
}

# Reverse mapping for display (canonical -> most recent name)
CANONICAL_TO_DISPLAY = {
    'Wolfpack': 'Wolfpack',  # Use most recent or generic
    'The Generous': 'The Generous',
    'Pels': 'Pels',
    'Mebs Militia': 'Mebs Militia',
    'The Ratpack': 'The Ratpack',
}


def normalize_team_name(team_name: str) -> str:
    """
    Normalize a team name to its canonical form.
    If no mapping exists, returns the original name.
    """
    if not team_name:
        return team_name
    
    # Check if we have a mapping
    normalized = TEAM_NAME_MAPPINGS.get(team_name, team_name)
    return normalized


def get_display_name(canonical_name: str, year: int = None) -> str:
    """
    Get the display name for a canonical team name.
    Optionally use year to show the name that was used in that year.
    """
    return CANONICAL_TO_DISPLAY.get(canonical_name, canonical_name)


def normalize_matchup(matchup: dict) -> dict:
    """
    Normalize team names in a matchup dictionary.
    """
    normalized = matchup.copy()
    
    if 'team1_name' in normalized:
        normalized['team1_name'] = normalize_team_name(normalized['team1_name'])
    
    if 'team2_name' in normalized:
        normalized['team2_name'] = normalize_team_name(normalized['team2_name'])
    
    if 'winner' in normalized and normalized['winner']:
        # Map winner if it's a tie or one of the teams
        if normalized['winner'] != 'Tie' and normalized['winner'] != 'tie':
            normalized['winner'] = normalize_team_name(normalized['winner'])
    
    return normalized


def get_all_canonical_teams() -> list:
    """
    Get list of all canonical team names.
    """
    canonical_teams = set()
    
    # Add all mapped canonical names
    canonical_teams.update(TEAM_NAME_MAPPINGS.values())
    
    # Add teams that don't have mappings (they are their own canonical name)
    all_teams = set(TEAM_NAME_MAPPINGS.keys())
    all_teams.update(TEAM_NAME_MAPPINGS.values())
    
    # This would need to be populated from actual data
    # For now, return the canonical names we know about
    return sorted(list(canonical_teams))


if __name__ == '__main__':
    # Test the mappings
    print("Team Name Mappings:")
    print("=" * 60)
    for old_name, canonical in sorted(TEAM_NAME_MAPPINGS.items()):
        print(f"  {old_name:40} -> {canonical}")
    
    print("\n" + "=" * 60)
    print("Test normalizations:")
    test_names = [
        'Make Wolfpack Great Again',
        'Generous Brady',
        'Palm Beach Pelicans',
        'Rats',
        'DirtyBirds',  # Should stay the same
    ]
    
    for name in test_names:
        normalized = normalize_team_name(name)
        print(f"  {name:40} -> {normalized}")

