"""
Evaluation Module for Election Campaign Analysis ML.

Evaluates the Safe vs Swing classifier on the test split,
saves performance metrics JSON, and exports visualizations:
- Confusion Matrix (2x2)
- Feature Coefficients (top signed influences)
- Competitiveness Score Distribution (across all constituencies)
"""

import sys
import logging
import json
from pathlib import Path
from typing import Dict, Any

# Ensure root workspace path is in Python path for clean module imports
base_dir = Path(__file__).resolve().parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)
import joblib

from src.ml.preprocess import load_and_engineer_target, preprocess_and_split, CATEGORICAL_FEATURES, NUMERICAL_FEATURES
from src.visualization.base import setup_matplotlib_style, save_figure

logger = logging.getLogger(__name__)


def generate_evaluation_artifacts(
    data_path: Path, models_dir: Path, outputs_dir: Path
) -> Dict[str, Any]:
    """
    Evaluate trained safe/swing classifier, save metrics, and generate figures.

    Args:
        data_path (Path): Path to dataset CSV.
        models_dir (Path): Model and encoder directory.
        outputs_dir (Path): Output directory for ML figures.

    Returns:
        Dict[str, Any]: Performance metrics.
    """
    logger.info("Starting model evaluation...")
    
    # 1. Load model and preprocessors
    model_path = models_dir / "safe_swing_classifier.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Trained model not found: {model_path}")
        
    model = joblib.load(model_path)
    encoder = joblib.load(models_dir / "categorical_encoder.joblib")
    scaler = joblib.load(models_dir / "numerical_scaler.joblib")
    
    # 2. Get preprocessed data
    ml_df = load_and_engineer_target(data_path)
    _, X_test, _, y_test = preprocess_and_split(ml_df, models_dir)
    
    # 3. Generate predictions
    logger.info("Predicting on test split...")
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] # Probability of Swing (class 1)
    
    # 4. Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average="binary", pos_label=1, zero_division=0
    )
    
    class_report_dict = classification_report(
        y_test, y_pred, target_names=["Safe Seat", "Swing Seat"], output_dict=True, zero_division=0
    )
    
    metrics_summary = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "classification_report": class_report_dict
    }
    
    # Save metrics JSON
    metrics_file = models_dir / "evaluation_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=4)
    logger.info(f"Evaluation metrics JSON saved to: {metrics_file}")
    
    # Configure styling
    setup_matplotlib_style()
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    # 5. Visual 1: Confusion Matrix (2x2)
    logger.info("Plotting Confusion Matrix...")
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Safe Seat", "Swing Seat"],
        yticklabels=["Safe Seat", "Swing Seat"],
        ax=ax,
        cbar=True,
        square=True
    )
    ax.set_title("Confusion Matrix: Safe vs Swing Seat", pad=15)
    ax.set_xlabel("Predicted Label", labelpad=10)
    ax.set_ylabel("Actual Label", labelpad=10)
    
    cm_path = outputs_dir / "confusion_matrix.png"
    save_figure(fig, cm_path)
    
    # 6. Visual 2: Feature Coefficients Plot (signed weights)
    logger.info("Plotting Feature Coefficients...")
    coefs = model.coef_[0]
    feature_names = list(encoder.get_feature_names_out(CATEGORICAL_FEATURES)) + NUMERICAL_FEATURES
    
    # Clean display names
    clean_names = []
    for name in feature_names:
        for orig in CATEGORICAL_FEATURES + NUMERICAL_FEATURES:
            if name.startswith(orig + "_"):
                val = name[len(orig) + 1:]
                clean_names.append(f"{orig}: {val}")
                break
        else:
            clean_names.append(name)
            
    coef_df = pd.DataFrame({
        "Feature": clean_names,
        "Coefficient": coefs,
        "Abs_Coefficient": np.abs(coefs)
    }).sort_values("Abs_Coefficient", ascending=False)
    
    # Save feature ranking JSON for tables
    coef_df.to_json(models_dir / "feature_coefficients.json", orient="records", indent=4)
    
    # Plot top 15 signed coefficients
    top_n = 15
    top_coef_df = coef_df.head(top_n).copy().sort_values("Coefficient", ascending=True)
    
    fig_feat, ax_feat = plt.subplots(figsize=(9, 6))
    colors = np.where(top_coef_df["Coefficient"] >= 0, "#10B981", "#EF4444") # Green for Swing shift, Red for Safe shift
    
    bars = ax_feat.barh(
        top_coef_df["Feature"],
        top_coef_df["Coefficient"],
        color=colors,
        edgecolor="none"
    )
    
    ax_feat.set_title("Top Logistic Regression Feature Influence (Signed Coefficients)", pad=15)
    ax_feat.set_xlabel("Coefficient Weight\n(Positive -> Predicts Swing Seat  |  Negative -> Predicts Safe Seat)", labelpad=10)
    ax_feat.axvline(0, color="gray", linestyle="-", linewidth=0.8)
    ax_feat.grid(True, linestyle="--", alpha=0.5)
    
    feat_path = outputs_dir / "feature_coefficients.png"
    save_figure(fig_feat, feat_path)
    
    # 7. Visual 3: Competitiveness Score Distribution
    logger.info("Plotting Competitiveness Distribution...")
    intelligence_file = models_dir / "election_intelligence.json"
    if not intelligence_file.exists():
        logger.warning("Intelligence database not found. Skipping competitiveness distribution plot.")
        return metrics_summary
        
    with open(intelligence_file, "r", encoding="utf-8") as f:
        intel_db = json.load(f)
        
    scores = [val["competitiveness_score"] for val in intel_db.values()]
    
    fig_dist, ax_dist = plt.subplots(figsize=(9, 5))
    
    # Background spans for categories
    # 0-30: Safe (Green)
    # 30-70: Moderately Competitive (Yellow/Orange)
    # 70-100: Highly Competitive (Red)
    ax_dist.axvspan(0, 30, color="#d1fae5", alpha=0.5, label="Safe (0-30)")
    ax_dist.axvspan(30, 70, color="#ffedd5", alpha=0.5, label="Moderately Competitive (31-70)")
    ax_dist.axvspan(70, 100, color="#fee2e2", alpha=0.5, label="Highly Competitive (71-100)")
    
    # Histogram plot
    sns.histplot(scores, kde=True, bins=25, color="#1E3A8A", edgecolor="white", alpha=0.8, ax=ax_dist)
    
    ax_dist.set_xlim(0, 100)
    ax_dist.set_title("Distribution of Constituency Competitiveness Scores", pad=15)
    ax_dist.set_xlabel("Competitiveness Score (0 - 100)", labelpad=10)
    ax_dist.set_ylabel("Number of Constituencies", labelpad=10)
    ax_dist.legend(loc="upper right")
    
    dist_path = outputs_dir / "competitiveness_distribution.png"
    save_figure(fig_dist, dist_path)
    
    logger.info("All evaluation outputs successfully generated.")
    return metrics_summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data_file = base_dir / "data" / "processed" / "constituency_engineered.csv"
    models_path = base_dir / "models"
    outputs_path = base_dir / "outputs" / "ml"
    
    metrics = generate_evaluation_artifacts(data_file, models_path, outputs_path)
    print("\n--- Safe vs Swing Performance Summary ---")
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1 Score:  {metrics['f1_score']:.4f}")
