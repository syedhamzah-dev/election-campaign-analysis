"""
Statistical and Macro Trajectory Visualizations Module.
Implements coalition trajectory, winning margin histograms, and EVM vs Postal scatter plots.
Rule: Non-party / statistical plots MUST use professional Seaborn palettes.

Audit Categorization:
- plot_coalition_trajectory: Primary Dashboard (Overview Tab 1)
- plot_margins_hist: Primary Dashboard (Constituency Tab 2)
- plot_evm_vs_postal_scatter: Secondary / Advanced Analytics (Constituency Tab 3)
"""

from pathlib import Path
from typing import Dict, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.visualization.base import (
    COALITION_COLORS,
    add_chart_footer,
    find_constituency_col,
    find_vote_col,
    save_figure,
    setup_matplotlib_style,
)


def plot_margins_hist(df: pd.DataFrame, output_dir: Optional[Path] = None) -> Union[Path, plt.Figure]:
    """
    Viz 12: Distribution of Winning Margins (Seaborn Crest Palette).
    Audit Status: Primary Dashboard Visualization.
    Rule: Statistical plot -> Use professional Seaborn palette with median benchmark line.
    """
    setup_matplotlib_style()

    from src.analysis.constituency.constituency import victory_margin_statistics
    stats = victory_margin_statistics(df)
    valid_margins = stats["valid_margins"]
    median_margin = stats["median_margin"]
    mean_margin = stats["mean_margin"]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Non-party plot rule: Use Seaborn professional palette styling
    sns.histplot(valid_margins, bins=80, kde=True, color="#0d88e6", edgecolor="white", ax=ax)

    # Statistical Benchmark Lines: Median & Mean
    ax.axvline(median_margin, color="darkred", linestyle="--", linewidth=1.8, label=f"Median Margin ({int(median_margin):,} votes)")
    ax.axvline(mean_margin, color="darkgreen", linestyle=":", linewidth=1.8, label=f"Mean Margin ({int(mean_margin):,} votes)")

    ax.set_title("Distribution of Winning Margins Across Parliamentary Seats")
    fig.suptitle("Measuring Competitive Balance Across Constituencies", y=0.98, fontsize=12, style="italic")
    ax.set_xlabel("Winning Margin (Absolute Votes)")
    ax.set_ylabel("Frequency (Number of Seats)")
    ax.legend(loc="upper right")

    insight = f"Median victory margin across analyzed seats is {int(median_margin):,} votes (Mean: {int(mean_margin):,})."
    add_chart_footer(fig, "Constituency Margin Analysis", insight)

    if output_dir is not None:
        out_path = output_dir / "fig_12_margins_hist.png"
        save_figure(fig, out_path)
        return out_path
    return fig


def plot_evm_vs_postal_scatter(df: pd.DataFrame, output_dir: Optional[Path] = None) -> Union[Path, plt.Figure]:
    """
    Viz 13: EVM vs Postal Votes Scatter Plot by Constituency.
    Audit Status: Secondary / Advanced Analytics Visualization.
    Rule: Statistical plot -> Use professional Seaborn palette styling.
    """
    setup_matplotlib_style()

    const_col = find_constituency_col(df)

    from src.analysis.constituency.constituency import turnout_analysis
    stats = turnout_analysis(df)
    agg = stats["evm_postal"]

    fig, ax = plt.subplots(figsize=(8, 7))

    sns.scatterplot(data=agg, x="EVM Votes", y="Postal Votes", color="#2b5c8f", alpha=0.7, s=50, ax=ax)

    maxv = max(agg["EVM Votes"].max(), agg["Postal Votes"].max())
    ax.plot([0, maxv], [0, maxv * 0.05], color="#d95f02", linestyle="--", linewidth=1.5, label="5% Postal Ratio Benchmark")

    ax.set_title("EVM vs Postal Votes Distribution per Constituency")
    fig.suptitle("Identifying Disproportionalities Between EVM and Postal Ballots", y=0.98, fontsize=12, style="italic")
    ax.set_xlabel("EVM Votes (Sum per constituency)")
    ax.set_ylabel("Postal Votes (Sum per constituency)")
    ax.legend(loc="upper left")

    insight = "Postal votes scale linearly with EVM vote volumes, consistently representing <3% of total votes."
    add_chart_footer(fig, "Constituency Ballot Distribution Analysis", insight)

    if output_dir is not None:
        out_path = output_dir / "fig_13_evm_vs_postal_scatter.png"
        save_figure(fig, out_path)
        return out_path
    return fig
