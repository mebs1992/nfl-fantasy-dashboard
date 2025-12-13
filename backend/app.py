"""
Flask API server for NFL Fantasy Dashboard
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from scraper import scrape_league_data
from data_manager import DataManager

# Get the project root directory (parent of backend/)
if os.path.basename(os.getcwd()) == 'backend':
    project_root = os.path.dirname(os.getcwd())
else:
    project_root = os.getcwd()

app = Flask(__name__)

# Configure CORS - allow requests from frontend
# For production, allow all origins (since we don't know the exact Vercel URL)
# In production, we'll allow the Vercel domain
frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3010')
is_production = os.getenv('FLASK_ENV') == 'production'

if is_production:
    # In production, allow Vercel and common origins
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "https://nfl-fantasy-dashboard-one.vercel.app",
                "https://*.vercel.app",  # Allow all Vercel preview deployments
                frontend_url
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "supports_credentials": False
        }
    })
else:
    # In development, allow localhost
    CORS(app, resources={
        r"/api/*": {
            "origins": [frontend_url, "http://localhost:3010", "http://localhost:3000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

# Initialize data manager with project root path
data_manager = DataManager(data_dir=os.path.join(project_root, 'data'))

LEAGUE_ID = "987449"  # The Greatest League


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/standings', methods=['GET'])
def get_standings():
    """Get current league standings (2025 season) - uses regular season"""
    try:
        from standings_scraper import load_standings_from_csv
        from team_mapper import normalize_team_name
        
        # Get data directory path
        data_dir = data_manager.data_dir
        csv_file = os.path.join(data_dir, 'standings.csv')
        # Use regular season standings for current season stats
        all_standings = load_standings_from_csv(csv_file, 'regular')
        
        # Filter for 2025 season only
        standings_2025 = [s for s in all_standings if s['year'] == 2025]
        
        # Get team logos
        from team_logos import get_team_logo_url
        
        # Normalize team names and format for frontend
        formatted_standings = []
        for s in standings_2025:
            team_name = normalize_team_name(s['team_name'])
            formatted_standings.append({
                'id': f"{s['year']}_{s['place']}",
                'name': team_name,
                'wins': s.get('wins', 0),
                'losses': s.get('losses', 0),
                'ties': s.get('ties', 0),
                'points_for': s.get('points_for', 0.0),
                'points_against': s.get('points_against', 0.0),
                'place': s['place'],
                'logo': s.get('team_logo') or get_team_logo_url(team_name, data_dir)
            })
        
        # Sort by place
        formatted_standings.sort(key=lambda x: x['place'])
        
        return jsonify({
            'success': True,
            'data': formatted_standings,
            'year': 2025
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/playoff-scenarios', methods=['GET'])
def get_playoff_scenarios():
    """Get playoff scenarios for current season"""
    try:
        from standings_scraper import load_standings_from_csv
        from team_mapper import normalize_team_name
        from historical_scraper import load_from_csv
        from playoff_calculator import calculate_playoff_scenarios
        
        # Get data directory path
        data_dir = data_manager.data_dir
        
        # Get 2025 standings
        csv_file = os.path.join(data_dir, 'standings.csv')
        all_standings = load_standings_from_csv(csv_file, 'regular')
        standings_2025 = [s for s in all_standings if s['year'] == 2025]
        
        # Format standings for calculator
        formatted_standings = []
        for s in standings_2025:
            formatted_standings.append({
                'team': normalize_team_name(s['team_name']),
                'wins': s.get('wins', 0),
                'losses': s.get('losses', 0),
                'points_for': s.get('points_for', 0.0)
            })
        
        # Get Week 15 matchups
        matchups_file = os.path.join(data_dir, 'matchups.csv')
        all_matchups = load_from_csv(matchups_file)
        week15_matchups = [m for m in all_matchups if m.get('year') == 2025 and m.get('week') == 15]
        
        # Calculate scenarios
        scenarios = calculate_playoff_scenarios(formatted_standings, week15_matchups)
        
        return jsonify({
            'success': True,
            'data': scenarios
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/head-to-head', methods=['GET'])
def get_head_to_head():
    """Get all-time head-to-head statistics"""
    try:
        team1 = request.args.get('team1')
        team2 = request.args.get('team2')
        
        if team1 and team2:
            # Get specific head-to-head
            h2h = data_manager.get_head_to_head(team1, team2)
            return jsonify({'success': True, 'data': h2h})
        else:
            # Get all head-to-head stats
            all_h2h = data_manager.get_all_head_to_head()
            return jsonify({'success': True, 'data': all_h2h})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/team-stats', methods=['GET'])
def get_team_stats():
    """Get comprehensive stats for a team"""
    try:
        team_id = request.args.get('team_id')
        team_name = request.args.get('team_name')
        
        if not team_id and not team_name:
            return jsonify({'success': False, 'error': 'team_id or team_name required'}), 400
        
        stats = data_manager.get_team_stats(team_id=team_id, team_name=team_name)
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/matchups', methods=['GET'])
def get_matchups():
    """Get weekly matchups"""
    try:
        week = request.args.get('week', type=int)
        matchups = data_manager.get_matchups(week=week)
        return jsonify({'success': True, 'data': matchups})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get recent transactions"""
    try:
        limit = request.args.get('limit', type=int, default=50)
        transactions = data_manager.get_transactions(limit=limit)
        return jsonify({'success': True, 'data': transactions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Manually trigger data refresh from NFL.com - only scrapes new weeks"""
    try:
        # Refresh current standings
        new_data = scrape_league_data(LEAGUE_ID)
        data_manager.update_data(new_data)
        
        # Import only new weeks for current season
        from import_historical import import_current_season
        import_current_season(LEAGUE_ID, year=2025, max_week=17, force=False)
        
        # Sync CSV to data manager
        from import_historical import sync_csv_to_data_manager
        sync_csv_to_data_manager()
        
        return jsonify({
            'success': True,
            'message': 'Data refreshed successfully (only new weeks scraped)',
            'updated_at': data_manager.get_last_update()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/league-info', methods=['GET'])
def get_league_info():
    """Get general league information"""
    try:
        info = data_manager.get_league_info()
        return jsonify({'success': True, 'data': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Get list of all unique team names (canonical/current names)"""
    try:
        from team_mapper import normalize_team_name, get_all_canonical_teams
        
        # Get teams from standings first (current names)
        standings = data_manager.get_standings()
        teams = [t.get('name') for t in standings if t.get('name')]
        
        # If no standings, get from matchups and normalize
        if not teams:
            matchups = data_manager.get_matchups()
            teams_set = set()
            for m in matchups:
                t1 = m.get('team1_name')
                t2 = m.get('team2_name')
                if t1:
                    teams_set.add(normalize_team_name(t1))
                if t2:
                    teams_set.add(normalize_team_name(t2))
            teams = sorted(list(teams_set))
        else:
            # Normalize team names to canonical forms
            teams = [normalize_team_name(t) for t in teams]
            teams = sorted(list(set(teams)))  # Remove duplicates
        
        return jsonify({'success': True, 'data': teams})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/import-historical', methods=['POST'])
def import_historical():
    """Import historical data from 2017-2024"""
    try:
        from import_historical import import_historical_data
        
        # This is a long-running operation, so we'll run it in the background
        # For now, just trigger it synchronously (could be improved with threading)
        start_year = request.json.get('start_year', 2017) if request.json else 2017
        end_year = request.json.get('end_year', 2024) if request.json else 2024
        
        import_historical_data(LEAGUE_ID, start_year, end_year)
        
        return jsonify({
            'success': True,
            'message': f'Historical data imported successfully for years {start_year}-{end_year}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/historical-standings', methods=['GET'])
def get_historical_standings():
    """Get historical standings data"""
    try:
        from standings_scraper import load_standings_from_csv
        from team_mapper import normalize_team_name
        
        # Get data directory path
        data_dir = data_manager.data_dir
        csv_file = os.path.join(data_dir, 'standings.csv')
        standings = load_standings_from_csv(csv_file)
        
        # Normalize team names
        for s in standings:
            s['team_name'] = normalize_team_name(s['team_name'])
        
        return jsonify({'success': True, 'data': standings})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/historical-stats', methods=['GET'])
def get_historical_stats():
    """Get aggregated historical statistics (Super Bowls, Playoffs, Spoons) - uses final standings"""
    try:
        from standings_scraper import load_standings_from_csv
        from team_mapper import normalize_team_name
        from collections import defaultdict
        
        # Get data directory path
        data_dir = data_manager.data_dir
        csv_file = os.path.join(data_dir, 'standings.csv')
        # Use final standings for championships and spoons
        standings = load_standings_from_csv(csv_file, 'final')
        
        # Get team logos
        from team_logos import get_team_logo_url
        
        # Normalize team names and aggregate with years
        super_bowls = defaultdict(lambda: {'count': 0, 'years': []})  # 1st place
        playoffs = defaultdict(lambda: {'count': 0, 'years': []})     # 1st-4th place
        spoons = defaultdict(lambda: {'count': 0, 'years': []})       # 12th place (last place)
        
        for s in standings:
            team_name = normalize_team_name(s['team_name'])
            place = s['place']
            year = s['year']
            
            # Only count 2017-2024 (exclude 2025 as season isn't over)
            if year <= 2024:
                if place == 1:
                    super_bowls[team_name]['count'] += 1
                    super_bowls[team_name]['years'].append(year)
                    playoffs[team_name]['count'] += 1
                    playoffs[team_name]['years'].append(year)
                elif place <= 4:
                    playoffs[team_name]['count'] += 1
                    playoffs[team_name]['years'].append(year)
                elif place == 12:  # Last place (Spoon)
                    spoons[team_name]['count'] += 1
                    spoons[team_name]['years'].append(year)
        
        # Sort years for each team and add logos
        for team_name in super_bowls.keys():
            super_bowls[team_name]['years'].sort()
            super_bowls[team_name]['logo'] = get_team_logo_url(team_name, data_dir)
        for team_name in playoffs.keys():
            playoffs[team_name]['years'].sort()
            playoffs[team_name]['logo'] = get_team_logo_url(team_name, data_dir)
        for team_name in spoons.keys():
            spoons[team_name]['years'].sort()
            spoons[team_name]['logo'] = get_team_logo_url(team_name, data_dir)
        
        return jsonify({
            'success': True,
            'data': {
                'super_bowls': {k: {'count': v['count'], 'years': v['years'], 'logo': v.get('logo', '')} for k, v in super_bowls.items()},
                'playoffs': {k: {'count': v['count'], 'years': v['years'], 'logo': v.get('logo', '')} for k, v in playoffs.items()},
                'spoons': {k: {'count': v['count'], 'years': v['years'], 'logo': v.get('logo', '')} for k, v in spoons.items()}
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/team-stats-all-time', methods=['GET'])
def get_team_stats_all_time():
    """Get all-time aggregated team statistics (points scored, win %, points against) - uses regular season"""
    try:
        from standings_scraper import load_standings_from_csv
        from team_mapper import normalize_team_name
        from collections import defaultdict
        
        # Get data directory path
        data_dir = data_manager.data_dir
        csv_file = os.path.join(data_dir, 'standings.csv')
        # Use regular season standings for stats (points, win %)
        standings = load_standings_from_csv(csv_file, 'regular')
        
        # Aggregate stats by team (normalized names)
        team_stats = defaultdict(lambda: {
            'total_points_for': 0.0,
            'total_points_against': 0.0,
            'total_wins': 0,
            'total_losses': 0,
            'total_ties': 0,
            'seasons': 0
        })
        
        for s in standings:
            team_name = normalize_team_name(s['team_name'])
            year = s['year']
            
            # Only count completed seasons (2017-2024)
            if year <= 2024:
                stats = team_stats[team_name]
                stats['total_points_for'] += s.get('points_for', 0.0)
                stats['total_points_against'] += s.get('points_against', 0.0)
                stats['total_wins'] += s.get('wins', 0)
                stats['total_losses'] += s.get('losses', 0)
                stats['total_ties'] += s.get('ties', 0)
                stats['seasons'] += 1
        
        # Get team logos
        from team_logos import get_team_logo_url
        
        # Calculate all-time win percentage and prepare data
        result = {
            'most_points_scored': [],
            'highest_win_pct': [],
            'most_points_against': []
        }
        
        for team_name, stats in team_stats.items():
            total_games = stats['total_wins'] + stats['total_losses'] + stats['total_ties']
            # Calculate win percentage as a percentage (0-100)
            win_pct = (stats['total_wins'] / total_games * 100) if total_games > 0 else 0.0
            
            team_logo = get_team_logo_url(team_name, data_dir)
            
            result['most_points_scored'].append({
                'team': team_name,
                'points': round(stats['total_points_for'], 2),
                'seasons': stats['seasons'],
                'logo': team_logo
            })
            
            result['highest_win_pct'].append({
                'team': team_name,
                'win_pct': round(win_pct, 2),
                'wins': stats['total_wins'],
                'losses': stats['total_losses'],
                'ties': stats['total_ties'],
                'seasons': stats['seasons'],
                'logo': team_logo
            })
            
            result['most_points_against'].append({
                'team': team_name,
                'points': round(stats['total_points_against'], 2),
                'seasons': stats['seasons'],
                'logo': team_logo
            })
        
        # Sort each category
        result['most_points_scored'].sort(key=lambda x: x['points'], reverse=True)
        result['highest_win_pct'].sort(key=lambda x: x['win_pct'], reverse=True)
        result['most_points_against'].sort(key=lambda x: x['points'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scoring-titles', methods=['GET'])
def get_scoring_titles():
    """Get scoring titles (highest points for in each season) - uses regular season"""
    try:
        from standings_scraper import load_standings_from_csv
        from team_mapper import normalize_team_name
        from collections import defaultdict
        from team_logos import get_team_logo_url
        
        # Get data directory path
        data_dir = data_manager.data_dir
        csv_file = os.path.join(data_dir, 'standings.csv')
        # Use regular season standings (has points_for data)
        standings = load_standings_from_csv(csv_file, 'regular')
        
        # Find highest points_for for each year (2017-2024 only, exclude 2025)
        scoring_titles = defaultdict(lambda: {'count': 0, 'years': []})
        
        for year in range(2017, 2025):  # 2017-2024 only
            year_standings = [s for s in standings if s['year'] == year]
            if year_standings:
                # Find team with highest points_for
                max_points_team = max(year_standings, key=lambda x: x.get('points_for', 0.0))
                team_name = normalize_team_name(max_points_team['team_name'])
                points = max_points_team.get('points_for', 0.0)
                
                scoring_titles[team_name]['count'] += 1
                scoring_titles[team_name]['years'].append({
                    'year': year,
                    'points': round(points, 2)
                })
        
        # Sort years for each team and add logos
        result = []
        for team_name, data in scoring_titles.items():
            data['years'].sort(key=lambda x: x['year'])
            data['logo'] = get_team_logo_url(team_name, data_dir)
            result.append({
                'team': team_name,
                'count': data['count'],
                'years': data['years'],
                'logo': data['logo']
            })
        
        # Sort by count (descending), then by first year
        result.sort(key=lambda x: (-x['count'], x['years'][0]['year'] if x['years'] else 9999))
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/win-pct-by-year', methods=['GET'])
def get_win_pct_by_year():
    """Get win percentage by year for each team - uses regular season"""
    try:
        from standings_scraper import load_standings_from_csv
        from team_mapper import normalize_team_name
        from collections import defaultdict
        
        # Get data directory path
        data_dir = data_manager.data_dir
        csv_file = os.path.join(data_dir, 'standings.csv')
        # Use regular season standings
        standings = load_standings_from_csv(csv_file, 'regular')
        
        # Group by year, then by team
        by_year = defaultdict(lambda: {})
        
        for s in standings:
            team_name = normalize_team_name(s['team_name'])
            year = s['year']
            
            # Only count completed seasons (2017-2024)
            if year <= 2024:
                wins = s.get('wins', 0)
                losses = s.get('losses', 0)
                ties = s.get('ties', 0)
                total_games = wins + losses + ties
                
                if total_games > 0:
                    win_pct = ((wins + ties * 0.5) / total_games) * 100
                else:
                    win_pct = 0.0
                
                by_year[year][team_name] = round(win_pct, 2)
        
        # Get all unique teams
        all_teams = set()
        for year_data in by_year.values():
            all_teams.update(year_data.keys())
        
        # Create data structure for line chart: [{year: 2017, Team1: 65.5, Team2: 72.3, ...}, ...]
        chart_data = []
        for year in sorted(by_year.keys()):
            row = {'year': year}
            for team in all_teams:
                row[team] = by_year[year].get(team, None)  # None for missing data
            chart_data.append(row)
        
        return jsonify({
            'success': True,
            'data': chart_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Load initial data if available
    data_manager.load_data()
    
    # Get port from environment variable (for Render, Railway, etc.) or default to 5000
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    print("Starting NFL Fantasy Dashboard API server...")
    print(f"League ID: {LEAGUE_ID}")
    print(f"API available at http://localhost:{port}/api")
    print(f"Debug mode: {debug}")
    app.run(debug=debug, host='0.0.0.0', port=port)

