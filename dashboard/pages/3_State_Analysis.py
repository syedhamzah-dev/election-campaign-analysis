"""
Page 3: State & Regional Intelligence Dashboard.
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt
import streamlit as st

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir))

from dashboard.utils.utils import load_processed_data, render_sidebar_filters, compute_dynamic_insights
from src.visualization.state import plot_state_volatility_ranking, plot_state_margin_distribution
from src.analysis.state.state import state_summary

st.title("🗺️ State & Regional Intelligence")
st.markdown("Analyzing battleground state volatility, seat distributions, and victory margin spreads across Indian States and UTs.")

c_df, p_df, s_df = load_processed_data()
c_filt, p_filt, s_filt = render_sidebar_filters(c_df, p_df, s_df)
insights = compute_dynamic_insights(c_filt, p_filt, s_filt)

# Dynamic Automated State Insights Callout
st.info(
    f"💡 **State Battleground Intelligence**:\n"
    f"- **Most Volatile State**: **{insights['volatile_state']}** with **{insights['volatile_rate']:.1f}% seat flip rate**.\n"
    f"- **Most Competitive State**: **{insights['competitive_state']}** (Median victory margin: **{insights['competitive_median_margin']:.1f}%**)."
)

col1, col2, col3 = st.columns(3)

summary_stats = state_summary(s_filt, c_filt)
most_volatile = summary_stats["most_volatile"]
highest_rate = summary_stats["highest_rate"]
state_count = summary_stats["state_count"]

with col1:
    st.metric("Top Battleground State", f"{most_volatile}")
with col2:
    st.metric("Peak State Volatility Rate", f"{highest_rate:.1f}%")
with col3:
    st.metric("States & UTs Analyzed", f"{state_count}")

st.markdown("---")

tab1, tab2 = st.tabs(["Battleground State Volatility", "Victory Margin Distribution"])

with tab1:
    st.subheader("Historical Seat Volatility Ranking by State")
    # For state comparative rankings, fallback to s_df if filter narrows to a single state
    df_vol = s_filt if len(s_filt) > 1 else s_df
    fig1 = plot_state_volatility_ranking(df_vol)
    try:
        st.pyplot(fig1, use_container_width=True)
    finally:
        plt.close(fig1)

with tab2:
    st.subheader("Victory Margin % Spread Across Major States")
    # For multi-state boxplots, fallback to c_df if filter narrows to a single state
    df_margin = c_filt if c_filt["State"].nunique() > 1 else c_df
    fig2 = plot_state_margin_distribution(df_margin)
    try:
        st.pyplot(fig2, use_container_width=True)
    finally:
        plt.close(fig2)

st.markdown("---")
st.subheader("State-Level Aggregated Summary Table")
st.dataframe(s_filt, use_container_width=True)
