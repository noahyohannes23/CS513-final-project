"""
Play Type Prediction - NFL Play-by-Play Analysis
Goal: Predict whether a play will be a run or pass using Logistic Regression
Approach: Use Polars for data manipulation, convert to numpy for sklearn
"""

import nflreadpy as nfl
import polars as pl
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, classification_report
)

print("=" * 70)
print("PLAY TYPE PREDICTION - DATA EXPLORATION")
print("=" * 70)

# Step 1: Load play-by-play data (Polars DataFrame)
print("\n[1/8] Loading play-by-play data for 2023 season...")
pbp = nfl.load_pbp(2023)
print(f"   Shape: {pbp.shape}")
print(f"   Columns: {len(pbp.columns)}")

print("\n[2/8] Exploring available columns...")
print(f"   Total columns: {len(pbp.columns)}")
print("\nKey columns (first 30):")
for i, col in enumerate(pbp.columns[:30], 1):
    print(f"   {i:2d}. {col}")

# Check for play type columns
print("\n[3/8] Looking for play type indicators...")
play_type_cols = [col for col in pbp.columns if 'play' in col.lower() or 'type' in col.lower()]
print(f"   Found {len(play_type_cols)} potential play type columns:")
for col in play_type_cols[:15]:  # Show first 15
    print(f"   - {col}")

# Check for run/pass indicators
print("\n[4/8] Checking for run/pass indicators...")
run_pass_cols = [col for col in pbp.columns if any(x in col.lower() for x in ['run', 'pass', 'rush'])]
print(f"   Found {len(run_pass_cols)} run/pass related columns:")
for col in run_pass_cols[:15]:
    print(f"   - {col}")

# Display sample rows (select a few key columns to avoid encoding issues)
print("\n[5/8] Sample play-by-play data (first 3 rows, key columns):")
sample_cols = ['game_id', 'posteam', 'defteam', 'down', 'ydstogo', 'yardline_100',
               'play_type', 'yards_gained']
available_sample_cols = [col for col in sample_cols if col in pbp.columns]
try:
    print(pbp.select(available_sample_cols).head(3))
except Exception as e:
    print(f"   (Could not display sample due to encoding: {type(e).__name__})")

# Check data types and missing values
print("\n[6/8] Data quality check...")
print(f"   Total rows: {pbp.height:,}")
print(f"   Memory usage: {pbp.estimated_size('mb'):.2f} MB")

# Look for key features we need
print("\n[7/8] Checking for key features needed for prediction...")
required_features = ['down', 'ydstogo', 'yardline_100', 'score_differential',
                     'qtr', 'half_seconds_remaining', 'posteam', 'defteam']
for feature in required_features:
    if feature in pbp.columns:
        non_null = pbp[feature].null_count()
        total = pbp.height
        print(f"   [OK] {feature:25s} - {total - non_null:,} non-null values ({non_null:,} nulls)")
    else:
        print(f"   [X]  {feature:25s} - NOT FOUND")

# Identify target variable
print("\n[8/8] Identifying target variable for play type...")
if 'play_type' in pbp.columns:
    print(f"   Using 'play_type' column")
    unique_vals = pbp['play_type'].unique().to_list()[:10]
    print(f"   Unique values (first 10): {unique_vals}")
    print(f"\n   Play type distribution:")
    # Convert to list of tuples to avoid encoding issues
    value_counts = pbp['play_type'].value_counts()
    for row in value_counts.head(10).iter_rows():
        play_type_val, count = row
        print(f"      {str(play_type_val):20s} - {count:,}")
elif 'run_pass' in pbp.columns:
    print(f"   Using 'run_pass' column")
    unique_vals = pbp['run_pass'].unique().to_list()
    print(f"   Unique values: {unique_vals}")
    print(f"\n   Run/Pass distribution:")
    value_counts = pbp['run_pass'].value_counts()
    for row in value_counts.iter_rows():
        val, count = row
        print(f"      {str(val):20s} - {count:,}")
else:
    print("   Searching for run/pass indicators in columns...")
    # Check if there's a rush or pass attempt column
    if 'rush_attempt' in pbp.columns and 'pass_attempt' in pbp.columns:
        print("   Found 'rush_attempt' and 'pass_attempt' columns")
        rush_count = pbp['rush_attempt'].sum()
        pass_count = pbp['pass_attempt'].sum()
        print(f"   Rush attempts: {rush_count:,}")
        print(f"   Pass attempts: {pass_count:,}")
        print(f"   Pass ratio: {pass_count / (pass_count + rush_count):.1%}")

print("\n" + "=" * 70)
print("DATA EXPLORATION COMPLETE")
print("=" * 70)
print("\nNext steps:")
print("1. Filter for run/pass plays only (exclude punts, FGs, kickoffs)")
print("2. Handle missing values")
print("3. Engineer features")
print("4. Create train/test split")
print("5. Train Logistic Regression model")
