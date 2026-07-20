"""
Page 2: Party Performance Analytics.
"""

from pathlib import Path
import sys
import streamlit as st

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir))

from app.utils import load_processed_data, render_sidebar_filters
from src.visualization import plot_vote_seat_conversion, plot_party_retention_loss

st.title("🚩 Party Performance Analytics")
st.markdown("Evaluating political party seat growth, retention rates, and vote conversion efficiency across election cycles.")

c_df, p_df, s_df = load_processed_data()
c_filt, p_filt, s_filt = render_sidebar_filters(c_df, p_df, s_df)

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

output_fig_dir = base_dir / "outputs" / "figures"

tab1, tab2 = st.tabs(["Incumbent Seat Retention vs Loss", "Vote Conversion Comparison"])

with tab1:
    st.subheader("Incumbent Party Seat Retention vs Loss Breakdown")
    fig_path = plot_party_retention_loss(c_filt if not c_filt.empty else c_df, output_fig_dir)
    st.image(str(fig_path), use_container_width=True)

with tab2:
    st.subheader("Vote Share vs Seat Efficiency")
    fig_path2 = plot_vote_seat_conversion(p_filt if not p_filt.empty else p_df, output_fig_dir)
    st.image(str(fig_path2), use_container_width=True)

st.markdown("---")
st.subheader("Detailed Party Performance Table")
st.dataframe(p_filt, use_container_width=True)
