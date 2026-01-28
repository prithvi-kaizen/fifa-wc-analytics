"""
Data processing module for FIFA World Cup Analytics Dashboard.
Handles CSV loading, data cleaning, and statistical computations.
"""

import pandas as pd
import os
from functools import lru_cache

# Team to continent mapping for goals by continent analysis
CONTINENT_MAPPING = {
    # South America
    'Brazil': 'South America', 'Argentina': 'South America', 'Uruguay': 'South America',
    'Colombia': 'South America', 'Chile': 'South America', 'Paraguay': 'South America',
    'Peru': 'South America', 'Ecuador': 'South America', 'Bolivia': 'South America',
    'Venezuela': 'South America',
    
    # Europe
    'Germany': 'Europe', 'West Germany': 'Europe', 'East Germany': 'Europe',
    'France': 'Europe', 'Italy': 'Europe', 'Spain': 'Europe', 'England': 'Europe',
    'Netherlands': 'Europe', 'Portugal': 'Europe', 'Belgium': 'Europe',
    'Croatia': 'Europe', 'Poland': 'Europe', 'Sweden': 'Europe', 'Switzerland': 'Europe',
    'Austria': 'Europe', 'Hungary': 'Europe', 'Czechoslovakia': 'Europe',
    'Yugoslavia': 'Europe', 'Soviet Union': 'Europe', 'Russia': 'Europe',
    'Ukraine': 'Europe', 'Romania': 'Europe', 'Bulgaria': 'Europe', 'Greece': 'Europe',
    'Denmark': 'Europe', 'Norway': 'Europe', 'Ireland': 'Europe', 'Northern Ireland': 'Europe',
    'Scotland': 'Europe', 'Wales': 'Europe', 'Turkey': 'Europe', 'Serbia': 'Europe',
    
    # Africa
    'Cameroon': 'Africa', 'Nigeria': 'Africa', 'Senegal': 'Africa', 'Ghana': 'Africa',
    'Morocco': 'Africa', 'Algeria': 'Africa', 'Egypt': 'Africa', 'South Africa': 'Africa',
    'Tunisia': 'Africa', 'Ivory Coast': 'Africa', 'Zaire': 'Africa',
    
    # Asia
    'South Korea': 'Asia', 'Japan': 'Asia', 'Saudi Arabia': 'Asia', 'Iran': 'Asia',
    'China': 'Asia', 'North Korea': 'Asia', 'Australia': 'Asia', 'Qatar': 'Asia',
    'Iraq': 'Asia', 'Kuwait': 'Asia', 'United Arab Emirates': 'Asia',
    'Indonesia': 'Asia', 'Dutch East Indies': 'Asia',
    
    # North/Central America & Caribbean
    'Mexico': 'North America', 'USA': 'North America', 'Costa Rica': 'North America',
    'Honduras': 'North America', 'Jamaica': 'North America', 'Canada': 'North America',
    'Cuba': 'North America', 'El Salvador': 'North America', 'Haiti': 'North America',
    'Trinidad and Tobago': 'North America', 'Panama': 'North America',
    
    # Oceania
    'New Zealand': 'Oceania'
}


class DataProcessor:
    """Handles all data operations for the World Cup dashboard."""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self._matches_df = None
        self._tournaments_df = None
    
    @property
    def matches(self):
        """Lazy load matches data."""
        if self._matches_df is None:
            self._matches_df = self._load_matches()
        return self._matches_df
    
    @property
    def tournaments(self):
        """Lazy load tournaments data."""
        if self._tournaments_df is None:
            self._tournaments_df = self._load_tournaments()
        return self._tournaments_df
    
    def _load_matches(self):
        """Load and preprocess match data."""
        path = os.path.join(self.data_dir, 'matches.csv')
        df = pd.read_csv(path)
        
        # Add computed columns
        df['total_goals'] = df['home_score'] + df['away_score']
        df['is_draw'] = df['home_score'] == df['away_score']
        
        # Determine winner
        df['winner'] = df.apply(
            lambda row: row['home_team'] if row['home_score'] > row['away_score']
            else (row['away_team'] if row['away_score'] > row['home_score'] else 'Draw'),
            axis=1
        )
        
        # Categorize stage
        df['stage_category'] = df['stage'].apply(self._categorize_stage)
        
        return df
    
    def _load_tournaments(self):
        """Load tournament summary data."""
        path = os.path.join(self.data_dir, 'tournaments.csv')
        return pd.read_csv(path)
    
    @staticmethod
    def _categorize_stage(stage):
        """Categorize match stage into Group or Knockout."""
        stage_lower = stage.lower()
        if 'group' in stage_lower:
            return 'Group'
        elif any(x in stage_lower for x in ['final', 'semi', 'quarter', 'round of', 'second round']):
            return 'Knockout'
        else:
            return 'Other'
    
    def get_goals_per_worldcup(self):
        """
        Calculate total goals and average goals per match for each World Cup.
        Used for: Line chart showing goal trends over time.
        """
        # Get goals from matches
        match_stats = self.matches.groupby('year').agg({
            'total_goals': 'sum',
            'year': 'count'
        }).rename(columns={'year': 'matches_played', 'total_goals': 'total_goals_from_matches'})
        
        # Merge with tournament data for additional context
        result = self.tournaments[['year', 'total_goals', 'total_matches', 'host', 'winner']].copy()
        result['avg_goals_per_match'] = round(result['total_goals'] / result['total_matches'], 2)
        
        return result.to_dict('records')
    
    def get_top_teams(self, metric='wins', limit=10):
        """
        Calculate top teams by various metrics.
        Used for: Bar chart showing team dominance.
        
        Args:
            metric: 'wins', 'goals', 'appearances', or 'titles'
            limit: Number of teams to return
        """
        if metric == 'titles':
            # Count World Cup titles - Pandas 3.0 compatible
            titles_series = self.tournaments['winner'].value_counts()
            titles = pd.DataFrame({
                'team': titles_series.index,
                'titles': titles_series.values
            })
            return titles.head(limit).to_dict('records')
        
        # Combine home and away team stats using explicit aggregation
        home_stats = self.matches.groupby('home_team', as_index=False).agg(
            goals=('home_score', 'sum'),
            matches=('year', 'count')
        ).rename(columns={'home_team': 'team'})
        
        away_stats = self.matches.groupby('away_team', as_index=False).agg(
            goals=('away_score', 'sum'),
            matches=('year', 'count')
        ).rename(columns={'away_team': 'team'})
        
        # Combine stats by merging and summing
        combined = pd.merge(home_stats, away_stats, on='team', how='outer', suffixes=('_home', '_away'))
        combined = combined.fillna(0)
        combined['goals'] = combined['goals_home'] + combined['goals_away']
        combined['matches'] = combined['matches_home'] + combined['matches_away']
        combined = combined[['team', 'goals', 'matches']]
        
        # Calculate wins - Pandas 3.0 compatible
        wins_series = self.matches[self.matches['winner'] != 'Draw']['winner'].value_counts()
        wins_df = pd.DataFrame({
            'team': wins_series.index,
            'wins': wins_series.values
        })
        
        combined = combined.merge(wins_df, on='team', how='left')
        combined['wins'] = combined['wins'].fillna(0).astype(int)
        combined['goals'] = combined['goals'].astype(int)
        combined['matches'] = combined['matches'].astype(int)
        
        # Sort by requested metric
        if metric == 'wins':
            result = combined.nlargest(limit, 'wins')[['team', 'wins', 'goals', 'matches']]
        elif metric == 'goals':
            result = combined.nlargest(limit, 'goals')[['team', 'goals', 'wins', 'matches']]
        else:  # appearances (matches)
            result = combined.nlargest(limit, 'matches')[['team', 'matches', 'wins', 'goals']]
        
        return result.to_dict('records')
    
    def get_goals_by_stage(self):
        """
        Compare goal scoring between Group and Knockout stages.
        Used for: Grouped bar chart answering if knockouts have fewer goals.
        """
        stage_stats = self.matches.groupby(['year', 'stage_category']).agg({
            'total_goals': ['sum', 'mean', 'count']
        }).reset_index()
        
        stage_stats.columns = ['year', 'stage', 'total_goals', 'avg_goals', 'matches']
        stage_stats['avg_goals'] = round(stage_stats['avg_goals'], 2)
        
        # Pivot for easier frontend consumption
        result = {
            'years': sorted(self.matches['year'].unique().tolist()),
            'group_avg': [],
            'knockout_avg': []
        }
        
        for year in result['years']:
            year_data = stage_stats[stage_stats['year'] == year]
            
            group_avg = year_data[year_data['stage'] == 'Group']['avg_goals'].values
            result['group_avg'].append(float(group_avg[0]) if len(group_avg) > 0 else 0)
            
            knockout_avg = year_data[year_data['stage'] == 'Knockout']['avg_goals'].values
            result['knockout_avg'].append(float(knockout_avg[0]) if len(knockout_avg) > 0 else 0)
        
        # Overall averages
        overall = self.matches.groupby('stage_category')['total_goals'].mean()
        result['overall'] = {
            'group': round(overall.get('Group', 0), 2),
            'knockout': round(overall.get('Knockout', 0), 2)
        }
        
        return result
    
    def get_goals_by_continent(self):
        """
        Calculate total goals scored by teams from each continent.
        Used for: Pie chart showing continental contribution.
        """
        goals_by_team = {}
        
        # Sum home goals
        for _, row in self.matches.iterrows():
            home_team = row['home_team']
            away_team = row['away_team']
            
            goals_by_team[home_team] = goals_by_team.get(home_team, 0) + row['home_score']
            goals_by_team[away_team] = goals_by_team.get(away_team, 0) + row['away_score']
        
        # Aggregate by continent
        continent_goals = {}
        for team, goals in goals_by_team.items():
            continent = CONTINENT_MAPPING.get(team, 'Other')
            continent_goals[continent] = continent_goals.get(continent, 0) + goals
        
        result = [
            {'continent': continent, 'goals': goals}
            for continent, goals in sorted(continent_goals.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return result
    
    def get_team_comparison(self, team1='Brazil', team2='Germany'):
        """
        Compare two teams head-to-head and overall performance.
        Used for: Comparative bar chart.
        """
        def get_team_stats(team):
            # Matches where team played
            as_home = self.matches[self.matches['home_team'] == team]
            as_away = self.matches[self.matches['away_team'] == team]
            
            total_matches = len(as_home) + len(as_away)
            total_goals = as_home['home_score'].sum() + as_away['away_score'].sum()
            goals_conceded = as_home['away_score'].sum() + as_away['home_score'].sum()
            
            # Wins
            wins = len(self.matches[(self.matches['winner'] == team)])
            
            # Titles
            titles = len(self.tournaments[self.tournaments['winner'] == team])
            
            # Finals reached
            finals = len(self.tournaments[
                (self.tournaments['winner'] == team) | 
                (self.tournaments['runner_up'] == team)
            ])
            
            return {
                'team': team,
                'matches': total_matches,
                'wins': wins,
                'goals_scored': int(total_goals),
                'goals_conceded': int(goals_conceded),
                'titles': titles,
                'finals': finals,
                'win_rate': round(wins / total_matches * 100, 1) if total_matches > 0 else 0
            }
        
        # Head to head
        h2h = self.matches[
            ((self.matches['home_team'] == team1) & (self.matches['away_team'] == team2)) |
            ((self.matches['home_team'] == team2) & (self.matches['away_team'] == team1))
        ]
        
        h2h_stats = {
            'matches': len(h2h),
            'team1_wins': len(h2h[h2h['winner'] == team1]),
            'team2_wins': len(h2h[h2h['winner'] == team2]),
            'draws': len(h2h[h2h['winner'] == 'Draw'])
        }
        
        return {
            'team1': get_team_stats(team1),
            'team2': get_team_stats(team2),
            'head_to_head': h2h_stats
        }
    
    def get_matches_per_year(self):
        """Get match count and total goals per World Cup year."""
        result = self.tournaments[['year', 'total_matches', 'total_goals', 'host', 'winner']].copy()
        return result.to_dict('records')


# Singleton instance for use across the application
_processor = None

def get_processor():
    """Get or create the data processor singleton."""
    global _processor
    if _processor is None:
        _processor = DataProcessor()
    return _processor
