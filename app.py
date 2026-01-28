"""
FIFA World Cup Analytics Dashboard - Flask Application
Serves JSON APIs for frontend visualization.
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from data_processor import get_processor

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests


@app.route('/')
def index():
    """Serve the main dashboard page."""
    return render_template('index.html')


@app.route('/api/goals-per-worldcup')
def goals_per_worldcup():
    """
    Get goals scored in each World Cup.
    Returns: List of {year, total_goals, avg_goals_per_match, host, winner}
    
    Chart: Line chart showing goal trends over time
    Question: Are modern World Cups more defensive?
    """
    processor = get_processor()
    data = processor.get_goals_per_worldcup()
    return jsonify({
        'success': True,
        'data': data,
        'insight': 'The 1954 World Cup in Switzerland holds the record for highest goals per match (5.38), while modern tournaments average around 2.5-2.7 goals per game.'
    })


@app.route('/api/top-teams')
def top_teams():
    """
    Get top performing teams.
    Query params:
        - metric: 'wins', 'goals', 'appearances', 'titles' (default: 'wins')
        - limit: number of teams (default: 10)
    
    Chart: Bar chart showing team dominance
    Question: Which teams have dominated across World Cups?
    """
    metric = request.args.get('metric', 'wins')
    limit = int(request.args.get('limit', 10))
    
    processor = get_processor()
    data = processor.get_top_teams(metric=metric, limit=limit)
    
    insights = {
        'wins': 'Brazil leads with the most World Cup match wins, followed by Germany and Argentina.',
        'goals': 'Brazil and Germany are the highest-scoring nations in World Cup history.',
        'titles': 'Brazil holds the record with 5 World Cup titles, followed by Germany and Italy with 4 each.',
        'appearances': 'Brazil is the only team to have participated in every World Cup since 1930.'
    }
    
    return jsonify({
        'success': True,
        'data': data,
        'metric': metric,
        'insight': insights.get(metric, '')
    })


@app.route('/api/goals-by-stage')
def goals_by_stage():
    """
    Compare goal scoring between Group and Knockout stages.
    
    Chart: Grouped bar chart
    Question: Do knockout matches have fewer goals than group matches?
    """
    processor = get_processor()
    data = processor.get_goals_by_stage()
    
    overall = data['overall']
    diff = round(overall['group'] - overall['knockout'], 2)
    
    return jsonify({
        'success': True,
        'data': data,
        'insight': f"Group stage matches average {overall['group']} goals, while knockout rounds average {overall['knockout']} goals. The pressure of elimination does reduce scoring by approximately {diff} goals per match."
    })


@app.route('/api/goals-by-continent')
def goals_by_continent():
    """
    Get total goals scored by teams from each continent.
    
    Chart: Pie chart
    Question: Which continents contribute most to World Cup goals?
    """
    processor = get_processor()
    data = processor.get_goals_by_continent()
    
    top_continent = data[0] if data else {'continent': 'N/A', 'goals': 0}
    
    return jsonify({
        'success': True,
        'data': data,
        'insight': f"Europe leads with the most goals scored, followed by South America. Together, these two continents account for over 80% of all World Cup goals."
    })


@app.route('/api/team-comparison')
def team_comparison():
    """
    Compare two teams' World Cup performance.
    Query params:
        - team1: First team name (default: 'Brazil')
        - team2: Second team name (default: 'Germany')
    
    Chart: Comparative bar chart
    Question: How do specific teams compare historically?
    """
    team1 = request.args.get('team1', 'Brazil')
    team2 = request.args.get('team2', 'Germany')
    
    processor = get_processor()
    data = processor.get_team_comparison(team1, team2)
    
    t1, t2 = data['team1'], data['team2']
    h2h = data['head_to_head']
    
    return jsonify({
        'success': True,
        'data': data,
        'insight': f"{t1['team']} has {t1['titles']} World Cup titles vs {t2['team']}'s {t2['titles']}. In head-to-head meetings ({h2h['matches']} matches), {t1['team']} has won {h2h['team1_wins']} times and {t2['team']} has won {h2h['team2_wins']} times."
    })


@app.route('/api/matches-per-year')
def matches_per_year():
    """
    Get match count and goals per World Cup year.
    
    Chart: Bar/Line combo chart
    """
    processor = get_processor()
    data = processor.get_matches_per_year()
    
    return jsonify({
        'success': True,
        'data': data,
        'insight': 'The tournament has grown from 17-18 matches in the 1930s to 64 matches since 1998, with 2026 expanding to 104 matches.'
    })


@app.route('/api/available-teams')
def available_teams():
    """Get list of all teams that have participated in World Cups."""
    processor = get_processor()
    
    # Get unique teams from matches
    home_teams = set(processor.matches['home_team'].unique())
    away_teams = set(processor.matches['away_team'].unique())
    all_teams = sorted(home_teams.union(away_teams))
    
    return jsonify({
        'success': True,
        'data': all_teams
    })


if __name__ == '__main__':
    print("🏆 FIFA World Cup Analytics Dashboard")
    print("=" * 40)
    print("Starting server at http://localhost:5001")
    print("API endpoints:")
    print("  GET /api/goals-per-worldcup")
    print("  GET /api/top-teams?metric=wins&limit=10")
    print("  GET /api/goals-by-stage")
    print("  GET /api/goals-by-continent")
    print("  GET /api/team-comparison?team1=Brazil&team2=Germany")
    print("  GET /api/matches-per-year")
    print("  GET /api/available-teams")
    print("=" * 40)
    app.run(debug=True, port=5001)
