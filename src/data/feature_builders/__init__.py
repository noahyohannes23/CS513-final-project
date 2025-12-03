"""
Feature Builders Package
Modular feature engineering for NFL play prediction

Each module contains functions to generate specific feature categories:
- team_tendencies: Historical team pass/run tendencies by situation
- momentum: Rolling drive and game momentum indicators
- fatigue: Tempo and snap count fatigue indicators
- personnel: Defensive alignment and personnel groupings
- context: Weather, venue, and game context features
- player_performance: Individual player efficiency and hot-hand features
- situational: Basic situational flags (red zone, third down, etc.)
"""

from .team_tendencies import add_team_tendency_features
from .momentum import add_momentum_features
from .fatigue import add_fatigue_features
from .personnel import add_personnel_features
from .context import add_context_features
from .player_performance import add_player_performance_features
from .situational import add_situational_features

__all__ = [
    'add_team_tendency_features',
    'add_momentum_features',
    'add_fatigue_features',
    'add_personnel_features',
    'add_context_features',
    'add_player_performance_features',
    'add_situational_features',
]
