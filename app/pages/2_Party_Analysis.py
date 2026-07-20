"""
Page 2: Party Performance Analytics.
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt
import streamlit as st

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir))

from app.utils import load_processed_data, render_sidebar_filters, compute_dynamic_insights
from src.visualizations.party import (
    plot_seats_by_party,
    plot_votes_by_party,
    plot_postal_vote_share,
    plot_party_retention_loss,
    plot_vote_seat_conversion,
)

st.title("🚩 Party Performance Analytics")
st.markdown("Evaluating political party seat growth, retention rates, postal vote dependence (%), and vote conversion efficiency.")

c_df, p_df, s_df = load_processed_data()
c_filt, p_filt, s_filt = render_sidebar_filters(c_df, p_df, s_df)
insights = compute_dynamic_insights(c_filt, p_filt, s_filt)

# Dynamic Automated Party Insights Callout
st.info(
    f"💡 **Party Intelligence Summary**:\n"
    f"- **Dominant Party**: **{insights['top_party']}** leading with **{insights['top_party_seats']} seats**.\n"
    f"- **Alliance Multiplier**: **{insights['top_alliance']}** holds **{insights['alliance_pct']:.1f}%** of seats in this selection."
)

col1, col2, col3 = st.columns(3)

top_party = p_filt.sort_values("Seats", ascending=False)["Party"].iloc[0] if not p_filt.empty else "BJP"
top_seats = p_filt.sort_values("Seats", ascending=False)["Seats"].iloc[0] if not p_filt.empty else 0
top_eff = p_filt.sort_values("Seat_Conversion_Efficiency", ascending=False)["Party"].iloc[0] if not p_filt.empty else "BJP"

with col1:
    st.metric("Top Seat Party", f"{top_party} ({top_seats} Seats)")
with col2:
    st.metric("Highest Conversion Efficiency", f"{top_eff}")
with col3:
    st.metric("Total Parties Analyzed", f"{p_filt['Party'].nunique()}")

st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Seats Won by Party",
    "Total Votes Received",
    "Postal Vote Share (%)",
    "Incumbent Seat Retention vs Loss",
    "Vote Conversion Efficiency"
])

with tab1:
    st.subheader("Top Parties by Seats Won")
    fig1 = plot_seats_by_party(p_filt if not p_filt.empty else p_df)
    try:
        st.pyplot(fig1, use_container_width=True)
    finally:
        plt.close(fig1)

with tab2:
    st.subheader("Top Parties by Total Votes Received")
    fig2 = plot_votes_by_party(p_filt if not p_filt.empty else p_df)
    try:
        st.pyplot(fig2, use_container_width=True)
    finally:
        plt.close(fig2)

with tab3:
    st.subheader("Postal Vote Share (%) Analysis per Party")
    st.markdown("*Calculates relative dependence on postal ballots: `postal_votes / (evm_votes + postal_votes) * 100`*")
    fig3 = plot_postal_vote_share(c_filt if not c_filt.empty else c_df)
    try:
        st.pyplot(fig3, use_container_width=True)
    finally:
        plt.close(fig3)

with tab4:
    st.subheader("Incumbent Party Seat Retention vs Loss Breakdown")
    fig4 = plot_party_retention_loss(c_filt if not c_filt.empty else c_df)
    try:
        st.pyplot(fig4, use_container_width=True)
    finally:
        plt.close(fig4)

with tab5:
    st.subheader("Vote Share % vs Parliamentary Seats Won")
    fig5 = plot_vote_seat_conversion(p_filt if not p_filt.empty else p_df)
    try:
        st.pyplot(fig5, use_container_width=True)
    finally:
        plt.close(fig5)

st.markdown("---")
st.subheader("Detailed Party Performance Table")
st.dataframe(p_filt, use_container_width=True)
