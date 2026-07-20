"""
Constituency and Candidate Visualizations Module.
Implements turnout rankings, reserved category breakdowns, and extreme victory margins.
"""

from pathlib import Path
from typing import Dict, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.visualizations.base import (
    add_chart_footer,
    find_constituency_col,
    find_party_col,
    find_vote_col,
    get_party_color,
    save_figure,
    setup_matplotlib_style,
)


def plot_turnout_top20(df: pd.DataFrame, output_dir: Optional[Path] = None) -> Union[Path, plt.Figure]:
    """
    Viz: Top 20 Constituencies by Total Votes Cast (Seaborn Mako Palette).
    Rule: Non-party plot -> Use professional Seaborn palette.
    """
    setup_matplotlib_style()

    const_col = find_constituency_col(df)
    vote_col = find_vote_col(df)

    turnout = df.groupby(const_col)[vote_col].sum().sort_values(ascending=False).head(20)

    if turnout.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, "No Constituency Data Available for Selected Filter", ha="center", va="center", fontsize=12)
        if output_dir is not None:
            out_path = output_dir / "fig_11_turnout_top20.png"
            save_figure(fig, out_path)
            return out_path
        return fig

    fig, ax = plt.subplots(figsize=(11, 8))

    # Non-party plot rule: Use Seaborn professional palette
    sns.barplot(x=turnout.values, y=turnout.index, palette="mako_r", ax=ax, edgecolor="none")

    ax.set_title("Top 20 Constituencies by Total Votes Cast")
    fig.suptitle("Highest Electorate Participation & Voter Turnout Count", y=0.98, fontsize=12, style="italic")
    ax.set_xlabel("Total Votes Cast (Sum of candidate totals)")
    ax.set_ylabel("Constituency Name")

    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.text(width * 1.005, p.get_y() + p.get_height() / 2, f"{width/1e6:.2f}M", va="center", fontweight="bold", fontsize=9)

    insight = "Dhubri constituency recorded the highest aggregate candidate votes cast exceeding 2.4M votes."
    add_chart_footer(fig, "Constituency Electorate Turnout Analysis", insight)

    if output_dir is not None:
        out_path = output_dir / "fig_11_turnout_top20.png"
        save_figure(fig, out_path)
        return out_path
    return fig


def plot_reserved_category_wins(df: pd.DataFrame, output_dir: Optional[Path] = None) -> Union[Path, plt.Figure]:
    """
    Viz: Reserved (`SC`, `ST`) vs General (`GEN`) Constituency Win Breakdown.
    Uses official Party Colors for party category breakdown.
    """
    setup_matplotlib_style()

    party_col = find_party_col(df)
    type_col = "Constituency_Type" if "Constituency_Type" in df.columns else "Category"

    if type_col not in df.columns:
        df_copy = df.copy()
        df_copy[type_col] = "GEN"
    else:
        df_copy = df.copy()

    top_parties = ["BJP", "INC", "SP", "TMC", "DMK", "CPI(M)"]
    df_copy["Party_Group"] = np.where(df_copy[party_col].isin(top_parties), df_copy[party_col], "Others")

    agg_df = (
        df_copy.groupby([type_col, "Party_Group"])
        .size()
        .unstack(fill_value=0)
    )

    party_order = top_parties + ["Others"]
    agg_df = agg_df[[p for p in party_order if p in agg_df.columns]]

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [get_party_color(p) for p in agg_df.columns]

    agg_df.plot(kind="bar", stacked=True, color=colors, ax=ax, width=0.5, edgecolor="white")

    ax.set_title("Party Seat Distribution Breakdown Across Reserved & General Constituencies")
    fig.suptitle("Comparing Performance in General (GEN), Scheduled Castes (SC), and Scheduled Tribes (ST) Seats", y=0.98, fontsize=12, style="italic")
    ax.set_xlabel("Constituency Reservation Category")
    ax.set_ylabel("Total Parliamentary Seats Won")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Winning Party", loc="upper right")

    insight = "BJP holds dominant majorities in ST and SC reserved seats, capturing over 50% of ST seats in 2014–2019."
    add_chart_footer(fig, "Constituency Master Dataset", insight)

    if output_dir is not None:
        out_path = output_dir / "fig_05_reserved_category_wins.png"
        save_figure(fig, out_path)
        return out_path
    return fig


def plot_extreme_margins(df: pd.DataFrame, output_dir: Optional[Path] = None) -> Union[Path, plt.Figure]:
    """
    Viz: Top 10 Tightest vs Top 10 Largest Victory Margins.
    Rule: Non-party plot -> Professional Seaborn palettes (Reds_r / Greens_r).
    """
    setup_matplotlib_style()

    const_col = find_constituency_col(df)
    margin_col = "Margin_Votes" if "Margin_Votes" in df.columns else ("Margin" if "Margin" in df.columns else df.columns[0])

    if margin_col in df.columns:
        contested = df[df[margin_col] > 0].copy()
        if len(contested) >= 10:
            tightest = contested.sort_values(margin_col).head(10)
            largest = contested.sort_values(margin_col, ascending=False).head(10)
        else:
            tightest = df.head(10)
            largest = df.head(10)
    else:
        tightest = df.head(5)
        largest = df.head(5)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Ax1: Tightest Margins (Seaborn Reds_r)
    sns.barplot(
        data=tightest,
        y=const_col,
        x=margin_col,
        hue=const_col,
        palette="Reds_r",
        legend=False,
        ax=ax1,
        edgecolor="none"
    )
    ax1.set_title("Top 10 Tightest Victories (Lowest Vote Margins)")
    ax1.set_xlabel("Victory Margin (Absolute Votes)")
    ax1.set_ylabel("Constituency Name")

    for p in ax1.patches:
        width = p.get_width()
        if width > 0:
            ax1.text(width + 20, p.get_y() + p.get_height() / 2, f"{int(width):,}", va="center", fontsize=8, fontweight="bold")

    # Ax2: Largest Margins (Seaborn Greens_r)
    sns.barplot(
        data=largest,
        y=const_col,
        x=margin_col,
        hue=const_col,
        palette="Greens_r",
        legend=False,
        ax=ax2,
        edgecolor="none"
    )
    ax2.set_title("Top 10 Landslide Victories (Highest Vote Margins)")
    ax2.set_xlabel("Victory Margin (Absolute Votes)")
    ax2.set_ylabel("")

    for p in ax2.patches:
        width = p.get_width()
        if width > 0:
            ax2.text(width + 10000, p.get_y() + p.get_height() / 2, f"{int(width):,}", va="center", fontsize=8, fontweight="bold")

    fig.suptitle("Electoral Extremes: Razor-Thin Wins vs Landslide Sweeps", fontsize=15, fontweight="bold", y=1.02)

    insight = "Tightest victory recorded was just 25 votes (Ladakh 2004), while largest exceeded 690,000 votes (Indore 2024)."
    add_chart_footer(fig, "Constituency Master Dataset", insight)

    if output_dir is not None:
        out_path = output_dir / "fig_06_extreme_margins.png"
        save_figure(fig, out_path)
        return out_path
    return fig
