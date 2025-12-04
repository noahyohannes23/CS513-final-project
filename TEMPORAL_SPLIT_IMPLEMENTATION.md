# Temporal Split Implementation Summary

## Overview
Implemented multi-season temporal split to replace random train/test split, following best practices for time-series data.

## Changes Made

### 1. Data Loading (`src/data/data_loading.py`)
**Changes:**
- Modified to load multiple seasons: 2021, 2022, 2023, 2024, 2025
- Loop through each season and cache separately
- Added season tracking in output

**Key Code:**
```python
SEASONS = [2021, 2022, 2023, 2024, 2025]
```

### 2. Feature Engineering (`src/data/feature_engineering_v2.py`)
**Changes:**
- Load and concatenate data from all 5 seasons
- Add 'season' column to each dataset for tracking
- Process all seasons together
- Save combined features as `dc_features_2021-2025.parquet`

**Key Code:**
```python
SEASONS = [2021, 2022, 2023, 2024, 2025]

def load_cached_data(seasons: list):
    # Loads each season, adds 'season' column
    # Concatenates using diagonal_relaxed (handles schema differences)
    pbp = pl.concat(pbp_list, how="diagonal_relaxed")
```

### 3. Model Training (`src/models/train_models.py`)
**Changes:**
- **Replaced random split with temporal split**
- Training set: 2021-2024 (full) + 2025 weeks 1-10
- Test set: 2025 weeks 11-13
- Removed `train_test_split()` from scikit-learn
- Implemented custom `split_data_temporal()` function

**Key Code:**
```python
TRAIN_CUTOFF_SEASON = 2025
TRAIN_CUTOFF_WEEK = 10   # Weeks 1-10 for training
TEST_START_WEEK = 11      # Weeks 11-13 for testing

def split_data_temporal(df: pl.DataFrame):
    train_mask = (
        (pl.col('season') < 2025) |  # All of 2021-2024
        ((pl.col('season') == 2025) & (pl.col('week') <= 10))
    )
    test_mask = (pl.col('season') == 2025) & (pl.col('week') >= 11)
```

## Temporal Split Breakdown

| Split | Data Included | Approximate Plays | Percentage |
|-------|--------------|-------------------|------------|
| **Training** | 2021 full season | ~35,000 | ~20% |
| | 2022 full season | ~35,000 | ~20% |
| | 2023 full season | ~35,000 | ~20% |
| | 2024 full season | ~35,000 | ~20% |
| | 2025 weeks 1-10 | ~20,000 | ~11% |
| | **Total** | **~160,000** | **~91%** |
| **Test** | 2025 weeks 11-13 | ~6,500 | ~3.5% |

## Why Temporal Split?

### Problems with Random Split
1. **Temporal leakage**: Training on Week 17, testing on Week 1
2. **Not realistic**: Defensive coordinators predict *future* games
3. **Overfitting**: Same-game plays in both sets (autocorrelation)

### Benefits of Temporal Split
1. **Realistic evaluation**: Test represents predicting future games
2. **No temporal leakage**: Training data always precedes test data
3. **True generalization**: Test accuracy reflects real-world performance

## How to Run

### Step 1: Load Multi-Season Data
```bash
"C:\Users\Noah Yohannes\miniconda3\envs\nfl-play-prediction\python.exe" src/data/data_loading.py
```
**What it does:**
- Downloads/caches 2021, 2022, 2023, 2024, 2025 data
- Creates `data/cache/*_YYYY.parquet` files
- Takes ~15-30 minutes for all seasons (first run)

### Step 2: Engineer Features (Multi-Season)
```bash
"C:\Users\Noah Yohannes\miniconda3\envs\nfl-play-prediction\python.exe" src/data/feature_engineering_v2.py
```
**What it does:**
- Loads all 5 seasons
- Concatenates into single dataset
- Engineers features across all seasons
- Saves `data/features/dc_features_2021-2025.parquet`
- Takes ~5-10 minutes

### Step 3: Train Models (Temporal Split)
```bash
"C:\Users\Noah Yohannes\miniconda3\envs\nfl-play-prediction\python.exe" src/models/train_models.py
```
**What it does:**
- Loads multi-season features
- Splits temporally (2025 wks 11-13 for test)
- Trains Logistic Regression, Random Forest, XGBoost
- Saves models as `*_2021-2025.pkl`
- Takes ~5-10 minutes

## Expected Results

### Test Accuracy Comparison

| Model | Old (Random Split) | Expected (Temporal Split) | Change |
|-------|-------------------|--------------------------|--------|
| Logistic Regression | 58% | 55-60% | Similar |
| Random Forest | **75%** | **68-72%** | -3 to -7 pp |
| XGBoost | **75%** | **68-72%** | -3 to -7 pp |

**Why lower accuracy is expected:**
- Random split was optimistic due to temporal leakage
- Temporal split is more honest/realistic
- This is the *true* performance for predicting future games

### Interpreting Results

**If test accuracy is 68-72%:**
✅ Good! Model generalizes well to future weeks
✅ Ready for production use

**If test accuracy is < 65%:**
⚠️ Model struggles with late-season games
🔍 Investigate:
- Are 2025 weeks 11-13 different from training data?
- Did team strategies change mid-season?
- Feature importance shifts?

**If test accuracy is > 75%:**
🚨 Possible data leakage still present
🔍 Check for features that shouldn't be known pre-snap

## Files Modified

```
src/data/data_loading.py          - Multi-season loading
src/data/feature_engineering_v2.py - Multi-season concatenation
src/models/train_models.py        - Temporal split logic
```

## Files Created (After Running)

```
data/cache/pbp_2021.parquet
data/cache/pbp_2022.parquet
data/cache/pbp_2023.parquet
data/cache/pbp_2024.parquet
data/cache/pbp_2025.parquet
... (similar for other datasets)

data/features/dc_features_2021-2025.parquet
data/features/feature_summary_2021-2025.txt

outputs/models/random_forest_2021-2025.pkl
outputs/models/xgboost_2021-2025.pkl
outputs/results/model_comparison_2021-2025.txt
```

## Next Steps

1. **Run the pipeline** (see "How to Run" above)
2. **Analyze results** in `outputs/results/model_comparison_2021-2025.txt`
3. **Compare** temporal split accuracy vs. old random split
4. **If accuracy drops significantly** (>10 pp), investigate:
   - Feature importance changes
   - Season-specific patterns
   - Team strategy shifts in 2025

## Configuration (Adjustable)

You can modify the split in `src/models/train_models.py`:

```python
# Current: Train on weeks 1-10, test on weeks 11-13
TRAIN_CUTOFF_WEEK = 10
TEST_START_WEEK = 11

# Alternative: More training data
TRAIN_CUTOFF_WEEK = 11  # Train on weeks 1-11
TEST_START_WEEK = 12     # Test on weeks 12-13
```

## Statistical Validity

- **Test set size**: ~6,500 plays
- **Margin of error**: ±1.2% at 95% confidence
- **Minimum needed**: ~385 plays (we have 17x that)
- **Conclusion**: Test set is statistically robust

---

**Implementation Date**: 2025-12-03
**Implemented By**: Claude Code
**Status**: ✅ Ready for testing
