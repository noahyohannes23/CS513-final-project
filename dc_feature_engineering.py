"""
DC-Perspective Feature Engineering - Phase 1
Goal: Build comprehensive features for play-type prediction from DC perspective
Features: Team tendencies, momentum, fatigue, personnel, context
"""

import polars as pl
import numpy as np
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

CACHE_DIR = Path("./nfl_data_cache")
OUTPUT_DIR = Path("./dc_features")
OUTPUT_DIR.mkdir(exist_ok=True)

SEASON = 2023

# ============================================================================
# LOAD CACHED DATA
# ============================================================================

print("=" * 80)
print("DC FEATURE ENGINEERING - PHASE 1")
print("=" * 80)

print("\n[1/10] Loading cached data...")
pbp = pl.read_parquet(CACHE_DIR / f"pbp_{SEASON}.parquet")
participation = pl.read_parquet(CACHE_DIR / f"participation_{SEASON}.parquet")
schedules = pl.read_parquet(CACHE_DIR / f"schedules_{SEASON}.parquet")
snap_counts = pl.read_parquet(CACHE_DIR / f"snap_counts_{SEASON}.parquet")

print(f"   PBP: {pbp.shape}")
print(f"   Participation: {participation.shape}")
print(f"   Schedules: {schedules.shape}")
print(f"   Snap counts: {snap_counts.shape}")

# ============================================================================
# DATA PREPARATION
# ============================================================================

print("\n[2/10] Filtering for run/pass plays...")
# Keep only run and pass plays
pbp_clean = pbp.filter(
    (pl.col('play_type').is_in(['run', 'pass']))
).with_columns([
    # Create target variable
    (pl.col('play_type') == 'pass').cast(pl.Int32).alias('is_pass')
])

print(f"   Filtered to {pbp_clean.height:,} run/pass plays")

# ============================================================================
# FEATURE ENGINEERING - CATEGORY 1: TEAM TENDENCIES
# ============================================================================

print("\n[3/10] Engineering team tendency features...")

# First, create situation categories
pbp_clean = pbp_clean.with_columns([
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

# Calculate team-level historical tendencies
# Group by team and situation, calculate pass rates
print("   Computing team pass rates by situation...")

# Overall team pass rate
team_overall = pbp_clean.group_by('posteam').agg([
    pl.col('is_pass').mean().alias('team_pass_rate_overall'),
    pl.col('is_pass').count().alias('team_play_count')
])

# Pass rate by down
team_by_down = pbp_clean.group_by(['posteam', 'down']).agg([
    pl.col('is_pass').mean().alias('pass_rate')
]).pivot(index='posteam', columns='down', values='pass_rate')
team_by_down = team_by_down.rename({
    '1.0': 'team_pass_rate_down_1',
    '2.0': 'team_pass_rate_down_2',
    '3.0': 'team_pass_rate_down_3',
    '4.0': 'team_pass_rate_down_4'
})

# Pass rate by distance category
team_by_distance = pbp_clean.group_by(['posteam', 'distance_category']).agg([
    pl.col('is_pass').mean().alias('pass_rate')
]).pivot(index='posteam', columns='distance_category', values='pass_rate')
team_by_distance = team_by_distance.rename({
    'short': 'team_pass_rate_short_distance',
    'medium': 'team_pass_rate_medium_distance',
    'long': 'team_pass_rate_long_distance'
})

# Pass rate by field position
team_by_field_pos = pbp_clean.group_by(['posteam', 'field_position_category']).agg([
    pl.col('is_pass').mean().alias('pass_rate')
]).pivot(index='posteam', columns='field_position_category', values='pass_rate')
# Rename with prefix
field_pos_rename = {col: f'team_pass_rate_{col}' for col in team_by_field_pos.columns if col != 'posteam'}
team_by_field_pos = team_by_field_pos.rename(field_pos_rename)

# Pass rate by score situation
team_by_score = pbp_clean.group_by(['posteam', 'score_situation']).agg([
    pl.col('is_pass').mean().alias('pass_rate')
]).pivot(index='posteam', columns='score_situation', values='pass_rate')
score_rename = {col: f'team_pass_rate_{col}' for col in team_by_score.columns if col != 'posteam'}
team_by_score = team_by_score.rename(score_rename)

# Pass rate in red zone
team_red_zone = pbp_clean.filter(pl.col('yardline_100') <= 20).group_by('posteam').agg([
    pl.col('is_pass').mean().alias('team_pass_rate_red_zone')
])

# Pass rate in 4th quarter
team_q4 = pbp_clean.filter(pl.col('qtr') == 4).group_by('posteam').agg([
    pl.col('is_pass').mean().alias('team_pass_rate_q4')
])

# Pass rate in two-minute situations
team_two_min = pbp_clean.filter(pl.col('two_minute_drill')).group_by('posteam').agg([
    pl.col('is_pass').mean().alias('team_pass_rate_two_minute')
])

# Merge all team tendency features
print("   Merging team tendency features...")
team_tendencies = team_overall
for df in [team_by_down, team_by_distance, team_by_field_pos, team_by_score,
           team_red_zone, team_q4, team_two_min]:
    team_tendencies = team_tendencies.join(df, on='posteam', how='left')

print(f"   Created {len(team_tendencies.columns)} team tendency features")

# Join team tendencies back to main data
pbp_features = pbp_clean.join(team_tendencies, on='posteam', how='left')

# ============================================================================
# FEATURE ENGINEERING - CATEGORY 2: MOMENTUM
# ============================================================================

print("\n[4/10] Engineering momentum features...")

# Sort by game and play sequence
pbp_features = pbp_features.sort(['game_id', 'play_id'])

# Calculate rolling success rate (EPA > 0 indicates success)
pbp_features = pbp_features.with_columns([
    # Success indicator
    (pl.col('epa') > 0).cast(pl.Int32).alias('play_success'),
    # Explosive play indicator
    (pl.col('yards_gained') >= 10).cast(pl.Int32).alias('explosive_play')
])

# Rolling momentum features over last N plays (within same drive)
# We'll compute these using window functions
pbp_features = pbp_features.with_columns([
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

    # Yards per play on current drive (cumulative)
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

    # Drive EPA
    pl.col('epa')
        .cum_sum()
        .over(['game_id', 'drive'])
        .alias('drive_epa')
])

# Yards per play on drive
pbp_features = pbp_features.with_columns([
    (pl.col('drive_total_yards') / pl.col('drive_play_count'))
        .alias('drive_yards_per_play')
])

print(f"   Created momentum features")

# ============================================================================
# FEATURE ENGINEERING - CATEGORY 3: FATIGUE
# ============================================================================

print("\n[5/10] Engineering fatigue features...")

# Fatigue is closely related to drive length and tempo
pbp_features = pbp_features.with_columns([
    # Drive length (already have drive_play_count)

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

    # Plays in last 5 game minutes
    # This is complex - we'll approximate with recent play count
    pl.lit(1)
        .rolling_sum(window_size=10, min_periods=1)
        .over(['game_id', 'posteam'])
        .alias('fatigue_plays_last_10'),

    # No-huddle indicator (tempo)
    pl.col('no_huddle').alias('fatigue_no_huddle'),

    # Shotgun frequency (also tempo-related)
    pl.col('shotgun').alias('formation_shotgun')
])

# Fast tempo indicator (< 20 seconds since last play)
pbp_features = pbp_features.with_columns([
    (pl.col('seconds_since_last_play') < 20)
        .fill_null(False)
        .cast(pl.Int32)
        .alias('fatigue_fast_tempo')
])

print(f"   Created fatigue features")

# ============================================================================
# FEATURE ENGINEERING - CATEGORY 4: PERSONNEL & FORMATION
# ============================================================================

print("\n[6/10] Engineering personnel features...")

# Join with participation data to get personnel info
pbp_features = pbp_features.join(
    participation.select([
        'nflverse_game_id', 'play_id', 'offense_personnel', 'defense_personnel',
        'defenders_in_box', 'number_of_pass_rushers', 'offense_formation'
    ]),
    left_on=['game_id', 'play_id'],
    right_on=['nflverse_game_id', 'play_id'],
    how='left'
)

# Parse personnel (e.g., "1 RB, 1 TE, 3 WR" -> extract counts)
# This is complex string parsing - we'll create simplified features
pbp_features = pbp_features.with_columns([
    # Defenders in box
    pl.col('defenders_in_box').alias('personnel_defenders_in_box'),

    # Light box (< 6 defenders)
    (pl.col('defenders_in_box') < 6).cast(pl.Int32).alias('personnel_light_box'),

    # Heavy box (8+ defenders)
    (pl.col('defenders_in_box') >= 8).cast(pl.Int32).alias('personnel_heavy_box'),

    # Number of pass rushers
    pl.col('number_of_pass_rushers').alias('personnel_pass_rushers')
])

print(f"   Created personnel features")

# ============================================================================
# FEATURE ENGINEERING - CATEGORY 5: ENVIRONMENTAL/CONTEXT
# ============================================================================

print("\n[7/10] Engineering contextual features...")

# Join with schedules for environmental data
game_context = schedules.select([
    'game_id', 'roof', 'surface', 'temp', 'wind',
    'away_rest', 'home_rest', 'div_game'
])

pbp_features = pbp_features.join(game_context, on='game_id', how='left')

# Create context features
pbp_features = pbp_features.with_columns([
    # Weather
    (pl.col('roof') == 'outdoors').cast(pl.Int32).alias('context_outdoor'),
    (pl.col('roof') == 'dome').cast(pl.Int32).alias('context_dome'),
    pl.col('temp').alias('context_temperature'),
    pl.col('wind').alias('context_wind'),
    (pl.col('temp') < 40).cast(pl.Int32).alias('context_cold_weather'),
    (pl.col('wind') > 15).cast(pl.Int32).alias('context_high_wind'),

    # Surface
    (pl.col('surface') == 'grass').cast(pl.Int32).alias('context_grass'),

    # Division game
    pl.col('div_game').alias('context_division_game'),

    # Rest days (fatigue at game level)
    pl.when(pl.col('posteam_type') == 'home')
        .then(pl.col('home_rest'))
        .otherwise(pl.col('away_rest'))
        .alias('context_team_rest_days')
])

print(f"   Created contextual features")

# ============================================================================
# FEATURE ENGINEERING - CATEGORY 6: BASIC FEATURES
# ============================================================================

print("\n[8/10] Adding basic situational features...")

# Add some derived basic features
pbp_features = pbp_features.with_columns([
    # Short yardage situation
    (pl.col('ydstogo') <= 3).cast(pl.Int32).alias('situation_short_yardage'),

    # Red zone
    (pl.col('yardline_100') <= 20).cast(pl.Int32).alias('situation_red_zone'),

    # Goal line
    (pl.col('yardline_100') <= 5).cast(pl.Int32).alias('situation_goal_line'),

    # Passing down (3rd or 4th)
    (pl.col('down') >= 3).cast(pl.Int32).alias('situation_passing_down'),

    # Third down
    (pl.col('down') == 3).cast(pl.Int32).alias('situation_third_down'),

    # Long distance (7+ yards)
    (pl.col('ydstogo') >= 7).cast(pl.Int32).alias('situation_long_distance'),

    # Losing (negative score diff)
    (pl.col('score_differential') < 0).cast(pl.Int32).alias('situation_losing'),

    # Winning (positive score diff)
    (pl.col('score_differential') > 0).cast(pl.Int32).alias('situation_winning'),

    # Two minute drill
    pl.col('two_minute_drill').cast(pl.Int32).alias('situation_two_minute'),

    # Fourth quarter
    pl.col('fourth_quarter').cast(pl.Int32).alias('situation_fourth_quarter')
])

print(f"   Created basic situational features")

# ============================================================================
# CLEAN UP AND SELECT FINAL FEATURES
# ============================================================================

print("\n[9/10] Selecting final feature set...")

# Core features we want to keep
core_features = [
    # Identifiers
    'game_id', 'play_id', 'posteam', 'defteam', 'week',

    # Target
    'is_pass',

    # Basic situational
    'down', 'ydstogo', 'yardline_100', 'score_differential',
    'qtr', 'half_seconds_remaining', 'game_seconds_remaining',

    # Situation flags
    'situation_short_yardage', 'situation_red_zone', 'situation_goal_line',
    'situation_passing_down', 'situation_third_down', 'situation_long_distance',
    'situation_losing', 'situation_winning', 'situation_two_minute', 'situation_fourth_quarter'
]

# Team tendency features
team_tendency_features = [col for col in pbp_features.columns if col.startswith('team_pass_rate')]

# Momentum features
momentum_features = [col for col in pbp_features.columns if col.startswith('momentum_') or col.startswith('drive_')]

# Fatigue features
fatigue_features = [col for col in pbp_features.columns if col.startswith('fatigue_')]

# Personnel features
personnel_features = [col for col in pbp_features.columns if col.startswith('personnel_')]

# Formation features
formation_features = ['formation_shotgun']

# Context features
context_features = [col for col in pbp_features.columns if col.startswith('context_')]

# Combine all feature groups
all_features = (core_features + team_tendency_features + momentum_features +
                fatigue_features + personnel_features + formation_features + context_features)

# Select only these columns
pbp_final = pbp_features.select(all_features)

# Drop nulls (for modeling)
pbp_final_clean = pbp_final.drop_nulls()

print(f"   Total features: {len(all_features)}")
print(f"   After dropping nulls: {pbp_final_clean.height:,} plays")

# ============================================================================
# SAVE ENGINEERED FEATURES
# ============================================================================

print("\n[10/10] Saving engineered features...")

# Save full feature set
output_path = OUTPUT_DIR / f"dc_features_{SEASON}.parquet"
pbp_final_clean.write_parquet(output_path)
print(f"   Saved to: {output_path}")

# Save feature summary
summary_path = OUTPUT_DIR / f"feature_summary_{SEASON}.txt"
with open(summary_path, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("DC FEATURE ENGINEERING SUMMARY\n")
    f.write(f"Generated: {datetime.now()}\n")
    f.write("=" * 80 + "\n\n")

    f.write(f"Total plays: {pbp_final_clean.height:,}\n")
    f.write(f"Total features: {len(all_features)}\n\n")

    f.write("FEATURE GROUPS:\n")
    f.write("-" * 80 + "\n")
    f.write(f"Core features: {len(core_features)}\n")
    f.write(f"Team tendency features: {len(team_tendency_features)}\n")
    f.write(f"Momentum features: {len(momentum_features)}\n")
    f.write(f"Fatigue features: {len(fatigue_features)}\n")
    f.write(f"Personnel features: {len(personnel_features)}\n")
    f.write(f"Formation features: {len(formation_features)}\n")
    f.write(f"Context features: {len(context_features)}\n\n")

    f.write("ALL FEATURES:\n")
    f.write("-" * 80 + "\n")
    for i, feat in enumerate(all_features, 1):
        f.write(f"{i:3d}. {feat}\n")

print(f"   Saved summary to: {summary_path}")

print("\n" + "=" * 80)
print("FEATURE ENGINEERING COMPLETE!")
print("=" * 80)
print(f"\nFeatures saved to: {output_path}")
print(f"Summary saved to: {summary_path}")
print(f"\nReady for model training!")
