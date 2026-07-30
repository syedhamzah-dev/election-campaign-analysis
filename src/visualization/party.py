"""
Party Performance Visualizations Module.
Implements party-specific publication charts using Official Party Colors.

Audit Categorization:
- plot_seats_by_party: Primary Dashboard (Party Analysis Tab 1)
- plot_votes_by_party: Primary Dashboard (Party Analysis Tab 2)
- plot_postal_vote_share: Primary Dashboard (Party Analysis Tab 3)
- plot_party_retention_loss: Primary Dashboard (Party Analysis Tab 4)
- plot_vote_seat_conversion: Primary Dashboard (Party Analysis Tab 5 & Overview)
- plot_evm_postal_by_party: Archived Redundant (Replaced by plot_postal_vote_share)
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.visualization.base import (
    PARTY_COLORS,
    add_chart_footer,
    find_party_col,
    find_vote_col,
    get_party_color,
    save_figure,
    setup_matplotlib_style,
)


def plot_seats_by_party(df: pd.DataFrame, output_dir: Optional[Path] = None) -> Union[Path, plt.Figure]:
    """
    Viz 8: Top Parties by Seats Won (Official Party Colors).
    Audit Status: Primary Dashboard Visualization.
    """
    setup_matplotlib_style()
    
    from src.analysis.party.party import vote_share_statistics
    stats = vote_share_statistics(df)
    seats = stats["seats"]

    if seats.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, "No Seats Data Available for Filter", ha="center", va="center", fontsize=14)
        if output_dir is not None:
            out_path = output_dir / "fig_08_seats_by_party.png"
            save_figure(fig, out_path)
            return out_path
        return fig

    fig, ax = plt.subplots(figsize=(11, 7))
    colors = [get_party_color(p) for p in seats.index]
    
    sns.barplot(x=seats.values, y=seats.index, palette=colors, ax=ax, edgecolor="white", linewidth=0.8)
    ax.set_title("Top Political Parties by Seats Won")
    fig.suptitle("Electoral Success Across Contested Parliamentary Constituencies", y=0.98, fontsize=12, style="italic")
    ax.set_xlabel("Number of Seats Won")
    ax.set_ylabel("Political Party")

    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.text(width + 0.5, p.get_y() + p.get_height() / 2, f"{int(width)}", va="center", fontweight="bold", fontsize=9)

    insight = "BJP and INC lead the overall seat tallies across major national election cycles."
    add_chart_footer(fig, "Election Commission of India | Party Results", insight)

    if output_dir is not None:
        out_path = output_dir / "fig_08_seats_by_party.png"
        save_figure(fig, out_path)
        return out_path
    return fig


def plot_votes_by_party(df: pd.DataFrame, output_dir: Optional[Path] = None) -> Union[Path, plt.Figure]:
    """
    Viz 9: Top Parties by Total Votes Received (Official Party Colors).
    Audit Status: Primary Dashboard Visualization.
    """
    setup_matplotlib_style()
    
    from src.analysis.party.party import vote_share_statistics
    stats = vote_share_statistics(df)
    votes = stats["votes"]

    if votes.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, "No Vote Data Available for Filter", ha="center", va="center", fontsize=14)
        if output_dir is not None:
            out_path = output_dir / "fig_09_votes_by_party.png"
            save_figure(fig, out_path)
            return out_path
        return fig

    fig, ax = plt.subplots(figsize=(11, 7))
    colors = [get_party_color(p) for p in votes.index]

    sns.barplot(x=votes.values, y=votes.index, palette=colors, ax=ax, edgecolor="white", linewidth=0.8)
    ax.set_title("Top Political Parties by Total Votes Received")
    fig.suptitle("Summed Candidate Vote Tallies Across National Contests", y=0.98, fontsize=12, style="italic")
    ax.set_xlabel("Total Votes Received (Sum across candidates)")
    ax.set_ylabel("Political Party")

    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.text(width * 1.01, p.get_y() + p.get_height() / 2, f"{width/1e6:.2f}M", va="center", fontweight="bold", fontsize=8)

    # Statistical benchmark line: Average votes per top party
    avg_votes = votes.mean()
    ax.axvline(avg_votes, color="darkred", linestyle="--", linewidth=1.5, label=f"Average Votes ({avg_votes/1e6:.1f}M)")
    ax.legend(loc="lower right")

    insight = f"Top party average vote tally is {avg_votes/1e6:.1f}M votes. BJP received over 230M total votes in 2024."
    add_chart_footer(fig, "Election Commission of India | Party Votes Summary", insight)

    if output_dir is not None:
        out_path = output_dir / "fig_09_votes_by_party.png"
        save_figure(fig, out_path)
        return out_path
    return fig


def plot_postal_vote_share(df: pd.DataFrame, output_dir: Optional[Path] = None) -> Union[Path, plt.Figure]:
    """
    Viz 10: Postal Vote Share (%) Breakdown by Party (Official Party Colors).
    Audit Status: Primary Dashboard Visualization (Replaces absolute EVM vs Postal chart).
    Calculates: postal_share_percentage = (postal_votes / (evm_votes + postal_votes)) * 100
    for Top 20 parties by total votes.
    """
    setup_matplotlib_style()
    
    from src.analysis.party.party import vote_share_statistics
    stats = vote_share_statistics(df)
    agg_top = stats["postal_vote_share"]

    fig, ax = plt.subplots(figsize=(11, 8))
    colors = [get_party_color(p) for p in agg_top.index]

    bars = ax.barh(agg_top.index, agg_top["Postal_Share_Pct"], color=colors, edgecolor="white", height=0.65)

    ax.set_title("Postal Vote Share (%) Breakdown by Political Party (Top 20)")
    fig.suptitle("Relative Reliance on Postal Ballots vs General EVM Voting", y=0.98, fontsize=12, style="italic")
    ax.set_xlabel("Postal Vote Share (% of Total Party Votes)")
    ax.set_ylabel("Political Party")

    max_val = agg_top["Postal_Share_Pct"].max() if not agg_top.empty else 3.0
    ax.set_xlim(0, max(max_val * 1.15, 1.0))

    for bar in bars:
        width = bar.get_width()
        ax.text(width + max_val * 0.015, bar.get_y() + bar.get_height() / 2, f"{width:.2f}%",
                va="center", ha="left", fontweight="bold", fontsize=9, color="#222222")

    avg_pct = (agg_top["Postal Votes"].sum() / agg_top["Total Votes"].sum() * 100) if agg_top["Total Votes"].sum() > 0 else 1.5
    ax.axvline(avg_pct, color="darkred", linestyle="--", linewidth=1.5, label=f"Average Share ({avg_pct:.2f}%)")
    ax.legend(loc="lower right")

    insight = f"Postal ballots average {avg_pct:.2f}% of party totals, highlighting relative reliance across services & government personnel."
    add_chart_footer(fig, "Election Commission of India | Detailed Vote Breakdown", insight)

    if output_dir is not None:
        out_path = output_dir / "fig_10_postal_vote_share.png"
        save_figure(fig, out_path)
        return out_path
    return fig


def plot_evm_postal_by_party(df: pd.DataFrame, output_dir: Optional[Path] = None) -> Union[Path, plt.Figure]:
    """
    Legacy Helper / Archived Visualization.
    Audit Status: Archived Redundant (Replaced by plot_postal_vote_share on primary dashboard).
    """
    return plot_postal_vote_share(df, output_dir)


def plot_vote_seat_conversion(df: pd.DataFrame, output_dir: Optional[Path] = None) -> Union[Path, plt.Figure]:
    """
    Viz 2: National Vote Share % vs Parliamentary Seats Won (FPTP Efficiency).
    Audit Status: Primary Dashboard Visualization.
    """
    setup_matplotlib_style()
    
    from src.analysis.party.party import seat_conversion
    latest = seat_conversion(df)

    fig, ax1 = plt.subplots(figsize=(11, 6.5))

    x = np.arange(len(latest))
    width = 0.35
    party_names = latest["Party"]
    bar_colors = [get_party_color(p) for p in party_names]

    # Plot Vote Share % on Left Axis (ax1)
    bars1 = ax1.bar(x - width / 2, latest["Percentage"], width, label="Vote Share (%)", color="#38bdf8", edgecolor="#0284c7", alpha=0.9)
    
    # Plot Seats Won on Right Axis (ax2)
    ax2 = ax1.twinx()
    bars2 = ax2.bar(x + width / 2, latest["Seats"], width, label="Seats Won", color=bar_colors, edgecolor="black", alpha=0.9)

    ax1.set_title("National Vote Share (%) vs Parliamentary Seats Won")
    fig.suptitle("Evaluating First-Past-The-Post Vote Conversion Efficiency Across Elections", y=0.98, fontsize=12, style="italic")
    ax1.set_xlabel("Election Year & Political Party")
    ax1.set_ylabel("National Vote Share (%)", color="#0284c7", fontweight="bold")
    ax2.set_ylabel("Seats Won Count", color="black", fontweight="bold")
    
    # Format x-ticks with Year & Party Name
    x_labels = []
    for idx, row in latest.iterrows():
        p_name = row["Party"]
        if "Year" in row and pd.notna(row["Year"]):
            x_labels.append(f"{p_name}\n({int(row['Year'])})")
        else:
            x_labels.append(str(p_name))

    ax1.set_xticks(x)
    ax1.set_xticklabels(x_labels, fontweight="bold", rotation=0)
    ax1.grid(False)

    # Annotate Vote Share % on ax1 bars
    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax1.annotate(f"{height:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8, color="#0284c7", fontweight="bold")

    # Annotate Seats Won on ax2 bars
    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax2.annotate(f"{int(height)}", xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontweight="bold", fontsize=9)

    # Unified explicit legend combining both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=True, facecolor="white", framealpha=0.9)

    insight = "FPTP rules disproportionately reward major parties with seat shares exceeding national vote shares."
    add_chart_footer(fig, "Party Summary Master Dataset", insight)

    if output_dir is not None:
        out_path = output_dir / "fig_02_vote_seat_conversion.png"
        save_figure(fig, out_path)
        return out_path
    return fig


def plot_party_retention_loss(df: pd.DataFrame, output_dir: Optional[Path] = None) -> Union[Path, plt.Figure]:
    """
    Viz 7: Incumbent Party Seat Retention vs Seat Loss Breakdown.
    Audit Status: Primary Dashboard Visualization.
    """
    setup_matplotlib_style()

    top_parties = ["BJP", "INC", "SP", "TMC", "DMK"]
    from src.analysis.party.party import retention_statistics
    retention_df = retention_statistics(df)

    fig, ax = plt.subplots(figsize=(10, 6))

    retention_df.plot(kind="barh", stacked=True, color=["#2ca02c", "#d62728"], ax=ax, width=0.55, edgecolor="white")

    ax.invert_yaxis()
    ax.set_title("Incumbent Party Seat Retention vs Seat Loss Breakdown")
    fig.suptitle("Evaluating Core Stronghold Defensive Stability Across Elections", y=0.98, fontsize=12, style="italic")
    ax.set_xlabel("Number of Constituency Transitions")
    ax.set_ylabel("Incumbent Party")
    ax.legend(title="Seat Status", loc="lower right")

    for i, (retained, lost) in enumerate(zip(retention_df["Retained Seats"], retention_df["Lost Seats"])):
        total = retained + lost
        pct_retained = (retained / total) * 100 if total > 0 else 0
        ax.text(total + 2, i, f"{retained}/{total} ({pct_retained:.1f}%)", va="center", fontweight="bold", fontsize=9)

    insight = "TMC & DMK maintain high stronghold retention rates (>75%)."
    add_chart_footer(fig, "Constituency Transition Master Dataset", insight)

    if output_dir is not None:
        out_path = output_dir / "fig_07_party_retention_loss.png"
        save_figure(fig, out_path)
        return out_path
    return fig
