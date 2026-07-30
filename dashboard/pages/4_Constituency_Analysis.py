"""
Page 4: Constituency & Candidate Deep-Dive Dashboard.
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt
import streamlit as st

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir))

from dashboard.utils.utils import load_processed_data, render_sidebar_filters, compute_dynamic_insights
from src.visualization.constituency import (
    plot_turnout_top20,
    plot_reserved_category_wins,
    plot_extreme_margins,
)
from src.visualization.statistical import (
    plot_margins_hist,
    plot_evm_vs_postal_scatter,
)
from src.analysis.constituency.constituency import constituency_summary

st.title("🎯 Constituency & Candidate Deep-Dive")
st.markdown("Investigating turnout, election outcomes across Reserved (`SC`, `ST`) vs General (`GEN`) seats, margin distributions, and EVM/Postal splits.")

c_df, p_df, s_df = load_processed_data()
c_filt, p_filt, s_filt = render_sidebar_filters(c_df, p_df, s_df)
insights = compute_dynamic_insights(c_filt, p_filt, s_filt)

# Dynamic Automated Constituency Insights Callout Box
st.info(
    f"💡 **Constituency Extremes & Turnout Intelligence**:\n"
    f"- **Closest Contest**: **{insights['closest_constituency']}** won by **{insights['closest_winner']}** with a margin of **{insights['closest_margin']:,} votes**.\n"
    f"- **Landslide Victory**: **{insights['largest_constituency']}** won by **{insights['largest_winner']}** with a margin of **{insights['largest_margin']:,} votes**.\n"
    f"- **Highest Turnout**: **{insights['highest_turnout_const']}** recording **{insights['highest_turnout_votes']:,} total votes**."
)

col1, col2, col3, col4 = st.columns(4)

summary_stats = constituency_summary(c_filt)
tightest_win = summary_stats["tightest_win"]
largest_win = summary_stats["largest_win"]
swing_seats = summary_stats["swing_seats"]
gen_seats = summary_stats["gen_seats"]

with col1:
    st.metric("Tightest Victory Margin", f"{int(tightest_win):,} Votes")
with col2:
    st.metric("Largest Landslide Margin", f"{int(largest_win):,} Votes")
with col3:
    st.metric("Seat Flips Recorded", f"{swing_seats}")
with col4:
    st.metric("General Seats Count", f"{gen_seats}")

st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Top 20 Constituencies by Turnout",
    "Distribution of Winning Margins",
    "EVM vs Postal Scatter (Advanced)",
    "Reserved vs General Category Wins",
    "Extreme Victory Margins"
])

with tab1:
    st.subheader("Top 20 Constituencies by Total Votes Cast")
    fig1 = plot_turnout_top20(c_filt if not c_filt.empty else c_df)
    try:
        st.pyplot(fig1, use_container_width=True)
    finally:
        plt.close(fig1)

with tab2:
    st.subheader("Distribution of Winning Margins Across Parliamentary Seats")
    fig2 = plot_margins_hist(c_filt if not c_filt.empty else c_df)
    try:
        st.pyplot(fig2, use_container_width=True)
    finally:
        plt.close(fig2)

with tab3:
    st.subheader("EVM vs Postal Votes Distribution per Constituency (Advanced View)")
    st.markdown("*Scatter plot comparing absolute EVM and Postal vote volumes per constituency.*")
    fig3 = plot_evm_vs_postal_scatter(c_filt if not c_filt.empty else c_df)
    try:
        st.pyplot(fig3, use_container_width=True)
    finally:
        plt.close(fig3)

with tab4:
    st.subheader("Party Win Distribution Across Reserved & General Seats")
    fig4 = plot_reserved_category_wins(c_filt if not c_filt.empty else c_df)
    try:
        st.pyplot(fig4, use_container_width=True)
    finally:
        plt.close(fig4)

with tab5:
    st.subheader("Top 10 Tightest Victories vs Landslide Sweeps")
    fig5 = plot_extreme_margins(c_filt if not c_filt.empty else c_df)
    try:
        st.pyplot(fig5, use_container_width=True)
    finally:
        plt.close(fig5)

st.markdown("---")
st.subheader("Searchable Constituency Fact Finder")
search_term = st.text_input("🔍 Search by Constituency Name, Candidate Name, or Party:", placeholder="e.g. Varanasi, Rahul Gandhi, BJP, Ambala")

if search_term:
    search_filt = c_filt[
        c_filt["Constituency_Name"].str.contains(search_term, case=False, na=False) |
        c_filt["Winner_Candidate"].str.contains(search_term, case=False, na=False) |
        c_filt["Winner_Party"].str.contains(search_term, case=False, na=False)
    ]
    st.dataframe(search_filt, use_container_width=True)
else:
    st.dataframe(c_filt.head(100), use_container_width=True)
