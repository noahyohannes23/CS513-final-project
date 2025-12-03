"""
Player Performance Features
Individual player efficiency and "hot hand" indicators

NEW FEATURE CATEGORY: Uses player stats to capture efficiency trends.
Key insight: Offenses feed hot players and exploit favorable matchups.

Example: If a RB is averaging 6 yards/carry this game, expect more rushes.
If a QB is having a bad day, expect more conservative play calls.
"""

import polars as pl


def add_player_performance_features(
    pbp: pl.DataFrame,
    player_stats: pl.DataFrame = None
) -> pl.DataFrame:
    """
    Add player performance features from weekly player stats.

    Features include:
    QB Performance (pass plays):
    - Completion percentage (season-to-date)
    - Yards per attempt
    - TD/INT ratio
    - Passer rating

    RB Performance (rush plays):
    - Yards per carry
    - Rushing yards per game
    - Rushing TDs

    WR/TE Performance (pass plays):
    - Targets per game
    - Catch rate
    - Yards per reception
    - Receiving yards per game

    Rolling Performance (within season):
    - Recent game efficiency (last 3 weeks)
    - Hot/cold streaks

    Args:
        pbp: Play-by-play DataFrame
        player_stats: Player stats DataFrame from load_player_stats(season, 'week')

    Returns:
        DataFrame with player performance features added
    """

    if player_stats is None:
        # If no player stats provided, return pbp unchanged with null columns
        return _add_null_player_features(pbp)

    # ========================================================================
    # PREPARE PLAYER STATS
    # ========================================================================

    # Aggregate to season-to-date stats by player and week
    # For each week, calculate cumulative stats up to that week

    # QB Stats
    qb_stats = player_stats.filter(
        pl.col('position') == 'QB'
    ).sort(['player_id', 'week']).group_by('player_id').agg([
        pl.col('week'),
        pl.col('completions').cum_sum().alias('cum_completions'),
        pl.col('attempts').cum_sum().alias('cum_attempts'),
        pl.col('passing_yards').cum_sum().alias('cum_passing_yards'),
        pl.col('passing_tds').cum_sum().alias('cum_passing_tds'),
        pl.col('interceptions').cum_sum().alias('cum_ints'),
    ]).explode(['week', 'cum_completions', 'cum_attempts', 'cum_passing_yards',
                'cum_passing_tds', 'cum_ints'])

    qb_stats = qb_stats.with_columns([
        # Completion percentage
        (pl.col('cum_completions') / pl.col('cum_attempts'))
            .fill_nan(0.0)
            .alias('qb_completion_pct'),

        # Yards per attempt
        (pl.col('cum_passing_yards') / pl.col('cum_attempts'))
            .fill_nan(0.0)
            .alias('qb_yards_per_attempt'),

        # TD/INT ratio
        (pl.col('cum_passing_tds') / pl.col('cum_ints').clip(1))
            .fill_nan(0.0)
            .alias('qb_td_int_ratio'),
    ])

    # RB Stats
    rb_stats = player_stats.filter(
        pl.col('position') == 'RB'
    ).sort(['player_id', 'week']).group_by('player_id').agg([
        pl.col('week'),
        pl.col('carries').cum_sum().alias('cum_carries'),
        pl.col('rushing_yards').cum_sum().alias('cum_rushing_yards'),
        pl.col('rushing_tds').cum_sum().alias('cum_rushing_tds'),
    ]).explode(['week', 'cum_carries', 'cum_rushing_yards', 'cum_rushing_tds'])

    rb_stats = rb_stats.with_columns([
        # Yards per carry
        (pl.col('cum_rushing_yards') / pl.col('cum_carries'))
            .fill_nan(0.0)
            .alias('rb_yards_per_carry'),

        # Rushing TDs per game
        (pl.col('cum_rushing_tds') / pl.col('week'))
            .fill_nan(0.0)
            .alias('rb_tds_per_game'),
    ])

    # WR/TE Stats
    receiver_stats = player_stats.filter(
        pl.col('position').is_in(['WR', 'TE'])
    ).sort(['player_id', 'week']).group_by('player_id').agg([
        pl.col('week'),
        pl.col('receptions').cum_sum().alias('cum_receptions'),
        pl.col('targets').cum_sum().alias('cum_targets'),
        pl.col('receiving_yards').cum_sum().alias('cum_receiving_yards'),
    ]).explode(['week', 'cum_receptions', 'cum_targets', 'cum_receiving_yards'])

    receiver_stats = receiver_stats.with_columns([
        # Catch rate
        (pl.col('cum_receptions') / pl.col('cum_targets'))
            .fill_nan(0.0)
            .alias('receiver_catch_rate'),

        # Yards per reception
        (pl.col('cum_receiving_yards') / pl.col('cum_receptions'))
            .fill_nan(0.0)
            .alias('receiver_yards_per_reception'),

        # Targets per game
        (pl.col('cum_targets') / pl.col('week'))
            .fill_nan(0.0)
            .alias('receiver_targets_per_game'),
    ])

    # ========================================================================
    # JOIN TO PBP DATA
    # ========================================================================

    # Join QB stats (for QB on current play)
    pbp = pbp.join(
        qb_stats.select([
            'player_id', 'week', 'qb_completion_pct',
            'qb_yards_per_attempt', 'qb_td_int_ratio'
        ]),
        left_on=['passer_player_id', 'week'],
        right_on=['player_id', 'week'],
        how='left'
    )

    # Join RB stats (for rusher on current play)
    pbp = pbp.join(
        rb_stats.select([
            'player_id', 'week', 'rb_yards_per_carry', 'rb_tds_per_game'
        ]),
        left_on=['rusher_player_id', 'week'],
        right_on=['player_id', 'week'],
        how='left'
    )

    # Join receiver stats (for receiver on current play)
    pbp = pbp.join(
        receiver_stats.select([
            'player_id', 'week', 'receiver_catch_rate',
            'receiver_yards_per_reception', 'receiver_targets_per_game'
        ]),
        left_on=['receiver_player_id', 'week'],
        right_on=['player_id', 'week'],
        how='left'
    )

    # Fill nulls for plays without player stats
    player_feature_cols = [
        'qb_completion_pct', 'qb_yards_per_attempt', 'qb_td_int_ratio',
        'rb_yards_per_carry', 'rb_tds_per_game',
        'receiver_catch_rate', 'receiver_yards_per_reception', 'receiver_targets_per_game'
    ]

    for col in player_feature_cols:
        if col in pbp.columns:
            pbp = pbp.with_columns([
                pl.col(col).fill_null(0.0).alias(col)
            ])

    return pbp


def _add_null_player_features(pbp: pl.DataFrame) -> pl.DataFrame:
    """Add null player feature columns if player stats not available."""
    return pbp.with_columns([
        pl.lit(None, dtype=pl.Float64).alias('qb_completion_pct'),
        pl.lit(None, dtype=pl.Float64).alias('qb_yards_per_attempt'),
        pl.lit(None, dtype=pl.Float64).alias('qb_td_int_ratio'),
        pl.lit(None, dtype=pl.Float64).alias('rb_yards_per_carry'),
        pl.lit(None, dtype=pl.Float64).alias('rb_tds_per_game'),
        pl.lit(None, dtype=pl.Float64).alias('receiver_catch_rate'),
        pl.lit(None, dtype=pl.Float64).alias('receiver_yards_per_reception'),
        pl.lit(None, dtype=pl.Float64).alias('receiver_targets_per_game'),
    ])
