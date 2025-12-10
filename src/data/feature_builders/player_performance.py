"""
Player Performance Features - TEAM-LEVEL AGGREGATES (LEAKAGE-FREE)
Team-level efficiency and performance indicators

CRITICAL FIX: Uses TEAM-level aggregates instead of individual player joins
to avoid NULL pattern leakage (rusher_player_id null = pass, non-null = run).

Key insight: Teams with efficient QBs pass more, teams with efficient RBs run more.
Use cumulative team stats from PREVIOUS weeks only (no look-ahead bias).
"""

import polars as pl


def add_player_performance_features(
    pbp: pl.DataFrame,
    player_stats: pl.DataFrame = None
) -> pl.DataFrame:
    """
    Add TEAM-LEVEL player performance features from weekly player stats.

    LEAKAGE-FREE APPROACH:
    - Aggregates to TEAM level (not individual players)
    - Every play gets stats (no NULL pattern based on play type)
    - Uses PREVIOUS week's cumulative stats (shifted forward by 1)

    Features include:
    Team QB Performance (from all QBs on team):
    - Team completion percentage (season-to-date)
    - Team yards per attempt
    - Team TD/INT ratio
    - Team passer rating

    Team RB Performance (from all RBs on team):
    - Team yards per carry
    - Team rushing yards per game
    - Team rushing TDs per game

    Team Receiving Performance (from all WRs/TEs):
    - Team targets per game
    - Team catch rate
    - Team yards per reception

    Args:
        pbp: Play-by-play DataFrame
        player_stats: Player stats DataFrame from load_player_stats(season, 'week')

    Returns:
        DataFrame with team-level player performance features added
    """

    if player_stats is None:
        # If no player stats provided, return pbp unchanged with null columns
        return _add_null_team_features(pbp)

    # ========================================================================
    # PREPARE TEAM-LEVEL STATS
    # ========================================================================

    # Aggregate QB stats to TEAM level by week
    team_qb_stats = player_stats.filter(
        pl.col('position') == 'QB'
    ).group_by(['team', 'season', 'week']).agg([
        pl.col('completions').sum().alias('team_completions'),
        pl.col('attempts').sum().alias('team_attempts'),
        pl.col('passing_yards').sum().alias('team_passing_yards'),
        pl.col('passing_tds').sum().alias('team_passing_tds'),
        pl.col('passing_interceptions').sum().alias('team_ints'),
    ])

    # Calculate cumulative team QB stats
    team_qb_stats = team_qb_stats.sort(['team', 'season', 'week']).group_by(
        ['team', 'season']
    ).agg([
        pl.col('week'),
        pl.col('team_completions').cum_sum().alias('cum_team_completions'),
        pl.col('team_attempts').cum_sum().alias('cum_team_attempts'),
        pl.col('team_passing_yards').cum_sum().alias('cum_team_passing_yards'),
        pl.col('team_passing_tds').cum_sum().alias('cum_team_passing_tds'),
        pl.col('team_ints').cum_sum().alias('cum_team_ints'),
    ]).explode([
        'week', 'cum_team_completions', 'cum_team_attempts',
        'cum_team_passing_yards', 'cum_team_passing_tds', 'cum_team_ints'
    ])

    # Calculate team QB efficiency metrics
    team_qb_stats = team_qb_stats.with_columns([
        # CRITICAL: Shift week forward to prevent look-ahead bias
        (pl.col('week') + 1).alias('week'),

        # Team completion percentage
        (pl.col('cum_team_completions') / pl.col('cum_team_attempts'))
            .fill_nan(0.0)
            .alias('team_qb_completion_pct'),

        # Team yards per attempt
        (pl.col('cum_team_passing_yards') / pl.col('cum_team_attempts'))
            .fill_nan(0.0)
            .alias('team_qb_yards_per_attempt'),

        # Team TD/INT ratio
        (pl.col('cum_team_passing_tds') / pl.col('cum_team_ints').clip(1))
            .fill_nan(0.0)
            .alias('team_qb_td_int_ratio'),
    ])

    # Aggregate RB stats to TEAM level by week
    team_rb_stats = player_stats.filter(
        pl.col('position') == 'RB'
    ).group_by(['team', 'season', 'week']).agg([
        pl.col('carries').sum().alias('team_carries'),
        pl.col('rushing_yards').sum().alias('team_rushing_yards'),
        pl.col('rushing_tds').sum().alias('team_rushing_tds'),
    ])

    # Calculate cumulative team RB stats
    team_rb_stats = team_rb_stats.sort(['team', 'season', 'week']).group_by(
        ['team', 'season']
    ).agg([
        pl.col('week'),
        pl.col('team_carries').cum_sum().alias('cum_team_carries'),
        pl.col('team_rushing_yards').cum_sum().alias('cum_team_rushing_yards'),
        pl.col('team_rushing_tds').cum_sum().alias('cum_team_rushing_tds'),
    ]).explode(['week', 'cum_team_carries', 'cum_team_rushing_yards', 'cum_team_rushing_tds'])

    # Calculate team RB efficiency metrics
    team_rb_stats = team_rb_stats.with_columns([
        # CRITICAL: Shift week forward to prevent look-ahead bias
        (pl.col('week') + 1).alias('week'),

        # Team yards per carry
        (pl.col('cum_team_rushing_yards') / pl.col('cum_team_carries'))
            .fill_nan(0.0)
            .alias('team_rb_yards_per_carry'),

        # Team rushing TDs per game (use week - 1 since shifted)
        (pl.col('cum_team_rushing_tds') / (pl.col('week') - 1).clip(1))
            .fill_nan(0.0)
            .alias('team_rb_tds_per_game'),
    ])

    # Aggregate WR/TE stats to TEAM level by week
    team_receiver_stats = player_stats.filter(
        pl.col('position').is_in(['WR', 'TE'])
    ).group_by(['team', 'season', 'week']).agg([
        pl.col('receptions').sum().alias('team_receptions'),
        pl.col('targets').sum().alias('team_targets'),
        pl.col('receiving_yards').sum().alias('team_receiving_yards'),
    ])

    # Calculate cumulative team receiver stats
    team_receiver_stats = team_receiver_stats.sort(['team', 'season', 'week']).group_by(
        ['team', 'season']
    ).agg([
        pl.col('week'),
        pl.col('team_receptions').cum_sum().alias('cum_team_receptions'),
        pl.col('team_targets').cum_sum().alias('cum_team_targets'),
        pl.col('team_receiving_yards').cum_sum().alias('cum_team_receiving_yards'),
    ]).explode(['week', 'cum_team_receptions', 'cum_team_targets', 'cum_team_receiving_yards'])

    # Calculate team receiver efficiency metrics
    team_receiver_stats = team_receiver_stats.with_columns([
        # CRITICAL: Shift week forward to prevent look-ahead bias
        (pl.col('week') + 1).alias('week'),

        # Team catch rate
        (pl.col('cum_team_receptions') / pl.col('cum_team_targets'))
            .fill_nan(0.0)
            .alias('team_receiver_catch_rate'),

        # Team yards per reception
        (pl.col('cum_team_receiving_yards') / pl.col('cum_team_receptions'))
            .fill_nan(0.0)
            .alias('team_receiver_yards_per_reception'),

        # Team targets per game (use week - 1 since shifted)
        (pl.col('cum_team_targets') / (pl.col('week') - 1).clip(1))
            .fill_nan(0.0)
            .alias('team_receiver_targets_per_game'),
    ])

    # ========================================================================
    # JOIN TO PBP DATA - TEAM LEVEL (NO NULL PATTERN LEAKAGE)
    # ========================================================================

    # Join team QB stats (for offensive team)
    pbp = pbp.join(
        team_qb_stats.select([
            'team', 'season', 'week', 'team_qb_completion_pct',
            'team_qb_yards_per_attempt', 'team_qb_td_int_ratio'
        ]),
        left_on=['posteam', 'season', 'week'],
        right_on=['team', 'season', 'week'],
        how='left'
    )

    # Join team RB stats (for offensive team)
    pbp = pbp.join(
        team_rb_stats.select([
            'team', 'season', 'week', 'team_rb_yards_per_carry', 'team_rb_tds_per_game'
        ]),
        left_on=['posteam', 'season', 'week'],
        right_on=['team', 'season', 'week'],
        how='left'
    )

    # Join team receiver stats (for offensive team)
    pbp = pbp.join(
        team_receiver_stats.select([
            'team', 'season', 'week', 'team_receiver_catch_rate',
            'team_receiver_yards_per_reception', 'team_receiver_targets_per_game'
        ]),
        left_on=['posteam', 'season', 'week'],
        right_on=['team', 'season', 'week'],
        how='left'
    )

    # Fill nulls for teams without player stats (mostly Week 1)
    team_feature_cols = [
        'team_qb_completion_pct', 'team_qb_yards_per_attempt', 'team_qb_td_int_ratio',
        'team_rb_yards_per_carry', 'team_rb_tds_per_game',
        'team_receiver_catch_rate', 'team_receiver_yards_per_reception', 'team_receiver_targets_per_game'
    ]

    for col in team_feature_cols:
        if col in pbp.columns:
            pbp = pbp.with_columns([
                pl.col(col).fill_null(0.0).alias(col)
            ])

    return pbp


def _add_null_team_features(pbp: pl.DataFrame) -> pl.DataFrame:
    """Add null team feature columns if player stats not available."""
    return pbp.with_columns([
        pl.lit(None, dtype=pl.Float64).alias('team_qb_completion_pct'),
        pl.lit(None, dtype=pl.Float64).alias('team_qb_yards_per_attempt'),
        pl.lit(None, dtype=pl.Float64).alias('team_qb_td_int_ratio'),
        pl.lit(None, dtype=pl.Float64).alias('team_rb_yards_per_carry'),
        pl.lit(None, dtype=pl.Float64).alias('team_rb_tds_per_game'),
        pl.lit(None, dtype=pl.Float64).alias('team_receiver_catch_rate'),
        pl.lit(None, dtype=pl.Float64).alias('team_receiver_yards_per_reception'),
        pl.lit(None, dtype=pl.Float64).alias('team_receiver_targets_per_game'),
    ])
