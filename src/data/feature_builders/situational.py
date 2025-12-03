"""
Situational Features
Basic game situation indicators for play prediction
"""

import polars as pl


def add_situational_features(pbp: pl.DataFrame) -> pl.DataFrame:
    """
    Add basic situational features to play-by-play data.

    Features include:
    - Short yardage situations (3 yards or less)
    - Red zone (20 yards from goal)
    - Goal line (5 yards from goal)
    - Passing downs (3rd/4th down)
    - Third down specifically
    - Long distance (7+ yards)
    - Winning/losing/tied situations
    - Two-minute drill
    - Fourth quarter

    Args:
        pbp: Play-by-play DataFrame

    Returns:
        DataFrame with situational features added
    """

    return pbp.with_columns([
        # Distance-based situations
        (pl.col('ydstogo') <= 3).cast(pl.Int32).alias('situation_short_yardage'),
        (pl.col('ydstogo') >= 7).cast(pl.Int32).alias('situation_long_distance'),

        # Field position situations
        (pl.col('yardline_100') <= 20).cast(pl.Int32).alias('situation_red_zone'),
        (pl.col('yardline_100') <= 5).cast(pl.Int32).alias('situation_goal_line'),

        # Down situations
        (pl.col('down') >= 3).cast(pl.Int32).alias('situation_passing_down'),
        (pl.col('down') == 3).cast(pl.Int32).alias('situation_third_down'),

        # Score situations
        (pl.col('score_differential') < 0).cast(pl.Int32).alias('situation_losing'),
        (pl.col('score_differential') > 0).cast(pl.Int32).alias('situation_winning'),
        (pl.col('score_differential') == 0).cast(pl.Int32).alias('situation_tied'),

        # Time-based situations (requires pre-computed columns)
        pl.when(pl.col('half_seconds_remaining').is_not_null())
          .then((pl.col('half_seconds_remaining') < 120).cast(pl.Int32))
          .otherwise(0)
          .alias('situation_two_minute'),

        (pl.col('qtr') == 4).cast(pl.Int32).alias('situation_fourth_quarter'),
    ])
