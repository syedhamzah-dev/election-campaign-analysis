"""
Page 5: Executive Insights & Strategic Campaign Recommendations.
"""

from pathlib import Path
import sys
import streamlit as st

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir))

from app.utils import load_processed_data, render_sidebar_filters, compute_dynamic_insights

st.title("💡 Executive Insights & Strategic Campaign Recommendations")
st.markdown("High-level data-backed findings, strategic campaign implications, limitations, and future machine learning roadmap.")

c_df, p_df, s_df = load_processed_data()
c_filt, p_filt, s_filt = render_sidebar_filters(c_df, p_df, s_df)
insights = compute_dynamic_insights(c_filt, p_filt, s_filt)

st.markdown("### Active Filter Analytics Summary")
st.info(
    f"📊 **Selected Filter Highlights**:\n"
    f"- **Coalition Control**: **{insights['top_alliance']}** holds **{insights['top_alliance_seats']} seats** ({insights['alliance_pct']:.1f}%).\n"
    f"- **Top Battleground State**: **{insights['volatile_state']}** ({insights['volatile_rate']:.1f}% seat flip rate).\n"
    f"- **Competitive Intensity**: **{insights['competitive_state']}** records median victory margin of **{insights['competitive_median_margin']:.1f}%**.\n"
    f"- **Electoral Extremes**: Closest win in **{insights['closest_constituency']}** ({insights['closest_margin']:,} votes); Landslide in **{insights['largest_constituency']}** ({insights['largest_margin']:,} votes)."
)

st.markdown("---")
st.markdown("### Key Strategic Campaign Takeaways")

st.markdown(
    """
    #### 1. Consolidation of a National Bipolar System
    - **Data Finding**: In general election cycles (2004–2024), **NDA** and **UPA / I.N.D.I.A.** coalitions together control over **97% of parliamentary seats**.
    - **Campaign Action**: Unaligned regional parties (`Others`) face severe electoral compression. Strategic pre-poll coalition formation is mandatory for campaign viability.

    #### 2. Identification of Core Battleground States
    - **Data Finding**: States like **Tamil Nadu**, **Uttar Pradesh**, **Karnataka**, and **Maharashtra** display historical seat volatility rates exceeding **55%**.
    - **Campaign Action**: Campaign resources (ground rallies, digital ad spend, leader appearances) should prioritize high-volatility battleground states where seat flip probabilities are highest.

    #### 3. First-Past-The-Post Vote Conversion Efficiency
    - **Data Finding**: Under FPTP rules, parties with concentrated regional support convert vote share into seats far more efficiently than parties with widely dispersed, diluted national vote shares.
    - **Campaign Action**: Parties must focus on constituency-level micro-targeting rather than spending resources chasing low-density national vote share increases.

    #### 4. Dominance in Reserved Constituencies (`SC` / `ST`)
    - **Data Finding**: Scheduled Tribes (`ST`) and Scheduled Castes (`SC`) reserved seats demonstrate strong alignment with national coalition waves, with BJP capturing >50% of ST seats in 2014–2019 and UPA/I.N.D.I.A. recovering reserved seats in 2024.
    - **Campaign Action**: Specialized outreach programs tailored to tribal and welfare-focused demographic issues in reserved constituencies yield high seat multipliers.
    """
)

st.markdown("---")
st.markdown("### Data Limitations & Boundary Constraints")

st.warning(
    "1. **Unrecorded Turnout Data**: Raw datasets record winning and runner-up candidate votes but omit total registered voters and total turnout percentages per constituency.\n"
    "2. **Candidate Demographics**: Datasets do not include candidate age, gender, education, financial net worth, or criminal record metrics.\n"
    "3. **Campaign Financials**: Campaign spending and advertising expenditure data are not present in the election commission raw files."
)

st.markdown("---")
st.markdown("### Future Work & Machine Learning Roadmap")

st.markdown(
    """
    - **Seat Flip Binary Classification Model** — Training Decision Tree & Logistic Regression models to predict constituency seat flip probabilities for upcoming elections using historical margins, runner-up ratios, and incumbent hold counts.
    - **Spatial Mapping** — Interactive GIS choropleth maps for state and constituency boundaries.
    """
)
