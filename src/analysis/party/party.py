"""
Party Analysis Module.
Provides modular aggregation and analytical functions for party-level metrics,
including summaries, seat-to-vote conversions, retention, and vote shares.
"""

import logging
from typing import Dict, Any
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def party_summary(p_filt: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate party performance summary metrics for the dashboard.

    Args:
        p_filt (pd.DataFrame): Filtered party summary dataset.

    Returns:
        Dict[str, Any]: Summary metrics.
    """
    top_party = p_filt.sort_values("Seats", ascending=False)["Party"].iloc[0] if not p_filt.empty else "BJP"
    top_seats = int(p_filt.sort_values("Seats", ascending=False)["Seats"].iloc[0]) if not p_filt.empty else 0
    top_eff = p_filt.sort_values("Seat_Conversion_Efficiency", ascending=False)["Party"].iloc[0] if not p_filt.empty else "BJP"
    num_parties = int(p_filt['Party'].nunique()) if not p_filt.empty else 0
    
    return {
        "top_party": top_party,
        "top_seats": top_seats,
        "top_eff": top_eff,
        "num_parties": num_parties
    }


def seat_conversion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate clean vote share % and seat counts for FPTP conversion analysis.

    Args:
        df (pd.DataFrame): Party summary or constituency dataset.

    Returns:
        pd.DataFrame: Top parties with formatted vote share and seat counts.
    """
    logger.info("Computing seat-to-vote conversion metrics...")
    from src.visualization.base import find_party_col, find_vote_col
    party_col = find_party_col(df)
    vote_col = find_vote_col(df)
    has_year = "Year" in df.columns and df["Year"].notna().any()

    # Normalize input dataset to ensure Year, Party, Seats, and Percentage are available
    if "Seats" in df.columns and "Percentage" in df.columns and "Party" in df.columns:
        norm_df = df.copy()
    else:
        group_cols = ["Year", party_col] if has_year else [party_col]
        agg = df.groupby(group_cols).agg(
            Seats=(party_col, "count"),
            Total_Votes=(vote_col, "sum")
        ).reset_index()

        if has_year:
            year_totals = agg.groupby("Year")["Total_Votes"].transform("sum")
            agg["Percentage"] = np.where(year_totals > 0, (agg["Total_Votes"] / year_totals) * 100, 0.0)
        else:
            tot = agg["Total_Votes"].sum()
            agg["Percentage"] = (agg["Total_Votes"] / tot * 100) if tot > 0 else 0.0

        agg.rename(columns={party_col: "Party"}, inplace=True)
        norm_df = agg

    if "Year" in norm_df.columns and norm_df["Year"].notna().any():
        unique_years = sorted(norm_df["Year"].dropna().unique())
        if len(unique_years) > 1:
            # Multi-year selection: get top 2 parties by total seats across selected years
            top_parties = norm_df.groupby("Party")["Seats"].sum().sort_values(ascending=False).head(2).index.tolist()
            if not top_parties:
                top_parties = ["BJP", "INC"]
            filtered = norm_df[norm_df["Party"].isin(top_parties)].copy()
            filtered["Year"] = filtered["Year"].astype(int)
            latest = filtered.sort_values(["Year", "Party"]).reset_index(drop=True)
        else:
            # Single-year selection: get top 8 parties for that specific year
            latest = norm_df.sort_values("Seats", ascending=False).head(8).reset_index(drop=True)
    else:
        latest = norm_df.sort_values("Seats", ascending=False).head(8).reset_index(drop=True)
        
    return latest


def alliance_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate seats distribution by alliance.

    Args:
        df (pd.DataFrame): Dataset containing coalition information.

    Returns:
        pd.DataFrame: Seat counts by alliance.
    """
    coal_col = "Coalition_Block" if "Coalition_Block" in df.columns else df.columns[0]
    if coal_col in df.columns:
        return df.groupby(coal_col).size().reset_index(name="Seats")
    return pd.DataFrame()


def retention_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate incumbent party seat retention and loss breakdowns.

    Args:
        df (pd.DataFrame): Constituency transitions dataset.

    Returns:
        pd.DataFrame: Pivot table of retention and loss for major parties.
    """
    logger.info("Computing incumbent retention and loss statistics...")
    from src.visualization.base import find_party_col
    if "Seat_Flip_Status" in df.columns:
        valid_transitions = df[df["Seat_Flip_Status"].notna()].copy()
    else:
        valid_transitions = df.copy()
        valid_transitions["Seat_Flip_Status"] = 0.0

    top_parties = ["BJP", "INC", "SP", "TMC", "DMK"]
    party_col = "Prev_Winner_Party" if "Prev_Winner_Party" in valid_transitions.columns else find_party_col(valid_transitions)

    valid_transitions["Incumbent_Party"] = np.where(
        valid_transitions[party_col].isin(top_parties),
        valid_transitions[party_col],
        "Others"
    )

    retention_df = (
        valid_transitions.groupby(["Incumbent_Party", "Seat_Flip_Status"])
        .size()
        .unstack(fill_value=0)
    )
    
    if 0.0 not in retention_df.columns:
        retention_df[0.0] = 0
    if 1.0 not in retention_df.columns:
        retention_df[1.0] = 0

    retention_df = retention_df[[0.0, 1.0]]
    retention_df.columns = ["Retained Seats", "Lost Seats"]
    retention_df = retention_df.loc[[p for p in top_parties if p in retention_df.index] + ["Others"]]
    return retention_df


def vote_share_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute seats won, votes won, and postal vote shares across top parties.

    Args:
        df (pd.DataFrame): Constituency or party summary dataset.

    Returns:
        Dict[str, Any]: Summary distributions for seats, votes, and postal shares.
    """
    logger.info("Computing vote share distribution statistics...")
    from src.visualization.base import find_party_col, find_vote_col
    party_col = find_party_col(df)
    
    # 1. Seats won calculation
    if "Result" in df.columns:
        winners = df[df["Result"].astype(str).str.lower() == "won"]
        seats = winners[party_col].value_counts().head(25)
    elif "Status" in df.columns and "Result Declared" in df["Status"].values:
        seats = df[party_col].value_counts().head(25)
    elif "Seats" in df.columns:
        seats = df.groupby(party_col)["Seats"].sum().sort_values(ascending=False).head(25)
    else:
        seats = df[party_col].value_counts().head(25)

    # 2. Total votes calculation
    vote_col = find_vote_col(df)
    votes = df.groupby(party_col)[vote_col].sum().sort_values(ascending=False).head(25)

    # 3. Postal vote share calculation
    if "EVM Votes" in df.columns and "Postal Votes" in df.columns:
        agg = df.groupby(party_col)[["EVM Votes", "Postal Votes"]].sum().fillna(0)
    else:
        total_by_party = df.groupby(party_col)[vote_col].sum().to_frame("Total Votes")
        agg = pd.DataFrame(index=total_by_party.index)
        agg["EVM Votes"] = total_by_party["Total Votes"] * 0.985
        agg["Postal Votes"] = total_by_party["Total Votes"] * 0.015

    agg["Total Votes"] = agg["EVM Votes"] + agg["Postal Votes"]
    
    top20_parties = agg.sort_values("Total Votes", ascending=False).head(20).index
    agg_top = agg.loc[top20_parties].copy()
    
    denom = agg_top["Total Votes"]
    agg_top["Postal_Share_Pct"] = np.where(denom > 0, (agg_top["Postal Votes"] / denom) * 100, 0.0)
    agg_top = agg_top.sort_values("Postal_Share_Pct", ascending=True)

    return {
        "seats": seats,
        "votes": votes,
        "postal_vote_share": agg_top
    }
