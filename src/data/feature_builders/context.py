"""
Context Features
Environmental and game context features (weather, venue, rest)

These features capture external factors that may influence play calling,
such as poor weather favoring run plays or short rest leading to simpler play calls.
"""

import polars as pl


def add_context_features(pbp: pl.DataFrame, schedules: pl.DataFrame = None) -> pl.DataFrame:
    """
    Add environmental and contextual features from schedules data.

    Features include:
    - Venue type (outdoor, dome, retractable)
    - Weather conditions (temperature, wind)
    - Surface type (grass vs. turf)
    - Division game indicator
    - Team rest days

    Args:
        pbp: Play-by-play DataFrame
        schedules: Schedules DataFrame (optional, will be joined if provided)

    Returns:
        DataFrame with context features added
    """

    if schedules is not None:
        # Join with schedules for environmental data
        game_context = schedules.select([
            'game_id', 'roof', 'surface', 'temp', 'wind',
            'away_rest', 'home_rest', 'div_game'
        ])
        pbp = pbp.join(game_context, on='game_id', how='left')

    # Create context features
    pbp = pbp.with_columns([
        # Venue type
        (pl.col('roof') == 'outdoors')
            .fill_null(False)
            .cast(pl.Int32)
            .alias('context_outdoor'),

        (pl.col('roof') == 'dome')
            .fill_null(False)
            .cast(pl.Int32)
            .alias('context_dome'),

        # Weather conditions
        pl.col('temp').alias('context_temperature'),
        pl.col('wind').alias('context_wind'),

        (pl.col('temp') < 40)
            .fill_null(False)
            .cast(pl.Int32)
            .alias('context_cold_weather'),

        (pl.col('wind') > 15)
            .fill_null(False)
            .cast(pl.Int32)
            .alias('context_high_wind'),

        # Surface type
        (pl.col('surface') == 'grass')
            .fill_null(False)
            .cast(pl.Int32)
            .alias('context_grass'),

        # Division game (higher intensity, more conservative?)
        pl.col('div_game')
            .fill_null(False)
            .cast(pl.Int32)
            .alias('context_division_game'),

        # Team rest days (fatigue at game level)
        pl.when(pl.col('posteam_type') == 'home')
            .then(pl.col('home_rest'))
            .otherwise(pl.col('away_rest'))
            .alias('context_team_rest_days')
    ])

    return pbp
