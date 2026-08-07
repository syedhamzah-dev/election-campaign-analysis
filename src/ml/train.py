"""
Training Module for Election Campaign Analysis ML.

Trains a binary Logistic Regression model to classify Safe vs Swing seats,
and saves the trained classifier to models/safe_swing_classifier.pkl.
"""

import logging
import json
import sys
from pathlib import Path
from sklearn.linear_model import LogisticRegression
import joblib

# Ensure root workspace path is in Python path for clean module imports
base_dir = Path(__file__).resolve().parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from src.ml.preprocess import load_and_engineer_target, preprocess_and_split, CATEGORICAL_FEATURES, NUMERICAL_FEATURES

logger = logging.getLogger(__name__)


def train_classifier(data_path: Path, models_dir: Path) -> LogisticRegression:
    """
    Train a Logistic Regression binary classifier and save the model object.

    Args:
        data_path (Path): Path to dataset CSV.
        models_dir (Path): Output directory for model files.

    Returns:
        LogisticRegression: Trained model.
    """
    logger.info("Starting model training pipeline...")
    
    # 1. Preprocess data
    ml_df = load_and_engineer_target(data_path)
    X_train, X_test, y_train, y_test = preprocess_and_split(ml_df, models_dir)

    # 2. Train Logistic Regression
    logger.info("Fitting binary Logistic Regression model...")
    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        solver="lbfgs"
    )
    model.fit(X_train, y_train)
    logger.info("Classifier fitting complete.")

    # 3. Export model (safe_swing_classifier.pkl)
    model_path = models_dir / "safe_swing_classifier.pkl"
    joblib.dump(model, model_path)
    logger.info(f"Saved trained classifier to: {model_path}")

    # 4. Save metadata JSON for the dashboard
    encoder = joblib.load(models_dir / "categorical_encoder.joblib")
    feature_names = list(encoder.get_feature_names_out(CATEGORICAL_FEATURES)) + NUMERICAL_FEATURES
    
    metadata = {
        "num_train_samples": int(X_train.shape[0]),
        "num_test_samples": int(X_test.shape[0]),
        "num_features": int(X_train.shape[1]),
        "feature_names": feature_names,
        "classes": ["Safe Seat", "Swing Seat"]
    }
    
    metadata_file = models_dir / "model_metadata.json"
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
    logger.info(f"Saved model metadata to: {metadata_file}")

    return model


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data_file = base_dir / "data" / "processed" / "constituency_engineered.csv"
    models_path = base_dir / "models"
    
    train_classifier(data_file, models_path)
    print("Classifier training complete.")
