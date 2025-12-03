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

SEASON = 2023

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def load_cached_data(season: int):
    """Load all cached data required for feature engineering."""
    print(f"\n[1/5] Loading cached data for {season}...")

    pbp = pl.read_parquet(CACHE_DIR / f"pbp_{season}.parquet")
    participation = pl.read_parquet(CACHE_DIR / f"participation_{season}.parquet")
    schedules = pl.read_parquet(CACHE_DIR / f"schedules_{season}.parquet")

    # Load player stats (newly added)
    try:
        player_stats = pl.read_parquet(CACHE_DIR / f"player_stats_{season}.parquet")
        print(f"   ✓ Player stats loaded: {player_stats.shape}")
    except FileNotFoundError:
        print(f"   ⚠ Player stats not found - run data_loading.py first")
        player_stats = None

    print(f"   ✓ PBP: {pbp.shape}")
    print(f"   ✓ Participation: {participation.shape}")
    print(f"   ✓ Schedules: {schedules.shape}")

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

    print(f"   ✓ Filtered to {pbp_clean.height:,} run/pass plays")
    return pbp_clean


def engineer_features(
    pbp: pl.DataFrame,
    participation: pl.DataFrame,
    schedules: pl.DataFrame,
    player_stats: pl.DataFrame
) -> pl.DataFrame:
    """Apply all feature engineering transformations."""
    print("\n[3/5] Engineering features...")

    # Category 1: Team Tendencies (historical pass rates by situation)
    print("   → Team tendency features...")
    pbp = add_team_tendency_features(pbp)

    # Category 2: Momentum (rolling drive/play success)
    print("   → Momentum features...")
    pbp = add_momentum_features(pbp)

    # Category 3: Fatigue (tempo, snap counts)
    print("   → Fatigue features...")
    pbp = add_fatigue_features(pbp)

    # Category 4: Personnel (defensive alignment)
    print("   → Personnel features...")
    pbp = add_personnel_features(pbp, participation)

    # Category 5: Context (weather, venue)
    print("   → Context features...")
    pbp = add_context_features(pbp, schedules)

    # Category 6: Player Performance (NEW - player efficiency stats)
    print("   → Player performance features (NEW)...")
    pbp = add_player_performance_features(pbp, player_stats)

    # Category 7: Situational (basic flags)
    print("   → Situational features...")
    pbp = add_situational_features(pbp)

    return pbp


def select_final_features(pbp: pl.DataFrame) -> pl.DataFrame:
    """Select final feature set and clean data."""
    print("\n[4/5] Selecting final features...")

    # Core features
    core_features = [
        # Identifiers
        'game_id', 'play_id', 'posteam', 'defteam', 'week',
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
    pbp_final_clean = pbp_final.drop_nulls()

    print(f"   ✓ Total features: {len(all_features)}")
    print(f"   ✓ After dropping nulls: {pbp_final_clean.height:,} plays")

    return pbp_final_clean, all_features


def save_features(pbp: pl.DataFrame, all_features: list, season: int):
    """Save engineered features and summary."""
    print("\n[5/5] Saving features...")

    # Save feature data
    output_path = OUTPUT_DIR / f"dc_features_{season}.parquet"
    pbp.write_parquet(output_path)
    print(f"   ✓ Features saved: {output_path}")

    # Save feature summary
    summary_path = OUTPUT_DIR / f"feature_summary_{season}.txt"
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

    print(f"   ✓ Summary saved: {summary_path}")


def main():
    """Main feature engineering pipeline."""
    print("=" * 80)
    print("DC FEATURE ENGINEERING - MODULAR VERSION")
    print("=" * 80)

    # Load data
    pbp, participation, schedules, player_stats = load_cached_data(SEASON)

    # Prepare data
    pbp = prepare_data(pbp)

    # Engineer features
    pbp = engineer_features(pbp, participation, schedules, player_stats)

    # Select final features
    pbp_final, all_features = select_final_features(pbp)

    # Save
    save_features(pbp_final, all_features, SEASON)

    print("\n" + "=" * 80)
    print("FEATURE ENGINEERING COMPLETE!")
    print("=" * 80)
    print(f"\nFeatures saved to: {OUTPUT_DIR / f'dc_features_{SEASON}.parquet'}")
    print(f"Summary saved to: {OUTPUT_DIR / f'feature_summary_{SEASON}.txt'}")
    print("\n✓ Ready for model training!")


if __name__ == "__main__":
    main()
