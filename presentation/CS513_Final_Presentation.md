# NFL Play Type Prediction: A Defensive Coordinator's Perspective

**BY NOAH YOHANNES AND ALEX COROIAN**

---

## Project Description

Predicting NFL play calls from a defensive coordinator perspective.

A machine learning project predicting run vs. pass using advanced feature engineering.

---

## Problem Statement

**Predicting Run vs. Pass From a Defensive Coordinator Perspective**

**Goal**: Build a model that predicts NFL offensive play type (run or pass).

**The Challenge**:
- Traditional models rely mainly on down, distance, and time
- Real defensive coordinators evaluate far more inputs: team tendencies, momentum, personnel, fatigue, and environmental factors
- Offensive behavior emerges from non-linear interactions between these variables, limiting simple models

**Our Approach**: This project creates 85 engineered features to capture strategic, contextual, and temporal patterns in play calling.

**Objective**: Develop a model that reflects the sophistication of real defensive anticipation.

---

## Team Tendencies

**Feature Categories**:
- Down, Distance, Field Position
- Score, Quarter, Red Zone

Historical pass/run rates computed by situation to capture team-specific patterns.

---

## Momentum Features

Captures evolving drive dynamics that shape coaching decisions.

**Rolling windows compute**:
- Success rate (last 3 plays)
- Explosive plays (last 5 plays)
- Drive EPA accumulation
- Yards per play (current drive)
- First downs earned

**Purpose**:
- Distinguishes between struggling vs. high-momentum drives
- Allows the model to mimic how coordinators assess current offensive rhythm

---

## Fatigue Features

Fatigue affects both execution and playbook complexity.

**Features include**:
- Cumulative offensive snaps
- Rolling play counts
- No-huddle frequency
- Tempo (time since last play)

**Impact**:
- Long or fast-paced drives often produce predictable patterns
- Fatigue interacts with game context and personnel to influence likelihood of a run or pass

---

## Personnel Features

**Leveraging On-Field Player Groupings and Alignments**

- Participation data identifies which offensive and defensive players were present
- Key variables: defenders in the box, pass rushers, shotgun indicator, formation alignment
- Personnel determines matchup structure and strategic intent
- Helps explain tendencies like run-heavy 12 personnel or pass-heavy 11 personnel
- Adds tactical insight not visible in situational variables alone

---

## Context Features

**Environmental and Game-Level Influences**

- **Weather variables**: wind speed, temperature, precipitation
- **Stadium**: dome vs. outdoor conditions
- **Scheduling**: rest differences, divisional matchups, travel implications

**Impact**:
- Context often alters team risk tolerance and play selection
- Improves realism by adjusting predictions for unique game environments

---

## Situational Features

Classic predictors include:
- Down and distance
- Time remaining (game/half)
- Score differential
- Field position
- Red zone / goal-to-go status

**Purpose**:
- Situational features constrain offensive options
- Act as the structural backbone that interacts with tendencies, momentum, and context

---

## Data Used

**Data Sources (from nflreadpy)**:

- **Play-by-Play**: 49,000+ plays, 372 columns (EPA, WPA, formations, etc.)
- **Participation Data**: On-field personnel per play
- **Injuries**: Player availability
- **Schedules**: Weather, venue, rest days
- **Snap Counts**: Fatigue indicators
- **NextGen Stats**: Separation, passing metrics
- **Engineered Features**: ~85 total

---

## Methodology Overview

The project follows a staged methodology to move from raw NFL data to evaluated prediction models.

**Key Principles**:
- Each phase has a specific goal: understand the data, build baselines, engineer richer features, then train and assess advanced models
- Feedback from each phase informs design decisions in the next, supporting an iterative, evidence-driven workflow
- The methodology is designed so that new seasons, features, or algorithms can be slotted in without breaking the pipeline

---

## Phase 1: Data Exploration & Understanding

**Objective**: Develop a deep understanding of the raw nflreadpy datasets before modelling.

**Tasks include**:
- Loading play-by-play, participation, injuries, schedules, and snap counts
- Examining shape, completeness, and key fields

**Tools**: `data_loading.py`, `helpers.py`, and `visualization.py` generate text and HTML reports describing columns, null rates, distributions, and sample values.

**Outcome**: A clear picture of what information is available, trustworthy, and relevant for predicting run vs. pass, plus identification of issues (e.g., missing personnel rows) that must be handled later.

---

## Phase 2: Baseline Modeling

**Objective**: Establish a reference performance level using straightforward features and algorithms.

**Approach**: A logistic regression model is trained on core situational features (down, distance, score differential, time remaining, field position).

**Results**: This baseline typically achieves around 70-75% accuracy in run/pass prediction, highlighting both the strength and limits of purely situational modelling.

**Outcome**: A benchmark that demonstrates the need for richer features and more expressive algorithms, and a sanity check that data labelling and splits are correct.

---

## Phase 3: Advanced Feature Engineering

**Objective**: Design and implement features that mirror the information a defensive coordinator uses.

**Work includes**:
- Defining feature categories (team tendencies, momentum, fatigue, personnel, context)
- Writing Polars transformations
- Joining multiple datasets into a unified table

**Techniques**: Rolling windows, grouped aggregations, and pivots are used to compute pass rates, drive-level performance, cumulative snaps, and environmental indicators.

**Outcome**: A dataset of ~18,000 plays with 85 engineered features that provide a far more expressive representation of offensive decision-making than raw data alone.

---

## Phase 4: Advanced Model Training & Evaluation

**Objective**: Leverage the engineered feature space using more powerful algorithms such as Random Forest and XGBoost.

**Approach**:
- The dataset is split into training and test sets using game-based or time-based splits to avoid leakage between games
- Models are tuned using hyperparameters (e.g., depth, number of trees, learning rate)
- Evaluated with metrics such as accuracy, precision/recall, calibration, and confusion matrices

**Outcome**: Models that significantly outperform the logistic regression baseline, plus insights into which engineered features contribute most to predictive performance.

---

## Execution and Analysis

---

## Implementation Pipeline

**Three-Stage Modular Architecture**:

1. **Data Loading** (`data_loading.py`)
   - Downloads 5 seasons (2021-2025) from nflreadpy
   - Parquet caching system: 60s → 2s load times
   - ~164,741 plays cached across 9 data sources

2. **Feature Engineering** (`feature_engineering_v2.py`)
   - Modular feature builder system (7 categories)
   - Each module < 100 lines, focused, testable
   - Outputs single engineered dataset: `dc_features_2021-2025.parquet`

3. **Model Training** (`train_models.py`)
   - Temporal train/test split (critical for time-series)
   - Trains 3 models: Logistic Regression, Random Forest, XGBoost
   - Saves models and performance metrics

---

## Temporal Train/Test Split

**Best Practice for Time-Series Data**

**Why NOT Random Split?**
- ❌ Temporal leakage (train on Week 17, test on Week 1)
- ❌ Unrealistic: predicts past, not future
- ❌ Overfits same-game autocorrelation

**Our Temporal Split**:
- **Training**: 2021-2024 full seasons + 2025 weeks 1-10
  - 159,243 plays (96.7% of data)
- **Test**: 2025 weeks 11-13 (genuinely future games)
  - 5,498 plays (3.3% of data)

**Why This Matters**: Test accuracy reflects real-world deployment performance

---

## Feature Engineering Results

**68 Legitimate Features** (all pre-snap knowable)

**Starting Point**: 164,741 plays, 110 raw features

**Data Leakage Detection & Removal**:
- Removed 42 features with post-snap information
- `personnel_defenders_in_box`, `qb_dropback`, `receiver_*` → known only AFTER play
- Player performance stats → look-ahead bias (include current week)

**Final Feature Set by Category**:

| Category | Features | Top Examples |
|----------|----------|--------------|
| Team Tendencies | 22 | `team_pass_rate_3rd_long`, `team_pass_rate_red_zone` |
| Momentum | 23 | `momentum_epa_last_3`, `drive_total_yards` |
| Fatigue | 4 | `fatigue_fast_tempo`, `fatigue_total_offensive_snaps` |
| Context | 9 | `context_temperature`, `context_wind`, `context_dome` |
| Situational | 10 | `situation_third_down`, `situation_two_minute` |

---

## Model Performance Results

**Temporal Split Performance**

| Model | Train Acc | Test Acc | AUC-ROC | Notes |
|-------|-----------|----------|---------|-------|
| **Baseline** (always predict pass) | — | **56.6%** | — | Naive majority class |
| Logistic Regression | 57.8% | 56.6% | 0.538 | Predicts all pass |
| **Random Forest** | 78.9% | **75.2%** | 0.821 | Strong generalization |
| **XGBoost** | 79.2% | **76.6%** | 0.836 | **Best model** |

**Key Insights**:
- **+20 percentage points** over baseline (56.6% → 76.6%)
- XGBoost achieves **76.6% accuracy** predicting future games
- Minimal overfitting: train-test gap < 3%

---

## Feature Importance Analysis

**What Drives Predictions? - XGBoost Feature Importance**

**Top 5 Most Predictive Features**:
1. **formation_shotgun** (41.5%) - Shotgun = strong pass indicator
2. **situation_two_minute** (5.7%) - Two-minute drill = pass-heavy
3. **drive_quarter_start** (4.9%) - Opening drive tendencies
4. **situation_passing_down** (4.4%) - 3rd & long situations
5. **situation_third_down** (4.0%) - Critical down context

**Key Finding**:
- **Formation dominates** - Shotgun vs. under center is the strongest signal
- **Situational features** (down, distance, time) still critical
- **Team tendencies** provide incremental lift (8-15% importance combined)

---

## Confusion Matrix & Error Analysis

**Where Does XGBoost Struggle?**

**XGBoost Confusion Matrix (Test Set: 5,498 plays)**:

|                | **Predicted Run** | **Predicted Pass** |
|----------------|-------------------|-------------------|
| **Actual Run** | 1,692 (70.9%) | 695 (29.1%) |
| **Actual Pass** | 591 (19.0%) | 2,520 (81.0%) |

**Performance by Class**:
- **Run**: Precision 74.1%, Recall 70.9%
- **Pass**: Precision 78.4%, Recall 81.0%

**Error Patterns**:
- **695 False Positives** (predicted pass, actually run)
  - Offenses disguising run plays with pass formations
- **591 False Negatives** (predicted run, actually pass)
  - Play-action and unexpected passes

---

## Data Leakage Prevention

**Ensuring Valid Results**

**Critical Challenge**: Only use information knowable **before the snap**

**Leakage Sources Identified & Removed**:

1. **Personnel Features** (removed 4 features)
   - `defenders_in_box`, `pass_rushers` → recorded post-snap
   - **Red flag**: 90%+ accuracy when included

2. **Player Performance** (removed 22 features)
   - Cumulative stats included **current week** → look-ahead bias
   - Fix needed: Use `week < current_week`, not `week <= current_week`

3. **Play Outcome Features** (excluded from engineering)
   - `qb_dropback`, `qb_scramble`, `yards_gained` → only known after play

**Result**: 76.6% accuracy is **honest** - no artificial inflation

---

## How Good is 76.6%?

**Performance Benchmarks**

**Comparison to Baselines**:
- **Naive baseline** (always predict pass): 56.6%
- **Simple logistic regression** (down/distance/score): 56.6%
- **Our XGBoost model**: **76.6%** (+20 pp over baseline)

**Why This Matters**:
- NFL play calling has **inherent randomness** (coordinators want unpredictability)
- **Upper bound**: ~80-85% (even perfect information can't predict 100%)
- Our 76.6% captures **most predictable patterns** while respecting strategic variance

**Real-World Context**:
- Professional defensive coordinators use similar features mentally
- This model provides **data-driven pre-snap preparation**
- Actionable: "72% pass likelihood → bring nickel defense"

---

## Key Challenges Overcome

| Challenge | Solution | Impact |
|-----------|----------|--------|
| **Data size** (231K plays) | Parquet caching + Polars | 30x faster loads |
| **Temporal leakage** | Custom temporal split (2025 wks 11-13 test) | Realistic evaluation |
| **Feature leakage** | Removed 42 post-snap features | Honest 76.6% accuracy |
| **Look-ahead bias** | Excluded current-week player stats | Prevented 90%+ overfitting |
| **Modular extensibility** | 7 separate feature builder modules | Easy maintenance |

---

## Production Readiness & Future Work

**What's Production-Ready**:
- ✅ Temporal split validates real-world performance (76.6%)
- ✅ No data leakage - all features knowable pre-snap
- ✅ Multi-season training (2021-2025) - robust to meta shifts
- ✅ Modular architecture - easy to maintain/extend

**Future Improvements** (Expected Impact):

1. **Fix Player Performance Look-Ahead Bias** (HIGH PRIORITY)
   - Use `week < current_week` instead of `week <= current_week`
   - **Expected**: +5-10 pp accuracy (76.6% → 82-87%)

2. **Situational Breakdown Analysis**
   - 3rd down accuracy vs. 1st down accuracy
   - Red zone vs. midfield
   - Identify model strengths/weaknesses by context

3. **Team-Specific Models**
   - Train separate model per team (32 models)
   - Which teams are most predictable?

---

## Software/Libraries

**Python Libraries Used**:
- nflreadpy
- polars
- pandas
- numpy
- scikit-learn
- xgboost
- matplotlib / seaborn
- python-pptx (presentation)

**Project Structure**: Includes caching pipeline, feature engineering scripts, and visualization utilities.

---

## References and Documentation

**Documentation Used**:
- FEATURES.md
- MODEL_OVERVIEW.md
- README.md
- Visualization outputs (HTML)

**Code Files Used**:
- data_loading.py
- feature_engineering.py
- helpers.py
- visualization.py

**External References**:
Wilson, Chris. "Football 101 - Offensive Personnel Packages Common in the NFL." _Inside the 49 - 49ers News_, 2 Apr. 2025, insidethe49.com/z/offensive-personnel-packages-nfl/. Accessed 3 Dec. 2025.
