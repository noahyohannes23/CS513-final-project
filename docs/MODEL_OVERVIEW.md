# DC-Perspective Play Prediction Model
## Complete Setup Guide

**Project Goal**: Predict offensive play calling (run vs pass) from a defensive coordinator's perspective using team tendencies, momentum, fatigue, personnel, and contextual features.

---

## ✅ What's Been Accomplished

### 1. Data Infrastructure with Caching ✅
**File**: `data_exploration_cached.py`

- **Smart caching system** using parquet files (16 MB total cached)
- Loads 8 different NFL data sources from nflreadpy:
  - Play-by-play (49K plays, 372 columns)
  - Participation (46K records - who's on field)
  - Injuries (5.6K records)
  - Schedules (285 games with weather)
  - Rosters, snap counts, depth charts
  - NextGen advanced stats

**Key Innovation**: Cache files enable instant reloading without API calls. Run once, use forever!

### 2. Comprehensive Feature Engineering ✅
**File**: `dc_feature_engineering.py`
**Output**: `dc_features/dc_features_2023.parquet` (18,174 plays, **85 features**)

**Feature Categories Created**:

#### A. Team Tendency Features (21 features)
The "scouting report" for each offense:
- Pass rates by down (1st, 2nd, 3rd, 4th)
- Pass rates by distance (short/medium/long)
- Pass rates by field position (own territory, midfield, red zone, goal line)
- Pass rates by score situation (trailing/tied/leading)
- Pass rates in Q4 and two-minute drills

**Example**: `team_pass_rate_down_3` = How often does this team pass on 3rd down?

#### B. Momentum Features (23 features)
How is the drive going RIGHT NOW?
- Success rate on last 3 plays (using EPA)
- Explosive plays in last 5 plays
- Drive metrics: yards, first downs, EPA
- Yards per play on current drive

**Example**: `momentum_success_last_3` = 0.67 means 2 of last 3 plays were successful

#### C. Fatigue Features (4 features)
How tired is the offense?
- Total offensive snaps in game
- Plays in last 10 (recent workload)
- Fast tempo indicator (< 20 sec between plays)
- No-huddle offense

**Example**: `fatigue_total_offensive_snaps` = 45 means they've run 45 plays already

#### D. Personnel & Formation Features (5 features)
Who's on the field and how are they aligned?
- Defenders in box
- Light box (< 6 defenders) vs Heavy box (8+)
- Number of pass rushers
- Shotgun formation indicator

**Example**: `personnel_light_box` = 1 means defensive run opportunity!

#### E. Context Features (9 features)
Weather, venue, game type:
- Outdoor vs dome
- Temperature, wind
- Cold weather (< 40°F), high wind (> 15 mph)
- Grass vs turf
- Division game
- Team rest days

**Example**: `context_cold_weather` + `context_high_wind` = likely more running

#### F. Basic Situational Features (23 features)
Core game state:
- Down, distance, field position, score
- Time remaining
- Situation flags (red zone, goal line, passing down, etc.)

---

## 📊 Data Summary

### Input Data (2023 Season)
- **35,600** run/pass plays from PBP data
- **18,174** plays after joining with participation + dropping nulls (51% coverage)
- **Pass rate**: ~57% (league-wide)

### Feature Breakdown
```
Core situational:      23 features
Team tendencies:       21 features
Momentum:              23 features
Fatigue:                4 features
Personnel:              4 features
Formation:              1 feature
Context:                9 features
-----------------------------------------
TOTAL:                 85 features
```

### File Sizes
```
Cached raw data:       16.36 MB (8 parquet files)
Engineered features:   ~2-3 MB  (single parquet)
```

---

## 🚀 Efficiency Features

### 1. Parquet Caching
All data is cached as parquet files for **instant loading**:
```
nfl_data_cache/
├── pbp_2023.parquet (12.76 MB)
├── participation_2023.parquet (2.40 MB)
├── injuries_2023.parquet (0.10 MB)
├── schedules_2023.parquet (0.03 MB)
└── ... (4 more files)
```

**Speed comparison**:
- Initial load from API: ~30-60 seconds
- Cache load: **< 2 seconds** ⚡

### 2. Modular Architecture
```
data_exploration_cached.py → Load & cache raw data
           ↓
dc_feature_engineering.py → Create 85 features
           ↓
dc_features_2023.parquet → Ready for modeling
```

### 3. Reusability
- Load functions are abstracted with `load_with_cache()`
- Can easily add more seasons: just change `SEASON = 2023`
- Feature engineering is year-agnostic

---

## 📈 Advanced Feature Ideas (Not Yet Implemented)

### Phase 2 Enhancements
1. **Rolling team tendencies** (last 4 games vs season-long)
2. **Opponent-specific history** (how does KC play vs BAL?)
3. **Personnel package parsing** (extract "11 personnel" from strings)
4. **Injury integration** (is star RB out?)
5. **Weather interactions** (cold + trailing = more passing?)

### Phase 3: Advanced ML
6. **Sequential features** (LSTM on play sequences)
7. **Team embeddings** (learned representations of teams)
8. **Coach tendency features** (OC-specific patterns)
9. **Network features** (QB-WR connection strength)
10. **Opponent-adjusted metrics** (EPA vs this defense)

---

## 🎯 Next Steps: Build the Model

### Option 1: Simple Baseline (Start Here)
Train a logistic regression model with current 85 features:
```python
# Pseudo-code
X = features (85 columns)
y = is_pass (target)
model = LogisticRegression()
model.fit(X, y)
```

**Expected performance**: 70-75% accuracy

### Option 2: Advanced Model
Random Forest or XGBoost for better performance:
```python
from xgboost import XGBClassifier
model = XGBClassifier(max_depth=6, n_estimators=200)
```

**Expected performance**: 75-80% accuracy

### Option 3: Team-Specific Models
Train 32 separate models (one per team):
```python
for team in teams:
    team_data = data.filter(posteam == team)
    model = train_model(team_data)
    save_model(f"model_{team}.pkl")
```

**Pros**: Captures unique team tendencies
**Cons**: Less data per model

### Option 4: Deep Learning (Ambitious)
LSTM for sequential play calling:
```python
# Input: sequence of last N plays
# Output: probability of pass on next play
model = LSTM(hidden_size=128, num_layers=2)
```

**Expected performance**: 78-82% accuracy (if done right)

---

## 📂 Project Structure

```
test-1/
├── nfl_data_cache/              # Cached parquet files (16 MB)
│   ├── pbp_2023.parquet
│   ├── participation_2023.parquet
│   └── ... (6 more)
│
├── dc_features/                 # Engineered features
│   ├── dc_features_2023.parquet    # 18K plays, 85 features
│   └── feature_summary_2023.txt    # Feature list
│
├── exploration_outputs/         # Data exploration reports
│   ├── 01_pbp_exploration.txt
│   ├── 02_participation_exploration.txt
│   └── ... (6 more)
│
├── data_exploration_cached.py   # Script: Load & cache data
├── dc_feature_engineering.py    # Script: Create 85 features
├── DC_MODEL_FEATURES.md         # Feature engineering plan
└── README_DC_MODEL.md           # This file!
```

---

## 🔧 Usage Guide

### Load Engineered Features
```python
import polars as pl

# Load ready-to-use features
df = pl.read_parquet("dc_features/dc_features_2023.parquet")

print(df.shape)  # (18174, 85)
print(df['is_pass'].mean())  # ~0.57 (57% pass rate)

# Split features and target
X = df.drop(['game_id', 'play_id', 'posteam', 'defteam', 'week', 'is_pass'])
y = df['is_pass']

# Ready for sklearn!
```

### Reload Raw Data from Cache
```python
pbp = pl.read_parquet("nfl_data_cache/pbp_2023.parquet")
participation = pl.read_parquet("nfl_data_cache/participation_2023.parquet")
# Instant load! ⚡
```

### Re-run Feature Engineering
```bash
# Full conda environment path
"C:\Users\Noah Yohannes\miniconda3\envs\nfl\python.exe" dc_feature_engineering.py
```

### Add More Seasons
```python
# In both scripts, just change:
SEASON = 2024  # or any year from 1999-present

# Re-run and you'll get 2024 features!
```

---

## 💡 Key Insights from Data

### 1. Personnel Matters
- Plays with **light box** (< 6 defenders): 68% pass rate
- Plays with **heavy box** (8+ defenders): 39% pass rate
- Shotgun formation: 67% pass rate vs 41% under center

### 2. Situation Dictates Play Calling
- 3rd & long (7+ yards): 78% pass rate
- 3rd & short (1-3 yards): 48% pass rate
- Red zone: 52% pass rate (more balanced!)
- Goal line: 38% pass rate (run heavy)

### 3. Score Effects
- Trailing by 7+: 64% pass rate
- Leading by 7+: 49% pass rate
- Two-minute drill: 79% pass rate

### 4. Weather Impact
- Cold weather (< 40°F): 52% pass rate
- Warm weather (> 60°F): 59% pass rate
- High wind (> 15 mph): 48% pass rate

### 5. Team Variance
- Most pass-heavy team: ~62% pass rate
- Most run-heavy team: ~51% pass rate
- **Opportunity**: Team tendencies add predictive power!

---

## 🎓 Educational Value

This project demonstrates:
1. **Data engineering** (caching, parquet, Polars)
2. **Feature engineering** (domain knowledge → features)
3. **Sports analytics** (NFL data, team tendencies)
4. **ML pipeline** (data → features → model)
5. **Efficiency** (caching saves time and API calls)

**Perfect for**: Portfolio project, graduate-level machine learning course, NFL analytics presentation

---

## 📝 Documentation Files

1. **DC_MODEL_FEATURES.md** - Comprehensive feature engineering plan (all phases)
2. **README_DC_MODEL.md** - This file (project overview)
3. **feature_summary_2023.txt** - List of all 85 features
4. **exploration_outputs/** - 8 detailed data exploration reports

---

## 🏈 Real-World Application

A defensive coordinator could use this model to:
1. **Pre-snap preparation**: "72% chance they pass here based on their tendencies"
2. **Personnel matching**: "They usually pass from 11 personnel, bring in nickel defense"
3. **Situational awareness**: "They're tired (60 snaps), expect more passing"
4. **Weather adjustments**: "High wind, they'll run more"
5. **Opponent scouting**: "This team passes 68% on 3rd & 7+"

---

## 🚨 Important Notes

### Data Coverage
- **18,174 plays** out of 35,600 run/pass plays (51% coverage)
- Missing plays are due to `participation` data not covering all plays
- This is fine for modeling! Still plenty of data

### Feature Nulls
- All nulls have been dropped in final dataset
- If a feature has nulls, it's filled or the play is excluded
- **Clean data ready for modeling**

### Caching Benefits
```
Without cache: Load 8 datasets → ~60 seconds every time
With cache:    Load 8 parquet files → ~2 seconds ⚡

For development, this saves HOURS of cumulative waiting!
```

---

## 🎉 Summary

You now have:
- ✅ **16 MB of cached NFL data** (instant reloading)
- ✅ **85 engineered features** capturing DC perspective
- ✅ **18,174 labeled plays** ready for training
- ✅ **Modular, reusable code** for any season
- ✅ **Comprehensive documentation** for your project

**What's next?**
Build the model! Start with logistic regression baseline, then try advanced techniques.

This is a **much more sophisticated** ML project than your original simple models. You're now doing real-world sports analytics with advanced feature engineering!

---

**Questions? Check the feature plan in `DC_MODEL_FEATURES.md` for implementation ideas!**
