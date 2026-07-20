"""
Page 4: Constituency & Candidate Deep-Dive Dashboard.
"""

from pathlib import Path
import sys
import streamlit as st

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir))

from app.utils import load_processed_data, render_sidebar_filters
from src.visualization import plot_reserved_category_wins, plot_extreme_margins

st.title("🎯 Constituency & Candidate Deep-Dive")
st.markdown("Investigating election outcomes across Reserved (`SC`, `ST`) vs General (`GEN`) seats and extreme victory margins.")

c_df, p_df, s_df = load_processed_data()
c_filt, p_filt, s_filt = render_sidebar_filters(c_df, p_df, s_df)

col1, col2, col3, col4 = st.columns(4)

tightest_win = c_filt[c_filt["Margin_Votes"] > 0]["Margin_Votes"].min() if not c_filt.empty else 25
largest_win = c_filt["Margin_Votes"].max() if not c_filt.empty else 690000
swing_seats = (c_filt["Seat_Flip_Status"] == 1.0).sum()
gen_seats = (c_filt["Constituency_Type"] == "GEN").sum()

with col1:
    st.metric("Tightest Victory Margin", f"{int(tightest_win):,} Votes")
with col2:
    st.metric("Largest Landslide Margin", f"{int(largest_win):,} Votes")
with col3:
    st.metric("Seat Flips Recorded", f"{swing_seats}")
with col4:
    st.metric("General Seats Count", f"{gen_seats}")

st.markdown("---")

output_fig_dir = base_dir / "outputs" / "figures"

tab1, tab2 = st.tabs(["Reserved vs General Category Wins", "Extreme Victory Margins"])

with tab1:
    st.subheader("Party Win Distribution Across Reserved & General Seats")
    fig_path = plot_reserved_category_wins(c_filt if not c_filt.empty else c_df, output_fig_dir)
    st.image(str(fig_path), use_container_width=True)

with tab2:
    st.subheader("Top 10 Tightest Victories vs Landslide Sweeps")
    fig_path2 = plot_extreme_margins(c_filt if not c_filt.empty else c_df, output_fig_dir)
    st.image(str(fig_path2), use_container_width=True)

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
