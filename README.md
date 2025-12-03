# NFL Play Type Prediction: A Defensive Coordinator's Perspective

**CS513 Final Project - Machine Learning**

## Project Overview

This project aims to predict offensive play calling (run vs. pass) from a defensive coordinator's perspective using NFL play-by-play data, team tendencies, momentum indicators, fatigue metrics, and contextual features.

## Project Evolution

This project has gone through several iterations as the complexity and understanding deepened:

### Phase 1: Dataset Exploration (Initial Discovery)
The project began with a focus on understanding the available NFL data:
- Created visualization scripts to explore dataset schemas
- Generated HTML documentation for key datasets (participation, play-by-play)
- Examined 372 columns of play-by-play data and 26 columns of participation data
- Output: `outputs/visualizations/*.html` files for manual inspection

**Key Insight**: The NFL provides incredibly rich data, but understanding what features to use required hands-on exploration.

### Phase 2: Simple Baseline Models (First Attempt)
Built initial prediction models with basic features:
- Implemented simple logistic regression models (`play_type_model.py`, `play_type_prediction.py`)
- Used straightforward features: down, distance, field position, score differential
- Achieved baseline accuracy but quickly hit a ceiling

**Key Problem**: Test accuracy was too low (~65-70%). The model wasn't capturing the nuance of play calling.

### Phase 3: Advanced Feature Engineering (Current Focus)
Pivoted to a comprehensive feature engineering approach:
- Developed DC (Defensive Coordinator) perspective features
- Implemented caching system for efficient data reloading
- **Refactored into modular architecture** for maintainability and extensibility
- Created 90+ engineered features across **7 categories**:
  - **Team Tendencies** (21 features): Historical pass rates by situation
  - **Momentum** (23 features): Recent play success, drive efficiency
  - **Fatigue** (6 features): Snap counts, tempo indicators
  - **Personnel** (4 features): Who's on field, formation alignment
  - **Context** (9 features): Weather, venue, game type
  - **Situational** (10 features): Basic game situation flags
  - **Player Performance** (8+ features) **NEW**: Individual player efficiency stats
- Modular feature builder system in `src/data/feature_builders/`
- Engineered features now stored in `data/features/` for model training

**Current Status**: Modular feature engineering complete with player stats integration. Ready for advanced model development.

## Repository Structure

```
test-1/
├── src/
│   ├── data/
│   │   ├── data_loading.py          # Data fetching with caching (includes player stats)
│   │   ├── feature_engineering.py   # Original monolithic version
│   │   ├── feature_engineering_v2.py # NEW: Modular orchestration script
│   │   └── feature_builders/        # NEW: Modular feature generation
│   │       ├── __init__.py          # Package exports
│   │       ├── team_tendencies.py   # Team historical tendencies
│   │       ├── momentum.py          # Drive/play momentum features
│   │       ├── fatigue.py           # Tempo and snap count features
│   │       ├── personnel.py         # Defensive alignment features
│   │       ├── context.py           # Weather and venue features
│   │       ├── player_performance.py # NEW: Player efficiency stats
│   │       └── situational.py       # Basic situational flags
│   ├── utils/
│   │   ├── helpers.py               # Utility functions
│   │   └── visualization.py         # Dataset documentation generator
│   └── models/                      # (Future: Advanced ML models)
│
├── data/
│   ├── cache/                       # Cached raw data (gitignored)
│   │   ├── pbp_2023.parquet
│   │   ├── participation_2023.parquet
│   │   ├── schedules_2023.parquet
│   │   ├── player_stats_2023.parquet # NEW: Player weekly stats
│   │   └── ...
│   └── features/                    # Engineered features (parquet)
│       ├── dc_features_2023.parquet
│       └── feature_summary_2023.txt
│
├── outputs/
│   ├── visualizations/              # HTML dataset documentation
│   └── logs/                        # Execution logs and data exploration
│
├── docs/
│   ├── FEATURES.md                  # Feature engineering plan
│   ├── MODEL_OVERVIEW.md            # Detailed model documentation
│   └── modular_feature_engineering.md # NEW: Architecture documentation
│
├── .gitignore
├── requirements.txt
└── README.md                        # This file
```

## Quick Start

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Pipeline

#### 1. Load and Cache Data
```bash
python src/data/data_loading.py
```
- Fetches NFL data from nflreadpy (play-by-play, participation, schedules, **player stats**)
- Caches to `data/cache/` as parquet files (fast reloading)
- Generates exploration reports in `outputs/logs/`
- **NEW**: Caches weekly player statistics for efficiency features

#### 2. Engineer Features (Modular Version - Recommended)
```bash
python src/data/feature_engineering_v2.py
```
- Loads cached data
- Uses modular feature builders for clean, maintainable code
- Creates 90+ DC-perspective features including **player performance metrics**
- Saves engineered dataset to `data/features/dc_features_2023.parquet`
- Generates feature summary in `data/features/feature_summary_2023.txt`

**Alternative**: Original monolithic version still available
```bash
python src/data/feature_engineering.py  # Original version (no player stats)
```

#### 3. (Future) Train Models
```bash
# Coming soon: Advanced model training scripts
python src/models/train_dc_model.py
```

### Visualizing the Data
To regenerate HTML dataset documentation:
```bash
python src/utils/visualization.py
```
HTML files will be saved to `outputs/visualizations/`

## Key Features

### What Makes This Project Unique?

1. **Defensive Coordinator Perspective**: Unlike most play prediction models that use basic game state, this model thinks like a DC preparing for the next play.

2. **Comprehensive Feature Engineering**:
   - Team-specific tendencies (how often does Team X pass on 3rd & long?)
   - In-game momentum (success on last 3 plays)
   - Fatigue indicators (how many plays has offense run?)
   - Personnel matchups (who's on the field right now?)
   - **NEW**: Player performance metrics (QB efficiency, RB hot hands, WR targets)

3. **Modular Architecture**:
   - Feature builders separated into focused modules (team_tendencies, momentum, fatigue, etc.)
   - Easy to test, extend, and maintain
   - Clean separation of feature generation from I/O operations
   - Each feature category in its own module (~50-100 lines)

4. **Efficient Data Pipeline**:
   - Parquet caching reduces load time from 60s → 2s
   - Multi-season training support (handles 2021-2023 concatenation)
   - Year-agnostic code (easily switch seasons)

5. **Production-Ready Structure**:
   - Clear separation of concerns (data, features, models, utils)
   - Reproducible outputs
   - Comprehensive documentation (architecture, features, usage)
   - MCP documentation server integration for easy reference

## Data Sources

This project uses NFL data from `nflreadpy`, which provides:
- **Play-by-Play**: 49,000+ plays, 372 columns (EPA, WPA, success indicators)
- **Participation**: Who was on field for each play, personnel packages
- **Schedules**: Weather, venue, rest days
- **Player Stats** **NEW**: Weekly individual player performance (completions, yards, TDs, etc.)
- **Injuries**: Player availability by week
- **Snap Counts**: Playing time and fatigue indicators
- **NextGen Stats**: Advanced passing metrics

## Current Results

**Phase 2 (Simple Models)**:
- Logistic Regression: ~68% accuracy
- XGBoost: ~60% accuracy
- Features: Basic situational + team tendencies
- **Problem**: Missing individual player performance dynamics

**Phase 3 (Modular Feature Engineering)**:
- Engineered Features: 90+ comprehensive features across 7 categories
- **NEW**: Player performance features (QB efficiency, RB hot hands, WR targets)
- Expected Accuracy: 65-70% with player stats (baseline 60% → +5-10% improvement)
- **Key Insight**: Player-level efficiency captures game dynamics team aggregates miss
- Current Status: Ready for model training with enhanced features

**Season-to-Season Generalization**:
- Multi-season training supported (2021-2023)
- Player features more stable than team tendencies across seasons
- Recommendation: Retrain annually, use 2-3 recent seasons

## Next Steps

1. **Model Development**:
   - Train XGBoost/Random Forest with enhanced feature set (90+ features)
   - Compare performance: baseline (60%) vs. with player stats (expected 65-70%)
   - Experiment with team-specific models
   - Develop ensemble approach

2. **Advanced Features** (Easy to add with modular architecture):
   - Rolling player performance (last 3 games vs. season-to-date)
   - Opponent-specific history (how does KC play vs. BAL?)
   - Injury impact features (star player out → play calling shifts)
   - Sequential features (LSTM on play sequences)
   - Additional player stats (NextGen Stats: separation, air yards)

3. **Evaluation**:
   - Situational accuracy (3rd down, red zone, two-minute drill)
   - Team-specific performance analysis
   - Feature importance interpretation (which features matter most?)
   - Season-to-season generalization testing (train on 2022, test on 2023)

4. **Architecture Extensions**:
   - Add new feature builder modules (see `docs/modular_feature_engineering.md`)
   - Implement multi-season training pipeline
   - Create feature ablation study framework

## Documentation

- **[Modular Feature Engineering Architecture](docs/modular_feature_engineering.md)** **NEW**: Complete guide to the modular architecture, feature categories, player stats integration, and how to extend the system
- **[Feature Engineering Plan](docs/FEATURES.md)**: Comprehensive overview of all feature categories and implementation details
- **[Model Overview](docs/MODEL_OVERVIEW.md)**: Detailed project setup, data summary, and usage guide

### Key Documentation Highlights

**For Understanding the Architecture**:
- Read `docs/modular_feature_engineering.md` for architecture overview
- Each feature builder module is self-documented with docstrings

**For Adding New Features**:
1. Create new module in `src/data/feature_builders/`
2. Implement `add_*_features(pbp)` function
3. Export in `__init__.py`
4. Add to `feature_engineering_v2.py`
- See detailed guide in architecture documentation

**For Multi-Season Training**:
- Modify `SEASON = 2023` → `SEASONS = [2021, 2022, 2023]` in scripts
- Player stats provide more stable features across seasons than team tendencies

## Project Context

**Course**: CS513 - Machine Learning
**Focus**: Real-world sports analytics with advanced feature engineering
**Techniques**: Classification, feature engineering, ensemble methods, time-series analysis

## Why This Matters

Understanding play calling has real-world applications:
- **For Defensive Coordinators**: Pre-snap preparation and personnel matching
- **For Analytics Teams**: Automated scouting reports and tendency identification
- **For Sports Betting**: Situational play prediction models
- **For Machine Learning Education**:
  - Demonstrates importance of domain knowledge in feature engineering
  - Shows how modular architecture improves maintainability
  - Illustrates player-level features vs. team-level aggregates
  - Addresses season-to-season generalization challenges

## Modular Architecture Benefits

**Before (Monolithic)**:
- 500+ lines in single file
- Hard to debug specific features
- Difficult to add new features
- Testing requires full pipeline run

**After (Modular)**:
- Each module < 100 lines, focused on one category
- Easy to debug: test one module at a time
- Adding features: create module, plug in
- Clear separation: generation vs. I/O
- **Result**: Added player stats in ~50 lines, integrated seamlessly

---

**License**: Educational Project
**Author**: Noah Yohannes
**Last Updated**: December 3, 2025

## Recent Updates

**December 3, 2025**:
- ✅ Refactored feature engineering into modular architecture
- ✅ Added player performance features (7th category)
- ✅ Integrated player stats (QB efficiency, RB hot hands, WR targets)
- ✅ Created comprehensive architecture documentation
- ✅ Enhanced data loading pipeline with player stats caching
- ✅ 90+ features ready for model training (up from 85)
