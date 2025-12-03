"""
Model Training Script
Train and compare Linear Regression, Random Forest, and XGBoost models
for play type prediction (run vs. pass)
"""

import polars as pl
import numpy as np
from pathlib import Path
from datetime import datetime
import pickle

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import xgboost as xgb

# ============================================================================
# CONFIGURATION
# ============================================================================

FEATURES_DIR = Path("./data/features")
MODELS_DIR = Path("./outputs/models")
RESULTS_DIR = Path("./outputs/results")

MODELS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SEASON = 2023
RANDOM_STATE = 42
TEST_SIZE = 0.2

# ============================================================================
# LOAD DATA
# ============================================================================

def load_features(season: int):
    """Load engineered features."""
    print(f"[1/6] Loading features for {season}...")

    features_path = FEATURES_DIR / f"dc_features_{season}.parquet"
    df = pl.read_parquet(features_path)

    print(f"   Loaded: {df.shape[0]:,} plays, {df.shape[1]} features")
    return df


# ============================================================================
# PREPARE DATA
# ============================================================================

def prepare_data(df: pl.DataFrame):
    """Prepare features and target for modeling."""
    print("\n[2/6] Preparing data...")

    # Separate features and target
    target = 'is_pass'

    # Exclude non-feature columns
    exclude_cols = ['game_id', 'play_id', 'posteam', 'defteam', 'week', target]

    # CRITICAL: Exclude data leakage columns (only known AFTER play happens)
    leakage_keywords = [
        'qb_dropback', 'qb_scramble', 'qb_hit', 'qb_kneel', 'qb_spike', 'qb_epa',
        'receiver_id', 'receiver_jersey', 'receiver_player', 'rusher_player',
        'passer_player', 'interception', 'fumble', 'sack', 'touchdown',
        'yards_gained', 'first_down', 'fourth_down_converted', 'incomplete_pass',
        'pass_attempt', 'rush_attempt', 'complete_pass', 'air_yards', 'yards_after_catch',
        # Player performance features (look-ahead bias - includes current week stats)
        'qb_completion', 'qb_yards_per_attempt', 'qb_td_int',
        'rb_yards_per_carry', 'rb_tds_per_game',
        'receiver_catch_rate', 'receiver_yards_per_reception', 'receiver_targets_per_game',
        # Personnel features (may be recorded AFTER play, not pre-snap)
        'personnel_pass_rushers', 'personnel_defenders_in_box', 'personnel_light_box', 'personnel_heavy_box'
    ]

    # Get numeric columns only (exclude strings like timestamps, player names, IDs)
    numeric_types = [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.Float32, pl.Float64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64]
    feature_cols = [
        col for col in df.columns
        if col not in exclude_cols
        and df[col].dtype in numeric_types
        and not any(keyword in col.lower() for keyword in leakage_keywords)
    ]

    print(f"   Excluded {len([c for c in df.columns if any(k in c.lower() for k in leakage_keywords)])} leakage columns")

    print(f"   Filtering to numeric columns...")
    print(f"   Original columns: {len(df.columns)}")
    print(f"   Numeric feature columns: {len(feature_cols)}")

    # Fill any remaining nulls with 0 (mostly player stats)
    df = df.fill_null(0)

    # Replace infinities with 0
    df = df.fill_nan(0)

    # Extract features and target as numpy arrays
    X = df.select(feature_cols).to_numpy()
    y = df.select(target).to_numpy().ravel()

    # Final safety check: replace any remaining NaN/inf with 0
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    # Calculate target distribution
    pass_count = int(y.sum())
    run_count = len(y) - pass_count
    pass_rate = y.mean()

    print(f"   Features: {len(feature_cols)}")
    print(f"   Samples: {len(y):,}")
    print(f"   Target distribution: Run={run_count:,}, Pass={pass_count:,}")
    print(f"   Pass rate: {pass_rate:.1%}")

    return X, y, feature_cols


# ============================================================================
# TRAIN-TEST SPLIT
# ============================================================================

def split_data(X, y):
    """Split data into train and test sets."""
    print("\n[3/6] Splitting data...")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    print(f"   Train: {X_train.shape[0]:,} plays")
    print(f"   Test:  {X_test.shape[0]:,} plays")
    print(f"   Train pass rate: {y_train.mean():.1%}")
    print(f"   Test pass rate:  {y_test.mean():.1%}")

    return X_train, X_test, y_train, y_test


# ============================================================================
# MODEL TRAINING
# ============================================================================

def train_models(X_train, y_train):
    """Train all three models."""
    print("\n[4/6] Training models...")

    models = {}

    # 1. Logistic Regression
    print("\n   [1/3] Training Logistic Regression...")
    lr = LogisticRegression(
        max_iter=1000,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
    lr.fit(X_train, y_train)
    models['Logistic Regression'] = lr
    print("      [OK] Trained")

    # 2. Random Forest
    print("\n   [2/3] Training Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=50,
        min_samples_leaf=20,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=0
    )
    rf.fit(X_train, y_train)
    models['Random Forest'] = rf
    print("      [OK] Trained")

    # 3. XGBoost
    print("\n   [3/3] Training XGBoost...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        eval_metric='logloss'
    )
    xgb_model.fit(X_train, y_train)
    models['XGBoost'] = xgb_model
    print("      [OK] Trained")

    return models


# ============================================================================
# MODEL EVALUATION
# ============================================================================

def evaluate_models(models, X_train, X_test, y_train, y_test, feature_cols):
    """Evaluate all models and return results."""
    print("\n[5/6] Evaluating models...")

    results = {}

    for name, model in models.items():
        print(f"\n   Evaluating {name}...")

        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        y_test_proba = model.predict_proba(X_test)[:, 1]

        # Metrics
        train_acc = accuracy_score(y_train, y_train_pred)
        test_acc = accuracy_score(y_test, y_test_pred)
        precision = precision_score(y_test, y_test_pred)
        recall = recall_score(y_test, y_test_pred)
        f1 = f1_score(y_test, y_test_pred)
        auc = roc_auc_score(y_test, y_test_proba)

        # Confusion matrix
        cm = confusion_matrix(y_test, y_test_pred)

        # Classification report
        report = classification_report(y_test, y_test_pred,
                                       target_names=['Run', 'Pass'],
                                       output_dict=True)

        # Feature importance (if available)
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            feature_importance = sorted(
                zip(feature_cols, importance),
                key=lambda x: x[1],
                reverse=True
            )[:20]  # Top 20
        elif hasattr(model, 'coef_'):
            importance = np.abs(model.coef_[0])
            feature_importance = sorted(
                zip(feature_cols, importance),
                key=lambda x: x[1],
                reverse=True
            )[:20]  # Top 20

        results[name] = {
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'auc_roc': auc,
            'confusion_matrix': cm,
            'classification_report': report,
            'feature_importance': feature_importance
        }

        print(f"      Train Accuracy: {train_acc:.1%}")
        print(f"      Test Accuracy:  {test_acc:.1%}")
        print(f"      Precision:      {precision:.1%}")
        print(f"      Recall:         {recall:.1%}")
        print(f"      F1 Score:       {f1:.3f}")
        print(f"      AUC-ROC:        {auc:.3f}")

    return results


# ============================================================================
# SAVE RESULTS
# ============================================================================

def save_results(models, results, feature_cols, season):
    """Save models and results."""
    print("\n[6/6] Saving models and results...")

    # Save models
    for name, model in models.items():
        model_filename = name.lower().replace(' ', '_')
        model_path = MODELS_DIR / f"{model_filename}_{season}.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"   [OK] Saved {name}: {model_path}")

    # Save results summary
    results_path = RESULTS_DIR / f"model_comparison_{season}.txt"
    with open(results_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("MODEL COMPARISON RESULTS\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Season: {season}\n")
        f.write("=" * 80 + "\n\n")

        # Summary table
        f.write("PERFORMANCE SUMMARY:\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Model':<20} {'Train Acc':<12} {'Test Acc':<12} {'Precision':<12} {'Recall':<12} {'F1':<10} {'AUC':<10}\n")
        f.write("-" * 80 + "\n")

        for name, res in results.items():
            f.write(f"{name:<20} "
                   f"{res['train_accuracy']:>10.1%}  "
                   f"{res['test_accuracy']:>10.1%}  "
                   f"{res['precision']:>10.1%}  "
                   f"{res['recall']:>10.1%}  "
                   f"{res['f1_score']:>8.3f}  "
                   f"{res['auc_roc']:>8.3f}\n")

        f.write("\n" + "=" * 80 + "\n\n")

        # Detailed results per model
        for name, res in results.items():
            f.write(f"\n{'=' * 80}\n")
            f.write(f"{name.upper()}\n")
            f.write(f"{'=' * 80}\n\n")

            f.write("Confusion Matrix:\n")
            cm = res['confusion_matrix']
            f.write(f"                Predicted Run    Predicted Pass\n")
            f.write(f"  Actual Run    {cm[0][0]:>13,}    {cm[0][1]:>14,}\n")
            f.write(f"  Actual Pass   {cm[1][0]:>13,}    {cm[1][1]:>14,}\n\n")

            f.write("Classification Report:\n")
            report = res['classification_report']
            f.write(f"  Run  - Precision: {report['Run']['precision']:.3f}, "
                   f"Recall: {report['Run']['recall']:.3f}, "
                   f"F1: {report['Run']['f1-score']:.3f}\n")
            f.write(f"  Pass - Precision: {report['Pass']['precision']:.3f}, "
                   f"Recall: {report['Pass']['recall']:.3f}, "
                   f"F1: {report['Pass']['f1-score']:.3f}\n\n")

            # Feature importance
            if res['feature_importance']:
                f.write("Top 20 Most Important Features:\n")
                f.write("-" * 60 + "\n")
                for i, (feat, importance) in enumerate(res['feature_importance'], 1):
                    f.write(f"  {i:2d}. {feat:<45s} {importance:.6f}\n")
                f.write("\n")

    print(f"   [OK] Saved results: {results_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main training pipeline."""
    print("=" * 80)
    print("MODEL TRAINING - LINEAR REGRESSION, RANDOM FOREST, XGBOOST")
    print("=" * 80)

    # Load features
    df = load_features(SEASON)

    # Prepare data
    X, y, feature_cols = prepare_data(df)

    # Split data
    X_train, X_test, y_train, y_test = split_data(X, y)

    # Train models
    models = train_models(X_train, y_train)

    # Evaluate models
    results = evaluate_models(models, X_train, X_test, y_train, y_test, feature_cols)

    # Save results
    save_results(models, results, feature_cols, SEASON)

    print("\n" + "=" * 80)
    print("MODEL TRAINING COMPLETE!")
    print("=" * 80)

    # Print summary
    print("\n" + "FINAL RESULTS SUMMARY:")
    print("-" * 80)
    print(f"{'Model':<20} {'Test Accuracy':<15} {'Improvement over Baseline'}")
    print("-" * 80)
    baseline = 0.60  # From your previous XGBoost baseline
    for name, res in results.items():
        improvement = (res['test_accuracy'] - baseline) * 100
        print(f"{name:<20} {res['test_accuracy']:>13.1%}  {improvement:>+6.1f} percentage points")

    print(f"\nModels saved to: {MODELS_DIR}")
    print(f"Results saved to: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
