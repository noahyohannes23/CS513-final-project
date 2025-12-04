# NFL Play Type Prediction: A Defensive Coordinator's Perspective

**CS513 Final Project - Machine Learning**

## Project Overview

This project predicts offensive play calling (run vs. pass) from a defensive coordinator's perspective using NFL play-by-play data. The model leverages **5 seasons of data (2021-2025)** with **temporal train/test splitting** to simulate real-world prediction of future games.

**Key Achievement**: **76.6% test accuracy** predicting 2025 playoff-race games (weeks 11-13) after training on historical data, using XGBoost with 68 engineered features.

### What Makes This Project Unique?

1. **Temporal Split (Best Practice)**:
   - Training: 2021-2024 full seasons + 2025 weeks 1-10
   - Test: 2025 weeks 11-13 (genuinely future games)
   - No temporal leakage - simulates real-world deployment

2. **Multi-Season Training**:
   - 159,243 training plays across 5 seasons
   - Robust to year-over-year NFL meta shifts
   - Production-ready generalization

3. **Modular Feature Engineering**:
   - 68 features across 7 categories
   - Clean architecture: each category in separate module
   - Easy to extend and maintain

4. **Defensive Coordinator Perspective**:
   - Features focus on pre-snap information only
   - Team tendencies, momentum, fatigue, context
   - No data leakage from post-snap outcomes

## Repository Structure

```
test-1/
├── src/
│   ├── data/
│   │   ├── data_loading.py              # Multi-season data fetching with caching
│   │   ├── feature_engineering_v2.py    # Modular feature orchestration
│   │   └── feature_builders/            # Modular feature generation
│   │       ├── team_tendencies.py       # Historical pass rates by situation
│   │       ├── momentum.py              # Rolling drive/play success
│   │       ├── fatigue.py               # Tempo and snap count indicators
│   │       ├── personnel.py             # Defensive alignment features (disabled)
│   │       ├── context.py               # Weather and venue conditions
│   │       ├── player_performance.py    # Player efficiency (disabled - has bias)
│   │       └── situational.py           # Basic game situation flags
│   ├── models/
│   │   └── train_models.py              # Model training with temporal split
│   └── utils/
│       └── visualization.py             # Dataset documentation generator
│
├── data/
│   ├── cache/                           # Cached raw data (gitignored)
│   │   ├── pbp_2021.parquet             # 49,922 plays
│   │   ├── pbp_2022.parquet             # 49,434 plays
│   │   ├── pbp_2023.parquet             # 49,665 plays
│   │   ├── pbp_2024.parquet             # 49,492 plays
│   │   ├── pbp_2025.parquet             # 33,292 plays (weeks 1-13)
│   │   └── ... (participation, schedules, player_stats per season)
│   └── features/
│       ├── dc_features_2021-2025.parquet    # 164,741 plays, 110 features
│       └── feature_summary_2021-2025.txt
│
├── outputs/
│   ├── models/                          # Trained models
│   │   ├── random_forest_2021-2025.pkl
│   │   └── xgboost_2021-2025.pkl
│   ├── results/
│   │   └── model_comparison_2021-2025.txt
│   └── logs/                            # Data exploration reports
│
├── docs/
│   ├── FEATURES.md                      # Feature engineering details
│   ├── MODEL_OVERVIEW.md                # Model documentation
│   └── modular_feature_engineering.md   # Architecture deep dive
│
├── TEMPORAL_SPLIT_IMPLEMENTATION.md     # Temporal split guide
├── CLAUDE.md                            # Development instructions
├── .gitignore
├── environment.yml                      # Conda environment
└── README.md                            # This file
```

## Quick Start

### Installation

**Windows + Conda** (Recommended):
```bash
conda env create -f environment.yml
conda activate nfl-play-prediction
```

### Running the Pipeline

**IMPORTANT**: This project uses a custom conda environment on Windows. Always use the full Python path:

```bash
# Full path to Python executable
"C:\Users\Noah Yohannes\miniconda3\envs\nfl-play-prediction\python.exe"
```

#### 1. Load Multi-Season Data (~15-30 min first run)
```bash
"C:\Users\Noah Yohannes\miniconda3\envs\nfl-play-prediction\python.exe" src/data/data_loading.py
```
**What it does**:
- Downloads 2021-2025 NFL data from nflreadpy
- Caches to `data/cache/*.parquet` (71.7 MB total)
- Subsequent runs: instant (reads from cache)

#### 2. Engineer Features (~5-10 min)
```bash
"C:\Users\Noah Yohannes\miniconda3\envs\nfl-play-prediction\python.exe" src/data/feature_engineering_v2.py
```
**What it does**:
- Loads and concatenates 5 seasons
- Generates 68 features across 7 categories
- Saves to `data/features/dc_features_2021-2025.parquet`

#### 3. Train Models with Temporal Split (~5-10 min)
```bash
"C:\Users\Noah Yohannes\miniconda3\envs\nfl-play-prediction\python.exe" src/models/train_models.py
```
**What it does**:
- Splits temporally: Train on 2021-2024 + 2025 weeks 1-10
- Test on 2025 weeks 11-13
- Trains Logistic Regression, Random Forest, XGBoost
- Saves models to `outputs/models/*.pkl`

## Model Results

### Final Performance (Temporal Split)

| Model | Train Acc | Test Acc | AUC-ROC | Notes |
|-------|-----------|----------|---------|-------|
| Logistic Regression | 57.8% | 56.6% | 0.538 | Baseline (predicts all pass) |
| **Random Forest** | 78.9% | **75.2%** | 0.821 | Strong generalization |
| **XGBoost** | 79.2% | **76.6%** | 0.836 | **Best model** |

**Test Set**: 5,498 plays from 2025 weeks 11-13 (3.3% of data)
**Baseline**: 56.6% (naive "always predict pass")
**Improvement**: +20 percentage points over baseline

### Temporal Split Benefits

**Why temporal split instead of random 80/20?**

❌ **Random Split Issues**:
- Training on Week 17, testing on Week 1 (temporal leakage)
- Same-game plays in both train and test (autocorrelation)
- Overly optimistic accuracy (~75% but unrealistic)

✅ **Temporal Split Advantages**:
- Train on past, test on future (realistic)
- No leakage: test represents genuinely unseen games
- Honest evaluation: 76.6% is what you'd get in production

### Top Predictive Features (XGBoost)

1. **formation_shotgun** (41.5%) - Shotgun formation strongly indicates pass
2. **situation_two_minute** (5.7%) - Two-minute drill = pass-heavy
3. **drive_quarter_start** (4.9%) - Opening drive tendencies
4. **situation_passing_down** (4.4%) - 3rd & long, etc.
5. **situation_third_down** (4.0%) - Critical down situations

## Feature Engineering

### 7 Feature Categories (68 Total Features)

| Category | Features | Description | Examples |
|----------|----------|-------------|----------|
| **Team Tendencies** | 22 | Historical pass rates by situation | `team_pass_rate_3rd_long`, `team_pass_rate_red_zone` |
| **Momentum** | 23 | Rolling drive/play success | `momentum_epa_last_3`, `drive_total_yards` |
| **Fatigue** | 4 | Tempo and snap counts | `fatigue_fast_tempo`, `fatigue_total_offensive_snaps` |
| **Personnel** | 0 | Defensive alignment (disabled - data leakage) | ~~`personnel_defenders_in_box`~~ |
| **Context** | 9 | Weather, venue, rest | `context_temperature`, `context_wind` |
| **Player Performance** | 0 | Player efficiency (disabled - look-ahead bias) | ~~`qb_completion_pct`~~ |
| **Situational** | 10 | Basic game flags | `situation_third_down`, `situation_red_zone` |

**Note**: Personnel and Player Performance features currently disabled due to data quality issues. See `CLAUDE.md` for details.

### Modular Architecture

Each feature category lives in its own module (`src/data/feature_builders/`):

```python
# Example: team_tendencies.py
def add_team_tendency_features(pbp: pl.DataFrame) -> pl.DataFrame:
    """Add historical team pass rates by situation."""
    # Feature engineering logic
    return pbp  # Returns DataFrame with new columns added
```

**Benefits**:
- Each module < 100 lines, focused, testable
- Easy to add features: create module → export → integrate
- Clear separation: feature generation vs. I/O

See `docs/modular_feature_engineering.md` for architecture details.

## Data Sources

Uses `nflreadpy` for NFL data (2021-2025):

| Dataset | Rows (per season) | Key Features | Purpose |
|---------|-------------------|--------------|---------|
| Play-by-Play | ~49,000 | `down`, `ydstogo`, `epa`, `play_type` | Target variable + base features |
| Participation | ~46,000 | `ngs_position`, `personnel` | Personnel packages |
| Schedules | ~285 | `temp`, `wind`, `roof`, `surface` | Weather/venue context |
| Player Stats | ~19,000 | `completions`, `attempts`, `rushing_yards` | Player efficiency (currently disabled) |

**Total Data**: 231,805 plays → 165,394 run/pass plays after filtering

## Known Issues and Future Work

### Current Limitations

1. **Personnel Features Disabled**:
   - `defenders_in_box`, `pass_rushers` recorded post-snap (not pre-snap)
   - Caused 90%+ accuracy (data leakage red flag)
   - **Status**: Excluded from training

2. **Player Performance Disabled**:
   - Look-ahead bias: cumulative stats include current week
   - **Fix needed**: Use `week < current_week` instead of `week <= current_week`
   - **Expected impact**: +5-10pp accuracy once fixed

3. **Small Test Set**:
   - 5,498 plays for test (only 3 weeks of 2025)
   - Statistically valid but limited to late-season games
   - **Future**: Extend to full 2025 season once data available

### Future Improvements

1. **Fix Player Performance Features** (High Priority):
   - Remove look-ahead bias in `player_performance.py`
   - Expected: 76.6% → 80-85% test accuracy

2. **Multi-Season Validation**:
   - Train on 2021-2023, test on 2024 (full season)
   - Validate temporal generalization

3. **Situational Accuracy Analysis**:
   - Break down by 3rd down, red zone, two-minute drill
   - Identify which situations are most/least predictable

4. **Team-Specific Models**:
   - Which teams are most predictable?
   - Customize models per opponent

## Documentation

- **[TEMPORAL_SPLIT_IMPLEMENTATION.md](TEMPORAL_SPLIT_IMPLEMENTATION.md)**: Complete guide to temporal split implementation
- **[CLAUDE.md](CLAUDE.md)**: Development instructions and architecture details
- **[docs/modular_feature_engineering.md](docs/modular_feature_engineering.md)**: Feature builder architecture
- **[docs/FEATURES.md](docs/FEATURES.md)**: Comprehensive feature engineering plan
- **[docs/MODEL_OVERVIEW.md](docs/MODEL_OVERVIEW.md)**: Model setup and usage guide

## Technical Stack

- **Python**: 3.11
- **Data**: nflreadpy 0.1.5, polars 1.35.2, numpy 2.3.5
- **ML**: scikit-learn 1.7.2, xgboost 3.1.1
- **Viz**: matplotlib 3.10.7, seaborn 0.13.2
- **Environment**: Conda (Windows)

## Why This Matters

Understanding play calling has real-world applications:

- **For Defensive Coordinators**: Pre-snap preparation and personnel decisions
- **For Analytics Teams**: Automated scouting reports and tendency identification
- **For Sports Betting**: Situational play prediction models
- **For Machine Learning Education**:
  - Demonstrates importance of temporal split for time-series data
  - Shows how domain knowledge drives feature engineering
  - Illustrates data leakage detection and prevention
  - Addresses production-ready model evaluation

## Project Context

**Course**: CS513 - Machine Learning
**Focus**: Real-world sports analytics with best-practice evaluation
**Techniques**: Classification, temporal validation, ensemble methods, feature engineering

---

**License**: Educational Project
**Author**: Noah Yohannes
**Last Updated**: December 3, 2025

## Recent Updates

**December 3, 2025**:
- ✅ Implemented multi-season training (2021-2025)
- ✅ Switched from random split to temporal split
- ✅ Achieved 76.6% test accuracy (XGBoost) on future games
- ✅ Fixed data duplication bug in player performance features
- ✅ Validated temporal generalization (2025 weeks 11-13)
- ✅ Created comprehensive temporal split documentation
