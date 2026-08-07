"""
Preprocessing Module for Election Campaign Analysis ML.

Handles target derivation (Safe vs Swing Seat), lag feature engineering,
target leakage prevention, train-test split, feature encoding, and scaling.
"""

import logging
import sys
from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import joblib

# Ensure root workspace path is in Python path for clean module imports
base_dir = Path(__file__).resolve().parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

logger = logging.getLogger(__name__)

# Features and target name
TARGET_COL = "Is_Swing"
CATEGORICAL_FEATURES = ["Year", "State", "Constituency_Type", "Prev_Winner_Party"]
NUMERICAL_FEATURES = ["Prev_Margin_Percentage", "Prev_Runner_Up_Ratio", "Prev_Incumbent_Hold_Count"]
ALL_FEATURE_COLS = CATEGORICAL_FEATURES + NUMERICAL_FEATURES

# Excluded columns explanations
EXCLUDED_COLS_EXPLANATION = {
    "Winner_Party": "Target variable or related to target in multi-class; causes target leakage.",
    "Winner_Candidate": "Post-hoc winner identity; directly correlates with the winner party.",
    "Winner_Votes": "Post-hoc winner vote count; unknown before election results.",
    "Winner_Percentage": "Post-hoc winner vote share; unknown before election results.",
    "Runner_up_Candidate": "Post-hoc runner-up identity; unknown before election results.",
    "Runner_up_Party": "Post-hoc runner-up party; highly correlates with and determines the winner party context.",
    "Runner_up_Votes": "Post-hoc runner-up vote count; unknown before election results.",
    "Runner_up_Percentage": "Post-hoc runner-up vote share; unknown before election results.",
    "Margin_Votes": "Post-hoc margin of victory in votes; unknown before election results.",
    "Margin_Percentage": "Post-hoc margin of victory percentage; unknown before election results.",
    "Status": "Post-hoc result status ('Result Declared' or 'Uncontested').",
    "Victory_Category": "Post-hoc classification of victory margin (Landslide/Comfortable/Tight).",
    "Coalition_Block": "Derived directly from Winner_Party; represents the coalition block of the winner.",
    "Runner_Up_Ratio": "Post-hoc ratio of runner-up votes to winner votes; unknown before election.",
    "Seat_Flip_Status": "Post-hoc binary flag indicating whether the seat flipped, derived using the current Winner_Party.",
    "Incumbent_Hold_Count": "Post-hoc consecutive hold count; resets based on whether the current seat flipped.",
    "Constituency_Name": "High cardinality (543 classes); causes overfitting in linear models.",
    "Constituency_No": "Constituency index sequence number; no continuous or linear relation to party performance."
}


def load_and_engineer_target(file_path: Path) -> pd.DataFrame:
    """
    Load data, compute lag features, and engineer the binary classification target.
    
    Target:
      Is_Swing = 1 (Swing Seat) if Seat_Flip_Status == 1.0 or Margin_Percentage < 5.0
      Is_Swing = 0 (Safe Seat) otherwise

    Args:
        file_path (Path): Path to constituency_engineered.csv

    Returns:
        pd.DataFrame: DataFrame with target and lag features computed.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Missing engineered dataset: {file_path}")

    logger.info(f"Loading constituency dataset from: {file_path}")
    df = pd.read_csv(file_path)

    # 1. Sort by State, Constituency_No, and Year to compute lags correctly
    df_sorted = df.sort_values(["State", "Constituency_No", "Year"]).copy()

    # 2. Derive lag features from T-1 within each constituency group
    logger.info("Generating lag features from election T-1...")
    groupby_obj = df_sorted.groupby(["State", "Constituency_No"])
    
    df_sorted["Prev_Margin_Percentage"] = groupby_obj["Margin_Percentage"].shift(1)
    df_sorted["Prev_Runner_Up_Ratio"] = groupby_obj["Runner_Up_Ratio"].shift(1)
    df_sorted["Prev_Incumbent_Hold_Count"] = groupby_obj["Incumbent_Hold_Count"].shift(1)
    # Note: Prev_Winner_Party is already in the CSV, but we can re-derive or verify it.
    
    # 3. Derive the binary target
    logger.info("Deriving binary target (Safe vs Swing Seat)...")
    df_sorted["Is_Swing"] = ((df_sorted["Seat_Flip_Status"] == 1.0) | (df_sorted["Margin_Percentage"] < 5.0)).astype(int)

    # 4. Filter out rows where lag features are missing (i.e. Year 2004 or first year of any seat)
    # This leaves us with a clean, leakage-free set of training features from prior years.
    df_ml = df_sorted.dropna(subset=["Prev_Margin_Percentage"]).copy()
    
    # Handle missing values in categorical fields (if any)
    df_ml["Prev_Winner_Party"] = df_ml["Prev_Winner_Party"].fillna("Unknown")

    return df_ml


def preprocess_and_split(
    df: pd.DataFrame, models_dir: Path
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Preprocess features (One-Hot Encode categoricals, Scale numericals),
    split into 80/20 train-test, and serialize the fitted transformers.

    Args:
        df (pd.DataFrame): Input ML DataFrame.
        models_dir (Path): Output directory for model files.

    Returns:
        Tuple: X_train, X_test, y_train, y_test arrays.
    """
    logger.info("Initializing ML preprocessing pipeline...")
    
    # Ensure types
    for col in CATEGORICAL_FEATURES:
        df[col] = df[col].astype(str)
    for col in NUMERICAL_FEATURES:
        df[col] = df[col].astype(float)

    # Separate features and target
    X_raw = df[ALL_FEATURE_COLS].copy()
    y = df[TARGET_COL].values

    # Train-test split (80/20) - stratify=y is safe here as it is binary classification
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_raw, y, test_size=0.20, random_state=42, stratify=y
    )

    logger.info(f"Train size: {len(X_train_raw)}, Test size: {len(X_test_raw)}")

    # Encode categorical features
    logger.info("Encoding categorical features...")
    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    encoder.fit(X_train_raw[CATEGORICAL_FEATURES])

    # Scale numerical features
    logger.info("Scaling numerical features...")
    scaler = StandardScaler()
    scaler.fit(X_train_raw[NUMERICAL_FEATURES])

    # Transform
    X_train_cat = encoder.transform(X_train_raw[CATEGORICAL_FEATURES])
    X_train_num = scaler.transform(X_train_raw[NUMERICAL_FEATURES])
    X_train = np.hstack([X_train_cat, X_train_num])

    X_test_cat = encoder.transform(X_test_raw[CATEGORICAL_FEATURES])
    X_test_num = scaler.transform(X_test_raw[NUMERICAL_FEATURES])
    X_test = np.hstack([X_test_cat, X_test_num])

    # Save preprocessing objects
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(encoder, models_dir / "categorical_encoder.joblib")
    joblib.dump(scaler, models_dir / "numerical_scaler.joblib")
    
    logger.info("One-hot encoder and standard scaler saved successfully.")
    
    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data_path = base_dir / "data" / "processed" / "constituency_engineered.csv"
    models_path = base_dir / "models"
    
    ml_df = load_and_engineer_target(data_path)
    X_tr, X_te, y_tr, y_te = preprocess_and_split(ml_df, models_path)
    print("Preprocessing completed successfully.")
    print("Train shape:", X_tr.shape)
    print("Test shape:", X_te.shape)
