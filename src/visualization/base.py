"""
Base Visualization Utilities & Global Theme Setup.
Enforces publication quality 300 DPI standards, official party color palettes, and footers.
"""

import logging
from pathlib import Path
from typing import Dict, Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)

# Official Political Party Color Palette Mapping
PARTY_COLORS: Dict[str, str] = {
    "BJP": "#FF9933",
    "Bharatiya Janata Party": "#FF9933",
    "INC": "#19A0FF",
    "Indian National Congress": "#19A0FF",
    "SP": "#E30613",
    "Samajwadi Party": "#E30613",
    "BSP": "#22409A",
    "Bahujan Samaj Party": "#22409A",
    "AAP": "#00B7EB",
    "Aam Aadmi Party": "#00B7EB",
    "AITC": "#00A651",
    "TMC": "#00A651",
    "All India Trinamool Congress": "#00A651",
    "DMK": "#D71920",
    "Dravida Munnetra Kazhagam": "#D71920",
    "AIADMK": "#008000",
    "All India Anna Dravida Munnetra Kazhagam": "#008000",
    "CPI(M)": "#B22222",
    "Communist Party of India  (Marxist)": "#B22222",
    "Communist Party of India (Marxist)": "#B22222",
    "NCP": "#1F77B4",
    "Nationalist Congress Party": "#1F77B4",
    "Shiv Sena": "#F58220",
    "SS": "#F58220",
    "SS(UBT)": "#F58220",
    "Shiv Sena (Uddhav Balasaheb Thackeray)": "#F58220",
    "Shiv Sena (Uddhav Balasaheb Thackrey)": "#F58220",
    "Others": "#808080",
    "Others / Regional": "#808080",
    "Independent": "#808080",
}

# Coalition Color Palette Mapping
COALITION_COLORS: Dict[str, str] = {
    "NDA": "#FF9933",
    "UPA / I.N.D.I.A.": "#19A0FF",
    "Left Front": "#B22222",
    "Others / Regional": "#808080",
}


def get_party_color(party_name: str) -> str:
    """Helper to return official party hex color with fallback to default Gray."""
    if not isinstance(party_name, str):
        return "#808080"
    party_str = party_name.strip()
    if party_str in PARTY_COLORS:
        return PARTY_COLORS[party_str]
    for k, v in PARTY_COLORS.items():
        if k.lower() in party_str.lower() or party_str.lower() in k.lower():
            return v
    return "#808080"


def setup_matplotlib_style() -> None:
    """Configure global Matplotlib and Seaborn style defaults for publication output."""
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.labelweight": "bold",
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 16,
        "figure.titleweight": "bold",
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })


def add_chart_footer(fig: plt.Figure, source_text: str, insight_text: str) -> None:
    """Add standardized source and key insight annotations to the bottom of the figure."""
    footer = f"Source: {source_text}\nKey Insight: {insight_text}"
    fig.text(
        0.01,
        -0.06,
        footer,
        ha="left",
        va="top",
        fontsize=9,
        style="italic",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#cccccc", alpha=0.9),
    )


def save_figure(fig: plt.Figure, output_path: Path) -> None:
    """Save figure with 300 DPI resolution and tight layout."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    logger.info(f"Saved publication figure: {output_path.resolve()}")
    plt.close(fig)


def find_party_col(df: pd.DataFrame) -> str:
    """Helper to detect party column across raw and processed datasets."""
    for col in ["Party", "Leading Party", "Winner_Party", "Leading_Party", "Party_Alliance"]:
        if col in df.columns:
            return col
    return df.columns[0]


def find_vote_col(df: pd.DataFrame) -> str:
    """Helper to detect votes column across raw and processed datasets."""
    for col in ["Total Votes", "Winner_Votes", "Votes", "Margin_Votes", "Margin"]:
        if col in df.columns:
            return col
    return df.columns[0]


def find_constituency_col(df: pd.DataFrame) -> str:
    """Helper to detect constituency column across raw and processed datasets."""
    for col in ["Constituency", "Constituency_Name", "Constituency_No"]:
        if col in df.columns:
            return col
    return df.columns[0]
