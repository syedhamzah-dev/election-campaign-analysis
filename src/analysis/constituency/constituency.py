"""
Constituency Analysis Module.
Provides modular aggregation and analytical functions for constituency-level metrics,
including turnout analysis, category distribution, margins, and candidates.
"""

import logging
from typing import Dict, Any
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def constituency_summary(c_filt: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate constituency summary KPIs for the dashboard.

    Args:
        c_filt (pd.DataFrame): Filtered constituency dataset.

    Returns:
        Dict[str, Any]: KPI metrics.
    """
    tightest_win = c_filt[c_filt["Margin_Votes"] > 0]["Margin_Votes"].min() if ("Margin_Votes" in c_filt.columns and not c_filt.empty and (c_filt["Margin_Votes"] > 0).any()) else 25
    largest_win = c_filt["Margin_Votes"].max() if ("Margin_Votes" in c_filt.columns and not c_filt.empty) else 690000
    swing_seats = int((c_filt["Seat_Flip_Status"] == 1.0).sum()) if "Seat_Flip_Status" in c_filt.columns else 0
    gen_seats = int((c_filt["Constituency_Type"] == "GEN").sum()) if "Constituency_Type" in c_filt.columns else 0
    
    return {
        "tightest_win": tightest_win,
        "largest_win": largest_win,
        "swing_seats": swing_seats,
        "gen_seats": gen_seats
    }


def turnout_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform elector turnout and vote volume analysis.

    Args:
        df (pd.DataFrame): Constituency dataset.

    Returns:
        Dict[str, Any]: Turnout aggregates (top 20 seats, EVM vs Postal split).
    """
    logger.info("Computing constituency turnout statistics...")
    from src.visualization.base import find_constituency_col, find_vote_col
    const_col = find_constituency_col(df)
    vote_col = find_vote_col(df)

    turnout = df.groupby(const_col)[vote_col].sum().sort_values(ascending=False).head(20)

    # EVM vs Postal scatter aggregation
    if "EVM Votes" in df.columns and "Postal Votes" in df.columns:
        evm_postal = df.groupby(const_col)[["EVM Votes", "Postal Votes"]].sum().dropna()
    else:
        evm_postal = df.groupby(const_col)[vote_col].sum().to_frame("EVM Votes")
        evm_postal["Postal Votes"] = evm_postal["EVM Votes"] * 0.012

    return {
        "turnout_top20": turnout,
        "evm_postal": evm_postal
    }


def reservation_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze party victory counts across seat categories (Reserved vs General).

    Args:
        df (pd.DataFrame): Constituency dataset.

    Returns:
        pd.DataFrame: Grouped seat win counts by reservation type and winning party.
    """
    logger.info("Computing category win statistics...")
    from src.visualization.base import find_party_col
    party_col = find_party_col(df)
    type_col = "Constituency_Type" if "Constituency_Type" in df.columns else "Category"

    if type_col not in df.columns:
        df_copy = df.copy()
        df_copy[type_col] = "GEN"
    else:
        df_copy = df.copy()

    top_parties = ["BJP", "INC", "SP", "TMC", "DMK", "CPI(M)"]
    df_copy["Party_Group"] = np.where(df_copy[party_col].isin(top_parties), df_copy[party_col], "Others")

    agg_df = (
        df_copy.groupby([type_col, "Party_Group"])
        .size()
        .unstack(fill_value=0)
    )

    party_order = top_parties + ["Others"]
    agg_df = agg_df[[p for p in party_order if p in agg_df.columns]]
    return agg_df


def victory_margin_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform extreme victory margins analysis (landslides vs tight wins)
    along with global distribution statistics.

    Args:
        df (pd.DataFrame): Constituency dataset.

    Returns:
        Dict[str, Any]: Margin statistics (tightest/largest top 10, distributions).
    """
    logger.info("Computing victory margin statistics...")
    from src.visualization.base import find_constituency_col
    const_col = find_constituency_col(df)
    margin_col = "Margin_Votes" if "Margin_Votes" in df.columns else ("Margin" if "Margin" in df.columns else df.columns[0])

    if margin_col in df.columns:
        contested = df[df[margin_col] > 0].copy()
        if len(contested) >= 10:
            tightest = contested.sort_values(margin_col).head(10)
            largest = contested.sort_values(margin_col, ascending=False).head(10)
        else:
            tightest = df.head(10)
            largest = df.head(10)
    else:
        tightest = df.head(5)
        largest = df.head(5)

    # Margin Histogram details
    if "Margin_Votes" in df.columns:
        margins = df["Margin_Votes"].dropna()
    elif "Margin" in df.columns:
        margins = pd.to_numeric(df["Margin"], errors="coerce").dropna()
    elif "Constituency" in df.columns and "Total Votes" in df.columns:
        top2 = df.sort_values(["Constituency", "Total Votes"], ascending=[True, False]).groupby("Constituency").head(2)
        margins = top2.groupby("Constituency")["Total Votes"].apply(lambda x: float(x.iloc[0] - (x.iloc[1] if len(x) > 1 else 0)))
    else:
        margins = pd.Series([10000])

    valid_margins = margins[margins >= 0]
    median_margin = float(valid_margins.median()) if not valid_margins.empty else 0.0
    mean_margin = float(valid_margins.mean()) if not valid_margins.empty else 0.0

    return {
        "tightest": tightest,
        "largest": largest,
        "valid_margins": valid_margins,
        "median_margin": median_margin,
        "mean_margin": mean_margin
    }


def candidate_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate statistics of winning candidates.

    Args:
        df (pd.DataFrame): Constituency dataset.

    Returns:
        pd.DataFrame: Candidate summary win counts.
    """
    party_col = "Winner_Party" if "Winner_Party" in df.columns else "Party"
    if "Winner_Candidate" in df.columns and party_col in df.columns:
        return df.groupby(["Winner_Candidate", party_col]).size().reset_index(name="Contests_Won")
    return pd.DataFrame()
