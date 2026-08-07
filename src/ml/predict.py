"""
Prediction Module for Election Campaign Analysis ML.

Provides an inference API for the Streamlit dashboard to predict whether
a constituency will behave as a Safe Seat or a Swing Seat based on T-1 lag features.
"""

import sys
import logging
from pathlib import Path
from typing import Union, Tuple
import pandas as pd
import numpy as np
import joblib

# Ensure root workspace path is in Python path for clean module imports
base_dir = Path(__file__).resolve().parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from src.ml.preprocess import CATEGORICAL_FEATURES, NUMERICAL_FEATURES

logger = logging.getLogger(__name__)


class SafeSwingPredictor:
    """Wrapper class to load ML artifacts and predict Safe vs Swing status."""

    def __init__(self, models_dir: Path):
        """
        Load all serialized model artifacts.

        Args:
            models_dir (Path): Directory where model files are stored.
        """
        self.models_dir = models_dir
        self.model_path = models_dir / "safe_swing_classifier.pkl"
        self.cat_encoder_path = models_dir / "categorical_encoder.joblib"
        self.num_scaler_path = models_dir / "numerical_scaler.joblib"
        
        # Load files
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        if not self.cat_encoder_path.exists():
            raise FileNotFoundError(f"Categorical encoder file not found: {self.cat_encoder_path}")
        if not self.num_scaler_path.exists():
            raise FileNotFoundError(f"Numerical scaler file not found: {self.num_scaler_path}")

        logger.info("Loading Safe vs Swing classifier artifacts...")
        self.model = joblib.load(self.model_path)
        self.cat_encoder = joblib.load(self.cat_encoder_path)
        self.num_scaler = joblib.load(self.num_scaler_path)

    def predict(
        self,
        year: Union[int, str],
        state: str,
        seat_type: str,
        prev_winner: str,
        prev_margin: float,
        prev_runner_up_ratio: float,
        prev_hold_count: int
    ) -> Tuple[str, float]:
        """
        Predict Safe vs Swing seat classification and return prediction label and confidence.

        Args:
            year: Election year
            state: Name of State/UT
            seat_type: Reserved category (GEN, SC, ST)
            prev_winner: Winning party in preceding election
            prev_margin: Victory margin percentage in preceding election
            prev_runner_up_ratio: Runner-up ratio in preceding election
            prev_hold_count: Incumbent hold count in preceding election

        Returns:
            Tuple[str, float]: (Predicted Label, Confidence Probability)
        """
        # Create raw input DataFrame
        input_data = pd.DataFrame([{
            "Year": str(year).strip(),
            "State": str(state).strip(),
            "Constituency_Type": str(seat_type).strip(),
            "Prev_Winner_Party": str(prev_winner).strip(),
            "Prev_Margin_Percentage": float(prev_margin),
            "Prev_Runner_Up_Ratio": float(prev_runner_up_ratio),
            "Prev_Incumbent_Hold_Count": float(prev_hold_count)
        }])

        # Transform inputs
        X_cat = self.cat_encoder.transform(input_data[CATEGORICAL_FEATURES])
        X_num = self.num_scaler.transform(input_data[NUMERICAL_FEATURES])
        X_encoded = np.hstack([X_cat, X_num])

        # Model inference
        pred_class = int(self.model.predict(X_encoded)[0])
        probabilities = self.model.predict_proba(X_encoded)[0]
        confidence = float(probabilities[pred_class])

        class_labels = {0: "Safe Seat", 1: "Swing Seat"}
        predicted_label = class_labels[pred_class]

        return predicted_label, confidence


# Global helper function for functional imports
def predict_safe_swing(
    year: int,
    state: str,
    seat_type: str,
    prev_winner: str,
    prev_margin: float,
    prev_runner_up_ratio: float,
    prev_hold_count: int,
    models_dir: Path
) -> Tuple[str, float]:
    """Helper wrapper for SafeSwingPredictor prediction."""
    predictor = SafeSwingPredictor(models_dir)
    return predictor.predict(
        year=year,
        state=state,
        seat_type=seat_type,
        prev_winner=prev_winner,
        prev_margin=prev_margin,
        prev_runner_up_ratio=prev_runner_up_ratio,
        prev_hold_count=prev_hold_count
    )


if __name__ == "__main__":
    models_path = base_dir / "models"
    try:
        label, conf = predict_safe_swing(
            year=2024,
            state="Uttar Pradesh",
            seat_type="GEN",
            prev_winner="BJP",
            prev_margin=18.1,
            prev_runner_up_ratio=0.6,
            prev_hold_count=1,
            models_dir=models_path
        )
        print("\n--- Test Prediction ---")
        print(f"Predicted Class: {label}")
        print(f"Confidence:      {conf:.2%}")
    except Exception as e:
        print(f"Prediction wrapper test failed: {e}")
