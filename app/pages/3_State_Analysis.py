"""
Page 3: State & Regional Intelligence Dashboard.
"""

from pathlib import Path
import sys
import streamlit as st

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir))

from app.utils import load_processed_data, render_sidebar_filters
from src.visualization import plot_state_volatility_ranking, plot_state_margin_distribution

st.title("🗺️ State & Regional Intelligence")
st.markdown("Analyzing battleground state volatility, seat distributions, and victory margin spreads across Indian States and UTs.")

c_df, p_df, s_df = load_processed_data()
c_filt, p_filt, s_filt = render_sidebar_filters(c_df, p_df, s_df)

col1, col2, col3 = st.columns(3)

most_volatile = s_df.sort_values("State_Volatility_Rate", ascending=False)["State_UT"].iloc[0] if not s_df.empty else "Tamil Nadu"
highest_rate = s_df["State_Volatility_Rate"].max() if not s_df.empty else 0.0

with col1:
    st.metric("Top Battleground State", f"{most_volatile}")
with col2:
    st.metric("Peak State Volatility Rate", f"{highest_rate:.1f}%")
with col3:
    st.metric("States & UTs Analyzed", f"{c_filt['State'].nunique()}")

st.markdown("---")

output_fig_dir = base_dir / "outputs" / "figures"

tab1, tab2 = st.tabs(["Battleground State Volatility", "Victory Margin Distribution"])

with tab1:
    st.subheader("Historical Seat Volatility Ranking by State")
    fig_path = plot_state_volatility_ranking(s_filt if not s_filt.empty else s_df, output_fig_dir)
    st.image(str(fig_path), use_container_width=True)

with tab2:
    st.subheader("Victory Margin % Spread Across Major States")
    fig_path2 = plot_state_margin_distribution(c_filt if not c_filt.empty else c_df, output_fig_dir)
    st.image(str(fig_path2), use_container_width=True)

st.markdown("---")
st.subheader("State-Level Aggregated Summary Table")
st.dataframe(s_filt, use_container_width=True)
