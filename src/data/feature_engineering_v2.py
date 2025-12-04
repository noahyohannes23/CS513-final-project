"""
DC-Perspective Feature Engineering - Modular Version
Goal: Build comprehensive features for play-type prediction from DC perspective

This modular version separates feature generation into logical categories,
making the codebase more maintainable and extensible.

NEW: Integrates player performance stats for "hot hand" features.
"""

import polars as pl
from pathlib import Path
from datetime import datetime

# Import modular feature builders
from feature_builders import (
    add_team_tendency_features,
    add_momentum_features,
    add_fatigue_features,
    add_personnel_features,
    add_context_features,
    add_player_performance_features,
    add_situational_features,
)

# ============================================================================
# CONFIGURATION
# ============================================================================

CACHE_DIR = Path("./data/cache")
OUTPUT_DIR = Path("./data/features")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Multi-season training for temporal split
SEASONS = [2021, 2022, 2023, 2024, 2025]

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def load_cached_data(seasons: list):
    """Load all cached data for multiple seasons and concatenate."""
    print(f"\n[1/5] Loading cached data for seasons {seasons}...")

    pbp_list = []
    participation_list = []
    schedules_list = []
    player_stats_list = []

    for season in seasons:
        print(f"\n   Loading {season}...")

        # Load PBP
        pbp_season = pl.read_parquet(CACHE_DIR / f"pbp_{season}.parquet")
        # Add season column for tracking
        pbp_season = pbp_season.with_columns(pl.lit(season).alias('season'))
        pbp_list.append(pbp_season)
        print(f"      PBP: {pbp_season.shape}")

        # Load participation
        try:
            participation_season = pl.read_parquet(CACHE_DIR / f"participation_{season}.parquet")
            participation_season = participation_season.with_columns(pl.lit(season).alias('season'))
            participation_list.append(participation_season)
            print(f"      Participation: {participation_season.shape}")
        except FileNotFoundError:
            print(f"      [WARNING] Participation not found for {season}")

        # Load schedules
        try:
            schedules_season = pl.read_parquet(CACHE_DIR / f"schedules_{season}.parquet")
            schedules_season = schedules_season.with_columns(pl.lit(season).alias('season'))
            schedules_list.append(schedules_season)
            print(f"      Schedules: {schedules_season.shape}")
        except FileNotFoundError:
            print(f"      [WARNING] Schedules not found for {season}")

        # Load player stats
        try:
            player_stats_season = pl.read_parquet(CACHE_DIR / f"player_stats_{season}.parquet")
            player_stats_season = player_stats_season.with_columns(pl.lit(season).alias('season'))
            player_stats_list.append(player_stats_season)
            print(f"      Player stats: {player_stats_season.shape}")
        except FileNotFoundError:
            print(f"      [WARNING] Player stats not found for {season}")

    # Concatenate all seasons
    print(f"\n   Concatenating {len(seasons)} seasons...")
    pbp = pl.concat(pbp_list, how="diagonal_relaxed")
    participation = pl.concat(participation_list, how="diagonal_relaxed") if participation_list else None
    schedules = pl.concat(schedules_list, how="diagonal_relaxed") if schedules_list else None
    player_stats = pl.concat(player_stats_list, how="diagonal_relaxed") if player_stats_list else None

    print(f"\n   [OK] Combined PBP: {pbp.shape}")
    if participation is not None:
        print(f"   [OK] Combined Participation: {participation.shape}")
    if schedules is not None:
        print(f"   [OK] Combined Schedules: {schedules.shape}")
    if player_stats is not None:
        print(f"   [OK] Combined Player stats: {player_stats.shape}")

    return pbp, participation, schedules, player_stats


def prepare_data(pbp: pl.DataFrame) -> pl.DataFrame:
    """Filter and prepare play-by-play data."""
    print("\n[2/5] Preparing data...")

    # Keep only run and pass plays
    pbp_clean = pbp.filter(
        (pl.col('play_type').is_in(['run', 'pass']))
    ).with_columns([
        # Create target variable
        (pl.col('play_type') == 'pass').cast(pl.Int32).alias('is_pass')
    ])

    print(f"   [OK] Filtered to {pbp_clean.height:,} run/pass plays")
    return pbp_clean


def engineer_features(
    pbp: pl.DataFrame,
    participation: pl.DataFrame,
    schedules: pl.DataFrame,
    player_stats: pl.DataFrame
) -> pl.DataFrame:
    """Apply all feature engineering transformations."""
    print("\n[3/5] Engineering features...")
    print(f"   Starting rows: {pbp.height:,}")

    # Category 1: Team Tendencies (historical pass rates by situation)
    print("   > Team tendency features...")
    pbp = add_team_tendency_features(pbp)
    print(f"      After team tendencies: {pbp.height:,} rows")

    # Category 2: Momentum (rolling drive/play success)
    print("   > Momentum features...")
    pbp = add_momentum_features(pbp)
    print(f"      After momentum: {pbp.height:,} rows")

    # Category 3: Fatigue (tempo, snap counts)
    print("   > Fatigue features...")
    pbp = add_fatigue_features(pbp)
    print(f"      After fatigue: {pbp.height:,} rows")

    # Category 4: Personnel (defensive alignment)
    print("   > Personnel features...")
    pbp = add_personnel_features(pbp, participation)
    print(f"      After personnel: {pbp.height:,} rows")

    # Category 5: Context (weather, venue)
    print("   > Context features...")
    pbp = add_context_features(pbp, schedules)
    print(f"      After context: {pbp.height:,} rows")

    # Category 6: Player Performance (NEW - player efficiency stats)
    print("   > Player performance features (NEW)...")
    pbp = add_player_performance_features(pbp, player_stats)
    print(f"      After player performance: {pbp.height:,} rows")

    # Category 7: Situational (basic flags)
    print("   > Situational features...")
    pbp = add_situational_features(pbp)
    print(f"      After situational: {pbp.height:,} rows")

    return pbp


def select_final_features(pbp: pl.DataFrame) -> pl.DataFrame:
    """Select final feature set and clean data."""
    print("\n[4/5] Selecting final features...")

    # Core features
    core_features = [
        # Identifiers
        'game_id', 'play_id', 'posteam', 'defteam', 'week', 'season',
        # Target
        'is_pass',
        # Basic situational
        'down', 'ydstogo', 'yardline_100', 'score_differential',
        'qtr', 'half_seconds_remaining', 'game_seconds_remaining',
    ]

    # Auto-collect features by prefix
    team_tendency_features = [col for col in pbp.columns if col.startswith('team_pass_rate')]
    momentum_features = [col for col in pbp.columns if col.startswith('momentum_') or col.startswith('drive_')]
    fatigue_features = [col for col in pbp.columns if col.startswith('fatigue_')]
    personnel_features = [col for col in pbp.columns if col.startswith('personnel_')]
    formation_features = [col for col in pbp.columns if col.startswith('formation_')]
    context_features = [col for col in pbp.columns if col.startswith('context_')]
    situation_features = [col for col in pbp.columns if col.startswith('situation_')]

    # NEW: Player performance features
    player_features = [col for col in pbp.columns if col.startswith(('qb_', 'rb_', 'receiver_'))]

    # Combine all
    all_features = (
        core_features + team_tendency_features + momentum_features +
        fatigue_features + personnel_features + formation_features +
        context_features + situation_features + player_features
    )

    # Select and clean
    pbp_final = pbp.select(all_features)

    # Only drop nulls on critical features (not player stats which may be legitimately null)
    critical_features = ['down', 'ydstogo', 'yardline_100', 'score_differential', 'is_pass']
    pbp_final_clean = pbp_final.drop_nulls(subset=critical_features)

    print(f"   [OK] Total features: {len(all_features)}")
    print(f"   [OK] After dropping nulls on critical features: {pbp_final_clean.height:,} plays")

    return pbp_final_clean, all_features


def save_features(pbp: pl.DataFrame, all_features: list, seasons: list):
    """Save engineered features and summary."""
    print("\n[5/5] Saving features...")

    # Create filename indicating multi-season
    season_range = f"{min(seasons)}-{max(seasons)}"
    output_path = OUTPUT_DIR / f"dc_features_{season_range}.parquet"
    pbp.write_parquet(output_path)
    print(f"   [OK] Features saved: {output_path}")

    # Save feature summary
    summary_path = OUTPUT_DIR / f"feature_summary_{season_range}.txt"
    with open(summary_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("DC FEATURE ENGINEERING SUMMARY (MODULAR VERSION)\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Total plays: {pbp.height:,}\n")
        f.write(f"Total features: {len(all_features)}\n\n")

        f.write("FEATURE GROUPS:\n")
        f.write("-" * 80 + "\n")

        # Count by prefix
        groups = {
            'Core': [c for c in all_features if not any(c.startswith(p) for p in
                    ['team_', 'momentum_', 'drive_', 'fatigue_', 'personnel_',
                     'formation_', 'context_', 'situation_', 'qb_', 'rb_', 'receiver_'])],
            'Team Tendencies': [c for c in all_features if c.startswith('team_')],
            'Momentum': [c for c in all_features if c.startswith(('momentum_', 'drive_'))],
            'Fatigue': [c for c in all_features if c.startswith('fatigue_')],
            'Personnel': [c for c in all_features if c.startswith('personnel_')],
            'Formation': [c for c in all_features if c.startswith('formation_')],
            'Context': [c for c in all_features if c.startswith('context_')],
            'Situational': [c for c in all_features if c.startswith('situation_')],
            'Player Performance (NEW)': [c for c in all_features if c.startswith(('qb_', 'rb_', 'receiver_'))],
        }

        for group_name, group_features in groups.items():
            f.write(f"{group_name}: {len(group_features)}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("ALL FEATURES BY CATEGORY:\n")
        f.write("=" * 80 + "\n\n")

        for group_name, group_features in groups.items():
            if group_features:
                f.write(f"\n{group_name}:\n")
                f.write("-" * 40 + "\n")
                for feat in sorted(group_features):
                    f.write(f"  • {feat}\n")

    print(f"   [OK] Summary saved: {summary_path}")


def main():
    """Main feature engineering pipeline."""
    print("=" * 80)
    print("DC FEATURE ENGINEERING - MULTI-SEASON MODULAR VERSION")
    print("=" * 80)
    print(f"Seasons: {SEASONS}")

    # Load data
    pbp, participation, schedules, player_stats = load_cached_data(SEASONS)

    # Prepare data
    pbp = prepare_data(pbp)

    # Engineer features
    pbp = engineer_features(pbp, participation, schedules, player_stats)

    # Select final features
    pbp_final, all_features = select_final_features(pbp)

    # Save
    save_features(pbp_final, all_features, SEASONS)

    season_range = f"{min(SEASONS)}-{max(SEASONS)}"
    print("\n" + "=" * 80)
    print("MULTI-SEASON FEATURE ENGINEERING COMPLETE!")
    print("=" * 80)
    print(f"\nSeasons processed: {SEASONS}")
    print(f"Features saved to: {OUTPUT_DIR / f'dc_features_{season_range}.parquet'}")
    print(f"Summary saved to: {OUTPUT_DIR / f'feature_summary_{season_range}.txt'}")
    print("\n[OK] Ready for temporal split model training!")


if __name__ == "__main__":
    main()
