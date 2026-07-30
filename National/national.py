"""
Exploratory Data Analysis Utilities Module for Election Campaign Analysis (2004-2024).

Provides modular aggregation functions and chart generation routines for
Essential EDA questions across National, Party, State, Constituency, and Candidate dimensions.
"""

import logging
from pathlib import Path
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.visualization.base import (
    COALITION_COLORS,
    PARTY_COLORS,
    save_figure,
    setup_matplotlib_style,
)

logger = logging.getLogger(__name__)


def analyze_coalition_trajectory(
    c_df: pd.DataFrame, figures_dir: Path
) -> Tuple[pd.DataFrame, Path]:
    """
    Execute Essential Analysis 1: National Coalition Trajectory (2004-2024).

    Args:
        c_df (pd.DataFrame): Feature-engineered constituency dataset.
        figures_dir (Path): Output directory for saving figures.

    Returns:
        Tuple[pd.DataFrame, Path]:
            - Summary aggregation table DataFrame.
            - Path to the saved publication figure.
    """
    setup_matplotlib_style()
    logger.info("Executing Essential Analysis 1: Coalition Trajectory...")

    # Aggregation: Group by Year and Coalition_Block
    agg_df = (
        c_df.groupby(["Year", "Coalition_Block"])
        .size()
        .unstack(fill_value=0)
    )

    # Ensure consistent column ordering
    desired_order = ["NDA", "UPA / I.N.D.I.A.", "Left Front", "Others / Regional"]
    columns_present = [col for col in desired_order if col in agg_df.columns]
    agg_df = agg_df[columns_present]

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = [COALITION_COLORS.get(col, "#808080") for col in agg_df.columns]
    
    bottom = np.zeros(len(agg_df))
    bars = []
    
    for col, color in zip(agg_df.columns, colors):
        bar = ax.bar(
            agg_df.index.astype(str),
            agg_df[col],
            bottom=bottom,
            label=col,
            color=color,
            width=0.55,
            edgecolor="white",
            linewidth=1.0,
        )
        bars.append(bar)
        
        # Add value labels inside segments
        for i, val in enumerate(agg_df[col]):
            if val >= 15:  # Only label segments large enough
                ax.text(
                    i,
                    bottom[i] + val / 2,
                    f"{val}",
                    ha="center",
                    va="center",
                    color="white" if color in ["#B22222", "#22409A"] else "black",
                    fontweight="bold",
                    fontsize=10,
                )
        bottom += agg_df[col].values

    ax.set_title("National Coalition Seat Share Trajectory (Lok Sabha 2004–2024)", pad=15)
    ax.set_xlabel("Election Year")
    ax.set_ylabel("Total Parliamentary Seats Won")
    ax.set_ylim(0, 600)
    ax.axhline(272, color="crimson", linestyle="--", linewidth=1.5, label="Majority Threshold (272 Seats)")
    
    ax.legend(title="Coalition Block", loc="upper left", bbox_to_anchor=(1.02, 1))
    
    # Save figure
    output_fig_path = figures_dir / "eda_01_coalition_trajectory.png"
    save_figure(fig, output_fig_path)

    # Formatting summary insight table
    summary_table = agg_df.reset_index()
    summary_table["Total_Seats"] = summary_table[columns_present].sum(axis=1)

    return summary_table, output_fig_path
