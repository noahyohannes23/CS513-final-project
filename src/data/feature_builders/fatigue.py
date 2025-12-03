"""
Fatigue Features
Tempo and snap count indicators that may influence play calling

High tempo and accumulated snaps can impact defensive performance,
potentially leading to defensive adjustments or offensive exploitation.
"""

import polars as pl


def add_fatigue_features(pbp: pl.DataFrame) -> pl.DataFrame:
    """
    Add fatigue-related features: tempo, snap counts, and pace indicators.

    Features include:
    - Seconds since last play (tempo indicator)
    - Fast tempo flag (< 20 seconds between plays)
    - Total offensive snaps so far in game
    - Recent play count (rolling 10-play window)
    - No-huddle indicator
    - Shotgun formation (tempo-related)

    NOTE: Data must be sorted by ['game_id', 'play_id'] before calling.

    Args:
        pbp: Play-by-play DataFrame

    Returns:
        DataFrame with fatigue features added
    """

    # Ensure proper sorting
    pbp = pbp.sort(['game_id', 'play_id'])

    pbp = pbp.with_columns([
        # Time since last play (tempo indicator)
        pl.col('game_seconds_remaining')
            .diff()
            .abs()
            .over(['game_id'])
            .alias('seconds_since_last_play'),

        # Total offensive snaps so far in game
        pl.lit(1)
            .cum_sum()
            .over(['game_id', 'posteam'])
            .alias('fatigue_total_offensive_snaps'),

        # Plays in last 10 plays (rolling window)
        pl.lit(1)
            .rolling_sum(window_size=10, min_periods=1)
            .over(['game_id', 'posteam'])
            .alias('fatigue_plays_last_10'),

        # No-huddle indicator (already in data)
        pl.col('no_huddle').cast(pl.Int32).alias('fatigue_no_huddle'),

        # Shotgun formation (also tempo-related)
        pl.col('shotgun').cast(pl.Int32).alias('formation_shotgun')
    ])

    # Fast tempo indicator (< 20 seconds since last play)
    pbp = pbp.with_columns([
        (pl.col('seconds_since_last_play') < 20)
            .fill_null(False)
            .cast(pl.Int32)
            .alias('fatigue_fast_tempo')
    ])

    return pbp
