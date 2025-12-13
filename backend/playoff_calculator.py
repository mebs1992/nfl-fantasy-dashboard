"""
Playoff Scenario Calculator
Calculates playoff scenarios based on current standings and remaining matchups
"""
from typing import Dict, List, Tuple, Set
from collections import defaultdict
from team_mapper import normalize_team_name


def calculate_playoff_scenarios(standings: List[Dict], week15_matchups: List[Dict]) -> Dict:
    """
    Calculate playoff scenarios for Week 15
    
    Args:
        standings: List of team standings with 'team', 'wins', 'losses', 'points_for'
        week15_matchups: List of Week 15 matchups with 'team1_name', 'team2_name'
        
    Returns:
        Dictionary with playoff scenario information
    """
    # Normalize all team names
    teams = {}
    for s in standings:
        team_name = normalize_team_name(s.get('team', s.get('team_name', '')))
        teams[team_name] = {
            'wins': s.get('wins', 0),
            'losses': s.get('losses', 0),
            'points_for': s.get('points_for', 0.0),
            'current_record': f"{s.get('wins', 0)}-{s.get('losses', 0)}"
        }
    
    # Normalize matchup team names
    normalized_matchups = []
    for matchup in week15_matchups:
        t1 = normalize_team_name(matchup.get('team1_name', ''))
        t2 = normalize_team_name(matchup.get('team2_name', ''))
        if t1 and t2 and t1 in teams and t2 in teams:
            normalized_matchups.append({
                'team1': t1,
                'team2': t2,
                'team1_record': teams[t1]['current_record'],
                'team2_record': teams[t2]['current_record'],
                'team1_points': teams[t1]['points_for'],
                'team2_points': teams[t2]['points_for']
            })
    
    # Sort teams by wins (desc), then points_for (desc)
    sorted_teams = sorted(teams.items(), key=lambda x: (-x[1]['wins'], -x[1]['points_for']))
    
    # Identify teams at 9-5 (locked for playoffs - top 3)
    teams_at_9_5 = [name for name, data in sorted_teams if data['wins'] == 9 and data['losses'] == 5]
    teams_at_9_5.sort(key=lambda x: -teams[x]['points_for'])
    
    # Calculate scenarios
    locked_teams = []
    can_make_it = []
    eliminated = []
    
    # Teams at 9-5 are locked (top 4 make playoffs, and these 3 are at 9-5)
    # Even if they lose Week 15, they'd be 9-6, and only 1 other team (The Ratpack at 8-6) could reach 9-6
    for team_name in teams_at_9_5:
        locked_teams.append({
            'team': team_name,
            'record': teams[team_name]['current_record'],
            'points_for': teams[team_name]['points_for'],
            'status': 'Locked for Playoffs',
            'reason': '9-5 record (cannot be eliminated)'
        })
    
    # Check The Ratpack (8-6) - they control their destiny
    ratpack_name = None
    for team_name, team_data in teams.items():
        if team_name == 'The Ratpack' and team_data['wins'] == 8 and team_data['losses'] == 6:
            ratpack_name = team_name
            # Check their Week 15 matchup
            ratpack_matchup = None
            for matchup in normalized_matchups:
                if matchup['team1'] == team_name or matchup['team2'] == team_name:
                    ratpack_matchup = matchup
                    break
            
            if ratpack_matchup:
                opponent = ratpack_matchup['team2'] if ratpack_matchup['team1'] == team_name else ratpack_matchup['team1']
                can_make_it.append({
                    'team': team_name,
                    'record': team_data['current_record'],
                    'points_for': team_data['points_for'],
                    'status': 'Controls Own Destiny',
                    'needs': f'Win vs {opponent} in Week 15',
                    'opponent': opponent,
                    'opponent_record': teams[opponent]['current_record']
                })
            break
    
    # Check teams at 7-7 (Mebs Militia, Freshie Vice, cheeseheads)
    # They need to win AND have The Ratpack lose to make playoffs
    teams_at_7_7 = [name for name, data in teams.items() if data['wins'] == 7 and data['losses'] == 7]
    teams_at_7_7.sort(key=lambda x: -teams[x]['points_for'])
    
    for team_name in teams_at_7_7:
        # Find their Week 15 matchup
        team_matchup = None
        for matchup in normalized_matchups:
            if matchup['team1'] == team_name or matchup['team2'] == team_name:
                team_matchup = matchup
                break
        
        if team_matchup:
            opponent = team_matchup['team2'] if team_matchup['team1'] == team_name else team_matchup['team1']
            needs = []
            needs.append(f'Win vs {opponent} in Week 15')
            if ratpack_name:
                # Find Ratpack's opponent
                for m in normalized_matchups:
                    if m['team1'] == ratpack_name or m['team2'] == ratpack_name:
                        ratpack_opponent = m['team2'] if m['team1'] == ratpack_name else m['team1']
                        needs.append(f'{ratpack_name} lose vs {ratpack_opponent}')
                        break
            
            can_make_it.append({
                'team': team_name,
                'record': teams[team_name]['current_record'],
                'points_for': teams[team_name]['points_for'],
                'status': 'Needs Help',
                'needs': needs,
                'opponent': opponent,
                'opponent_record': teams[opponent]['current_record']
            })
    
    # All other teams are eliminated
    locked_team_names = {t['team'] for t in locked_teams}
    can_make_team_names = {t['team'] for t in can_make_it}
    
    for team_name, team_data in teams.items():
        if team_name not in locked_team_names and team_name not in can_make_team_names:
            eliminated.append({
                'team': team_name,
                'record': team_data['current_record'],
                'points_for': team_data['points_for'],
                'status': 'Eliminated'
            })
    
    # Sort by wins, then points
    can_make_it.sort(key=lambda x: (-teams[x['team']]['wins'], -teams[x['team']]['points_for']))
    eliminated.sort(key=lambda x: (-teams[x['team']]['wins'], -teams[x['team']]['points_for']))
    
    return {
        'locked': locked_teams,
        'can_make_it': can_make_it,
        'eliminated': eliminated,
        'week15_matchups': normalized_matchups,
        'playoff_spots': 4,
        'current_week': 15
    }
