"""
Main Streamlit Application Entrypoint for Election Campaign Analysis (2004-2024).

Implements multi-page navigation, page configuration, custom CSS styling, and dashboard landing.
"""

from pathlib import Path
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Election Campaign Analysis (2004–2024)",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Custom CSS Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #64748B;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. Main Landing Header
st.markdown('<div class="main-header">🗳️ Election Campaign Analysis (Lok Sabha 2004–2024)</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Data-Driven Intelligence Dashboard Covering 20 Years of Indian General Elections</div>',
    unsafe_allow_html=True,
)

st.info(
    "👈 **Use the Sidebar Navigation** to explore **Overview**, **Party Analysis**, **State Analysis**, "
    "**Constituency Analysis**, and **Executive Insights** pages. All visualizations reuse modular, 300 DPI matplotlib/seaborn plot engines."
)

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Elections Analyzed</div>
            <div class="metric-value">5 Cycles</div>
            <div style="font-size:0.8rem; color:#059669;">2004 – 2024</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Total Seats Recorded</div>
            <div class="metric-value">2,715 Seats</div>
            <div style="font-size:0.8rem; color:#059669;">543 per cycle</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Major Coalitions</div>
            <div class="metric-value">NDA & UPA</div>
            <div style="font-size:0.8rem; color:#059669;">97.1% seats in 2024</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Historical Seat Flips</div>
            <div class="metric-value">1,060 Flips</div>
            <div style="font-size:0.8rem; color:#DC2626;">49.2% Volatility</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Dashboard Features & Module Overview")
st.markdown(
    """
    - **Page 1: Overview** — National coalition seat share trajectories, FPTP vote conversion efficiency, macro KPIs.
    - **Page 2: Party Analysis** — Party performance comparisons, seat retention vs loss trajectory, party conversion metrics.
    - **Page 3: State Analysis** — Battleground state volatility rankings, victory margin boxplots per state, state dominance index.
    - **Page 4: Constituency Analysis** — Reserved vs General seat breakdown, top 10 razor-thin wins vs landslide sweeps, searchable fact finder.
    - **Page 5: Executive Insights** — Strategic campaign recommendations, data-backed findings, limitations, and future ML roadmap.
    """
)
