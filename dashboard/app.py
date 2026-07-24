"""
Main Streamlit Application Entrypoint for Election Campaign Analysis (2004-2024).

Executive Landing Page & Analytics Dashboard Homepage.
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt
import streamlit as st

# Ensure root workspace path is in Python path for clean module imports
base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from dashboard.utils.utils import load_processed_data
from src.visualization.national import plot_coalition_trajectory
from src.visualization.statistical import plot_margins_hist
from src.visualization.party import (
    plot_vote_seat_conversion,
    plot_seats_by_party,
)
from src.visualization.state import plot_state_volatility_ranking
from src.visualization.constituency import plot_turnout_top20


# 1. Streamlit Page Configuration
st.set_page_config(
    page_title="Election Campaign Analysis (2004–2024)",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 2. Executive Custom CSS Styling
st.markdown(
    """
    <style>
    /* Main Layout & Typography */
    .main-header {
        font-size: 2.4rem;
        font-weight: 800;
        color: var(--text-color, #0F172A);
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: var(--text-color, #475569);
        opacity: 0.85;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    
    /* Section Headers */
    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-color, #1E3A8A);
        margin-top: 1.5rem;
        margin-bottom: 0.3rem;
    }
    .section-subtitle {
        font-size: 0.9rem;
        color: var(--text-color, #64748B);
        opacity: 0.8;
        margin-bottom: 1.2rem;
    }

    /* Executive KPI Cards */
    .kpi-card {
        background-color: var(--secondary-background-color, #f8fafc);
        border: 1px solid rgba(148, 163, 184, 0.3);
        border-radius: 10px;
        padding: 16px 12px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        border-color: rgba(148, 163, 184, 0.6);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
    }
    .kpi-icon {
        font-size: 1.4rem;
        margin-bottom: 4px;
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--text-color, #64748B);
        opacity: 0.75;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: #2563EB;
        line-height: 1.2;
    }
    .kpi-subtext {
        font-size: 0.75rem;
        font-weight: 600;
        color: #10B981;
        margin-top: 4px;
    }

    /* Dashboard Highlights Cards */
    .highlight-card {
        background-color: var(--secondary-background-color, #ffffff);
        border: 1px solid rgba(148, 163, 184, 0.3);
        border-radius: 10px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
        border-top: 4px solid #2563EB;
    }
    .highlight-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--text-color, #1E3A8A);
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .highlight-desc {
        font-size: 0.88rem;
        color: var(--text-color, #475569);
        opacity: 0.85;
        line-height: 1.5;
    }

    /* Dashboard Workflow Sequence */
    .workflow-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: var(--secondary-background-color, #f8fafc);
        border: 1px solid rgba(148, 163, 184, 0.3);
        border-radius: 12px;
        padding: 20px 24px;
        margin-top: 10px;
        margin-bottom: 25px;
        flex-wrap: wrap;
        gap: 8px;
    }
    .workflow-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        flex: 1;
        min-width: 110px;
    }
    .workflow-icon {
        font-size: 1.5rem;
        margin-bottom: 6px;
        background-color: var(--background-color, #ffffff);
        width: 46px;
        height: 46px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(148, 163, 184, 0.4);
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .workflow-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--text-color, #1E3A8A);
    }
    .workflow-desc {
        font-size: 0.72rem;
        color: var(--text-color, #64748B);
        opacity: 0.8;
    }
    .workflow-arrow {
        font-size: 1.2rem;
        color: var(--text-color, #94A3B8);
        opacity: 0.6;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# 3. Load Processed Data (Cached)
c_df, p_df, s_df = load_processed_data()


# 4. Header & Project Information
st.markdown('<div class="main-header">🗳️ Election Campaign Analysis (Lok Sabha 2004–2024)</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Data-Driven Intelligence Dashboard Covering 20 Years of Indian General Elections</div>',
    unsafe_allow_html=True,
)


# 5. Section 1 — Executive KPIs
st.markdown('<div class="section-title">📊 Executive Key Performance Indicators</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Macro-level summary statistics across 20 years of general election cycles</div>', unsafe_allow_html=True)

# Dynamic KPI Metric Calculations
elections_count = c_df["Year"].nunique() if "Year" in c_df.columns else 5
years_min = int(c_df["Year"].min()) if "Year" in c_df.columns else 2004
years_max = int(c_df["Year"].max()) if "Year" in c_df.columns else 2024
total_seats_per_cycle = int(c_df.groupby("Year").size().max()) if "Year" in c_df.columns else 543
total_records = len(c_df)
total_parties = p_df["Party"].nunique() if "Party" in p_df.columns else 1500
if "State" in c_df.columns:
    total_states = c_df["State"].replace({
        "Dadra and Nagar Haveli": "Dadra and Nagar Haveli and Daman and Diu",
        "Daman and Diu": "Dadra and Nagar Haveli and Daman and Diu"
    }).nunique()
else:
    total_states = 36
avg_winning_margin = c_df["Margin_Percentage"].mean() if "Margin_Percentage" in c_df.columns else 12.84

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

with kpi1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🗳️</div>
            <div class="kpi-label">Elections Analyzed</div>
            <div class="kpi-value">{elections_count} Cycles</div>
            <div class="kpi-subtext">{years_min} – {years_max}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🏛️</div>
            <div class="kpi-label">Total Constituencies</div>
            <div class="kpi-value">{total_seats_per_cycle} Seats</div>
            <div class="kpi-subtext">{total_records:,} Total Contests</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">📅</div>
            <div class="kpi-label">Years Covered</div>
            <div class="kpi-value">{years_max - years_min} Years</div>
            <div class="kpi-subtext">{years_min} – {years_max}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🚩</div>
            <div class="kpi-label">Political Parties</div>
            <div class="kpi-value">{total_parties:,}+</div>
            <div class="kpi-subtext">Tracked Nationally</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi5:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🗺️</div>
            <div class="kpi-label">States & UTs Covered</div>
            <div class="kpi-value" style="font-size: 1.45rem;">{total_states} States & UTs</div>
            <div class="kpi-subtext">100% Pan-India</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi6:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">📈</div>
            <div class="kpi-label">Avg Winning Margin</div>
            <div class="kpi-value">{avg_winning_margin:.2f}%</div>
            <div class="kpi-subtext">Constituency Mean</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")


# 6. Section 2 — Key Visualizations
st.markdown('<div class="section-title">📈 Key Executive Visualizations</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Core analytical overview across coalition seat share, vote conversion, party tallies, margins, state volatility, and voter turnout</div>', unsafe_allow_html=True)

# Row 1
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Coalition Seat Share Trajectory")
    fig1 = plot_coalition_trajectory(c_df)
    try:
        st.pyplot(fig1, use_container_width=True)
    finally:
        plt.close(fig1)

with row1_col2:
    st.subheader("Vote Share vs Parliamentary Seats")
    fig2 = plot_vote_seat_conversion(p_df)
    try:
        st.pyplot(fig2, use_container_width=True)
    finally:
        plt.close(fig2)

# Row 2
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Seats Won by Major Parties")
    fig3 = plot_seats_by_party(p_df)
    try:
        st.pyplot(fig3, use_container_width=True)
    finally:
        plt.close(fig3)

with row2_col2:
    st.subheader("Winning Margin Distribution")
    fig4 = plot_margins_hist(c_df)
    try:
        st.pyplot(fig4, use_container_width=True)
    finally:
        plt.close(fig4)

# Row 3
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.subheader("State Volatility Ranking")
    fig5 = plot_state_volatility_ranking(s_df)
    try:
        st.pyplot(fig5, use_container_width=True)
    finally:
        plt.close(fig5)

with row3_col2:
    st.subheader("Top Turnout Constituencies")
    fig6 = plot_turnout_top20(c_df)
    try:
        st.pyplot(fig6, use_container_width=True)
    finally:
        plt.close(fig6)

st.markdown("---")


# 7. Section 3 — Dashboard Highlights
st.markdown('<div class="section-title">💡 Analytical Module Highlights</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Key strategic pillars covered within the dashboard analytical suite</div>', unsafe_allow_html=True)

hl_col1, hl_col2, hl_col3 = st.columns(3)

with hl_col1:
    st.markdown(
        """
        <div class="highlight-card">
            <div class="highlight-title">🏛️ National Analysis</div>
            <div class="highlight-desc">
                Analyze national coalition performance (NDA vs UPA/I.N.D.I.A.), 272 majority threshold trajectories, 
                and macro-level electoral shifts across five Lok Sabha election cycles (2004–2024).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hl_col2:
    st.markdown(
        """
        <div class="highlight-card">
            <div class="highlight-title">🚩 Party Analysis</div>
            <div class="highlight-desc">
                Compare vote share vs seat share, First-Past-The-Post (FPTP) vote conversion efficiency, 
                incumbent seat retention vs loss rates, and postal vote dependence across national & regional parties.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hl_col3:
    st.markdown(
        """
        <div class="highlight-card">
            <div class="highlight-title">🎯 State & Constituency Analysis</div>
            <div class="highlight-desc">
                Identify battleground swing states, seat flip volatility, competitive razor-thin constituencies (<5% margin), 
                turnout patterns, and Reserved (SC/ST) vs General category performance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")


# 8. Section 4 — Dashboard Workflow
st.markdown('<div class="section-title">🔄 End-to-End Analytics Pipeline</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Systematic workflow from raw Election Commission data to strategic insights</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="workflow-container">
        <div class="workflow-step">
            <div class="workflow-icon">📁</div>
            <div class="workflow-title">Raw Data</div>
            <div class="workflow-desc">ECI Results</div>
        </div>
        <div class="workflow-arrow">➔</div>
        <div class="workflow-step">
            <div class="workflow-icon">🧹</div>
            <div class="workflow-title">Data Cleaning</div>
            <div class="workflow-desc">Standardization</div>
        </div>
        <div class="workflow-arrow">➔</div>
        <div class="workflow-step">
            <div class="workflow-icon">⚙️</div>
            <div class="workflow-title">Feature Eng.</div>
            <div class="workflow-desc">Flips & Coalitions</div>
        </div>
        <div class="workflow-arrow">➔</div>
        <div class="workflow-step">
            <div class="workflow-icon">📈</div>
            <div class="workflow-title">EDA</div>
            <div class="workflow-desc">300 DPI Seaborn</div>
        </div>
        <div class="workflow-arrow">➔</div>
        <div class="workflow-step">
            <div class="workflow-icon">💻</div>
            <div class="workflow-title">Interactive App</div>
            <div class="workflow-desc">Streamlit Suite</div>
        </div>
        <div class="workflow-arrow">➔</div>
        <div class="workflow-step">
            <div class="workflow-icon">💡</div>
            <div class="workflow-title">Insights</div>
            <div class="workflow-desc">Campaign Strategy</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")


# 9. Section 5 — Quick Navigation
st.markdown('<div class="section-title">🚀 Quick Dashboard Navigation</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Directly access deep-dive analytical modules and strategic insights</div>', unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)

with nav_col1:
    st.page_link("pages/1_Overview.py", label="Overview", icon="📊", use_container_width=True)

with nav_col2:
    st.page_link("pages/2_Party_Analysis.py", label="Party Analysis", icon="🚩", use_container_width=True)

with nav_col3:
    st.page_link("pages/3_State_Analysis.py", label="State Analysis", icon="🗺️", use_container_width=True)

with nav_col4:
    st.page_link("pages/4_Constituency_Analysis.py", label="Constituency Analysis", icon="🎯", use_container_width=True)

with nav_col5:
    st.page_link("pages/5_Insights.py", label="Executive Insights", icon="💡", use_container_width=True)
