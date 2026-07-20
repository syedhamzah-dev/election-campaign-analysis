"""
Feature Engineering Module for Election Campaign Analysis (2004-2024).

Implements vectorized, modular feature engineering functions to generate
analytically meaningful metrics for EDA, Streamlit dashboard visuals, and ML.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Political Alliance Coalition Mapping Sets
NDA_PARTIES = {
    "BJP", "TDP", "JD(U)", "SS", "LJP", "LJPRV", "SAD", "AD(S)", "RLD",
    "AGP", "HAM(S)", "AJSU", "JSP", "UPPL", "SKM", "NCP", "NPF", "NDPP"
}

UPA_INDIA_PARTIES = {
    "INC", "SP", "TMC", "DMK", "RJD", "NCP-SP", "SS(UBT)", "JMM", "IUML",
    "AAP", "CPI(M)", "CPI", "CPI(ML)L", "VCK", "JKNC", "RSP", "MDMK", "RLP",
    "BAP", "VPP", "KEC", "KEC(M)", "JVM(P)", "RLTP"
}

LEFT_FRONT_PARTIES = {"CPI(M)", "CPI", "AIFB", "RSP", "CPI(ML)L", "SUCI"}


def compute_margin_percentage(df: pd.DataFrame) -> pd.Series:
    """
    Compute normalized victory margin percentage relative to top-2 total valid votes.

    Formula: (Margin_Votes / (Winner_Votes + Runner_up_Votes)) * 100

    Args:
        df (pd.DataFrame): Constituency DataFrame containing vote metrics.

    Returns:
        pd.Series: Computed Margin_Percentage series.
    """
    top2_total = df["Winner_Votes"] + df["Runner_up_Votes"]
    valid_mask = top2_total > 0

    margin_pct = np.zeros(len(df), dtype=np.float64)
    margin_pct[valid_mask] = np.round(
        (df.loc[valid_mask, "Margin_Votes"] / top2_total[valid_mask]) * 100, 2
    )
    return pd.Series(margin_pct, index=df.index)


def categorize_victory_margin(margin_pct_series: pd.Series) -> pd.Series:
    """
    Categorize victory margins into competitiveness tiers.

    Tiers:
    - Landslide: Margin % > 15.0%
    - Comfortable: 5.0% <= Margin % <= 15.0%
    - Tight / Close Contest: Margin % < 5.0%

    Args:
        margin_pct_series (pd.Series): Margin_Percentage series.

    Returns:
        pd.Series: Categorical Victory_Category series.
    """
    conditions = [
        margin_pct_series > 15.0,
        (margin_pct_series >= 5.0) & (margin_pct_series <= 15.0),
        margin_pct_series < 5.0,
    ]
    choices = ["Landslide", "Comfortable", "Tight / Close Contest"]

    categories = np.select(conditions, choices, default="Comfortable")
    return pd.Series(categories, index=margin_pct_series.index)


def assign_coalition_block(party_series: pd.Series) -> pd.Series:
    """
    Assign major political coalition block to each winning party.

    Categories:
    - NDA
    - UPA / I.N.D.I.A.
    - Left Front
    - Others / Regional

    Args:
        party_series (pd.Series): Winning party acronyms series.

    Returns:
        pd.Series: Coalition_Block categorical series.
    """
    coalitions = np.full(len(party_series), "Others / Regional", dtype=object)

    is_nda = party_series.isin(NDA_PARTIES)
    is_upa = party_series.isin(UPA_INDIA_PARTIES)
    is_left = party_series.isin(LEFT_FRONT_PARTIES)

    coalitions[is_nda] = "NDA"
    coalitions[is_upa] = "UPA / I.N.D.I.A."
    coalitions[is_left & ~is_upa] = "Left Front"

    return pd.Series(coalitions, index=party_series.index)


def compute_runner_up_ratio(df: pd.DataFrame) -> pd.Series:
    """
    Compute runner-up challenge intensity ratio relative to winner votes.

    Formula: Runner_up_Votes / Winner_Votes

    Args:
        df (pd.DataFrame): Constituency DataFrame.

    Returns:
        pd.Series: Runner_Up_Ratio series (range: 0.0 to 1.0).
    """
    winner_votes = df["Winner_Votes"]
    valid_mask = winner_votes > 0

    ratio = np.zeros(len(df), dtype=np.float64)
    ratio[valid_mask] = np.round(
        (df.loc[valid_mask, "Runner_up_Votes"] / winner_votes[valid_mask]), 4
    )
    return pd.Series(ratio, index=df.index)


def compute_seat_flip_status(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Track historical seat flips and incumbent holds across consecutive election cycles.

    Args:
        df (pd.DataFrame): Cleaned constituency DataFrame.

    Returns:
        Tuple[pd.Series, pd.Series, pd.Series]:
            - Prev_Winner_Party: Winner party in election T-1.
            - Seat_Flip_Status: 1.0 if winner party changed from election T-1, 0.0 if retained, NaN for base 2004.
            - Incumbent_Hold_Count: Number of consecutive holds.
    """
    original_index = df.index
    sorted_df = df.sort_values(["State", "Constituency_No", "Year"]).copy()

    sorted_df["Prev_Winner_Party"] = sorted_df.groupby(["State", "Constituency_No"])["Winner_Party"].shift(1)
    sorted_df["Prev_Year"] = sorted_df.groupby(["State", "Constituency_No"])["Year"].shift(1)

    is_consecutive = (sorted_df["Year"] - sorted_df["Prev_Year"]) == 5

    seat_flip = np.full(len(sorted_df), np.nan, dtype=np.float64)
    seat_flip[is_consecutive] = (
        sorted_df.loc[is_consecutive, "Winner_Party"] != sorted_df.loc[is_consecutive, "Prev_Winner_Party"]
    ).astype(np.float64)

    sorted_df["Seat_Flip_Status"] = seat_flip

    # Compute consecutive hold count vectorially
    sorted_df["_flip_flag"] = (sorted_df["Seat_Flip_Status"] == 1.0).astype(int)
    sorted_df["_flip_block"] = sorted_df.groupby(["State", "Constituency_No"])["_flip_flag"].cumsum()
    sorted_df["Incumbent_Hold_Count"] = sorted_df.groupby(["State", "Constituency_No", "_flip_block"]).cumcount()
    sorted_df.loc[sorted_df["Seat_Flip_Status"].isna(), "Incumbent_Hold_Count"] = 0

    # Sort back to original index
    aligned_df = sorted_df.reindex(original_index)

    return (
        aligned_df["Prev_Winner_Party"],
        aligned_df["Seat_Flip_Status"],
        aligned_df["Incumbent_Hold_Count"].astype(np.int64),
    )


def engineer_constituency_features(c_df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline to engineer all constituency-level features.

    Args:
        c_df (pd.DataFrame): Cleaned constituency master dataset.

    Returns:
        pd.DataFrame: Feature-enriched constituency dataset.
    """
    logger.info("Engineering constituency-level features...")
    df = c_df.copy()

    df["Margin_Percentage"] = compute_margin_percentage(df)
    df["Victory_Category"] = categorize_victory_margin(df["Margin_Percentage"])
    df["Coalition_Block"] = assign_coalition_block(df["Winner_Party"])
    df["Runner_Up_Ratio"] = compute_runner_up_ratio(df)

    prev_party, flip_status, hold_count = compute_seat_flip_status(df)
    df["Prev_Winner_Party"] = prev_party
    df["Seat_Flip_Status"] = flip_status
    df["Incumbent_Hold_Count"] = hold_count

    logger.info(f"Constituency feature engineering complete. Enriched shape: {df.shape}")
    return df


def engineer_party_summary_features(p_df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer national party summary features.

    Features:
    - Seat_Conversion_Efficiency: Seats / Percentage (Vote share to seat conversion ratio).
    - Coalition_Block: National alliance categorization.

    Args:
        p_df (pd.DataFrame): Cleaned party summary dataset.

    Returns:
        pd.DataFrame: Feature-enriched party summary dataset.
    """
    logger.info("Engineering party-level features...")
    df = p_df.copy()

    df["Coalition_Block"] = assign_coalition_block(df["Party"])

    valid_pct_mask = df["Percentage"] > 0
    df["Seat_Conversion_Efficiency"] = 0.0
    df.loc[valid_pct_mask, "Seat_Conversion_Efficiency"] = np.round(
        df.loc[valid_pct_mask, "Seats"] / df.loc[valid_pct_mask, "Percentage"], 2
    )

    logger.info(f"Party summary feature engineering complete. Enriched shape: {df.shape}")
    return df


def engineer_state_summary_features(s_df: pd.DataFrame, c_eng: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer state summary features including state volatility metrics.

    Features:
    - State_Total_Seats: Total Lok Sabha seats in the state for that year.
    - State_Seat_Share: Seats won as a percentage of total state seats.
    - State_Volatility_Rate: Average seat flip rate in the state across elections.

    Args:
        s_df (pd.DataFrame): Cleaned state summary dataset.
        c_eng (pd.DataFrame): Feature-enriched constituency dataset.

    Returns:
        pd.DataFrame: Feature-enriched state summary dataset.
    """
    logger.info("Engineering state-level features...")
    df = s_df.copy()

    df["Coalition_Block"] = assign_coalition_block(df["Party_Alliance"])

    # Compute total seats per state per year
    state_totals = df.groupby(["Year", "State_UT"])["Seats_Won"].transform("sum")
    valid_totals = state_totals > 0

    df["State_Total_Seats"] = state_totals
    df["State_Seat_Share"] = 0.0
    df.loc[valid_totals, "State_Seat_Share"] = np.round(
        (df.loc[valid_totals, "Seats_Won"] / state_totals[valid_totals]) * 100, 2
    )

    # Compute state-level seat flip volatility rate from constituency data
    state_volatility = (
        c_eng.groupby("State")["Seat_Flip_Status"]
        .mean()
        .reset_index()
        .rename(columns={"Seat_Flip_Status": "State_Volatility_Rate"})
    )
    state_volatility["State_Volatility_Rate"] = np.round(state_volatility["State_Volatility_Rate"] * 100, 2)

    df = pd.merge(df, state_volatility, left_on="State_UT", right_on="State", how="left")
    df = df.drop(columns=["State"], errors="ignore")
    df["State_Volatility_Rate"] = df["State_Volatility_Rate"].fillna(0.0)

    logger.info(f"State summary feature engineering complete. Enriched shape: {df.shape}")
    return df


def generate_feature_engineering_report(
    report_path: Path,
    c_df: pd.DataFrame,
    p_df: pd.DataFrame,
    s_df: pd.DataFrame
) -> None:
    """
    Generate markdown report documenting all engineered features and their utility.

    Args:
        report_path (Path): Target markdown file path.
        c_df (pd.DataFrame): Feature-engineered constituency dataset.
        p_df (pd.DataFrame): Feature-engineered party summary dataset.
        s_df (pd.DataFrame): Feature-engineered state summary dataset.
    """
    report_content = f"""# Feature Engineering Report: Module 2 Pipeline

> [!NOTE]
> This report documents the engineered features created during **Module 2 (Feature Engineering Pipeline)** for the Election Campaign Analysis (2004–2024) project.

---

## 1. Summary of Engineered Features

### A. Constituency-Level Features (`constituency_engineered.csv`)
- **`Margin_Percentage`** (`float64`): Normalized victory margin relative to top-2 total polled valid votes.
  - *Utility*: Eliminates turnout magnitude bias; supports EDA margin analysis, dashboard filtering, and ML inputs.
- **`Victory_Category`** (`object`): Categorical tier (`Landslide` >15%, `Comfortable` 5-15%, `Tight / Close Contest` <5%).
  - *Utility*: Enables rapid competitive intensity filtering in Streamlit dashboard views.
- **`Seat_Flip_Status`** (`float64`): Binary flag (`1.0` if winning party changed from election $T-1$, `0.0` if retained, `NaN` for base 2004).
  - *Utility*: Key target variable for Machine Learning classification model and seat volatility tracking.
- **`Coalition_Block`** (`object`): Categorical alliance tag (`NDA`, `UPA / I.N.D.I.A.`, `Left Front`, `Others / Regional`).
  - *Utility*: Tracks macro-alliance consolidation and power shifts across two decades.
- **`Runner_Up_Ratio`** (`float64`): Ratio of runner-up votes to winner votes (`Runner_up_Votes / Winner_Votes`).
  - *Utility*: Quantifies challenge intensity (closer to 1.0 indicates fierce contest).
- **`Incumbent_Hold_Count`** (`int64`): Count of consecutive elections the incumbent party has retained the seat.
  - *Utility*: Identifies party strongholds versus vulnerable seats.

### B. Party-Level Features (`party_summary_engineered.csv`)
- **`Seat_Conversion_Efficiency`** (`float64`): Ratio of national seats won to national vote percentage share (`Seats / Percentage`).
  - *Utility*: Quantifies First-Past-The-Post vote conversion efficiency for national vs regional parties.
- **`Coalition_Block`** (`object`): National alliance mapping per political party.

### C. State-Level Features (`state_summary_engineered.csv`)
- **`State_Total_Seats`** (`int64`): Total Lok Sabha seats in the state.
- **`State_Seat_Share`** (`float64`): Percentage share of state seats won by a party/alliance (`Seats_Won / State_Total_Seats * 100`).
- **`State_Volatility_Rate`** (`float64`): Historical percentage of seat flips in the state.
  - *Utility*: Ranks battleground swing states for campaign strategy.

---

## 2. Feature Distribution Highlights

- **Total Constituency Records**: {len(c_df)}
- **Victory Category Breakdown**:
  - Landslide (>15% margin): {(c_df['Victory_Category'] == 'Landslide').sum()} seats
  - Comfortable (5-15% margin): {(c_df['Victory_Category'] == 'Comfortable').sum()} seats
  - Tight / Close Contest (<5% margin): {(c_df['Victory_Category'] == 'Tight / Close Contest').sum()} seats
- **Coalition Block Distribution**:
  - NDA Seats: {(c_df['Coalition_Block'] == 'NDA').sum()}
  - UPA / I.N.D.I.A. Seats: {(c_df['Coalition_Block'] == 'UPA / I.N.D.I.A.').sum()}
  - Left Front Seats: {(c_df['Coalition_Block'] == 'Left Front').sum()}
  - Regional / Others Seats: {(c_df['Coalition_Block'] == 'Others / Regional').sum()}
- **Seat Flip Totals (2009–2024 Transitions)**:
  - Total Seat Flips Recorded: {(c_df['Seat_Flip_Status'] == 1.0).sum()} seats
  - Total Incumbent Retentions: {(c_df['Seat_Flip_Status'] == 0.0).sum()} seats
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_content, encoding="utf-8")
    logger.info(f"Feature Engineering Report saved to {report_path}")


def run_feature_engineering_pipeline(processed_dir: Path) -> Dict[str, pd.DataFrame]:
    """
    Orchestrate the feature engineering pipeline.

    Args:
        processed_dir (Path): Directory containing cleaned datasets.

    Returns:
        Dict[str, pd.DataFrame]: Feature-enriched DataFrames.
    """
    logger.info("Starting Module 2 Feature Engineering Pipeline...")

    c_master = pd.read_csv(processed_dir / "constituency_master.csv")
    p_master = pd.read_csv(processed_dir / "party_summary_master.csv")
    s_master = pd.read_csv(processed_dir / "state_summary_master.csv")

    c_eng = engineer_constituency_features(c_master)
    p_eng = engineer_party_summary_features(p_master)
    s_eng = engineer_state_summary_features(s_master, c_eng)

    # Save engineered datasets
    c_eng.to_csv(processed_dir / "constituency_engineered.csv", index=False)
    p_eng.to_csv(processed_dir / "party_summary_engineered.csv", index=False)
    s_eng.to_csv(processed_dir / "state_summary_engineered.csv", index=False)

    logger.info(f"Saved feature-engineered datasets to: {processed_dir}")

    # Generate Feature Engineering Report
    generate_feature_engineering_report(
        report_path=processed_dir / "feature_engineering_report.md",
        c_df=c_eng,
        p_df=p_eng,
        s_df=s_eng
    )

    logger.info("Module 2 Feature Engineering Pipeline Completed Successfully.")
    return {
        "constituency_engineered": c_eng,
        "party_summary_engineered": p_eng,
        "state_summary_engineered": s_eng,
    }


if __name__ == "__main__":
    import sys
    base_dir = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(base_dir))
    run_feature_engineering_pipeline(processed_dir=base_dir / "data" / "processed")
