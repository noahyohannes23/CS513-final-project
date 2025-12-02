"""
Explore advanced features in play-by-play data:
- Detailed play types (pass types, run types)
- Player information
- Situational details
"""

import nflreadpy as nfl
import polars as pl

print("=" * 70)
print("ADVANCED FEATURE EXPLORATION")
print("=" * 70)

# Load data
print("\n[1] Loading 2023 play-by-play data...")
pbp = nfl.load_pbp(2023)
print(f"   Total columns: {len(pbp.columns)}")

# Filter for run/pass plays
pbp_plays = pbp.filter(
    (pl.col('play_type') == 'run') | (pl.col('play_type') == 'pass')
)
print(f"   Total run/pass plays: {pbp_plays.height:,}")

# ============================================================================
# PLAY TYPE DETAILS
# ============================================================================
print("\n" + "=" * 70)
print("PLAY TYPE DETAILS")
print("=" * 70)

# Pass play details
print("\n[2] PASS PLAY SUBTYPES:")
pass_cols = [col for col in pbp.columns if 'pass' in col.lower()]
print(f"   Found {len(pass_cols)} pass-related columns")

# Pass length (short, deep, etc.)
if 'pass_length' in pbp.columns:
    print("\n   Pass Length Distribution:")
    pass_plays = pbp_plays.filter(pl.col('play_type') == 'pass')
    pass_length_counts = pass_plays['pass_length'].value_counts()
    for row in pass_length_counts.iter_rows():
        val, count = row
        if val is not None:
            print(f"      {str(val):20s} - {count:,}")

# Pass location (left, middle, right)
if 'pass_location' in pbp.columns:
    print("\n   Pass Location Distribution:")
    pass_location_counts = pass_plays['pass_location'].value_counts()
    for row in pass_location_counts.iter_rows():
        val, count = row
        if val is not None:
            print(f"      {str(val):20s} - {count:,}")

# Run play details
print("\n[3] RUN PLAY SUBTYPES:")
run_cols = [col for col in pbp.columns if 'run' in col.lower() or 'rush' in col.lower()]
print(f"   Found {len(run_cols)} run-related columns")

# Run location
if 'run_location' in pbp.columns:
    print("\n   Run Location Distribution:")
    run_plays = pbp_plays.filter(pl.col('play_type') == 'run')
    run_location_counts = run_plays['run_location'].value_counts()
    for row in run_location_counts.iter_rows():
        val, count = row
        if val is not None:
            print(f"      {str(val):20s} - {count:,}")

# Run gap
if 'run_gap' in pbp.columns:
    print("\n   Run Gap Distribution:")
    run_gap_counts = run_plays['run_gap'].value_counts()
    for row in run_gap_counts.iter_rows():
        val, count = row
        if val is not None:
            print(f"      {str(val):20s} - {count:,}")

# ============================================================================
# PLAYER INFORMATION
# ============================================================================
print("\n" + "=" * 70)
print("PLAYER INFORMATION")
print("=" * 70)

print("\n[4] PLAYER-RELATED COLUMNS:")
player_cols = [col for col in pbp.columns if 'player' in col.lower()]
print(f"   Found {len(player_cols)} player-related columns:")
for i, col in enumerate(player_cols[:20], 1):
    print(f"      {i:2d}. {col}")

# Passer information
if 'passer_player_name' in pbp.columns:
    print("\n[5] TOP 10 PASSERS (by attempts):")
    passer_counts = pass_plays['passer_player_name'].value_counts().head(10)
    for row in passer_counts.iter_rows():
        name, count = row
        if name is not None:
            print(f"      {str(name):30s} - {count:,} attempts")

# Rusher information
if 'rusher_player_name' in pbp.columns:
    print("\n[6] TOP 10 RUSHERS (by attempts):")
    rusher_counts = run_plays['rusher_player_name'].value_counts().head(10)
    for row in rusher_counts.iter_rows():
        name, count = row
        if name is not None:
            print(f"      {str(name):30s} - {count:,} attempts")

# Receiver information
if 'receiver_player_name' in pbp.columns:
    print("\n[7] TOP 10 RECEIVERS (by targets):")
    receiver_counts = pass_plays['receiver_player_name'].value_counts().head(10)
    for row in receiver_counts.iter_rows():
        name, count = row
        if name is not None:
            print(f"      {str(name):30s} - {count:,} targets")

# ============================================================================
# ADVANCED METRICS
# ============================================================================
print("\n" + "=" * 70)
print("ADVANCED METRICS AVAILABLE")
print("=" * 70)

print("\n[8] EPA (Expected Points Added):")
epa_cols = [col for col in pbp.columns if 'epa' in col.lower()]
print(f"   Found {len(epa_cols)} EPA-related columns:")
for col in epa_cols[:10]:
    print(f"      - {col}")

print("\n[9] WPA (Win Probability Added):")
wpa_cols = [col for col in pbp.columns if 'wpa' in col.lower()]
print(f"   Found {len(wpa_cols)} WPA-related columns:")
for col in wpa_cols[:10]:
    print(f"      - {col}")

print("\n[10] Air Yards and YAC (Yards After Catch):")
air_yac_cols = [col for col in pbp.columns if any(x in col.lower() for x in ['air', 'yac', 'yards_after'])]
print(f"   Found {len(air_yac_cols)} air yards/YAC columns:")
for col in air_yac_cols[:10]:
    print(f"      - {col}")

# ============================================================================
# SITUATIONAL FEATURES
# ============================================================================
print("\n" + "=" * 70)
print("SITUATIONAL FEATURES")
print("=" * 70)

print("\n[11] Formation and Personnel:")
formation_cols = [col for col in pbp.columns if any(x in col.lower() for x in ['formation', 'personnel', 'shotgun', 'no_huddle'])]
print(f"   Found {len(formation_cols)} formation/personnel columns:")
for col in formation_cols:
    print(f"      - {col}")

# Check shotgun
if 'shotgun' in pbp.columns:
    print("\n   Shotgun Usage:")
    shotgun_counts = pbp_plays['shotgun'].value_counts()
    for row in shotgun_counts.iter_rows():
        val, count = row
        print(f"      Shotgun={val}: {count:,} plays")

# Check no_huddle
if 'no_huddle' in pbp.columns:
    print("\n   No-Huddle Usage:")
    no_huddle_counts = pbp_plays['no_huddle'].value_counts()
    for row in no_huddle_counts.iter_rows():
        val, count = row
        print(f"      No-Huddle={val}: {count:,} plays")

# ============================================================================
# ADDITIONAL DATASETS
# ============================================================================
print("\n" + "=" * 70)
print("ADDITIONAL DATASETS AVAILABLE")
print("=" * 70)

print("\n[12] Loading additional player data...")

# Load player stats
try:
    player_stats = nfl.load_player_stats(2023)
    print(f"\n   Player Stats Dataset:")
    print(f"      Rows: {player_stats.height:,}")
    print(f"      Columns: {len(player_stats.columns)}")
    print(f"      Sample columns: {player_stats.columns[:10]}")
except Exception as e:
    print(f"   Error loading player stats: {e}")

# Load NextGen Stats
try:
    nextgen = nfl.load_nextgen_stats(2023)
    print(f"\n   NextGen Stats Dataset:")
    print(f"      Rows: {nextgen.height:,}")
    print(f"      Columns: {len(nextgen.columns)}")
    print(f"      Sample columns: {nextgen.columns[:10]}")
except Exception as e:
    print(f"   Error loading NextGen stats: {e}")

print("\n" + "=" * 70)
print("EXPLORATION COMPLETE!")
print("=" * 70)

print("\nPOSSIBLE ADVANCED ANALYSES:")
print("1. Predict pass type (short/deep, left/middle/right)")
print("2. Predict run direction (left/middle/right)")
print("3. Predict specific rusher/receiver on a play")
print("4. Analyze QB tendencies (shotgun %, pass location preferences)")
print("5. Analyze RB styles (inside/outside runner)")
print("6. Predict EPA or success rate of plays")
print("7. Model impact of specific players on play calling")
print("8. Cluster QBs/RBs by playing style")
