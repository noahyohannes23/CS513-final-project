"""
Momentum Features
Rolling drive and recent play success indicators

These features capture "hot hand" effects and drive momentum that might
influence play calling decisions.

CRITICAL FIX (2025-12-10): All features now use .shift(1) to exclude the current play
from rolling windows and cumulative statistics. This prevents look-ahead bias since EPA
and yards are only known AFTER the play executes.
"""

import polars as pl


def add_momentum_features(pbp: pl.DataFrame) -> pl.DataFrame:
    """
    Add momentum features based on recent play success and drive performance.

    Features include:
    - Success rate in last 3 plays (within drive, EXCLUDING current play)
    - EPA in last 3 plays (EXCLUDING current play)
    - Explosive plays (10+ yards) in last 5 plays (EXCLUDING current play)
    - Drive statistics (total yards, play count, first downs, EPA - all EXCLUDING current play)
    - Yards per play on current drive (EXCLUDING current play)

    CRITICAL: All features use .shift(1) to exclude the current play, preventing look-ahead bias.
    This ensures we only use information knowable BEFORE the current play executes.

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
    # CRITICAL: Shift by 1 to exclude current play (prevents look-ahead bias)
    pbp = pbp.with_columns([
        # Success rate in last 3 plays (within drive)
        pl.col('play_success')
            .shift(1)  # Exclude current play
            .rolling_mean(window_size=3, min_periods=1)
            .over(['game_id', 'drive'])
            .alias('momentum_success_last_3'),

        # EPA in last 3 plays
        pl.col('epa')
            .shift(1)  # Exclude current play
            .rolling_mean(window_size=3, min_periods=1)
            .over(['game_id', 'drive'])
            .alias('momentum_epa_last_3'),

        # Explosive plays in last 5 plays
        pl.col('explosive_play')
            .shift(1)  # Exclude current play
            .rolling_sum(window_size=5, min_periods=1)
            .over(['game_id', 'drive'])
            .alias('momentum_explosive_last_5'),
    ])

    # Drive-level cumulative statistics
    # CRITICAL: Shift by 1 to exclude current play (prevents look-ahead bias)
    pbp = pbp.with_columns([
        # Total yards on current drive (cumulative, excluding current play)
        pl.col('yards_gained')
            .shift(1)  # Exclude current play
            .cum_sum()
            .over(['game_id', 'drive'])
            .alias('drive_total_yards'),

        # Number of plays on current drive (excluding current play)
        pl.lit(1)
            .shift(1)  # Exclude current play
            .cum_sum()
            .over(['game_id', 'drive'])
            .alias('drive_play_count'),

        # First downs on current drive (cumulative, excluding current play)
        (pl.col('first_down_rush').fill_null(0) + pl.col('first_down_pass').fill_null(0))
            .shift(1)  # Exclude current play
            .cum_sum()
            .over(['game_id', 'drive'])
            .alias('drive_first_downs'),

        # Drive EPA (cumulative, excluding current play)
        pl.col('epa')
            .shift(1)  # Exclude current play
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
