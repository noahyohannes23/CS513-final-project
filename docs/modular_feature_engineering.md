# Modular Feature Engineering Architecture

## Overview

The feature engineering codebase has been refactored into a modular architecture that separates feature generation logic from I/O operations. This improves:
- **Maintainability**: Each feature category in its own module
- **Testability**: Individual components can be tested in isolation
- **Extensibility**: Easy to add new feature categories
- **Readability**: Clear separation of concerns

## Architecture

```
src/data/
├── data_loading.py              # Data loading with caching
├── feature_engineering.py       # Original monolithic version
├── feature_engineering_v2.py    # NEW: Modular orchestration script
└── feature_builders/            # NEW: Modular feature generation
    ├── __init__.py              # Package exports
    ├── team_tendencies.py       # Team historical pass/run tendencies
    ├── momentum.py              # Rolling drive/play momentum
    ├── fatigue.py               # Tempo and snap count indicators
    ├── personnel.py             # Defensive alignment features
    ├── context.py               # Weather and venue features
    ├── player_performance.py    # NEW: Player efficiency stats
    └── situational.py           # Basic situational flags
```

## Feature Categories

### 1. Team Tendencies (`team_tendencies.py`)
**Purpose**: Capture how teams historically call plays in different situations

**Key Features**:
- Overall team pass rate
- Pass rate by down (1st, 2nd, 3rd, 4th)
- Pass rate by distance (short, medium, long)
- Pass rate by field position (own territory, midfield, opponent territory, red zone, goal line)
- Pass rate by score situation (trailing, tied, leading)
- Special situations (two-minute drill, 4th quarter)

**Rationale**: Defensive coordinators study opponent tendencies. Teams that pass 70% on 3rd-and-long are predictable.

### 2. Momentum (`momentum.py`)
**Purpose**: Capture "hot hand" effects and drive momentum

**Key Features**:
- Success rate in last 3 plays
- EPA in last 3 plays
- Explosive plays (10+ yards) in last 5 plays
- Drive statistics (total yards, play count, first downs, EPA)
- Yards per play on current drive

**Rationale**: Teams ride momentum. A drive with 3 successful plays is more likely to keep doing what works.

### 3. Fatigue (`fatigue.py`)
**Purpose**: Identify tempo and fatigue indicators

**Key Features**:
- Seconds since last play (tempo indicator)
- Fast tempo flag (< 20 seconds between plays)
- Total offensive snaps so far in game
- Recent play count (rolling 10-play window)
- No-huddle indicator
- Shotgun formation

**Rationale**: Up-tempo offenses (< 20 sec between plays) favor passing. Fatigued defenses are exploitable.

### 4. Personnel (`personnel.py`)
**Purpose**: Defensive alignment signals expected play type

**Key Features**:
- Defenders in box count
- Light box indicator (< 6 defenders)
- Heavy box indicator (8+ defenders)
- Number of pass rushers

**Rationale**: 8+ defenders in the box strongly signals run expectation. Light boxes favor passing.

### 5. Context (`context.py`)
**Purpose**: Environmental factors that influence play calling

**Key Features**:
- Venue type (outdoor, dome)
- Weather conditions (temperature, wind)
- Cold weather flag (< 40°F)
- High wind flag (> 15 mph)
- Surface type (grass vs. turf)
- Division game indicator
- Team rest days

**Rationale**: Poor weather (cold, wind) favors running. Short rest favors simpler play calls.

### 6. Player Performance (`player_performance.py`) **NEW**
**Purpose**: Individual player efficiency and "hot hand" indicators

**Key Features**:

**QB Performance**:
- Completion percentage (season-to-date)
- Yards per attempt
- TD/INT ratio

**RB Performance**:
- Yards per carry
- Rushing TDs per game

**WR/TE Performance**:
- Catch rate
- Yards per reception
- Targets per game

**Rationale**: Offenses feed hot players. A QB completing 75% goes to the air. An RB averaging 6 yards/carry gets more touches. This was the **missing ingredient** in the original 60% accuracy model.

### 7. Situational (`situational.py`)
**Purpose**: Basic game situation flags

**Key Features**:
- Short yardage (≤ 3 yards)
- Long distance (≥ 7 yards)
- Red zone, goal line
- Passing downs (3rd/4th)
- Third down specifically
- Winning/losing/tied
- Two-minute drill, fourth quarter

**Rationale**: 3rd-and-15 = obvious passing down. Goal line = run heavy.

## Usage

### Running the Modular Pipeline

1. **First, ensure data is cached** (only needed once per season):
```bash
python src/data/data_loading.py
```

This caches:
- Play-by-play data
- Participation data
- Schedules
- **Player stats (NEW)**

2. **Run modular feature engineering**:
```bash
python src/data/feature_engineering_v2.py
```

This generates:
- `data/features/dc_features_2023.parquet` - Feature matrix ready for modeling
- `data/features/feature_summary_2023.txt` - Human-readable feature list

### Adding New Feature Categories

1. **Create new module** in `src/data/feature_builders/`:
```python
# example_features.py
import polars as pl

def add_example_features(pbp: pl.DataFrame) -> pl.DataFrame:
    """Add example features."""
    return pbp.with_columns([
        # Your features here
        pl.col('some_column').alias('example_feature_1'),
    ])
```

2. **Update `__init__.py`**:
```python
from .example_features import add_example_features

__all__ = [
    # ... existing exports
    'add_example_features',
]
```

3. **Add to orchestration** in `feature_engineering_v2.py`:
```python
from feature_builders import (
    # ... existing imports
    add_example_features,
)

# In engineer_features():
pbp = add_example_features(pbp)
```

## Player Stats Integration

### Data Source
- **Function**: `nflreadpy.load_player_stats(season, summary_level='week')`
- **Granularity**: Weekly player statistics
- **Columns**: ~50+ statistical categories per player per week

### Why Player Stats Matter

**Original Model Performance**: 60% accuracy
- Had team tendencies, momentum, fatigue, etc.
- Missing: **Individual player performance**

**Hypothesis**: Offenses exploit player matchups and efficiency
- Hot RB (6 YPC) → More rushes
- Struggling QB (45% completion) → More conservative calls
- Star WR getting open → More targets

**Expected Impact**: Player efficiency features should capture game-level dynamics that team-level aggregates miss.

### Season-to-Season Generalization

**Problem**: Training on 2023, testing on 2024 may be inaccurate due to:
- Coaching turnover (new offensive coordinators)
- Rule changes
- League-wide meta shifts (e.g., RPO trends)
- Personnel changes

**Solutions Implemented**:

1. **Multi-season training**:
   - Easy to modify `SEASON` to list: `SEASONS = [2021, 2022, 2023]`
   - Concatenate features before training

2. **Player-level features**:
   - More stable across seasons than team tendencies
   - Player efficiency transcends coaching philosophy

3. **Cumulative stats approach**:
   - Season-to-date stats avoid look-ahead bias
   - Rolling 3-game windows could be added for recent form

**Recommended**: Train on 2-3 recent seasons, retrain annually

## File Structure

```
data/
├── cache/                       # Cached raw data (parquet)
│   ├── pbp_2023.parquet
│   ├── participation_2023.parquet
│   ├── schedules_2023.parquet
│   ├── player_stats_2023.parquet  # NEW
│   └── ...
└── features/                    # Engineered features
    ├── dc_features_2023.parquet
    └── feature_summary_2023.txt

src/data/
├── data_loading.py              # Step 1: Load and cache data
├── feature_engineering_v2.py    # Step 2: Generate features (modular)
└── feature_builders/            # Feature generation modules
    └── *.py

outputs/logs/                    # Data exploration reports
├── 01_pbp_exploration.txt
├── 09_player_stats_exploration.txt  # NEW
└── ...
```

## Benefits of Modular Design

### Before (Monolithic)
- 500+ lines in single file
- Hard to debug specific feature categories
- Difficult to add new features
- Testing requires running entire pipeline
- Feature generation mixed with I/O

### After (Modular)
- Each module < 100 lines, focused on one category
- Easy to debug: test one module at a time
- Adding features: create new module, plug in
- Can test feature generation independently
- Clear separation: generate vs. save

## Testing Strategy

Test individual feature builders:
```python
import polars as pl
from feature_builders import add_momentum_features

# Mock data
pbp = pl.DataFrame({
    'game_id': [1, 1, 1],
    'play_id': [1, 2, 3],
    'drive': [1, 1, 1],
    'epa': [0.5, -0.2, 1.0],
    'yards_gained': [5, 2, 12],
})

# Test
result = add_momentum_features(pbp)
assert 'momentum_epa_last_3' in result.columns
```

## Next Steps

1. **Load player stats**: Run `python src/data/data_loading.py` (adds player_stats to cache)

2. **Generate features**: Run `python src/data/feature_engineering_v2.py`

3. **Train model**: Use `data/features/dc_features_2023.parquet`

4. **Compare performance**:
   - Baseline (original features): 60% accuracy
   - With player stats: Expected improvement to 65-70%

5. **Multi-season training**: Modify script to load 2021-2023, test generalization

## Troubleshooting

**Error**: `FileNotFoundError: player_stats_2023.parquet`
- **Solution**: Run `python src/data/data_loading.py` first

**Error**: `ModuleNotFoundError: No module named 'feature_builders'`
- **Solution**: Run from project root, not from `src/data/` directory

**Error**: `Missing columns in player_stats`
- **Solution**: Check `load_player_stats()` returns expected columns (completions, attempts, etc.)

## References

- nflreadpy documentation: [https://nflreadpy.nflverse.com](https://nflreadpy.nflverse.com)
- nflverse data dictionary: [https://nflreadr.nflverse.com/articles/](https://nflreadr.nflverse.com/articles/)
