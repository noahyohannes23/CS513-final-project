"""
Play Type Prediction - Full Pipeline
Goal: Predict whether a play will be a run or pass using Logistic Regression
Steps: Data loading -> Cleaning -> Feature Engineering -> Model Training -> Evaluation
"""

import nflreadpy as nfl
import polars as pl
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, classification_report
)

print("=" * 70)
print("PLAY TYPE PREDICTION - LOGISTIC REGRESSION BASELINE")
print("=" * 70)

# ============================================================================
# STEP 1: Load Data
# ============================================================================
print("\n[STEP 1] Loading play-by-play data for 2023 season...")
pbp = nfl.load_pbp(2023)
print(f"   Initial shape: {pbp.shape}")

# ============================================================================
# STEP 2: Filter for Run/Pass Plays Only
# ============================================================================
print("\n[STEP 2] Filtering for run and pass plays only...")
print(f"   Before filtering: {pbp.height:,} plays")

# Keep only plays where play_type is 'run' or 'pass'
pbp_clean = pbp.filter(
    (pl.col('play_type') == 'run') | (pl.col('play_type') == 'pass')
)
print(f"   After filtering: {pbp_clean.height:,} plays")

# Count by play type
run_count = pbp_clean.filter(pl.col('play_type') == 'run').height
pass_count = pbp_clean.filter(pl.col('play_type') == 'pass').height
print(f"   Run plays: {run_count:,} ({run_count/(run_count+pass_count):.1%})")
print(f"   Pass plays: {pass_count:,} ({pass_count/(run_count+pass_count):.1%})")

# ============================================================================
# STEP 3: Handle Missing Values
# ============================================================================
print("\n[STEP 3] Handling missing values...")

# Key features we'll use
feature_cols = ['down', 'ydstogo', 'yardline_100', 'score_differential',
                'qtr', 'half_seconds_remaining']

# Check missing values before
print("   Missing values before cleaning:")
for col in feature_cols:
    null_count = pbp_clean[col].null_count()
    print(f"      {col:25s} - {null_count:,} nulls")

# Drop rows with any missing values in key features
pbp_clean = pbp_clean.drop_nulls(subset=feature_cols)
print(f"\n   After dropping nulls: {pbp_clean.height:,} plays")

# Verify no missing values
print("   Missing values after cleaning:")
for col in feature_cols:
    null_count = pbp_clean[col].null_count()
    print(f"      {col:25s} - {null_count:,} nulls")

# ============================================================================
# STEP 4: Feature Engineering
# ============================================================================
print("\n[STEP 4] Engineering features...")

# Create binary target variable (0 = run, 1 = pass)
pbp_clean = pbp_clean.with_columns([
    (pl.col('play_type') == 'pass').cast(pl.Int32).alias('is_pass')
])

# Feature engineering - add some helpful features
pbp_clean = pbp_clean.with_columns([
    # Is it a short yardage situation? (3 yards or less to go)
    (pl.col('ydstogo') <= 3).cast(pl.Int32).alias('short_yardage'),

    # Is it in the red zone? (inside 20 yard line)
    (pl.col('yardline_100') <= 20).cast(pl.Int32).alias('red_zone'),

    # Is it 3rd or 4th down?
    (pl.col('down') >= 3).cast(pl.Int32).alias('passing_down'),

    # Is team losing? (negative score differential means losing)
    (pl.col('score_differential') < 0).cast(pl.Int32).alias('losing'),

    # Is it late in the half? (less than 2 minutes)
    (pl.col('half_seconds_remaining') < 120).cast(pl.Int32).alias('two_minute_drill')
])

# Final feature list
final_features = [
    'down', 'ydstogo', 'yardline_100', 'score_differential',
    'qtr', 'half_seconds_remaining',
    'short_yardage', 'red_zone', 'passing_down', 'losing', 'two_minute_drill'
]

print(f"   Total features: {len(final_features)}")
print(f"   Feature list: {final_features}")

# ============================================================================
# STEP 5: Train/Test Split
# ============================================================================
print("\n[STEP 5] Creating train/test split...")

# Convert to numpy arrays for sklearn
X = pbp_clean.select(final_features).to_numpy()
y = pbp_clean.select('is_pass').to_numpy().ravel()

print(f"   X shape: {X.shape}")
print(f"   y shape: {y.shape}")

# Split: 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"   Training set: {X_train.shape[0]:,} plays")
print(f"   Test set: {X_test.shape[0]:,} plays")
print(f"   Train pass rate: {y_train.mean():.1%}")
print(f"   Test pass rate: {y_test.mean():.1%}")

# ============================================================================
# STEP 6: Feature Scaling
# ============================================================================
print("\n[STEP 6] Scaling features...")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"   Features scaled using StandardScaler")
print(f"   Mean (should be ~0): {X_train_scaled.mean(axis=0)[:3]}")
print(f"   Std (should be ~1): {X_train_scaled.std(axis=0)[:3]}")

# ============================================================================
# STEP 7: Train Logistic Regression Model
# ============================================================================
print("\n[STEP 7] Training Logistic Regression model...")

# Create and train model
model = LogisticRegression(
    max_iter=1000,
    random_state=42,
    solver='lbfgs'
)

model.fit(X_train_scaled, y_train)
print(f"   Model trained successfully!")
print(f"   Converged: {model.n_iter_} iterations")

# ============================================================================
# STEP 8: Evaluate Model
# ============================================================================
print("\n[STEP 8] Evaluating model performance...")

# Predictions
y_train_pred = model.predict(X_train_scaled)
y_test_pred = model.predict(X_test_scaled)

# Prediction probabilities for ROC-AUC
y_train_proba = model.predict_proba(X_train_scaled)[:, 1]
y_test_proba = model.predict_proba(X_test_scaled)[:, 1]

# Calculate metrics
print("\n   TRAINING SET PERFORMANCE:")
print(f"      Accuracy:  {accuracy_score(y_train, y_train_pred):.4f}")
print(f"      Precision: {precision_score(y_train, y_train_pred):.4f}")
print(f"      Recall:    {recall_score(y_train, y_train_pred):.4f}")
print(f"      F1 Score:  {f1_score(y_train, y_train_pred):.4f}")
print(f"      ROC-AUC:   {roc_auc_score(y_train, y_train_proba):.4f}")

print("\n   TEST SET PERFORMANCE:")
print(f"      Accuracy:  {accuracy_score(y_test, y_test_pred):.4f}")
print(f"      Precision: {precision_score(y_test, y_test_pred):.4f}")
print(f"      Recall:    {recall_score(y_test, y_test_pred):.4f}")
print(f"      F1 Score:  {f1_score(y_test, y_test_pred):.4f}")
print(f"      ROC-AUC:   {roc_auc_score(y_test, y_test_proba):.4f}")

# Confusion Matrix
print("\n   CONFUSION MATRIX (Test Set):")
cm = confusion_matrix(y_test, y_test_pred)
print(f"      True Negatives (Run predicted as Run):   {cm[0, 0]:,}")
print(f"      False Positives (Run predicted as Pass): {cm[0, 1]:,}")
print(f"      False Negatives (Pass predicted as Run): {cm[1, 0]:,}")
print(f"      True Positives (Pass predicted as Pass): {cm[1, 1]:,}")

# Classification Report
print("\n   DETAILED CLASSIFICATION REPORT (Test Set):")
print(classification_report(y_test, y_test_pred,
                          target_names=['Run', 'Pass'],
                          digits=4))

# ============================================================================
# STEP 9: Feature Importance Analysis
# ============================================================================
print("\n[STEP 9] Analyzing feature importance...")

# Get coefficients
coefficients = model.coef_[0]

# Create feature importance list
feature_importance = list(zip(final_features, coefficients))
feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)

print("\n   FEATURE IMPORTANCE (by absolute coefficient value):")
print(f"   {'Feature':<25s} {'Coefficient':>12s} {'Impact':>10s}")
print("   " + "-" * 50)
for feature, coef in feature_importance:
    impact = "Pass+" if coef > 0 else "Run+"
    print(f"   {feature:<25s} {coef:>12.4f} {impact:>10s}")

print("\n   Interpretation:")
print("   - Positive coefficients increase probability of PASS")
print("   - Negative coefficients increase probability of RUN")

print("\n" + "=" * 70)
print("MODEL TRAINING AND EVALUATION COMPLETE!")
print("=" * 70)
