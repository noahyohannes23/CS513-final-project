"""
Data Exploration with Caching - NFL Play Prediction
Goal: Explore all nflreadpy data sources efficiently with caching
Strategy: Load data once, cache to parquet, save exploration to text files
"""

import nflreadpy as nfl
import polars as pl
import os
from pathlib import Path
from datetime import datetime

# ============================================================================
# CACHING INFRASTRUCTURE
# ============================================================================

# Updated paths for new structure
CACHE_DIR = Path("./data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_DIR = Path("./outputs/logs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_cache_path(data_type, season=None):
    """Generate cache file path"""
    if season:
        return CACHE_DIR / f"{data_type}_{season}.parquet"
    return CACHE_DIR / f"{data_type}.parquet"

def load_with_cache(data_type, load_func, season=None, force_reload=False):
    """
    Load data with caching support

    Args:
        data_type: Name of data type (e.g., 'pbp', 'participation')
        load_func: Function to call if cache miss
        season: Season year if applicable
        force_reload: Force reload from API even if cached

    Returns:
        Polars DataFrame
    """
    cache_path = get_cache_path(data_type, season)

    # Check if cache exists and we're not forcing reload
    if cache_path.exists() and not force_reload:
        print(f"   [CACHE HIT] Loading {data_type} from cache: {cache_path}")
        try:
            return pl.read_parquet(cache_path)
        except Exception as e:
            print(f"   [CACHE ERROR] Failed to read cache, reloading: {e}")

    # Cache miss or forced reload
    print(f"   [CACHE MISS] Loading {data_type} from API...")
    data = load_func()

    # Save to cache
    try:
        data.write_parquet(cache_path)
        print(f"   [CACHED] Saved to {cache_path}")
    except Exception as e:
        print(f"   [WARNING] Could not cache data: {e}")

    return data

# ============================================================================
# EXPLORATION HELPER FUNCTIONS
# ============================================================================

def explore_dataframe(df, name, output_file):
    """
    Comprehensive DataFrame exploration, save to file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"EXPLORATION: {name}\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write("=" * 80 + "\n\n")

        # Basic info
        f.write(f"Shape: {df.shape}\n")
        f.write(f"Rows: {df.height:,}\n")
        f.write(f"Columns: {df.width}\n")
        f.write(f"Memory: {df.estimated_size('mb'):.2f} MB\n\n")

        # Column list
        f.write("COLUMNS:\n")
        f.write("-" * 80 + "\n")
        for i, col in enumerate(df.columns, 1):
            dtype = df[col].dtype
            null_count = df[col].null_count()
            null_pct = (null_count / df.height * 100) if df.height > 0 else 0
            f.write(f"{i:3d}. {col:40s} {str(dtype):15s} ({null_count:,} nulls, {null_pct:.1f}%)\n")

        # Sample data (first 5 rows)
        f.write("\n" + "=" * 80 + "\n")
        f.write("SAMPLE DATA (First 5 rows):\n")
        f.write("=" * 80 + "\n")
        f.write(str(df.head(5)) + "\n")

        # Key statistics for numeric columns
        numeric_cols = [col for col in df.columns if df[col].dtype in [pl.Int64, pl.Int32, pl.Float64, pl.Float32]]
        if numeric_cols:
            f.write("\n" + "=" * 80 + "\n")
            f.write("NUMERIC COLUMN STATISTICS:\n")
            f.write("=" * 80 + "\n")
            try:
                f.write(str(df.select(numeric_cols).describe()) + "\n")
            except:
                f.write("(Could not generate statistics)\n")

    print(f"   [SAVED] Exploration saved to {output_file}")

# ============================================================================
# MAIN EXPLORATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("NFL DATA EXPLORATION WITH CACHING - MULTI-SEASON")
    print("=" * 80)

    # Multi-season support for temporal split training
    SEASONS = [2021, 2022, 2023, 2024, 2025]

    print(f"\nSeasons to load: {SEASONS}")
    print("=" * 80)

    # Loop through all seasons and cache data
    for season_idx, SEASON in enumerate(SEASONS, 1):
        print(f"\n{'='*80}")
        print(f"LOADING SEASON {SEASON} ({season_idx}/{len(SEASONS)})")
        print(f"{'='*80}")

        # ----------------------------------------------------------------------------
        # 1. PLAY-BY-PLAY DATA (Already explored, but cache it)
        # ----------------------------------------------------------------------------
        print("\n[1/9] Play-by-Play Data")
        pbp = load_with_cache('pbp', lambda: nfl.load_pbp(SEASON), SEASON)

        # Only save exploration for first season to avoid clutter
        if season_idx == 1:
            explore_dataframe(pbp, f"Play-by-Play {SEASON}", OUTPUT_DIR / "01_pbp_exploration.txt")

        # ----------------------------------------------------------------------------
        # 2. PARTICIPATION DATA (Who was on field for each play)
        # ----------------------------------------------------------------------------
        print("\n[2/9] Participation Data")
        try:
            participation = load_with_cache('participation', lambda: nfl.load_participation(SEASON), SEASON)

            if season_idx == 1:
                explore_dataframe(participation, f"Participation {SEASON}", OUTPUT_DIR / "02_participation_exploration.txt")

            # Extra analysis: count players per play (only for first season)
            if season_idx == 1:
                with open(OUTPUT_DIR / "02_participation_exploration.txt", 'a', encoding='utf-8') as f:
                    f.write("\n" + "=" * 80 + "\n")
                    f.write("PARTICIPATION ANALYSIS:\n")
                    f.write("=" * 80 + "\n")
                    if 'nfl_id' in participation.columns and 'play_id' in participation.columns:
                        players_per_play = participation.group_by('play_id').agg(pl.col('nfl_id').count().alias('num_players'))
                        f.write(f"Average players per play: {players_per_play['num_players'].mean():.1f}\n")
                        f.write(str(players_per_play.describe()) + "\n")
        except Exception as e:
            print(f"   [ERROR] Could not load participation: {e}")

        # ----------------------------------------------------------------------------
        # 3. SCHEDULES DATA (Game context: weather, venue, etc.)
        # ----------------------------------------------------------------------------
        print("\n[3/9] Schedules Data")
        try:
            schedules = load_with_cache('schedules', lambda: nfl.load_schedules(SEASON), SEASON)
            if season_idx == 1:
                explore_dataframe(schedules, f"Schedules {SEASON}", OUTPUT_DIR / "04_schedules_exploration.txt")
        except Exception as e:
            print(f"   [ERROR] Could not load schedules: {e}")

        # ----------------------------------------------------------------------------
        # 4. PLAYER STATS DATA (Weekly individual performance)
        # ----------------------------------------------------------------------------
        print("\n[4/9] Player Stats Data (Weekly)")
        try:
            player_stats = load_with_cache('player_stats', lambda: nfl.load_player_stats(SEASON, 'week'), SEASON)
            if season_idx == 1:
                explore_dataframe(player_stats, f"Player Stats {SEASON}", OUTPUT_DIR / "09_player_stats_exploration.txt")
        except Exception as e:
            print(f"   [ERROR] Could not load player stats: {e}")

        # Optional: Load other datasets if needed for future features
        # For now, we'll skip injuries, rosters, snap_counts, depth_charts, nextgen
        # to speed up the data loading process. Uncomment if you need them:

        # print("\n[5/9] Injuries Data")
        # try:
        #     injuries = load_with_cache('injuries', lambda: nfl.load_injuries(SEASON), SEASON)
        # except Exception as e:
        #     print(f"   [ERROR] Could not load injuries: {e}")

        print(f"\n[OK] Season {SEASON} data cached successfully")

    print("\n" + "=" * 80)
    print("MULTI-SEASON DATA LOADING COMPLETE!")
    print("=" * 80)
    print(f"\nSeasons loaded: {SEASONS}")
    print(f"Cached data saved to: {CACHE_DIR}")
    print(f"Exploration reports saved to: {OUTPUT_DIR}")
    print("\nCache files by season:")
    for season in SEASONS:
        season_files = sorted(CACHE_DIR.glob(f"*_{season}.parquet"))
        if season_files:
            print(f"\n  Season {season}:")
            for cache_file in season_files:
                size_mb = cache_file.stat().st_size / (1024 * 1024)
                print(f"    - {cache_file.name:40s} ({size_mb:.2f} MB)")

    # Summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY:")
    total_files = len(list(CACHE_DIR.glob("*.parquet")))
    total_size = sum(f.stat().st_size for f in CACHE_DIR.glob("*.parquet")) / (1024 * 1024)
    print(f"  Total cache files: {total_files}")
    print(f"  Total cache size: {total_size:.2f} MB")
    print(f"  Ready for multi-season feature engineering!")
    print("=" * 80)
