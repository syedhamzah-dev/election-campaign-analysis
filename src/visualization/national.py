"""
National Visualizations Module.
Implements national coalition trajectory plots.
"""

from pathlib import Path
from typing import Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.visualization.base import (
    COALITION_COLORS,
    add_chart_footer,
    save_figure,
    setup_matplotlib_style,
)


def plot_coalition_trajectory(c_df: pd.DataFrame, output_dir: Optional[Path] = None) -> Union[Path, plt.Figure]:
    """
    Viz 1: Coalition Seat Share Trajectory (2004-2024).
    Audit Status: Primary Dashboard Visualization.
    """
    setup_matplotlib_style()

    from src.analysis.national.national import analyze_coalition_trajectory
    agg_df = analyze_coalition_trajectory(c_df)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [COALITION_COLORS.get(col, "#808080") for col in agg_df.columns]

    bottom = np.zeros(len(agg_df))
    for col, color in zip(agg_df.columns, colors):
        values = agg_df[col].values
        ax.bar(
            agg_df.index.astype(str),
            values,
            bottom=bottom,
            label=col,
            color=color,
            width=0.55,
            edgecolor="white",
            linewidth=1.0,
        )
        for i, val in enumerate(values):
            if val >= 15:
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
        bottom += values

    ax.axhline(272, color="crimson", linestyle="--", linewidth=1.5, label="Majority Threshold (272 Seats)")
    ax.set_title("National Coalition Seat Share Trajectory (2004–2024)")
    fig.suptitle("Longitudinal Shift in Parliamentary Majority Control", y=0.98, fontsize=12, style="italic")
    ax.set_xlabel("Election Year")
    ax.set_ylabel("Total Parliamentary Seats Won")
    ax.set_ylim(0, 600)
    ax.legend(title="Coalition Block", loc="upper left", bbox_to_anchor=(1.02, 1))

    insight = "In 2024, NDA & UPA/I.N.D.I.A. captured 97.1% of seats (527/543), signaling a near-total collapse of unaligned regional seats."
    add_chart_footer(fig, "Election Commission of India | Processed Dataset", insight)

    if output_dir is not None:
        out_path = output_dir / "fig_01_coalition_trajectory.png"
        save_figure(fig, out_path)
        return out_path
    return fig
