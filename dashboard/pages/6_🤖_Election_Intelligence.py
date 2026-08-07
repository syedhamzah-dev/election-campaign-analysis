"""
Page 6: Election Intelligence Dashboard Page.
Provides constituency-level behavior analysis and safe/swing classification forecasting.
"""

import sys
import json
from pathlib import Path
import pandas as pd
import streamlit as st

# Ensure root workspace path is in Python path for clean module imports
base_dir = Path(__file__).resolve().parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from dashboard.utils.utils import load_processed_data, render_sidebar_filters
from src.ml.predict import SafeSwingPredictor
from src.visualization.base import get_party_color

# Page title
st.title("🤖 Election Intelligence Hub")
st.markdown("Deep constituency-level behavioral analysis, Safe vs Swing classification, Flip Risk indexing, and Similarity Mapping.")

# Standard sidebar filters for visual consistency
c_df, p_df, s_df = load_processed_data()
_, _, _ = render_sidebar_filters(c_df, p_df, s_df)

# Cache data loading
@st.cache_data
def load_intelligence_db():
    intel_file = base_dir / "models" / "election_intelligence.json"
    if not intel_file.exists():
        st.error(f"Intelligence database not found at: {intel_file}. Please run the pipeline first.")
        return {}
    with open(intel_file, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_performance_metrics():
    metrics_file = base_dir / "models" / "evaluation_metrics.json"
    if not metrics_file.exists():
        return {}
    with open(metrics_file, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_resource
def get_predictor():
    return SafeSwingPredictor(base_dir / "models")

# Load data
db = load_intelligence_db()
metrics = load_performance_metrics()
try:
    predictor = get_predictor()
    has_predictor = True
except Exception as e:
    st.error(f"Error loading predictor: {e}")
    has_predictor = False

if db:
    all_consts = sorted(list(db.keys()))
    
    # Initialize session state for selected constituency
    if "selected_const_disp" not in st.session_state or st.session_state.selected_const_disp not in db:
        # Default to a well-known seat if available
        default_seat = "Amethi (Uttar Pradesh)"
        if default_seat in db:
            st.session_state.selected_const_disp = default_seat
        else:
            st.session_state.selected_const_disp = all_consts[0]

    # --- SECTION 1: Constituency Selector ---
    st.markdown("---")
    st.subheader("🎯 Constituency Selector")
    
    # State dropdown first
    all_states = sorted(list(set(c["state"] for c in db.values())))
    current_state = db[st.session_state.selected_const_disp]["state"]
    selected_state = st.selectbox("Filter by State / UT", options=all_states, index=all_states.index(current_state))
    
    # Filter constituencies of selected state
    state_consts = sorted([k for k, v in db.items() if v["state"] == selected_state])
    
    # Selected constituency selectbox linked to session state
    if st.session_state.selected_const_disp not in state_consts:
        # If state filter changed and current selection isn't in it, select the first in new state
        st.session_state.selected_const_disp = state_consts[0]
        
    selected_const = st.selectbox(
        "Select Constituency to Analyze", 
        options=state_consts,
        index=state_consts.index(st.session_state.selected_const_disp)
    )
    
    # Update session state to match selectbox change
    st.session_state.selected_const_disp = selected_const
    c_data = db[selected_const]

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render layout columns
    col_left, col_right = st.columns([3, 2])

    with col_left:
        # --- SECTION 2: Safe vs Swing Forecast ---
        st.markdown("#### 🔮 Safe vs Swing Forecast (Next Election)")
        
        # Load 2024 lag features from cached c_df to run predictions
        try:
            # Query the 2024 row for this constituency
            c_rows = c_df[(c_df["State"] == c_data["state"]) & (c_df["Constituency_No"] == c_data["constituency_no"])]
            row_2024 = c_rows[c_rows["Year"] == 2024]
            
            if not row_2024.empty and has_predictor:
                r_2024 = row_2024.iloc[0]
                prev_winner = str(r_2024["Winner_Party"])
                prev_margin = float(r_2024["Margin_Percentage"])
                prev_runner_up_ratio = float(r_2024["Runner_Up_Ratio"])
                prev_hold_count = int(r_2024["Incumbent_Hold_Count"])
                
                # Predict
                pred_label, confidence = predictor.predict(
                    year=2029,
                    state=c_data["state"],
                    seat_type=c_data["reservation_type"],
                    prev_winner=prev_winner,
                    prev_margin=prev_margin,
                    prev_runner_up_ratio=prev_runner_up_ratio,
                    prev_hold_count=prev_hold_count
                )
                
                # Render predicted card
                card_color = "#EF4444" if pred_label == "Swing Seat" else "#10B981"
                text_color = "#F87171" if pred_label == "Swing Seat" else "#34D399"
                
                st.markdown(
                    f"""
                    <div style="padding: 22px; border-radius: 12px; border-left: 8px solid {card_color}; background-color: var(--secondary-background-color, #1e293b); box-shadow: 0 4px 10px rgba(0,0,0,0.15); margin-bottom: 20px;">
                        <span style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: var(--text-color, #94a3b8); letter-spacing: 0.5px;">Model Classification</span>
                        <h2 style="color: {card_color}; margin-top: 5px; margin-bottom: 5px; font-weight: 800; font-size: 2.0rem;">{pred_label}</h2>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                            <span style="font-weight: 700; color: #3b82f6; font-size: 0.95rem;">Confidence Probability: {confidence:.2%}</span>
                            <span style="font-size: 0.8rem; color: #94a3b8; font-style: italic;">Based on 2024 results</span>
                        </div>
                        <hr style="border: 0; border-top: 1px solid rgba(148,163,184,0.2); margin: 15px 0;">
                        <p style="font-size: 0.9rem; line-height: 1.5; color: var(--text-color, #cbd5e1); margin: 0;">
                            <b>Historical Justification:</b> {c_data['risk_explanation']}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.warning("Insufficient historical data in 2024 to compute classifier inputs for this seat.")
        except Exception as e:
            st.error(f"Inference pipeline error: {e}")

    with col_right:
        # --- SECTIONS 3, 4, 5: Indicators ---
        st.markdown("#### 📊 Key Historical Indicators")
        
        # Grid of columns
        ind_col1, ind_col2 = st.columns(2)
        
        # 3. Flip Risk
        with ind_col1:
            risk = c_data["flip_risk"]
            risk_color = {"Low": "#10B981", "Medium": "#F59E0B", "High": "#EF4444"}.get(risk, "#808080")
            st.markdown(
                f"""
                <div style="text-align: center; padding: 15px; border-radius: 10px; background-color: var(--secondary-background-color, #f8fafc); border: 1px solid rgba(148,163,184,0.2); height: 100%;">
                    <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #64748b;">Seat Flip Risk</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: {risk_color}; margin-top: 8px;">{risk}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # 4. Coalition Leaning
        with ind_col2:
            lean = c_data["coalition_leaning"]
            lean_color = {"NDA": "#FF9933", "INDIA": "#19A0FF", "Regional": "#808080", "Highly Competitive": "#A855F7"}.get(lean, "#808080")
            st.markdown(
                f"""
                <div style="text-align: center; padding: 15px; border-radius: 10px; background-color: var(--secondary-background-color, #f8fafc); border: 1px solid rgba(148,163,184,0.2); height: 100%;">
                    <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #64748b;">Coalition Leaning</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: {lean_color}; margin-top: 12px; line-height: 1.1;">{lean}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # 5. Competitiveness Score
        st.markdown("<br>", unsafe_allow_html=True)
        comp_score = c_data["competitiveness_score"]
        comp_cat = c_data["competitiveness_category"]
        comp_color = {"Safe": "#10B981", "Moderately Competitive": "#F59E0B", "Highly Competitive": "#EF4444"}.get(comp_cat, "#808080")
        
        st.markdown(f"**Competitiveness Score**: `{comp_score:.1f} / 100` — <span style='color: {comp_color}; font-weight: bold;'>{comp_cat}</span>", unsafe_allow_html=True)
        st.progress(comp_score / 100.0)

    # --- SECTION 6: Historical Timeline ---
    st.markdown("---")
    st.subheader("⏳ 6. Historical Performance Timeline (2004–2024)")
    st.markdown("Constituency performance metrics and campaign context across five Lok Sabha general elections:")

    timeline = c_data["timeline"]
    time_cols = st.columns(len(timeline))
    
    for t_col, t_point in zip(time_cols, timeline):
        with t_col:
            party = t_point["winner_party"]
            color = get_party_color(party)
            
            st.markdown(
                f"""
                <div style="padding: 15px; border-radius: 10px; border-top: 5px solid {color}; background-color: var(--secondary-background-color, #f8fafc); border-left: 1px solid rgba(148,163,184,0.15); border-right: 1px solid rgba(148,163,184,0.15); border-bottom: 1px solid rgba(148,163,184,0.15); height: 100%;">
                    <div style="font-size: 1.1rem; font-weight: 800; color: var(--text-color, #1e293b); text-align: center;">{t_point['year']}</div>
                    <div style="font-size: 1.2rem; font-weight: 800; color: {color}; text-align: center; margin-top: 5px;">{party}</div>
                    <div style="margin-top: 10px; font-size: 0.82rem; color: var(--text-color, #475569);">
                        <b>Vote Share:</b> {t_point['vote_share']:.1f}%<br>
                        <b>Win Margin:</b> {t_point['victory_margin']:.1f}%
                    </div>
                    <hr style="border: 0; border-top: 1px dashed rgba(148,163,184,0.3); margin: 8px 0;">
                    <div style="font-size: 0.72rem; color: #4b5563; font-style: italic; line-height: 1.3;">
                        {t_point['trend']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # --- SECTION 7: Similar Constituencies ---
    st.markdown("---")
    st.subheader("👥 7. Similar Constituencies Analysis")
    st.markdown("Behaviorally closest constituencies identified via Nearest-Neighbors (Euclidean distance on competitiveness, coalition leans, and seat type):")
    
    similar_seats = c_data["similar_constituencies"]
    sim_cols = st.columns(5)
    
    for s_col, n_seat in zip(sim_cols, similar_seats):
        with s_col:
            st.markdown(
                f"""
                <div style="padding: 12px; border-radius: 8px; background-color: var(--secondary-background-color, #f8fafc); border: 1px solid rgba(148,163,184,0.15); min-height: 140px; margin-bottom: 10px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #1e3a8a; line-height: 1.2;">{n_seat['display_name']}</div>
                    <p style="font-size: 0.72rem; color: #475569; margin-top: 6px; line-height: 1.3;">{n_seat['explanation']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Inspect Seat", key=f"btn_sim_{n_seat['display_name']}", use_container_width=True):
                st.session_state.selected_const_disp = n_seat["display_name"]
                st.rerun()

    # --- SECTION 8: Model Performance & Methodology ---
    st.markdown("---")
    with st.expander("🛠️ View Global Model Training & Performance Metrics"):
        st.subheader("Model Validation Dashboard")
        st.markdown("This Logistic Regression classifier analyzes Safe/Swing seat dynamics across 2,172 constituency contests.")
        
        overview_col1, overview_col2 = st.columns(2)
        with overview_col1:
            st.info("**Target Definition**\n\n- **Safe Seat**: Incumbent held the seat with $\ge$ 5.0% victory margin.\n- **Swing Seat**: Seat flipped party in that year or was won by a tight margin ($<$ 5.0%).")
        with overview_col2:
            st.info("**Selected Predictors (Pre-Election Lags)**\n\n- **Categorical**: State, Constituency Type, Previous Winning Party\n- **Numerical**: Previous win margin %, Previous runner-up ratio, Consecutive hold count")
            
        if metrics:
            perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
            with perf_col1:
                st.metric(label="Model Accuracy", value=f"{metrics.get('accuracy', 0.0):.2%}")
            with perf_col2:
                st.metric(label="Precision", value=f"{metrics.get('precision', 0.0):.2%}")
            with perf_col3:
                st.metric(label="Recall (Sensitivity)", value=f"{metrics.get('recall', 0.0):.2%}")
            with perf_col4:
                st.metric(label="F1 Score", value=f"{metrics.get('f1_score', 0.0):.2%}")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Confusion Matrix & Classification Report side by side
            rep_col1, rep_col2 = st.columns([3, 2])
            with rep_col1:
                st.markdown("**Classification Report (Test Partition)**")
                report_df = pd.DataFrame(metrics["classification_report"]).T
                # Filter out average summaries from the main table
                class_table = report_df.drop(["accuracy", "macro avg", "weighted avg"], errors="ignore")
                st.dataframe(class_table.style.format({
                    "precision": "{:.2%}",
                    "recall": "{:.2%}",
                    "f1-score": "{:.2%}",
                    "support": "{:,.0f}"
                }), use_container_width=True)
                
                # Print macro average
                macro_avg = report_df.loc["macro avg"]
                st.markdown(f"- **Macro Average**: Precision `{macro_avg['precision']:.2%}` | Recall `{macro_avg['recall']:.2%}` | F1 `{macro_avg['f1-score']:.2%}`")
            with rep_col2:
                cm_path = base_dir / "outputs" / "ml" / "confusion_matrix.png"
                if cm_path.exists():
                    st.image(str(cm_path), caption="Confusion Matrix on Test Partition", use_container_width=True)
                    
            # Distributions & Importance
            st.markdown("---")
            dist_col1, dist_col2 = st.columns(2)
            with dist_col1:
                feat_path = base_dir / "outputs" / "ml" / "feature_coefficients.png"
                if feat_path.exists():
                    st.image(str(feat_path), caption="Logistic Regression Signed Coefficients (Predictor Influences)", use_container_width=True)
            with dist_col2:
                dist_path = base_dir / "outputs" / "ml" / "competitiveness_distribution.png"
                if dist_path.exists():
                    st.image(str(dist_path), caption="National Distribution of Competitiveness Scores", use_container_width=True)
        else:
            st.warning("Performance metrics not found.")
else:
    st.error("Election Intelligence precomputations not loaded. Please ensure models/election_intelligence.json exists.")
