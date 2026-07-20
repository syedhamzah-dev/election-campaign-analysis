"""
Page 1: Executive Overview Dashboard.
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt
import streamlit as st

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir))

from app.utils import load_processed_data, render_sidebar_filters, compute_dynamic_insights
from src.visualizations.statistical import plot_coalition_trajectory
from src.visualizations.party import plot_vote_seat_conversion

st.title("📊 National Executive Overview")
st.markdown("Macro-level electoral trajectory, national coalition dominance, and First-Past-The-Post vote conversion efficiency.")

# 1. Load Data & Render Shared Centralized Filters
c_df, p_df, s_df = load_processed_data()
c_filt, p_filt, s_filt = render_sidebar_filters(c_df, p_df, s_df)
insights = compute_dynamic_insights(c_filt, p_filt, s_filt)

# 2. Dynamic Automated Insights Callout Box
st.info(
    f"💡 **Real-Time Filter Intelligence**:\n"
    f"- **Dominant Alliance**: **{insights['top_alliance']}** with **{insights['top_alliance_seats']} seats** ({insights['alliance_pct']:.1f}% of selected view).\n"
    f"- **Leading Party**: **{insights['top_party']}** with **{insights['top_party_seats']} seats**.\n"
    f"- **Most Competitive State**: **{insights['competitive_state']}** (Median victory margin: **{insights['competitive_median_margin']:.1f}%**)."
)

# 3. KPI Cards
col1, col2, col3, col4 = st.columns(4)

total_seats = len(c_filt)
nda_seats = (c_filt["Coalition_Block"] == "NDA").sum() if "Coalition_Block" in c_filt.columns else 0
upa_seats = (c_filt["Coalition_Block"] == "UPA / I.N.D.I.A.").sum() if "Coalition_Block" in c_filt.columns else 0
avg_margin = c_filt["Margin_Percentage"].mean() if ("Margin_Percentage" in c_filt.columns and not c_filt.empty) else 0.0
close_contests = (c_filt["Victory_Category"] == "Tight / Close Contest").sum() if "Victory_Category" in c_filt.columns else 0

with col1:
    st.metric("Total Seats Analyzed", f"{total_seats}")
with col2:
    st.metric("NDA vs UPA/INDIA Seats", f"{nda_seats} vs {upa_seats}")
with col3:
    st.metric("Average Victory Margin", f"{avg_margin:.2f}%")
with col4:
    st.metric("Tight Contests (<5%)", f"{close_contests}")

st.markdown("---")

tab1, tab2 = st.tabs(["Coalition Trajectory", "Vote vs Seat Conversion"])

with tab1:
    st.subheader("National Coalition Seat Share Trajectory (2004–2024)")
    fig1 = plot_coalition_trajectory(c_filt if not c_filt.empty else c_df)
    try:
        st.pyplot(fig1, use_container_width=True)
    finally:
        plt.close(fig1)

with tab2:
    st.subheader("Vote Share % vs Parliamentary Seats Won")
    fig2 = plot_vote_seat_conversion(p_filt if not p_filt.empty else p_df)
    try:
        st.pyplot(fig2, use_container_width=True)
    finally:
        plt.close(fig2)

st.markdown("---")
st.subheader("National Party Summary Data Table")
st.dataframe(p_filt, use_container_width=True)
