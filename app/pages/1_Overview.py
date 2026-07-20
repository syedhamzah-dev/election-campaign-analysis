"""
Page 1: Executive Overview Dashboard.
"""

from pathlib import Path
import sys
import streamlit as st

# Setup sys.path for importing project modules
base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir))

from app.utils import load_processed_data, render_sidebar_filters
from src.visualization import plot_coalition_trajectory, plot_vote_seat_conversion

st.title("📊 National Executive Overview")
st.markdown("Macro-level electoral trajectory, national coalition dominance, and First-Past-The-Post vote conversion efficiency.")

# 1. Load Data & Render Filters
c_df, p_df, s_df = load_processed_data()
c_filt, p_filt, s_filt = render_sidebar_filters(c_df, p_df, s_df)

# 2. KPI Cards
col1, col2, col3, col4 = st.columns(4)

total_seats = len(c_filt)
nda_seats = (c_filt["Coalition_Block"] == "NDA").sum()
upa_seats = (c_filt["Coalition_Block"] == "UPA / I.N.D.I.A.").sum()
avg_margin = c_filt["Margin_Percentage"].mean() if not c_filt.empty else 0.0
close_contests = (c_filt["Victory_Category"] == "Tight / Close Contest").sum()

with col1:
    st.metric("Total Seats Analyzed", f"{total_seats}")
with col2:
    st.metric("NDA vs UPA/INDIA Seats", f"{nda_seats} vs {upa_seats}")
with col3:
    st.metric("Average Victory Margin", f"{avg_margin:.2f}%")
with col4:
    st.metric("Tight Contests (<5%)", f"{close_contests}")

st.markdown("---")

# 3. Visualizations Reusing src/visualization.py Engine
output_fig_dir = base_dir / "outputs" / "figures"

tab1, tab2 = st.tabs(["Coalition Trajectory", "Vote vs Seat Conversion"])

with tab1:
    st.subheader("National Coalition Seat Share Trajectory (2004–2024)")
    fig_path = plot_coalition_trajectory(c_filt if not c_filt.empty else c_df, output_fig_dir)
    st.image(str(fig_path), use_container_width=True)

with tab2:
    st.subheader("Vote Share % vs Parliamentary Seats Won")
    fig_path2 = plot_vote_seat_conversion(p_filt if not p_filt.empty else p_df, output_fig_dir)
    st.image(str(fig_path2), use_container_width=True)

# 4. Filtered Summary Data Table
st.markdown("---")
st.subheader("National Party Summary Data Table")
st.dataframe(p_filt, use_container_width=True)
