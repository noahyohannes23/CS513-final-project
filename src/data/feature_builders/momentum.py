"""
Momentum Features
Rolling drive and recent play success indicators

These features capture "hot hand" effects and drive momentum that might
influence play calling decisions.
"""

import polars as pl


def add_momentum_features(pbp: pl.DataFrame) -> pl.DataFrame:
    """
    Add momentum features based on recent play success and drive performance.

    Features include:
    - Success rate in last 3 plays (within drive)
    - EPA in last 3 plays
    - Explosive plays (10+ yards) in last 5 plays
    - Drive statistics (total yards, play count, first downs, EPA)
    - Yards per play on current drive

    NOTE: Data must be sorted by ['game_id', 'play_id'] before calling.

    Args:
        pbp: Play-by-play DataFrame (must have 'game_id', 'drive', 'play_id', 'epa', 'yards_gained')

    Returns:
        DataFrame with momentum features added
    """

    # Ensure proper sorting for rolling windows
    pbp = pbp.sort(['game_id', 'play_id'])

    # Calculate success and explosive play indicators
    pbp = pbp.with_columns([
        # Success indicator (EPA > 0)
        (pl.col('epa') > 0).cast(pl.Int32).alias('play_success'),

        # Explosive play indicator (10+ yards)
        (pl.col('yards_gained') >= 10).cast(pl.Int32).alias('explosive_play')
    ])

    # Rolling momentum features over last N plays within same drive
    pbp = pbp.with_columns([
        # Success rate in last 3 plays (within drive)
        pl.col('play_success')
            .rolling_mean(window_size=3, min_periods=1)
            .over(['game_id', 'drive'])
            .alias('momentum_success_last_3'),

        # EPA in last 3 plays
        pl.col('epa')
            .rolling_mean(window_size=3, min_periods=1)
            .over(['game_id', 'drive'])
            .alias('momentum_epa_last_3'),

        # Explosive plays in last 5 plays
        pl.col('explosive_play')
            .rolling_sum(window_size=5, min_periods=1)
            .over(['game_id', 'drive'])
            .alias('momentum_explosive_last_5'),
    ])

    # Drive-level cumulative statistics
    pbp = pbp.with_columns([
        # Total yards on current drive (cumulative)
        pl.col('yards_gained')
            .cum_sum()
            .over(['game_id', 'drive'])
            .alias('drive_total_yards'),

        # Number of plays on current drive
        pl.lit(1)
            .cum_sum()
            .over(['game_id', 'drive'])
            .alias('drive_play_count'),

        # First downs on current drive (cumulative)
        (pl.col('first_down_rush').fill_null(0) + pl.col('first_down_pass').fill_null(0))
            .cum_sum()
            .over(['game_id', 'drive'])
            .alias('drive_first_downs'),

        # Drive EPA (cumulative)
        pl.col('epa')
            .cum_sum()
            .over(['game_id', 'drive'])
            .alias('drive_epa')
    ])

    # Derived drive metric
    pbp = pbp.with_columns([
        # Yards per play on current drive
        (pl.col('drive_total_yards') / pl.col('drive_play_count'))
            .alias('drive_yards_per_play')
    ])

    return pbp
