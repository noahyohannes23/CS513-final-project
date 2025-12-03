"""
Team Tendency Features
Historical team pass/run tendencies by situation

These features capture how teams typically call plays in different game situations
based on historical data. Key insight: Defensive coordinators study these tendencies.
"""

import polars as pl


def _create_situation_categories(pbp: pl.DataFrame) -> pl.DataFrame:
    """Add categorical situation columns for grouping."""
    return pbp.with_columns([
        # Distance categories
        pl.when(pl.col('ydstogo') <= 3)
            .then(pl.lit('short'))
        .when(pl.col('ydstogo') <= 7)
            .then(pl.lit('medium'))
        .otherwise(pl.lit('long'))
            .alias('distance_category'),

        # Field position categories
        pl.when(pl.col('yardline_100') > 80)
            .then(pl.lit('own_territory'))
        .when(pl.col('yardline_100') > 50)
            .then(pl.lit('midfield_approach'))
        .when(pl.col('yardline_100') > 20)
            .then(pl.lit('opponent_territory'))
        .when(pl.col('yardline_100') > 10)
            .then(pl.lit('red_zone'))
        .otherwise(pl.lit('goal_line'))
            .alias('field_position_category'),

        # Score differential categories
        pl.when(pl.col('score_differential') < -7)
            .then(pl.lit('trailing_big'))
        .when(pl.col('score_differential') < 0)
            .then(pl.lit('trailing_small'))
        .when(pl.col('score_differential') == 0)
            .then(pl.lit('tied'))
        .when(pl.col('score_differential') <= 7)
            .then(pl.lit('leading_small'))
        .otherwise(pl.lit('leading_big'))
            .alias('score_situation'),

        # Time categories
        (pl.col('half_seconds_remaining') < 120).alias('two_minute_drill'),
        (pl.col('qtr') == 4).alias('fourth_quarter')
    ])


def add_team_tendency_features(pbp: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate team-level historical pass tendencies by various situations.

    Computes pass rate (% of plays that are passes) for each team across:
    - Overall
    - By down (1st, 2nd, 3rd, 4th)
    - By distance (short, medium, long)
    - By field position (own territory, midfield, opponent territory, red zone, goal line)
    - By score situation (trailing big/small, tied, leading small/big)
    - Special situations (red zone, 4th quarter, two-minute drill)

    Args:
        pbp: Play-by-play DataFrame with 'posteam' and 'is_pass' columns

    Returns:
        DataFrame with team tendency features joined
    """

    # Add situation categories
    pbp_with_situations = _create_situation_categories(pbp)

    # Overall team pass rate
    team_overall = pbp_with_situations.group_by('posteam').agg([
        pl.col('is_pass').mean().alias('team_pass_rate_overall'),
        pl.col('is_pass').count().alias('team_play_count')
    ])

    # Pass rate by down
    team_by_down = pbp_with_situations.group_by(['posteam', 'down']).agg([
        pl.col('is_pass').mean().alias('pass_rate')
    ]).pivot(index='posteam', columns='down', values='pass_rate')

    # Rename columns safely
    down_rename = {}
    for col in team_by_down.columns:
        if col != 'posteam':
            down_rename[col] = f'team_pass_rate_down_{col}'.replace('.0', '')
    team_by_down = team_by_down.rename(down_rename)

    # Pass rate by distance category
    team_by_distance = pbp_with_situations.group_by(['posteam', 'distance_category']).agg([
        pl.col('is_pass').mean().alias('pass_rate')
    ]).pivot(index='posteam', columns='distance_category', values='pass_rate')
    distance_rename = {col: f'team_pass_rate_{col}_distance'
                       for col in team_by_distance.columns if col != 'posteam'}
    team_by_distance = team_by_distance.rename(distance_rename)

    # Pass rate by field position
    team_by_field_pos = pbp_with_situations.group_by(['posteam', 'field_position_category']).agg([
        pl.col('is_pass').mean().alias('pass_rate')
    ]).pivot(index='posteam', columns='field_position_category', values='pass_rate')
    field_pos_rename = {col: f'team_pass_rate_{col}'
                        for col in team_by_field_pos.columns if col != 'posteam'}
    team_by_field_pos = team_by_field_pos.rename(field_pos_rename)

    # Pass rate by score situation
    team_by_score = pbp_with_situations.group_by(['posteam', 'score_situation']).agg([
        pl.col('is_pass').mean().alias('pass_rate')
    ]).pivot(index='posteam', columns='score_situation', values='pass_rate')
    score_rename = {col: f'team_pass_rate_{col}'
                    for col in team_by_score.columns if col != 'posteam'}
    team_by_score = team_by_score.rename(score_rename)

    # Pass rate in red zone
    team_red_zone = pbp_with_situations.filter(
        pl.col('yardline_100') <= 20
    ).group_by('posteam').agg([
        pl.col('is_pass').mean().alias('team_pass_rate_red_zone_special')
    ])

    # Pass rate in 4th quarter
    team_q4 = pbp_with_situations.filter(
        pl.col('qtr') == 4
    ).group_by('posteam').agg([
        pl.col('is_pass').mean().alias('team_pass_rate_q4')
    ])

    # Pass rate in two-minute situations
    team_two_min = pbp_with_situations.filter(
        pl.col('two_minute_drill')
    ).group_by('posteam').agg([
        pl.col('is_pass').mean().alias('team_pass_rate_two_minute')
    ])

    # Merge all team tendency features
    team_tendencies = team_overall
    for df in [team_by_down, team_by_distance, team_by_field_pos, team_by_score,
               team_red_zone, team_q4, team_two_min]:
        team_tendencies = team_tendencies.join(df, on='posteam', how='left')

    # Join back to original pbp
    # Keep situation categories for use by other feature builders
    result = pbp_with_situations.join(team_tendencies, on='posteam', how='left')

    return result
