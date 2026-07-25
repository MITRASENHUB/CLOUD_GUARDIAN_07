#!/usr/bin/env python3
"""
CloudGuardian ML Model Training Script
Train Random Forest classifier for risk prioritization
"""

import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

from feature_definitions import engineer_features, create_target_labels, get_feature_columns

# Paths
DATA_DIR = Path("../cspm-scans/consolidated")
OUTPUT_DIR = Path("./data")
MODEL_DIR = Path("./models")

# Create directories
OUTPUT_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

def load_consolidated_findings() -> pd.DataFrame:
    """Load consolidated CSPM findings"""
    findings_file = DATA_DIR / "consolidated-findings.json"
    
    if not findings_file.exists():
        raise FileNotFoundError(
            f"Consolidated findings not found at {findings_file}. "
            "Run consolidation script first."
        )
    
    with open(findings_file, 'r') as f:
        findings = json.load(f)
    
    return pd.DataFrame(findings)

def augment_training_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Augment training data with synthetic examples
    This helps balance classes and improve model robustness
    """
    # Generate synthetic CRITICAL priority examples
    critical_synthetic = pd.DataFrame([
        {
            'service': 'iam',
            'severity': 'CRITICAL',
            'public_exposure': 1,
            'service_critical': 1,
            'encryption_issue': 0,
            'risk': 'Admin access with wildcard permissions to all resources',
            'compliance': {'iso27001': True, 'hipaa': True, 'pci_dss': True}
        },
        {
            'service': 's3',
            'severity': 'CRITICAL',
            'public_exposure': 1,
            'service_critical': 1,
            'encryption_issue': 1,
            'risk': 'Publicly accessible S3 bucket with sensitive data',
            'compliance': {'iso27001': True, 'dpdp': True}
        },
        {
            'service': 'rds',
            'severity': 'CRITICAL',
            'public_exposure': 1,
            'service_critical': 1,
            'encryption_issue': 1,
            'risk': 'Database publicly accessible from internet',
            'compliance': {'hipaa': True, 'pci_dss': True}
        }
    ])
    
    # Generate synthetic LOW priority examples
    low_synthetic = pd.DataFrame([
        {
            'service': 'cloudwatch',
            'severity': 'LOW',
            'public_exposure': 0,
            'service_critical': 0,
            'encryption_issue': 0,
            'risk': 'CloudWatch log retention period is short',
            'compliance': {}
        },
        {
            'service': 'sns',
            'severity': 'LOW',
            'public_exposure': 0,
            'service_critical': 0,
            'encryption_issue': 0,
            'risk': 'SNS topic without encryption',
            'compliance': {}
        }
    ])
    
    return pd.concat([df, critical_synthetic, low_synthetic], ignore_index=True)

def train_model(X_train, y_train, X_test, y_test):
    """
    Train Random Forest classifier
    
    Returns:
        Trained model and metrics
    """
    print("\nTraining Random Forest Classifier...")
    
    # Initialize model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight='balanced',  # Handle class imbalance
        random_state=42,
        n_jobs=-1
    )
    
    # Train model
    model.fit(X_train, y_train)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
    print(f"Cross-validation scores: {cv_scores}")
    print(f"Mean CV score: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Evaluation metrics
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy: {accuracy:.3f}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred, labels=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'])
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': get_feature_columns(),
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    print(feature_importance)
    
    return model, {
        'accuracy': accuracy,
        'cv_scores': cv_scores.tolist(),
        'feature_importance': feature_importance.to_dict('records'),
        'confusion_matrix': cm.tolist()
    }

def save_model_artifacts(model, metrics, feature_cols):
    """Save trained model and metadata"""
    # Save model
    model_path = MODEL_DIR / "risk_classifier.pkl"
    joblib.dump(model, model_path)
    print(f"\n✓ Model saved to {model_path}")
    
    # Save metadata
    metadata = {
        'model_type': 'RandomForestClassifier',
        'n_estimators': 100,
        'feature_columns': feature_cols,
        'target_classes': ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
        'metrics': metrics,
        'training_date': pd.Timestamp.now().isoformat()
    }
    
    metadata_path = MODEL_DIR / "model_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved to {metadata_path}")
    
    # Save feature importance
    importance_df = pd.DataFrame(metrics['feature_importance'])
    importance_path = OUTPUT_DIR / "feature-importance.csv"
    importance_df.to_csv(importance_path, index=False)
    print(f"✓ Feature importance saved to {importance_path}")

def main():
    print("="*60)
    print("CloudGuardian ML Model Training")
    print("="*60)
    
    # Load data
    print("\n1. Loading consolidated findings...")
    df = load_consolidated_findings()
    print(f"   Loaded {len(df)} findings")
    
    # Augment with synthetic data
    print("\n2. Augmenting training data...")
    df = augment_training_data(df)
    print(f"   Total samples: {len(df)}")
    
    # Feature engineering
    print("\n3. Engineering features...")
    df = engineer_features(df)
    
    # Create target labels
    print("\n4. Creating target labels...")
    df['risk_priority'] = create_target_labels(df)
    print("   Priority distribution:")
    print(df['risk_priority'].value_counts())
    
    # Save training data
    training_data_path = OUTPUT_DIR / "training-data.csv"
    df.to_csv(training_data_path, index=False)
    print(f"\n   ✓ Training data saved to {training_data_path}")
    
    # Prepare features and target
    feature_cols = get_feature_columns()
    X = df[feature_cols]
    y = df['risk_priority']
    
    # Train-test split
    print("\n5. Splitting data (80/20 train/test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Training samples: {len(X_train)}")
    print(f"   Test samples: {len(X_test)}")
    
    # Train model
    print("\n6. Training model...")
    model, metrics = train_model(X_train, y_train, X_test, y_test)
    
    # Save artifacts
    print("\n7. Saving model artifacts...")
    save_model_artifacts(model, metrics, feature_cols)
    
    print("\n" + "="*60)
    print("✓ Model training complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Review feature importance: cat data/feature-importance.csv")
    print("  2. Run predictions: python src/predict.py")
    print("  3. Generate LLM remediation: cd ../llm-remediation")
    print()

if __name__ == "__main__":
    main()
