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
- Created 85 engineered features across 6 categories:
  - **Team Tendencies** (21 features): Historical pass rates by situation
  - **Momentum** (23 features): Recent play success, drive efficiency
  - **Fatigue** (4 features): Snap counts, tempo indicators
  - **Personnel** (4 features): Who's on field, formation alignment
  - **Formation** (1 feature): Shotgun vs. under center
  - **Context** (9 features): Weather, venue, game type
- Engineered features now stored in `data/features/` for model training

**Current Status**: Feature engineering complete. Ready for advanced model development.

## Repository Structure

```
test-1/
├── src/
│   ├── data/
│   │   ├── data_loading.py          # Data fetching with caching
│   │   └── feature_engineering.py   # DC-perspective feature creation
│   ├── utils/
│   │   ├── helpers.py               # Utility functions
│   │   └── visualization.py         # Dataset documentation generator
│   └── models/                      # (Future: Advanced ML models)
│
├── data/
│   ├── cache/                       # Cached raw data (gitignored)
│   └── features/                    # Engineered features (parquet)
│
├── outputs/
│   ├── visualizations/              # HTML dataset documentation
│   └── logs/                        # Execution logs and outputs
│
├── docs/
│   ├── FEATURES.md                  # Feature engineering plan
│   └── MODEL_OVERVIEW.md            # Detailed model documentation
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
- Fetches NFL data from nflreadpy
- Caches to `data/cache/` as parquet files (fast reloading)
- Generates exploration reports in `outputs/logs/`

#### 2. Engineer Features
```bash
python src/data/feature_engineering.py
```
- Loads cached data
- Creates 85 DC-perspective features
- Saves engineered dataset to `data/features/dc_features_2023.parquet`

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

3. **Efficient Data Pipeline**:
   - Parquet caching reduces load time from 60s → 2s
   - Modular architecture (data → features → models)
   - Year-agnostic code (easily switch from 2023 to other seasons)

4. **Production-Ready Structure**:
   - Clear separation of concerns (data, features, models, utils)
   - Reproducible outputs
   - Documentation at every level

## Data Sources

This project uses NFL data from `nflreadpy`, which provides:
- **Play-by-Play**: 49,000+ plays, 372 columns (EPA, WPA, success indicators)
- **Participation**: Who was on field for each play, personnel packages
- **Schedules**: Weather, venue, rest days
- **Injuries**: Player availability by week
- **Snap Counts**: Playing time and fatigue indicators
- **NextGen Stats**: Advanced passing metrics

## Current Results

**Phase 2 (Simple Models)**:
- Logistic Regression: ~68% accuracy
- Features: 11 basic situational features

**Phase 3 (Target)**:
- Engineered Features: 85 comprehensive features
- Expected Accuracy: 75-82% (with advanced models)
- Current Status: Ready for model training

## Next Steps

1. **Model Development**:
   - Train XGBoost/Random Forest with engineered features
   - Experiment with team-specific models
   - Develop ensemble approach

2. **Advanced Features**:
   - Rolling team tendencies (last 4 games vs. season-long)
   - Opponent-specific history (how does KC play vs. BAL?)
   - Sequential features (LSTM on play sequences)

3. **Evaluation**:
   - Situational accuracy (3rd down, red zone, two-minute drill)
   - Team-specific performance analysis
   - Feature importance interpretation

## Documentation

- **[Feature Engineering Plan](docs/FEATURES.md)**: Comprehensive overview of all feature categories and implementation details
- **[Model Overview](docs/MODEL_OVERVIEW.md)**: Detailed project setup, data summary, and usage guide

## Project Context

**Course**: CS513 - Machine Learning
**Focus**: Real-world sports analytics with advanced feature engineering
**Techniques**: Classification, feature engineering, ensemble methods, time-series analysis

## Why This Matters

Understanding play calling has real-world applications:
- **For Defensive Coordinators**: Pre-snap preparation and personnel matching
- **For Analytics Teams**: Automated scouting reports and tendency identification
- **For Sports Betting**: Situational play prediction models
- **For Machine Learning**: Demonstrates importance of domain knowledge in feature engineering

---

**License**: Educational Project
**Author**: Noah Yohannes
**Last Updated**: December 2025
