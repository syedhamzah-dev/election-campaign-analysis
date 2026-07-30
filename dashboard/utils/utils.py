"""
Streamlit App Utilities for Election Campaign Analysis (2004-2024).

Provides cached data loading, single centralized sidebar filtering pipeline,
and an automated dynamic election insights calculation engine.
"""

from pathlib import Path
from typing import Dict, Tuple, Any

import pandas as pd
import streamlit as st

from src.analysis.national.national import compute_dynamic_insights


@st.cache_data(show_spinner=False)
def load_processed_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load feature-engineered processed datasets with Streamlit caching.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
            - constituency_engineered
            - party_summary_engineered
            - state_summary_engineered
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    proc_dir = base_dir / "data" / "processed"

    c_df = pd.read_csv(proc_dir / "constituency_engineered.csv")
    p_df = pd.read_csv(proc_dir / "party_summary_engineered.csv")
    s_df = pd.read_csv(proc_dir / "state_summary_engineered.csv")

    return c_df, p_df, s_df


def render_sidebar_filters(
    c_df: pd.DataFrame, p_df: pd.DataFrame, s_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Render standardized sidebar filters and return synchronized filtered DataFrames.
    Single centralized filtering pipeline covering Year, State, Alliance, Party, and Seat Type.

    Args:
        c_df (pd.DataFrame): Constituency dataset.
        p_df (pd.DataFrame): Party summary dataset.
        s_df (pd.DataFrame): State summary dataset.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Filtered DataFrames (c_filt, p_filt, s_filt).
    """
    st.sidebar.image(
        "https://raw.githubusercontent.com/feathericons/feather/master/icons/bar-chart-2.svg",
        width=40
    )
    st.sidebar.title("Dashboard Controls")
    st.sidebar.markdown("Centralized filters for Year, State, Alliance, Party, and Seat Type.")

    # 1. Year Filter
    years = sorted(c_df["Year"].unique().tolist())
    selected_years = st.sidebar.multiselect(
        "Select Election Year(s)",
        options=years,
        default=years,
        help="Filter data by general election cycles."
    )
    if not selected_years:
        selected_years = years

    # 2. State Filter
    states = ["All States"] + sorted(c_df["State"].unique().tolist())
    selected_state = st.sidebar.selectbox(
        "Select State / UT",
        options=states,
        index=0,
        help="Filter metrics by specific State or Union Territory."
    )

    # 3. Alliance Filter
    alliances = ["All Alliances", "NDA", "UPA / I.N.D.I.A.", "Left Front", "Others / Regional"]
    selected_alliance = st.sidebar.selectbox(
        "Select Alliance / Block",
        options=alliances,
        index=0,
        help="Filter by national electoral alliance."
    )

    # 4. Party Filter
    all_parties = sorted(c_df["Winner_Party"].unique().tolist())
    selected_parties = st.sidebar.multiselect(
        "Select Party",
        options=all_parties,
        default=[],
        help="Leave empty to include all parties."
    )

    # 5. Seat Type Filter
    seat_types = ["All", "General (GEN)", "Scheduled Castes (SC)", "Scheduled Tribes (ST)"]
    selected_type = st.sidebar.radio(
        "Constituency Type",
        options=seat_types,
        index=0,
    )

    # Centralized Filtering Logic
    c_filtered = c_df[c_df["Year"].isin(selected_years)].copy()
    p_filtered = p_df[p_df["Year"].isin(selected_years)].copy()
    s_filtered = s_df[s_df["Year"].isin(selected_years)].copy()

    if selected_state != "All States":
        c_filtered = c_filtered[c_filtered["State"] == selected_state]
        s_filtered = s_filtered[s_filtered["State_UT"] == selected_state]
        valid_parties = c_filtered["Winner_Party"].unique()
        p_filtered = p_filtered[p_filtered["Party"].isin(valid_parties)]

    if selected_alliance != "All Alliances":
        if "Coalition_Block" in c_filtered.columns:
            c_filtered = c_filtered[c_filtered["Coalition_Block"] == selected_alliance]
        if "Coalition_Block" in p_filtered.columns:
            p_filtered = p_filtered[p_filtered["Coalition_Block"] == selected_alliance]
        if "Coalition_Block" in s_filtered.columns:
            s_filtered = s_filtered[s_filtered["Coalition_Block"] == selected_alliance]

    if selected_parties:
        c_filtered = c_filtered[c_filtered["Winner_Party"].isin(selected_parties)]
        p_filtered = p_filtered[p_filtered["Party"].isin(selected_parties)]
        if "Party_Alliance" in s_filtered.columns:
            s_filtered = s_filtered[s_filtered["Party_Alliance"].isin(selected_parties)]

    if selected_type != "All":
        code_map = {
            "General (GEN)": "GEN",
            "Scheduled Castes (SC)": "SC",
            "Scheduled Tribes (ST)": "ST",
        }
        target_code = code_map.get(selected_type)
        if target_code and "Constituency_Type" in c_filtered.columns:
            c_filtered = c_filtered[c_filtered["Constituency_Type"] == target_code]

    st.sidebar.markdown("---")
    st.sidebar.caption("Lok Sabha Campaign Analytics | 2004–2024")

    return c_filtered, p_filtered, s_filtered


# compute_dynamic_insights is imported from src.analysis.national.national
