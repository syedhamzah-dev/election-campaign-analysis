"""
Election Intelligence Module for Election Campaign Analysis.

Computes Competitiveness Scores, Coalition Leanings, Flip Risks, Historical Timelines,
and Nearest-Neighbor similar constituencies. Saves a precomputed JSON for high-performance dashboard loading.
"""

import logging
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors

# Ensure root workspace path is in Python path for clean module imports
base_dir = Path(__file__).resolve().parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

logger = logging.getLogger(__name__)


def compute_constituency_intelligence(data_path: Path, models_dir: Path) -> Dict[str, Any]:
    """
    Orchestrate the election intelligence data pipeline.

    Args:
        data_path (Path): Path to constituency_engineered.csv
        models_dir (Path): Output directory for JSON files.

    Returns:
        Dict[str, Any]: Nested dictionary of constituency intelligence data.
    """
    logger.info("Starting Election Intelligence computation...")
    
    if not data_path.exists():
        raise FileNotFoundError(f"Missing engineered dataset: {data_path}")
        
    df = pd.read_csv(data_path)
    
    # Standardize names and create unique display names
    df["Display_Name"] = df["Constituency_Name"] + " (" + df["State"] + ")"
    
    # Sort for chronologically stable lists
    df_sorted = df.sort_values(["State", "Constituency_No", "Year"]).copy()
    
    # Identify unique constituencies by Display_Name
    constituencies = df_sorted["Display_Name"].unique()
    logger.info(f"Analyzing {len(constituencies)} unique constituencies...")

    intelligence_db = {}
    feature_list = []

    # 1. First Pass: Compute historical metrics for each constituency
    for disp_name in constituencies:
        c_rows = df_sorted[df_sorted["Display_Name"] == disp_name].copy()
        c_rows = c_rows.sort_values("Year")
        
        state = c_rows["State"].iloc[0]
        const_name = c_rows["Constituency_Name"].iloc[0]
        const_no = int(c_rows["Constituency_No"].iloc[0])
        
        # Timeline details
        timeline = []
        for i, row in enumerate(c_rows.itertuples()):
            # Calculate Trend compared to previous year in this constituency's records
            if i == 0:
                trend = "Baseline Election"
            else:
                prev_row = c_rows.iloc[i - 1]
                margin_diff = row.Margin_Percentage - prev_row.Margin_Percentage
                if row.Winner_Party != prev_row.Winner_Party:
                    trend = f"Seat Flipped from {prev_row.Winner_Party} to {row.Winner_Party}"
                elif margin_diff > 0:
                    trend = f"Incumbent {row.Winner_Party} expanded victory margin (+{margin_diff:.2f}%)"
                else:
                    trend = f"Incumbent {row.Winner_Party} victory margin shrunk ({margin_diff:.2f}%)"

            timeline.append({
                "year": int(row.Year),
                "winner_party": str(row.Winner_Party),
                "vote_share": float(row.Winner_Percentage),
                "victory_margin": float(row.Margin_Percentage),
                "trend": trend
            })
            
        # Coalition Leaning
        coal_counts = c_rows["Coalition_Block"].value_counts()
        # Mapping coalition blocks
        nda_wins = int(coal_counts.get("NDA", 0))
        india_wins = int(coal_counts.get("UPA / I.N.D.I.A.", 0))
        regional_wins = int(coal_counts.get("Others / Regional", 0)) + int(coal_counts.get("Left Front", 0))
        
        total_wins = len(c_rows)
        
        if nda_wins >= 3:
            leaning = "NDA"
        elif india_wins >= 3:
            leaning = "INDIA"
        elif regional_wins >= 3:
            leaning = "Regional"
        else:
            leaning = "Highly Competitive"
            
        # Flip rate and latest metrics
        latest_row = c_rows.iloc[-1]
        flips = float(c_rows["Seat_Flip_Status"].sum(skipna=True))
        valid_flips_count = float(c_rows["Seat_Flip_Status"].dropna().count())
        flip_rate = flips / valid_flips_count if valid_flips_count > 0 else 0.0
        
        avg_margin = float(c_rows["Margin_Percentage"].mean())
        unique_parties_count = int(c_rows["Winner_Party"].nunique())
        latest_margin = float(latest_row.Margin_Percentage)
        latest_winner = str(latest_row.Winner_Party)
        res_type = str(latest_row.Constituency_Type)

        # Competitiveness Score (0-100)
        # Low margin = high competitiveness
        margin_score = max(0.0, 100.0 - avg_margin * 3.0)
        # Flip rate = high competitiveness
        flip_score = flip_rate * 100.0
        # Unique parties count = high competitiveness
        party_score = ((unique_parties_count - 1) / max(1, total_wins - 1)) * 100.0
        
        comp_score = 0.4 * margin_score + 0.3 * flip_score + 0.3 * party_score
        comp_score = float(np.clip(comp_score, 0.0, 100.0))
        
        if comp_score <= 30.0:
            comp_category = "Safe"
        elif comp_score <= 70.0:
            comp_category = "Moderately Competitive"
        else:
            comp_category = "Highly Competitive"

        # Flip Risk
        if flip_rate >= 0.5 or latest_margin < 5.0:
            flip_risk = "High"
        elif flip_rate == 0.0 and latest_margin >= 10.0:
            flip_risk = "Low"
        else:
            flip_risk = "Medium"

        # Safe vs Swing explanation
        if flip_risk == "High" or latest_margin < 5.0:
            risk_explanation = f"Classified as High Flip Risk due to high historic seat volatility ({flip_rate:.1%}) or narrow victory margin in the last election ({latest_margin:.2f}%)."
        elif flip_risk == "Low":
            risk_explanation = f"Classified as Low Flip Risk. Retained by the incumbent party in all recorded election cycles with a comfortable margin of {latest_margin:.2f}% in 2024."
        else:
            risk_explanation = f"Classified as Medium Flip Risk. Moderate competitiveness historically with an average victory margin of {avg_margin:.2f}%."

        intelligence_db[disp_name] = {
            "name": const_name,
            "state": state,
            "constituency_no": const_no,
            "display_name": disp_name,
            "timeline": timeline,
            "coalition_leaning": leaning,
            "competitiveness_score": comp_score,
            "competitiveness_category": comp_category,
            "flip_risk": flip_risk,
            "risk_explanation": risk_explanation,
            "avg_margin": avg_margin,
            "flip_rate": flip_rate,
            "unique_parties": unique_parties_count,
            "latest_margin": latest_margin,
            "latest_winner": latest_winner,
            "reservation_type": res_type
        }
        
        # Build features for Nearest Neighbors (one row per constituency)
        feature_list.append({
            "display_name": disp_name,
            "comp_score": comp_score,
            "avg_margin": avg_margin,
            "flip_rate": flip_rate,
            "unique_parties": unique_parties_count,
            "latest_margin": latest_margin,
            # Leaning encodes
            "lean_NDA": 1.0 if leaning == "NDA" else 0.0,
            "lean_INDIA": 1.0 if leaning == "INDIA" else 0.0,
            "lean_Regional": 1.0 if leaning == "Regional" else 0.0,
            "lean_Competitive": 1.0 if leaning == "Highly Competitive" else 0.0,
            # Reservation encodes
            "res_GEN": 1.0 if res_type == "GEN" else 0.0,
            "res_SC": 1.0 if res_type == "SC" else 0.0,
            "res_ST": 1.0 if res_type == "ST" else 0.0,
        })

    # 2. Second Pass: Compute Nearest Neighbors similarity
    feat_df = pd.DataFrame(feature_list)
    cols_to_scale = ["comp_score", "avg_margin", "flip_rate", "unique_parties", "latest_margin"]
    
    scaler = MinMaxScaler()
    scaled_num = scaler.fit_transform(feat_df[cols_to_scale])
    
    # Reassemble features
    scaled_feats = np.hstack([
        scaled_num, 
        feat_df[["lean_NDA", "lean_INDIA", "lean_Regional", "lean_Competitive", "res_GEN", "res_SC", "res_ST"]].values
    ])
    
    # Fit Nearest Neighbors
    nn = NearestNeighbors(n_neighbors=6, metric="euclidean")
    nn.fit(scaled_feats)
    
    distances, indices = nn.kneighbors(scaled_feats)
    
    # Save neighbors for each constituency
    for idx, disp_name in enumerate(feat_df["display_name"]):
        neighbor_indices = indices[idx][1:] # Drop first which is the seat itself
        neighbor_distances = distances[idx][1:]
        
        similar_seats = []
        for n_idx, dist in zip(neighbor_indices, neighbor_distances):
            n_name = feat_df["display_name"].iloc[n_idx]
            
            # Generate Similarity Explanation
            seat_a = intelligence_db[disp_name]
            seat_b = intelligence_db[n_name]
            
            explanations = []
            if seat_a["coalition_leaning"] == seat_b["coalition_leaning"]:
                explanations.append(f"both lean {seat_a['coalition_leaning']}")
            else:
                explanations.append("similar voting behavior")
                
            if seat_a["competitiveness_category"] == seat_b["competitiveness_category"]:
                explanations.append(f"both are {seat_a['competitiveness_category']} seats")
                
            if seat_a["reservation_type"] == seat_b["reservation_type"]:
                explanations.append(f"both are reserved {seat_a['reservation_type']} seats" if seat_a['reservation_type'] != "GEN" else "both are GEN seats")
                
            score_diff = abs(seat_a["competitiveness_score"] - seat_b["competitiveness_score"])
            if score_diff <= 10.0:
                explanations.append(f"very close competitiveness scores (diff of {score_diff:.1f})")
                
            explanation_str = ", ".join(explanations)
            explanation_str = explanation_str[0].upper() + explanation_str[1:] + "."
            
            similar_seats.append({
                "display_name": n_name,
                "distance": float(dist),
                "explanation": explanation_str
            })
            
        intelligence_db[disp_name]["similar_constituencies"] = similar_seats

    # Save to JSON
    models_dir.mkdir(parents=True, exist_ok=True)
    intelligence_file = models_dir / "election_intelligence.json"
    with open(intelligence_file, "w", encoding="utf-8") as f:
        json.dump(intelligence_db, f, indent=4)
        
    logger.info(f"Saved election intelligence to: {intelligence_file}")
    return intelligence_db


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data_path = base_dir / "data" / "processed" / "constituency_engineered.csv"
    models_path = base_dir / "models"
    
    compute_constituency_intelligence(data_path, models_path)
    print("Intelligence processing complete.")
