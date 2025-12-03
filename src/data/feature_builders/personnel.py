"""
Personnel Features
Defensive alignment and personnel grouping indicators

These features capture defensive setup which strongly signals
expected play type (e.g., heavy box = expecting run).
"""

import polars as pl
from pathlib import Path


def add_personnel_features(pbp: pl.DataFrame, participation: pl.DataFrame = None) -> pl.DataFrame:
    """
    Add personnel features from participation data.

    Features include:
    - Defenders in box count
    - Light box indicator (< 6 defenders)
    - Heavy box indicator (8+ defenders)
    - Number of pass rushers

    Args:
        pbp: Play-by-play DataFrame
        participation: Participation DataFrame (optional, will be joined if provided)

    Returns:
        DataFrame with personnel features added
    """

    if participation is not None:
        # Join with participation data
        pbp = pbp.join(
            participation.select([
                'nflverse_game_id', 'play_id', 'offense_personnel', 'defense_personnel',
                'defenders_in_box', 'number_of_pass_rushers', 'offense_formation'
            ]),
            left_on=['game_id', 'play_id'],
            right_on=['nflverse_game_id', 'play_id'],
            how='left'
        )

    # Create personnel features
    pbp = pbp.with_columns([
        # Defenders in box
        pl.col('defenders_in_box').alias('personnel_defenders_in_box'),

        # Light box (< 6 defenders)
        (pl.col('defenders_in_box') < 6)
            .fill_null(False)
            .cast(pl.Int32)
            .alias('personnel_light_box'),

        # Heavy box (8+ defenders)
        (pl.col('defenders_in_box') >= 8)
            .fill_null(False)
            .cast(pl.Int32)
            .alias('personnel_heavy_box'),

        # Number of pass rushers
        pl.col('number_of_pass_rushers').alias('personnel_pass_rushers')
    ])

    return pbp
