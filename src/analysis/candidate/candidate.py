"""
Candidate Analysis Module.
Provides modular aggregation and analytical functions for candidate-level metrics.
"""

import logging
from typing import Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)


def candidate_profile(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """
    Search and retrieve records for a candidate by name.

    Args:
        df (pd.DataFrame): Constituency dataset.
        name (str): Candidate name (or partial name).

    Returns:
        pd.DataFrame: Matching candidate rows.
    """
    if "Winner_Candidate" in df.columns:
        return df[df["Winner_Candidate"].str.contains(name, case=False, na=False)]
    return pd.DataFrame()


def candidate_history(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """
    Retrieve historical contest details for a given candidate.

    Args:
        df (pd.DataFrame): Constituency dataset.
        name (str): Candidate name.

    Returns:
        pd.DataFrame: Candidate history records.
    """
    return candidate_profile(df, name)


def candidate_performance(df: pd.DataFrame, name: str) -> Dict[str, Any]:
    """
    Evaluate candidate historical performance statistics.

    Args:
        df (pd.DataFrame): Constituency dataset.
        name (str): Candidate name.

    Returns:
        Dict[str, Any]: Performance stats (contests won, avg margin, parties represented).
    """
    prof = candidate_profile(df, name)
    if prof.empty:
        return {
            "wins": 0,
            "avg_margin": 0.0,
            "parties": []
        }
    
    margin_col = "Margin_Percentage" if "Margin_Percentage" in prof.columns else "Margin_Votes"
    avg_margin = float(prof[margin_col].mean()) if margin_col in prof.columns else 0.0
    parties = prof["Winner_Party"].unique().tolist() if "Winner_Party" in prof.columns else []

    return {
        "wins": len(prof),
        "avg_margin": avg_margin,
        "parties": parties
    }
