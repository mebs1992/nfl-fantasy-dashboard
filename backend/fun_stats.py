"""
Fun Statistics Calculator for NFL Fantasy Dashboard
Calculates rivalries, streaks, blowouts, bad beats, weekly awards, consistency, clutch performance, etc.
"""
from collections import defaultdict
from typing import Dict, List, Tuple
from datetime import datetime
import os


def calculate_rivalries(matchups: List[Dict], normalize_team_name) -> List[Dict]:
    """Calculate top rivalries based on games played, win differential, and recency"""
    rivalry_data = defaultdict(lambda: {
        'team1': '',
        'team2': '',
        'games_played': 0,
        'team1_wins': 0,
        'team2_wins': 0,
        'ties': 0,
        'total_points': 0,
        'avg_margin': 0,
        'recent_games': []
    })
    
    for matchup in matchups:
        t1 = normalize_team_name(matchup.get('team1_name', ''))
        t2 = normalize_team_name(matchup.get('team2_name', ''))
        
        if not t1 or not t2 or t1 == t2:
            continue
        
        # Create consistent key (alphabetical order)
        key = tuple(sorted([t1, t2]))
        
        if rivalry_data[key]['team1'] == '':
            rivalry_data[key]['team1'] = t1
            rivalry_data[key]['team2'] = t2
        
        rivalry_data[key]['games_played'] += 1
        rivalry_data[key]['total_points'] += matchup.get('team1_score', 0) + matchup.get('team2_score', 0)
        
        winner = normalize_team_name(matchup.get('winner', ''))
        if winner == t1:
            rivalry_data[key]['team1_wins'] += 1
        elif winner == t2:
            rivalry_data[key]['team2_wins'] += 1
        else:
            rivalry_data[key]['ties'] += 1
        
        # Store recent games (last 5)
        margin = abs(matchup.get('team1_score', 0) - matchup.get('team2_score', 0))
        rivalry_data[key]['recent_games'].append({
            'year': matchup.get('year', 0),
            'week': matchup.get('week', 0),
            'margin': margin,
            'winner': winner
        })
        if len(rivalry_data[key]['recent_games']) > 5:
            rivalry_data[key]['recent_games'] = sorted(
                rivalry_data[key]['recent_games'],
                key=lambda x: (x['year'], x['week']),
                reverse=True
            )[:5]
    
    # Calculate rivalry scores and format
    rivalries = []
    for key, data in rivalry_data.items():
        if data['games_played'] < 3:  # Minimum 3 games for a rivalry
            continue
        
        # Calculate average margin
        margins = [g['margin'] for g in data['recent_games']]
        data['avg_margin'] = sum(margins) / len(margins) if margins else 0
        
        # Calculate rivalry score (games played * closeness factor * recency)
        win_diff = abs(data['team1_wins'] - data['team2_wins'])
        closeness = 1.0 - (win_diff / data['games_played']) if data['games_played'] > 0 else 0
        recency_bonus = min(len(data['recent_games']), 5) / 5.0
        
        rivalry_score = data['games_played'] * closeness * (1 + recency_bonus * 0.5)
        
        rivalries.append({
            'team1': data['team1'],
            'team2': data['team2'],
            'games_played': data['games_played'],
            'team1_wins': data['team1_wins'],
            'team2_wins': data['team2_wins'],
            'ties': data['ties'],
            'win_differential': win_diff,
            'avg_margin': round(data['avg_margin'], 2),
            'rivalry_score': round(rivalry_score, 2),
            'recent_games': data['recent_games']
        })
    
    # Sort by rivalry score
    rivalries.sort(key=lambda x: x['rivalry_score'], reverse=True)
    return rivalries[:20]  # Top 20 rivalries


def generate_trash_talk(team1: str, team2: str, rivalry_data: Dict, normalize_team_name) -> List[str]:
    """Generate trash talk based on head-to-head record"""
    t1 = normalize_team_name(team1)
    t2 = normalize_team_name(team2)
    
    if not rivalry_data:
        return ["No history between these teams yet!"]
    
    # Find the rivalry
    rivalry = None
    for r in rivalry_data:
        if (r['team1'] == t1 and r['team2'] == t2) or (r['team1'] == t2 and r['team2'] == t1):
            rivalry = r
            break
    
    if not rivalry:
        return ["These teams haven't faced off enough to generate trash talk!"]
    
    trash_talk = []
    games = rivalry['games_played']
    t1_wins = rivalry['team1_wins'] if rivalry['team1'] == t1 else rivalry['team2_wins']
    t2_wins = rivalry['team2_wins'] if rivalry['team2'] == t2 else rivalry['team1_wins']
    
    # Win percentage facts
    if t1_wins > t2_wins:
        pct = (t1_wins / games * 100) if games > 0 else 0
        trash_talk.append(f"{team1} has dominated {team2}, winning {t1_wins} out of {games} games ({pct:.0f}% win rate)!")
        if t1_wins >= games * 0.7:
            trash_talk.append(f"{team2} might want to consider forfeiting when they see {team1} on the schedule.")
    elif t2_wins > t1_wins:
        pct = (t2_wins / games * 100) if games > 0 else 0
        trash_talk.append(f"{team2} has {team1}'s number, winning {t2_wins} out of {games} games ({pct:.0f}% win rate)!")
    else:
        trash_talk.append(f"These teams are evenly matched with {t1_wins}-{t2_wins} records in {games} games!")
    
    # Recent performance
    if rivalry['recent_games']:
        recent = rivalry['recent_games'][0]
        if recent['winner'] == t1:
            trash_talk.append(f"In their last meeting ({recent['year']} Week {recent['week']}), {team1} came out on top!")
        elif recent['winner'] == t2:
            trash_talk.append(f"In their last meeting ({recent['year']} Week {recent['week']}), {team2} got the W!")
    
    # Close games
    if rivalry['avg_margin'] < 10:
        trash_talk.append(f"These matchups are always close - average margin of victory is only {rivalry['avg_margin']:.1f} points!")
    
    return trash_talk


def calculate_streaks(matchups: List[Dict], standings: List[Dict], normalize_team_name) -> Dict:
    """Calculate current and all-time streaks"""
    # Organize matchups by team and year/week
    team_games = defaultdict(lambda: defaultdict(list))
    
    for matchup in matchups:
        t1 = normalize_team_name(matchup.get('team1_name', ''))
        t2 = normalize_team_name(matchup.get('team2_name', ''))
        winner = normalize_team_name(matchup.get('winner', ''))
        
        if not t1 or not t2:
            continue
        
        year = matchup.get('year', 0)
        week = matchup.get('week', 0)
        
        # Record game for team1
        team_games[t1][(year, week)] = {
            'opponent': t2,
            'score': matchup.get('team1_score', 0),
            'opponent_score': matchup.get('team2_score', 0),
            'won': winner == t1,
            'tie': winner.lower() == 'tie'
        }
        
        # Record game for team2
        team_games[t2][(year, week)] = {
            'opponent': t1,
            'score': matchup.get('team2_score', 0),
            'opponent_score': matchup.get('team1_score', 0),
            'won': winner == t2,
            'tie': winner.lower() == 'tie'
        }
    
    # Calculate current streaks (2025 season)
    current_streaks = []
    all_time_streaks = []
    
    for team, games_dict in team_games.items():
        # Sort games chronologically
        sorted_games = sorted(games_dict.items(), key=lambda x: (x[0][0], x[0][1]))
        
        # Current streak (2025 only)
        current_2025_games = [(y, w, g) for (y, w), g in sorted_games if y == 2025]
        if current_2025_games:
            current_streak = 0
            current_type = None
            for year, week, game in reversed(current_2025_games):
                if game['tie']:
                    break
                if current_type is None:
                    current_type = 'win' if game['won'] else 'loss'
                    current_streak = 1
                elif (game['won'] and current_type == 'win') or (not game['won'] and current_type == 'loss'):
                    current_streak += 1
                else:
                    break
            
            if current_streak > 0:
                current_streaks.append({
                    'team': team,
                    'streak': current_streak,
                    'type': current_type,
                    'current': True
                })
        
        # All-time streaks
        current_streak = 0
        current_type = None
        max_streak = 0
        max_type = None
        
        for (year, week), game in sorted_games:
            if game['tie']:
                current_streak = 0
                current_type = None
                continue
            
            if current_type is None:
                current_type = 'win' if game['won'] else 'loss'
                current_streak = 1
            elif (game['won'] and current_type == 'win') or (not game['won'] and current_type == 'loss'):
                current_streak += 1
            else:
                # Streak broken
                if current_streak > max_streak:
                    max_streak = current_streak
                    max_type = current_type
                current_type = 'win' if game['won'] else 'loss'
                current_streak = 1
        
        # Check final streak
        if current_streak > max_streak:
            max_streak = current_streak
            max_type = current_type
        
        if max_streak > 0:
            all_time_streaks.append({
                'team': team,
                'streak': max_streak,
                'type': max_type,
                'current': False
            })
    
    # Sort streaks
    current_streaks.sort(key=lambda x: x['streak'], reverse=True)
    all_time_streaks.sort(key=lambda x: x['streak'], reverse=True)
    
    return {
        'current': current_streaks[:20],
        'all_time': all_time_streaks[:20]
    }


def calculate_blowouts(matchups: List[Dict], normalize_team_name) -> List[Dict]:
    """Calculate biggest blowouts (largest margins of victory)"""
    blowouts = []
    
    for matchup in matchups:
        t1 = normalize_team_name(matchup.get('team1_name', ''))
        t2 = normalize_team_name(matchup.get('team2_name', ''))
        score1 = matchup.get('team1_score', 0)
        score2 = matchup.get('team2_score', 0)
        winner = normalize_team_name(matchup.get('winner', ''))
        
        if not t1 or not t2 or winner.lower() == 'tie':
            continue
        
        margin = abs(score1 - score2)
        winner_name = t1 if winner == t1 else t2
        loser_name = t2 if winner == t1 else t1
        winner_score = score1 if winner == t1 else score2
        loser_score = score2 if winner == t1 else score1
        
        blowouts.append({
            'year': matchup.get('year', 0),
            'week': matchup.get('week', 0),
            'week_type': matchup.get('week_type', 'regular'),
            'winner': winner_name,
            'loser': loser_name,
            'winner_score': winner_score,
            'loser_score': loser_score,
            'margin': margin
        })
    
    blowouts.sort(key=lambda x: x['margin'], reverse=True)
    return blowouts[:50]  # Top 50 blowouts


def calculate_bad_beats(matchups: List[Dict], normalize_team_name) -> List[Dict]:
    """Calculate bad beats - teams that lost despite scoring high, or won despite scoring low"""
    bad_beats = []
    
    for matchup in matchups:
        t1 = normalize_team_name(matchup.get('team1_name', ''))
        t2 = normalize_team_name(matchup.get('team2_name', ''))
        score1 = matchup.get('team1_score', 0)
        score2 = matchup.get('team2_score', 0)
        winner = normalize_team_name(matchup.get('winner', ''))
        
        if not t1 or not t2 or winner.lower() == 'tie':
            continue
        
        # High score loss (scored 130+ and lost)
        if score1 >= 130 and winner == t2:
            bad_beats.append({
                'type': 'high_score_loss',
                'year': matchup.get('year', 0),
                'week': matchup.get('week', 0),
                'week_type': matchup.get('week_type', 'regular'),
                'team': t1,
                'opponent': t2,
                'team_score': score1,
                'opponent_score': score2,
                'margin': score2 - score1
            })
        
        if score2 >= 130 and winner == t1:
            bad_beats.append({
                'type': 'high_score_loss',
                'year': matchup.get('year', 0),
                'week': matchup.get('week', 0),
                'week_type': matchup.get('week_type', 'regular'),
                'team': t2,
                'opponent': t1,
                'team_score': score2,
                'opponent_score': score1,
                'margin': score1 - score2
            })
        
        # Low score win (scored < 90 and won)
        if score1 < 90 and winner == t1:
            bad_beats.append({
                'type': 'low_score_win',
                'year': matchup.get('year', 0),
                'week': matchup.get('week', 0),
                'week_type': matchup.get('week_type', 'regular'),
                'team': t1,
                'opponent': t2,
                'team_score': score1,
                'opponent_score': score2,
                'margin': score1 - score2
            })
        
        if score2 < 90 and winner == t2:
            bad_beats.append({
                'type': 'low_score_win',
                'year': matchup.get('year', 0),
                'week': matchup.get('week', 0),
                'week_type': matchup.get('week_type', 'regular'),
                'team': t2,
                'opponent': t1,
                'team_score': score2,
                'opponent_score': score1,
                'margin': score2 - score1
            })
    
    # Sort by margin (for high score losses) or by how low the score was (for low score wins)
    high_score_losses = [b for b in bad_beats if b['type'] == 'high_score_loss']
    low_score_wins = [b for b in bad_beats if b['type'] == 'low_score_win']
    
    high_score_losses.sort(key=lambda x: (x['team_score'], -x['margin']), reverse=True)
    low_score_wins.sort(key=lambda x: x['team_score'])
    
    return {
        'high_score_losses': high_score_losses[:30],
        'low_score_wins': low_score_wins[:30]
    }


def calculate_weekly_awards(matchups: List[Dict], normalize_team_name) -> Dict:
    """Calculate weekly awards (highest score, lowest winning score, biggest comeback, etc.)"""
    # Organize by year and week
    weekly_data = defaultdict(lambda: {
        'games': [],
        'highest_score': 0,
        'lowest_winning_score': float('inf'),
        'biggest_margin': 0
    })
    
    for matchup in matchups:
        year = matchup.get('year', 0)
        week = matchup.get('week', 0)
        key = (year, week)
        
        t1 = normalize_team_name(matchup.get('team1_name', ''))
        t2 = normalize_team_name(matchup.get('team2_name', ''))
        score1 = matchup.get('team1_score', 0)
        score2 = matchup.get('team2_score', 0)
        winner = normalize_team_name(matchup.get('winner', ''))
        
        if not t1 or not t2:
            continue
        
        weekly_data[key]['games'].append({
            'team1': t1,
            'team2': t2,
            'score1': score1,
            'score2': score2,
            'winner': winner
        })
        
        # Track highest score
        weekly_data[key]['highest_score'] = max(
            weekly_data[key]['highest_score'],
            score1,
            score2
        )
        
        # Track lowest winning score
        if winner == t1:
            weekly_data[key]['lowest_winning_score'] = min(
                weekly_data[key]['lowest_winning_score'],
                score1
            )
        elif winner == t2:
            weekly_data[key]['lowest_winning_score'] = min(
                weekly_data[key]['lowest_winning_score'],
                score2
            )
        
        # Track biggest margin
        margin = abs(score1 - score2)
        weekly_data[key]['biggest_margin'] = max(weekly_data[key]['biggest_margin'], margin)
    
    # Find award winners
    awards = {
        'highest_scores': [],
        'lowest_winning_scores': [],
        'biggest_margins': []
    }
    
    for (year, week), data in weekly_data.items():
        # Find highest score game
        for game in data['games']:
            if game['score1'] == data['highest_score']:
                awards['highest_scores'].append({
                    'year': year,
                    'week': week,
                    'team': game['team1'],
                    'score': game['score1'],
                    'opponent': game['team2'],
                    'opponent_score': game['score2']
                })
            elif game['score2'] == data['highest_score']:
                awards['highest_scores'].append({
                    'year': year,
                    'week': week,
                    'team': game['team2'],
                    'score': game['score2'],
                    'opponent': game['team1'],
                    'opponent_score': game['score1']
                })
        
        # Find lowest winning score
        if data['lowest_winning_score'] != float('inf'):
            for game in data['games']:
                if (game['winner'] == game['team1'] and game['score1'] == data['lowest_winning_score']) or \
                   (game['winner'] == game['team2'] and game['score2'] == data['lowest_winning_score']):
                    awards['lowest_winning_scores'].append({
                        'year': year,
                        'week': week,
                        'team': game['winner'],
                        'score': data['lowest_winning_score'],
                        'opponent': game['team2'] if game['winner'] == game['team1'] else game['team1'],
                        'opponent_score': game['score2'] if game['winner'] == game['team1'] else game['score1']
                    })
                    break
        
        # Find biggest margin
        for game in data['games']:
            margin = abs(game['score1'] - game['score2'])
            if margin == data['biggest_margin']:
                winner = game['team1'] if game['score1'] > game['score2'] else game['team2']
                loser = game['team2'] if game['score1'] > game['score2'] else game['team1']
                winner_score = max(game['score1'], game['score2'])
                loser_score = min(game['score1'], game['score2'])
                
                awards['biggest_margins'].append({
                    'year': year,
                    'week': week,
                    'winner': winner,
                    'loser': loser,
                    'winner_score': winner_score,
                    'loser_score': loser_score,
                    'margin': margin
                })
                break
    
    # Sort and limit
    awards['highest_scores'].sort(key=lambda x: x['score'], reverse=True)
    awards['lowest_winning_scores'].sort(key=lambda x: x['score'])
    awards['biggest_margins'].sort(key=lambda x: x['margin'], reverse=True)
    
    return {
        'highest_scores': awards['highest_scores'][:30],
        'lowest_winning_scores': awards['lowest_winning_scores'][:30],
        'biggest_margins': awards['biggest_margins'][:30]
    }


def calculate_consistency(matchups: List[Dict], normalize_team_name) -> List[Dict]:
    """Calculate consistency scores (standard deviation of weekly scores)"""
    team_scores = defaultdict(list)
    
    for matchup in matchups:
        t1 = normalize_team_name(matchup.get('team1_name', ''))
        t2 = normalize_team_name(matchup.get('team2_name', ''))
        score1 = matchup.get('team1_score', 0)
        score2 = matchup.get('team2_score', 0)
        
        if t1:
            team_scores[t1].append(score1)
        if t2:
            team_scores[t2].append(score2)
    
    consistency_scores = []
    for team, scores in team_scores.items():
        if len(scores) < 5:  # Need at least 5 games
            continue
        
        avg = sum(scores) / len(scores)
        variance = sum((x - avg) ** 2 for x in scores) / len(scores)
        std_dev = variance ** 0.5
        coefficient_of_variation = (std_dev / avg * 100) if avg > 0 else 0
        
        consistency_scores.append({
            'team': team,
            'avg_score': round(avg, 2),
            'std_dev': round(std_dev, 2),
            'coefficient_of_variation': round(coefficient_of_variation, 2),
            'games_played': len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'range': max(scores) - min(scores)
        })
    
    # Sort by coefficient of variation (lower = more consistent)
    consistency_scores.sort(key=lambda x: x['coefficient_of_variation'])
    return consistency_scores


def calculate_clutch_performance(matchups: List[Dict], normalize_team_name) -> List[Dict]:
    """Calculate clutch performance (win % in close games, defined as <10 point margin)"""
    team_close_games = defaultdict(lambda: {'wins': 0, 'losses': 0, 'ties': 0, 'total': 0})
    team_all_games = defaultdict(lambda: {'wins': 0, 'losses': 0, 'ties': 0})
    
    for matchup in matchups:
        t1 = normalize_team_name(matchup.get('team1_name', ''))
        t2 = normalize_team_name(matchup.get('team2_name', ''))
        score1 = matchup.get('team1_score', 0)
        score2 = matchup.get('team2_score', 0)
        winner = normalize_team_name(matchup.get('winner', ''))
        
        if not t1 or not t2:
            continue
        
        margin = abs(score1 - score2)
        is_close = margin < 10
        
        # Record all games
        if winner == t1:
            team_all_games[t1]['wins'] += 1
            team_all_games[t2]['losses'] += 1
        elif winner == t2:
            team_all_games[t2]['wins'] += 1
            team_all_games[t1]['losses'] += 1
        else:
            team_all_games[t1]['ties'] += 1
            team_all_games[t2]['ties'] += 1
        
        # Record close games
        if is_close:
            team_close_games[t1]['total'] += 1
            team_close_games[t2]['total'] += 1
            
            if winner == t1:
                team_close_games[t1]['wins'] += 1
                team_close_games[t2]['losses'] += 1
            elif winner == t2:
                team_close_games[t2]['wins'] += 1
                team_close_games[t1]['losses'] += 1
            else:
                team_close_games[t1]['ties'] += 1
                team_close_games[t2]['ties'] += 1
    
    clutch_scores = []
    for team in team_all_games.keys():
        close = team_close_games[team]
        all_g = team_all_games[team]
        
        if close['total'] < 5:  # Need at least 5 close games
            continue
        
        close_win_pct = ((close['wins'] + close['ties'] * 0.5) / close['total'] * 100) if close['total'] > 0 else 0
        all_win_pct = ((all_g['wins'] + all_g['ties'] * 0.5) / (all_g['wins'] + all_g['losses'] + all_g['ties']) * 100) if (all_g['wins'] + all_g['losses'] + all_g['ties']) > 0 else 0
        
        clutch_factor = close_win_pct - all_win_pct  # Positive = better in close games
        
        clutch_scores.append({
            'team': team,
            'close_games': close['total'],
            'close_wins': close['wins'],
            'close_losses': close['losses'],
            'close_ties': close['ties'],
            'close_win_pct': round(close_win_pct, 1),
            'all_win_pct': round(all_win_pct, 1),
            'clutch_factor': round(clutch_factor, 1)
        })
    
    # Sort by clutch factor
    clutch_scores.sort(key=lambda x: x['clutch_factor'], reverse=True)
    return clutch_scores


def calculate_team_dna(matchups: List[Dict], standings: List[Dict], normalize_team_name) -> List[Dict]:
    """Calculate team DNA/personality profiles based on performance patterns"""
    # Get consistency data
    consistency = calculate_consistency(matchups, normalize_team_name)
    consistency_dict = {c['team']: c for c in consistency}
    
    # Get clutch data
    clutch = calculate_clutch_performance(matchups, normalize_team_name)
    clutch_dict = {c['team']: c for c in clutch}
    
    # Get playoff/championship data
    from standings_scraper import load_standings_from_csv
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    final_standings_file = os.path.join(data_dir, 'standings_final.csv')
    final_standings = load_standings_from_csv(final_standings_file, 'final')
    
    team_championships = defaultdict(int)
    team_playoff_appearances = defaultdict(int)
    team_seasons = defaultdict(int)
    
    for standing in final_standings:
        if standing.get('year', 0) > 2024:  # Exclude incomplete seasons
            continue
        team = normalize_team_name(standing.get('team_name', ''))
        place = standing.get('place', 0)
        team_seasons[team] += 1
        if place == 1:
            team_championships[team] += 1
        if place <= 4:
            team_playoff_appearances[team] += 1
    
    # Calculate team DNA
    team_dna = []
    all_teams = set(consistency_dict.keys()) | set(clutch_dict.keys()) | set(team_seasons.keys())
    
    for team in all_teams:
        cons = consistency_dict.get(team, {})
        clu = clutch_dict.get(team, {})
        
        # Determine personality traits
        traits = []
        personality = "Balanced"
        
        # Consistency analysis
        if cons:
            cv = cons.get('coefficient_of_variation', 50)
            if cv < 15:
                traits.append("Steady Eddie")
                personality = "Consistent Contender"
            elif cv > 25:
                traits.append("Boom or Bust")
                personality = "High Risk, High Reward"
        
        # Clutch analysis
        if clu:
            clutch_factor = clu.get('clutch_factor', 0)
            if clutch_factor > 10:
                traits.append("Clutch Performer")
            elif clutch_factor < -10:
                traits.append("Chokes Under Pressure")
        
        # Championship analysis
        championships = team_championships.get(team, 0)
        playoff_apps = team_playoff_appearances.get(team, 0)
        seasons = team_seasons.get(team, 0)
        
        if seasons > 0:
            playoff_rate = (playoff_apps / seasons * 100) if seasons > 0 else 0
            if playoff_rate > 70 and championships == 0:
                traits.append("Regular Season Hero")
                personality = "Playoff Underachiever"
            elif championships > 0 and playoff_rate < 30:
                traits.append("Spoiler Specialist")
        
        if not traits:
            traits = ["Balanced"]
        
        team_dna.append({
            'team': team,
            'personality': personality,
            'traits': traits,
            'consistency': cons,
            'clutch': clu,
            'championships': championships,
            'playoff_appearances': playoff_apps,
            'seasons': seasons,
            'playoff_rate': round(playoff_rate, 1) if seasons > 0 else 0
        })
    
    return team_dna


def calculate_trophy_case(matchups: List[Dict], standings: List[Dict], normalize_team_name) -> Dict:
    """Calculate trophy case achievements for each team"""
    # Load final standings for championships
    from standings_scraper import load_standings_from_csv
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    final_standings_file = os.path.join(data_dir, 'standings_final.csv')
    final_standings = load_standings_from_csv(final_standings_file, 'final')
    
    # Organize achievements by team
    trophies = defaultdict(lambda: {
        'championships': [],
        'playoff_appearances': [],
        'spoons': [],
        'highest_weekly_score': {'score': 0, 'year': 0, 'week': 0},
        'perfect_seasons': [],
        'longest_win_streak': 0,
        'scoring_titles': []
    })
    
    # Championships, playoffs, spoons
    for standing in final_standings:
        if standing.get('year', 0) > 2024:
            continue
        team = normalize_team_name(standing.get('team_name', ''))
        year = standing.get('year', 0)
        place = standing.get('place', 0)
        
        if place == 1:
            trophies[team]['championships'].append(year)
        if place <= 4:
            trophies[team]['playoff_appearances'].append(year)
        if place == 12:
            trophies[team]['spoons'].append(year)
    
    # Highest weekly scores
    for matchup in matchups:
        t1 = normalize_team_name(matchup.get('team1_name', ''))
        t2 = normalize_team_name(matchup.get('team2_name', ''))
        score1 = matchup.get('team1_score', 0)
        score2 = matchup.get('team2_score', 0)
        year = matchup.get('year', 0)
        week = matchup.get('week', 0)
        
        if score1 > trophies[t1]['highest_weekly_score']['score']:
            trophies[t1]['highest_weekly_score'] = {'score': score1, 'year': year, 'week': week}
        if score2 > trophies[t2]['highest_weekly_score']['score']:
            trophies[t2]['highest_weekly_score'] = {'score': score2, 'year': year, 'week': week}
    
    # Calculate longest win streaks inline
    team_games = defaultdict(lambda: defaultdict(list))
    for matchup in matchups:
        t1 = normalize_team_name(matchup.get('team1_name', ''))
        t2 = normalize_team_name(matchup.get('team2_name', ''))
        winner = normalize_team_name(matchup.get('winner', ''))
        year = matchup.get('year', 0)
        week = matchup.get('week', 0)
        
        if t1:
            team_games[t1][(year, week)] = {'won': winner == t1, 'tie': winner.lower() == 'tie'}
        if t2:
            team_games[t2][(year, week)] = {'won': winner == t2, 'tie': winner.lower() == 'tie'}
    
    for team, games_dict in team_games.items():
        sorted_games = sorted(games_dict.items(), key=lambda x: (x[0][0], x[0][1]))
        current_streak = 0
        current_type = None
        max_streak = 0
        
        for (year, week), game in sorted_games:
            if game['tie']:
                if current_type == 'win' and current_streak > max_streak:
                    max_streak = current_streak
                current_streak = 0
                current_type = None
                continue
            
            if current_type is None:
                current_type = 'win' if game['won'] else 'loss'
                current_streak = 1
            elif (game['won'] and current_type == 'win') or (not game['won'] and current_type == 'loss'):
                current_streak += 1
            else:
                if current_type == 'win' and current_streak > max_streak:
                    max_streak = current_streak
                current_type = 'win' if game['won'] else 'loss'
                current_streak = 1
        
        if current_type == 'win' and current_streak > max_streak:
            max_streak = current_streak
        
        if max_streak > trophies[team]['longest_win_streak']:
            trophies[team]['longest_win_streak'] = max_streak
    
    # Perfect seasons (need to check regular season records)
    regular_standings_file = os.path.join(data_dir, 'standings.csv')
    regular_standings = load_standings_from_csv(regular_standings_file, 'regular')
    for standing in regular_standings:
        if standing.get('year', 0) > 2024:
            continue
        team = normalize_team_name(standing.get('team_name', ''))
        year = standing.get('year', 0)
        wins = standing.get('wins', 0)
        losses = standing.get('losses', 0)
        if losses == 0 and wins >= 10:  # Perfect or near-perfect regular season
            trophies[team]['perfect_seasons'].append(year)
    
    # Scoring titles (highest points for in a season)
    from collections import defaultdict as dd
    season_points = dd(lambda: dd(float))
    for standing in regular_standings:
        if standing.get('year', 0) > 2024:
            continue
        team = normalize_team_name(standing.get('team_name', ''))
        year = standing.get('year', 0)
        points = standing.get('points_for', 0)
        season_points[year][team] = points
    
    for year, teams in season_points.items():
        if teams:
            max_points = max(teams.values())
            for team, points in teams.items():
                if points == max_points:
                    trophies[team]['scoring_titles'].append(year)
    
    # Format for frontend
    formatted_trophies = {}
    for team, data in trophies.items():
        formatted_trophies[team] = {
            'championships': sorted(data['championships'], reverse=True),
            'playoff_appearances': sorted(data['playoff_appearances'], reverse=True),
            'spoons': sorted(data['spoons'], reverse=True),
            'highest_weekly_score': data['highest_weekly_score'],
            'perfect_seasons': sorted(data['perfect_seasons'], reverse=True),
            'longest_win_streak': data['longest_win_streak'],
            'scoring_titles': sorted(data['scoring_titles'], reverse=True)
        }
    
    return formatted_trophies


def calculate_points_trends(matchups: List[Dict], normalize_team_name) -> Dict:
    """Calculate points trends over time for each team"""
    team_yearly_scores = defaultdict(lambda: defaultdict(list))
    
    for matchup in matchups:
        year = matchup.get('year', 0)
        if year > 2024:  # Only historical
            continue
        
        t1 = normalize_team_name(matchup.get('team1_name', ''))
        t2 = normalize_team_name(matchup.get('team2_name', ''))
        score1 = matchup.get('team1_score', 0)
        score2 = matchup.get('team2_score', 0)
        
        if t1:
            team_yearly_scores[t1][year].append(score1)
        if t2:
            team_yearly_scores[t2][year].append(score2)
    
    trends = {}
    for team, yearly_scores in team_yearly_scores.items():
        yearly_avgs = []
        for year in sorted(yearly_scores.keys()):
            scores = yearly_scores[year]
            if scores:
                yearly_avgs.append({
                    'year': year,
                    'avg_score': round(sum(scores) / len(scores), 2),
                    'games': len(scores),
                    'total_points': sum(scores)
                })
        
        # Calculate trend (improving, declining, stable)
        if len(yearly_avgs) >= 3:
            recent_avg = sum([y['avg_score'] for y in yearly_avgs[-3:]]) / 3
            older_avg = sum([y['avg_score'] for y in yearly_avgs[:3]]) / 3 if len(yearly_avgs) >= 6 else yearly_avgs[0]['avg_score']
            trend_direction = 'improving' if recent_avg > older_avg else 'declining' if recent_avg < older_avg else 'stable'
        else:
            trend_direction = 'stable'
        
        trends[team] = {
            'yearly_averages': yearly_avgs,
            'trend': trend_direction,
            'current_avg': yearly_avgs[-1]['avg_score'] if yearly_avgs else 0,
            'overall_avg': round(sum([y['avg_score'] for y in yearly_avgs]) / len(yearly_avgs), 2) if yearly_avgs else 0
        }
    
    return trends


def calculate_playoff_probability_over_time(standings: List[Dict], current_year: int = 2025) -> Dict:
    """Calculate how playoff probability changed week-by-week for current season"""
    # This would require week-by-week standings data
    # For now, return placeholder structure
    return {
        'message': 'Week-by-week playoff probability requires additional data collection'
    }


def calculate_matchup_difficulty(standings: List[Dict], matchups: List[Dict], normalize_team_name, current_year: int = 2025) -> List[Dict]:
    """Calculate strength of schedule / matchup difficulty for current season"""
    # Get current season standings to determine team strength
    current_standings = [s for s in standings if s.get('year') == current_year]
    team_strength = {}
    for s in current_standings:
        team = normalize_team_name(s.get('team_name', ''))
        wins = s.get('wins', 0)
        losses = s.get('losses', 0)
        win_pct = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0
        team_strength[team] = win_pct
    
    # Get current season matchups
    current_matchups = [m for m in matchups if m.get('year') == current_year]
    
    # Calculate difficulty for each team
    team_difficulty = defaultdict(lambda: {'opponents': [], 'avg_opponent_win_pct': 0})
    
    for matchup in current_matchups:
        t1 = normalize_team_name(matchup.get('team1_name', ''))
        t2 = normalize_team_name(matchup.get('team2_name', ''))
        
        if t1 in team_strength and t2 in team_strength:
            team_difficulty[t1]['opponents'].append(team_strength[t2])
            team_difficulty[t2]['opponents'].append(team_strength[t1])
    
    difficulty_scores = []
    for team, data in team_difficulty.items():
        if data['opponents']:
            avg_opp_win_pct = sum(data['opponents']) / len(data['opponents'])
            data['avg_opponent_win_pct'] = round(avg_opp_win_pct, 1)
            difficulty_scores.append({
                'team': team,
                'avg_opponent_win_pct': avg_opp_win_pct,
                'opponents_faced': len(data['opponents']),
                'difficulty_rating': 'Hard' if avg_opp_win_pct > 55 else 'Easy' if avg_opp_win_pct < 45 else 'Average'
            })
    
    difficulty_scores.sort(key=lambda x: x['avg_opponent_win_pct'], reverse=True)
    return difficulty_scores


def generate_weekly_recap(matchups: List[Dict], standings: List[Dict], year: int, week: int, normalize_team_name) -> Dict:
    """Generate automated weekly recap"""
    week_matchups = [m for m in matchups if m.get('year') == year and m.get('week') == week]
    
    if not week_matchups:
        return {'error': f'No data found for {year} Week {week}'}
    
    # Find highest score
    highest_score = 0
    highest_game = None
    for m in week_matchups:
        score1 = m.get('team1_score', 0)
        score2 = m.get('team2_score', 0)
        if score1 > highest_score:
            highest_score = score1
            highest_game = {'team': normalize_team_name(m.get('team1_name', '')), 'score': score1, 'opponent': normalize_team_name(m.get('team2_name', '')), 'opponent_score': score2}
        if score2 > highest_score:
            highest_score = score2
            highest_game = {'team': normalize_team_name(m.get('team2_name', '')), 'score': score2, 'opponent': normalize_team_name(m.get('team1_name', '')), 'opponent_score': score1}
    
    # Find biggest blowout
    biggest_blowout = None
    biggest_margin = 0
    for m in week_matchups:
        margin = abs(m.get('team1_score', 0) - m.get('team2_score', 0))
        if margin > biggest_margin:
            biggest_margin = margin
            winner = normalize_team_name(m.get('winner', ''))
            t1 = normalize_team_name(m.get('team1_name', ''))
            t2 = normalize_team_name(m.get('team2_name', ''))
            if winner == t1:
                biggest_blowout = {'winner': t1, 'loser': t2, 'winner_score': m.get('team1_score', 0), 'loser_score': m.get('team2_score', 0), 'margin': margin}
            else:
                biggest_blowout = {'winner': t2, 'loser': t1, 'winner_score': m.get('team2_score', 0), 'loser_score': m.get('team1_score', 0), 'margin': margin}
    
    # Find closest game
    closest_game = None
    closest_margin = float('inf')
    for m in week_matchups:
        margin = abs(m.get('team1_score', 0) - m.get('team2_score', 0))
        if margin < closest_margin and margin > 0:
            closest_margin = margin
            t1 = normalize_team_name(m.get('team1_name', ''))
            t2 = normalize_team_name(m.get('team2_name', ''))
            winner = normalize_team_name(m.get('winner', ''))
            closest_game = {'team1': t1, 'team2': t2, 'score1': m.get('team1_score', 0), 'score2': m.get('team2_score', 0), 'winner': winner, 'margin': margin}
    
    # Find upsets (team with lower win % beat team with higher win %)
    # This would require current standings data
    
    recap = {
        'year': year,
        'week': week,
        'total_games': len(week_matchups),
        'highest_score': highest_game,
        'biggest_blowout': biggest_blowout,
        'closest_game': closest_game,
        'summary': f"Week {week} of {year} featured {len(week_matchups)} matchups."
    }
    
    if highest_game:
        recap['summary'] += f" {highest_game['team']} put up the highest score of the week with {highest_game['score']:.1f} points."
    
    if biggest_blowout:
        recap['summary'] += f" {biggest_blowout['winner']} delivered the biggest blowout, winning by {biggest_blowout['margin']:.1f} points."
    
    if closest_game:
        recap['summary'] += f" The closest game was between {closest_game['team1']} and {closest_game['team2']}, decided by just {closest_game['margin']:.1f} points."
    
    return recap

