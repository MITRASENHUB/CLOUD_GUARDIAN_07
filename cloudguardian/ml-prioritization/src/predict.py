#!/usr/bin/env python3
"""
CloudGuardian ML Prediction Script
Generate risk predictions for new findings
"""

import pandas as pd
import joblib
import json
from pathlib import Path
from feature_definitions import engineer_features, get_feature_columns

# Paths
MODEL_PATH = Path("./models/risk_classifier.pkl")
FINDINGS_PATH = Path("../cspm-scans/consolidated/consolidated-findings.json")
OUTPUT_PATH = Path("./data/prioritized-findings.csv")

def load_model():
    """Load trained ML model"""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found at {MODEL_PATH}. "
            "Run training script first: python src/train_model.py"
        )
    
    return joblib.load(MODEL_PATH)

def load_findings() -> pd.DataFrame:
    """Load consolidated findings"""
    if not FINDINGS_PATH.exists():
        raise FileNotFoundError(
            f"Consolidated findings not found at {FINDINGS_PATH}. "
            "Run consolidation first."
        )
    
    with open(FINDINGS_PATH, 'r') as f:
        findings = json.load(f)
    
    return pd.DataFrame(findings)

def generate_predictions(model, df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate risk predictions
    
    Returns:
        DataFrame with predictions and confidence scores
    """
    # Engineer features
    df = engineer_features(df)
    
    # Get feature columns
    feature_cols = get_feature_columns()
    X = df[feature_cols]
    
    # Generate predictions
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    
    # Add to dataframe
    df['ml_risk_priority'] = predictions
    df['ml_confidence'] = probabilities.max(axis=1)
    
    # Add probability for each class
    classes = model.classes_
    for idx, cls in enumerate(classes):
        df[f'prob_{cls.lower()}'] = probabilities[:, idx]
    
    return df

def rank_findings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rank findings by ML priority and confidence
    """
    # Priority order
    priority_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
    df['priority_score'] = df['ml_risk_priority'].map(priority_order)
    
    # Sort by priority then confidence
    df = df.sort_values(
        by=['priority_score', 'ml_confidence'],
        ascending=[False, False]
    )
    
    # Add rank
    df['rank'] = range(1, len(df) + 1)
    
    return df

def main():
    print("="*60)
    print("CloudGuardian ML Risk Prediction")
    print("="*60)
    
    # Load model
    print("\n1. Loading trained model...")
    model = load_model()
    print("   ✓ Model loaded")
    
    # Load findings
    print("\n2. Loading consolidated findings...")
    df = load_findings()
    print(f"   Loaded {len(df)} findings")
    
    # Generate predictions
    print("\n3. Generating risk predictions...")
    df = generate_predictions(model, df)
    print("   ✓ Predictions complete")
    
    # Rank findings
    print("\n4. Ranking findings...")
    df = rank_findings(df)
    
    # Summary statistics
    print("\n" + "="*60)
    print("Prediction Summary")
    print("="*60)
    print(f"\nRisk Priority Distribution:")
    print(df['ml_risk_priority'].value_counts())
    print(f"\nAverage Confidence: {df['ml_confidence'].mean():.2%}")
    print(f"\nTop 10 Highest Priority Findings:")
    print(df[[
        'rank', 'ml_risk_priority', 'ml_confidence',
        'service', 'severity', 'check_title'
    ]].head(10).to_string(index=False))
    
    # Save predictions
    print(f"\n5. Saving prioritized findings...")
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"   ✓ Saved to {OUTPUT_PATH}")
    
    # Save top priority findings for LLM
    top_critical = df[df['ml_risk_priority'] == 'CRITICAL'].head(10)
    llm_input_path = Path("../llm-remediation/inputs/top-priority-findings.json")
    llm_input_path.parent.mkdir(exist_ok=True, parents=True)
    
    top_critical_json = top_critical[[
        'finding_id', 'check_id', 'check_title', 'service',
        'resource', 'severity', 'risk', 'ml_risk_priority', 'ml_confidence'
    ]].to_dict('records')
    
    with open(llm_input_path, 'w') as f:
        json.dump(top_critical_json, f, indent=2)
    print(f"   ✓ Top priority findings for LLM saved to {llm_input_path}")
    
    print("\n" + "="*60)
    print("✓ Risk prioritization complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Review prioritized findings: cat data/prioritized-findings.csv")
    print("  2. Generate LLM remediation: cd ../llm-remediation && python src/generate_guidance.py")
    print()

if __name__ == "__main__":
    main()
