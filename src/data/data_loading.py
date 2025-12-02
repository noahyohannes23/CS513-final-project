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
    print("NFL DATA EXPLORATION WITH CACHING")
    print("=" * 80)

    SEASON = 2023

    # ----------------------------------------------------------------------------
    # 1. PLAY-BY-PLAY DATA (Already explored, but cache it)
    # ----------------------------------------------------------------------------
    print("\n[1/8] Play-by-Play Data")
    pbp = load_with_cache('pbp', lambda: nfl.load_pbp(SEASON), SEASON)
    explore_dataframe(pbp, f"Play-by-Play {SEASON}", OUTPUT_DIR / "01_pbp_exploration.txt")

    # ----------------------------------------------------------------------------
    # 2. PARTICIPATION DATA (Who was on field for each play)
    # ----------------------------------------------------------------------------
    print("\n[2/8] Participation Data")
    try:
        participation = load_with_cache('participation', lambda: nfl.load_participation(SEASON), SEASON)
        explore_dataframe(participation, f"Participation {SEASON}", OUTPUT_DIR / "02_participation_exploration.txt")

        # Extra analysis: count players per play
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
    # 3. INJURIES DATA (Player availability)
    # ----------------------------------------------------------------------------
    print("\n[3/8] Injuries Data")
    try:
        injuries = load_with_cache('injuries', lambda: nfl.load_injuries(SEASON), SEASON)
        explore_dataframe(injuries, f"Injuries {SEASON}", OUTPUT_DIR / "03_injuries_exploration.txt")

        # Extra analysis: injury status distribution
        with open(OUTPUT_DIR / "03_injuries_exploration.txt", 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write("INJURY STATUS DISTRIBUTION:\n")
            f.write("=" * 80 + "\n")
            if 'game_status' in injuries.columns:
                status_counts = injuries['game_status'].value_counts()
                f.write(str(status_counts) + "\n")
    except Exception as e:
        print(f"   [ERROR] Could not load injuries: {e}")

    # ----------------------------------------------------------------------------
    # 4. SCHEDULES DATA (Game context: weather, venue, etc.)
    # ----------------------------------------------------------------------------
    print("\n[4/8] Schedules Data")
    try:
        schedules = load_with_cache('schedules', lambda: nfl.load_schedules(SEASON), SEASON)
        explore_dataframe(schedules, f"Schedules {SEASON}", OUTPUT_DIR / "04_schedules_exploration.txt")

        # Extra analysis: game types
        with open(OUTPUT_DIR / "04_schedules_exploration.txt", 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write("SCHEDULE ANALYSIS:\n")
            f.write("=" * 80 + "\n")
            if 'roof' in schedules.columns:
                roof_counts = schedules['roof'].value_counts()
                f.write("Roof types:\n")
                f.write(str(roof_counts) + "\n\n")
            if 'gameday' in schedules.columns:
                gameday_counts = schedules['gameday'].value_counts()
                f.write("Game days:\n")
                f.write(str(gameday_counts.head(10)) + "\n")
    except Exception as e:
        print(f"   [ERROR] Could not load schedules: {e}")

    # ----------------------------------------------------------------------------
    # 5. ROSTERS DATA (Team composition)
    # ----------------------------------------------------------------------------
    print("\n[5/8] Rosters Data")
    try:
        rosters = load_with_cache('rosters', lambda: nfl.load_rosters(SEASON), SEASON)
        explore_dataframe(rosters, f"Rosters {SEASON}", OUTPUT_DIR / "05_rosters_exploration.txt")

        # Extra analysis: position distribution
        with open(OUTPUT_DIR / "05_rosters_exploration.txt", 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write("ROSTER ANALYSIS:\n")
            f.write("=" * 80 + "\n")
            if 'position' in rosters.columns:
                pos_counts = rosters['position'].value_counts()
                f.write("Position distribution:\n")
                f.write(str(pos_counts) + "\n")
    except Exception as e:
        print(f"   [ERROR] Could not load rosters: {e}")

    # ----------------------------------------------------------------------------
    # 6. SNAP COUNTS DATA (Playing time)
    # ----------------------------------------------------------------------------
    print("\n[6/8] Snap Counts Data")
    try:
        snap_counts = load_with_cache('snap_counts', lambda: nfl.load_snap_counts(SEASON), SEASON)
        explore_dataframe(snap_counts, f"Snap Counts {SEASON}", OUTPUT_DIR / "06_snap_counts_exploration.txt")

        # Extra analysis: snap percentage distribution
        with open(OUTPUT_DIR / "06_snap_counts_exploration.txt", 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write("SNAP COUNT ANALYSIS:\n")
            f.write("=" * 80 + "\n")
            if 'offense_pct' in snap_counts.columns:
                f.write(str(snap_counts['offense_pct'].describe()) + "\n")
    except Exception as e:
        print(f"   [ERROR] Could not load snap_counts: {e}")

    # ----------------------------------------------------------------------------
    # 7. DEPTH CHARTS DATA (Starting lineups)
    # ----------------------------------------------------------------------------
    print("\n[7/8] Depth Charts Data")
    try:
        depth_charts = load_with_cache('depth_charts', lambda: nfl.load_depth_charts(SEASON), SEASON)
        explore_dataframe(depth_charts, f"Depth Charts {SEASON}", OUTPUT_DIR / "07_depth_charts_exploration.txt")

        # Extra analysis: depth distribution
        with open(OUTPUT_DIR / "07_depth_charts_exploration.txt", 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write("DEPTH CHART ANALYSIS:\n")
            f.write("=" * 80 + "\n")
            if 'depth_team' in depth_charts.columns:
                depth_counts = depth_charts['depth_team'].value_counts()
                f.write("Depth position distribution:\n")
                f.write(str(depth_counts.head(10)) + "\n")
    except Exception as e:
        print(f"   [ERROR] Could not load depth_charts: {e}")

    # ----------------------------------------------------------------------------
    # 8. NEXTGEN STATS DATA (Advanced metrics)
    # ----------------------------------------------------------------------------
    print("\n[8/8] NextGen Stats Data (Passing)")
    try:
        nextgen_pass = load_with_cache('nextgen_pass', lambda: nfl.load_nextgen_stats(SEASON, 'passing'), SEASON)
        explore_dataframe(nextgen_pass, f"NextGen Passing Stats {SEASON}", OUTPUT_DIR / "08_nextgen_pass_exploration.txt")
    except Exception as e:
        print(f"   [ERROR] Could not load nextgen passing stats: {e}")

    print("\n" + "=" * 80)
    print("EXPLORATION COMPLETE!")
    print("=" * 80)
    print(f"\nCached data saved to: {CACHE_DIR}")
    print(f"Exploration reports saved to: {OUTPUT_DIR}")
    print("\nCache files:")
    for cache_file in sorted(CACHE_DIR.glob("*.parquet")):
        size_mb = cache_file.stat().st_size / (1024 * 1024)
        print(f"  - {cache_file.name:40s} ({size_mb:.2f} MB)")
    print("\nExploration reports:")
    for report_file in sorted(OUTPUT_DIR.glob("*.txt")):
        print(f"  - {report_file.name}")
