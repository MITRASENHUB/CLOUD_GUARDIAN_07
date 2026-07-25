# CloudGuardian ML Risk Prioritization

This directory contains the machine learning model for risk prioritization of security findings.

## Overview

The ML model uses a **Random Forest Classifier** to predict risk priority levels based on:
- Severity score
- Service criticality
- Public exposure
- Encryption issues
- Resource type
- Compliance impact

## Files

- `notebooks/ml-prioritization-model.ipynb` - Jupyter notebook with full ML pipeline
- `src/data_preprocessing.py` - Feature engineering
- `src/train_model.py` - Model training script
- `src/predict.py` - Inference script
- `src/feature_definitions.py` - Feature engineering logic
- `models/risk_classifier.pkl` - Trained model
- `data/training-data.csv` - Training dataset
- `data/prioritized-findings.csv` - Model predictions

## Quick Start

### 1. Train Model
```bash
python src/train_model.py
```

### 2. Generate Predictions
```bash
python src/predict.py
```

### 3. Interactive Development
```bash
jupyter notebook notebooks/ml-prioritization-model.ipynb
```

## Model Performance

**Target Metrics:**
- Accuracy: > 85%
- Precision (Critical): > 90%
- Recall (Critical): > 85%
- F1-Score: > 0.85

## Features

### Input Features (8)
1. `severity_score` - Numerical severity (0-4)
2. `service_critical` - Binary (1=critical service)
3. `public_exposure` - Binary (1=publicly exposed)
4. `encryption_issue` - Binary (1=encryption problem)
5. `resource_count` - Number of affected resources
6. `compliance_frameworks` - Number of frameworks violated
7. `exploitability` - Estimated ease of exploitation (0-3)
8. `blast_radius` - Impact scope (0-3)

### Output Classes (4)
- **CRITICAL** - Immediate action required
- **HIGH** - Action within 24 hours
- **MEDIUM** - Action within 1 week
- **LOW** - Action within 1 month

## Training Data

Training data combines:
- Consolidated CSPM findings
- Historical remediation data
- Manual risk assessments
- Synthetic examples for rare cases

## Model Architecture

```python
RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    class_weight='balanced',
    random_state=42
)
```

## Usage Example

```python
import joblib
import pandas as pd

# Load model
model = joblib.load('models/risk_classifier.pkl')

# Prepare features
features = pd.DataFrame([{
    'severity_score': 4,
    'service_critical': 1,
    'public_exposure': 1,
    'encryption_issue': 0,
    'resource_count': 1,
    'compliance_frameworks': 3,
    'exploitability': 3,
    'blast_radius': 2
}])

# Predict
risk_level = model.predict(features)[0]
confidence = model.predict_proba(features).max()

print(f"Risk Level: {risk_level} (confidence: {confidence:.2%})")
```

## Next Steps

After ML prioritization:
1. Feed prioritized findings to LLM for remediation guidance
2. Deploy Lambda functions for top-priority remediations
3. Generate compliance reports
