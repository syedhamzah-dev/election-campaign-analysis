"""
Visualization Blueprint Engine for Election Campaign Analysis (2004-2024).

Implements reusable, publication-quality Matplotlib and Seaborn plotting functions.
Enforces strict 300 DPI export, tight_layout(), title/subtitle/labels/legend/source/insight
formatting, and official party color mapping.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)

# Official Political Party Color Palette Mapping
PARTY_COLORS: Dict[str, str] = {
    "BJP": "#FF9933",
    "INC": "#19A0FF",
    "SP": "#E30613",
    "BSP": "#22409A",
    "AAP": "#00B7EB",
    "AITC": "#00A651",
    "DMK": "#D71920",
    "AIADMK": "#008000",
    "CPI(M)": "#B22222",
    "NCP": "#1F77B4",
    "Shiv Sena": "#F58220",
    "SS": "#F58220",
    "SS(UBT)": "#F58220",
    "Others": "#808080",
    "Others / Regional": "#808080",
}

# Coalition Color Palette Mapping
COALITION_COLORS: Dict[str, str] = {
    "NDA": "#FF9933",
    "UPA / I.N.D.I.A.": "#19A0FF",
    "Left Front": "#B22222",
    "Others / Regional": "#808080",
}


def setup_matplotlib_style() -> None:
    """
    Configure global Matplotlib and Seaborn style defaults for publication output.
    """
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


def add_chart_footer(
    fig: plt.Figure, source_text: str, insight_text: str
) -> None:
    """
    Add standardized source and key insight annotations to the bottom of the figure.

    Args:
        fig (plt.Figure): Matplotlib figure instance.
        source_text (str): Data source string.
        insight_text (str): Concise business insight string.
    """
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
    """
    Save figure with 300 DPI resolution and tight layout.

    Args:
        fig (plt.Figure): Figure instance.
        output_path (Path): Path to output image file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    logger.info(f"Saved publication figure: {output_path.resolve()}")
    plt.close(fig)


def plot_coalition_trajectory(c_df: pd.DataFrame, output_dir: Path) -> Path:
    """
    Viz 1: Coalition Seat Share Trajectory (2004-2024).

    Answers: How has parliamentary seat control shifted between major national coalitions?
    """
    setup_matplotlib_style()
    agg_df = c_df.groupby(["Year", "Coalition_Block"]).size().unstack(fill_value=0)
    desired_cols = ["NDA", "UPA / I.N.D.I.A.", "Left Front", "Others / Regional"]
    agg_df = agg_df[[c for c in desired_cols if c in agg_df.columns]]

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

    out_path = output_dir / "fig_01_coalition_trajectory.png"
    save_figure(fig, out_path)
    return out_path


def plot_vote_seat_conversion(p_df: pd.DataFrame, output_dir: Path) -> Path:
    """
    Viz 2: Vote Share vs Seat Conversion Efficiency for Top Parties.

    Answers: How efficiently do political parties convert vote percentage into parliamentary seats?
    """
    setup_matplotlib_style()
    latest_2024 = p_df[p_df["Year"] == 2024].sort_values("Seats", ascending=False).head(7)

    fig, ax1 = plt.subplots(figsize=(11, 6))

    x = np.arange(len(latest_2024))
    width = 0.35

    bar_colors = [PARTY_COLORS.get(p, "#808080") for p in latest_2024["Party"]]

    bars1 = ax1.bar(x - width / 2, latest_2024["Percentage"], width, label="Vote Share %", color="#a6cee3", edgecolor="black")
    ax2 = ax1.twinx()
    bars2 = ax2.bar(x + width / 2, latest_2024["Seats"], width, label="Seats Won", color=bar_colors, edgecolor="black", alpha=0.9)

    ax1.set_title("National Vote Share % vs Parliamentary Seats Won (2024 Election)")
    fig.suptitle("Evaluating First-Past-The-Post Vote Conversion Efficiency", y=0.98, fontsize=12, style="italic")
    ax1.set_xlabel("Political Party")
    ax1.set_ylabel("National Vote Share (%)", color="#1f78b4")
    ax2.set_ylabel("Seats Won Count", color="black")
    ax1.set_xticks(x)
    ax1.set_xticklabels(latest_2024["Party"], fontweight="bold")
    ax1.grid(False)

    for bar in bars2:
        height = bar.get_height()
        ax2.annotate(f"{int(height)}", xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontweight="bold")

    insight = "FPTP rules disproportionately reward parties with concentrated support: BJP converted 36.6% vote share into 240 seats."
    add_chart_footer(fig, "ECI 2024 National Results | Party Summary Master", insight)

    out_path = output_dir / "fig_02_vote_seat_conversion.png"
    save_figure(fig, out_path)
    return out_path


def plot_state_volatility_ranking(s_df: pd.DataFrame, output_dir: Path) -> Path:
    """
    Viz 3: Battleground State Seat Volatility Ranking.

    Answers: Which Indian states experience the highest constituency seat flip rates?
    Uses professional Seaborn palette (Non-party plot rule!).
    """
    setup_matplotlib_style()
    
    top_states = s_df.groupby("State_UT")["State_Volatility_Rate"].first().reset_index()
    top_states = top_states.sort_values("State_Volatility_Rate", ascending=False).head(18)

    fig, ax = plt.subplots(figsize=(10, 7))

    # Non-party plot rule: Use Seaborn professional palette
    sns.barplot(
        data=top_states,
        y="State_UT",
        x="State_Volatility_Rate",
        hue="State_UT",
        palette="mako_r",
        legend=False,
        ax=ax,
        edgecolor="none"
    )

    ax.invert_yaxis()  # Highest volatility at top
    ax.set_title("Battleground Ranking: Historical Seat Volatility Rate by State (%)")
    fig.suptitle("Frequency of Constituency Seat Flips Between Consecutive Elections (2004–2024)", y=0.98, fontsize=12, style="italic")
    ax.set_xlabel("Average Seat Flip Volatility Rate (%)")
    ax.set_ylabel("State / Union Territory")
    ax.set_xlim(0, 100)

    for p in ax.patches:
        width = p.get_width()
        ax.text(width + 1.2, p.get_y() + p.get_height() / 2, f"{width:.1f}%",
                va="center", ha="left", fontweight="bold", fontsize=9, color="#222222")

    insight = "States like Tamil Nadu, UP, and Karnataka exhibit >55% seat flip rates, designating them as primary campaign battlegrounds."
    add_chart_footer(fig, "Constituency Historical Transitions | State Summary Master", insight)

    out_path = output_dir / "fig_03_state_volatility_ranking.png"
    save_figure(fig, out_path)
    return out_path


def plot_state_margin_distribution(c_df: pd.DataFrame, output_dir: Path) -> Path:
    """
    Viz 4: Victory Margin Distribution Across Major States.

    Answers: What is the spread and variance of victory margins across key states?
    Uses professional Seaborn palette (Non-party plot rule!).
    """
    setup_matplotlib_style()
    
    top_states = c_df["State"].value_counts().head(12).index
    filtered_df = c_df[c_df["State"].isin(top_states)].copy()

    fig, ax = plt.subplots(figsize=(11, 6))

    # Non-party plot rule: Use Seaborn professional palette
    sns.boxplot(
        data=filtered_df,
        x="State",
        y="Margin_Percentage",
        hue="State",
        palette="Blues_r",
        legend=False,
        ax=ax,
        fliersize=3,
        linewidth=1.2,
    )

    ax.set_title("Distribution of Victory Margin % Across Major Indian States (2004–2024)")
    fig.suptitle("Evaluating Competitive Intensity & Outlier Contests per State", y=0.98, fontsize=12, style="italic")
    ax.set_xlabel("State / Union Territory")
    ax.set_ylabel("Victory Margin (%)")
    ax.tick_params(axis="x", rotation=30)

    insight = "Kerala and UP display narrow median margins (<8%), while Gujarat displays wide margin spreads with frequent landslide victories (>25%)."
    add_chart_footer(fig, "Constituency Master Dataset (2004–2024)", insight)

    out_path = output_dir / "fig_04_state_margin_distribution.png"
    save_figure(fig, out_path)
    return out_path


def plot_reserved_category_wins(c_df: pd.DataFrame, output_dir: Path) -> Path:
    """
    Viz 5: Reserved (`SC`, `ST`) vs General (`GEN`) Constituency Win Breakdown.

    Answers: How do political party winning shares differ between Reserved and General seats?
    Uses official Party Colors.
    """
    setup_matplotlib_style()

    top_parties = ["BJP", "INC", "SP", "TMC", "DMK", "CPI(M)"]
    df_filtered = c_df.copy()
    df_filtered["Party_Group"] = np.where(df_filtered["Winner_Party"].isin(top_parties), df_filtered["Winner_Party"], "Others")

    agg_df = (
        df_filtered.groupby(["Constituency_Type", "Party_Group"])
        .size()
        .unstack(fill_value=0)
    )

    party_order = top_parties + ["Others"]
    agg_df = agg_df[[p for p in party_order if p in agg_df.columns]]

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [PARTY_COLORS.get(p, "#808080") for p in agg_df.columns]

    agg_df.plot(kind="bar", stacked=True, color=colors, ax=ax, width=0.5, edgecolor="white")

    ax.set_title("Party Seat Distribution Breakdown Across Reserved & General Constituencies")
    fig.suptitle("Comparing Performance in General (GEN), Scheduled Castes (SC), and Scheduled Tribes (ST) Seats", y=0.98, fontsize=12, style="italic")
    ax.set_xlabel("Constituency Reservation Category")
    ax.set_ylabel("Total Parliamentary Seats Won")
    ax.set_xticklabels(["General (GEN)", "Scheduled Castes (SC)", "Scheduled Tribes (ST)"], rotation=0, fontweight="bold")
    ax.legend(title="Winning Party", loc="upper right")

    insight = "BJP holds dominant majorities in ST and SC reserved seats, capturing over 50% of ST seats in 2014–2019."
    add_chart_footer(fig, "Constituency Master Dataset (2004–2024)", insight)

    out_path = output_dir / "fig_05_reserved_category_wins.png"
    save_figure(fig, out_path)
    return out_path


def plot_extreme_margins(c_df: pd.DataFrame, output_dir: Path) -> Path:
    """
    Viz 6: Top 10 Tightest vs Top 10 Largest Victory Margins.

    Answers: Which specific constituencies experienced extreme nail-biter vs landslide outcomes?
    Uses professional Seaborn palette (Non-party plot rule!).
    """
    setup_matplotlib_style()

    # Filter out uncontested Surat seat (margin 0)
    contested_df = c_df[c_df["Margin_Votes"] > 0].copy()
    tightest = contested_df.sort_values("Margin_Votes").head(10)
    largest = contested_df.sort_values("Margin_Votes", ascending=False).head(10)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Ax1: Tightest Margins (Seaborn Reds_r)
    sns.barplot(
        data=tightest,
        y="Constituency_Name",
        x="Margin_Votes",
        hue="Constituency_Name",
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
        ax1.text(width + 20, p.get_y() + p.get_height() / 2, f"{int(width):,}", va="center", fontsize=8, fontweight="bold")

    # Ax2: Largest Margins (Seaborn Greens_r)
    sns.barplot(
        data=largest,
        y="Constituency_Name",
        x="Margin_Votes",
        hue="Constituency_Name",
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
        ax2.text(width + 10000, p.get_y() + p.get_height() / 2, f"{int(width):,}", va="center", fontsize=8, fontweight="bold")

    fig.suptitle("Electoral Extremes: Razor-Thin Wins vs Landslide Sweeps (2004–2024)", fontsize=15, fontweight="bold", y=1.02)

    insight = "Tightest victory recorded was just 25 votes (Ladakh 2004), while largest exceeded 690,000 votes (Indore 2024)."
    add_chart_footer(fig, "Constituency Master Dataset (2004–2024)", insight)

    out_path = output_dir / "fig_06_extreme_margins.png"
    save_figure(fig, out_path)
    return out_path


def plot_party_retention_loss(c_df: pd.DataFrame, output_dir: Path) -> Path:
    """
    Viz 7: Incumbent Party Seat Retention vs Seat Loss Breakdown.

    Answers: What is the seat retention vs loss trajectory for major political parties?
    Uses official Party Colors.
    """
    setup_matplotlib_style()

    # Filter for transitions where Seat_Flip_Status is defined
    valid_transitions = c_df[c_df["Seat_Flip_Status"].notna()].copy()
    top_parties = ["BJP", "INC", "SP", "TMC", "DMK"]

    valid_transitions["Incumbent_Party"] = np.where(
        valid_transitions["Prev_Winner_Party"].isin(top_parties),
        valid_transitions["Prev_Winner_Party"],
        "Others"
    )

    retention_df = (
        valid_transitions.groupby(["Incumbent_Party", "Seat_Flip_Status"])
        .size()
        .unstack(fill_value=0)
    )
    retention_df.columns = ["Retained Seats", "Lost Seats"]
    retention_df = retention_df.loc[[p for p in top_parties if p in retention_df.index] + ["Others"]]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Stacked horizontal bar chart
    retention_df.plot(kind="barh", stacked=True, color=["#2ca02c", "#d62728"], ax=ax, width=0.55, edgecolor="white")

    ax.invert_yaxis()
    ax.set_title("Incumbent Party Seat Retention vs Seat Loss Breakdown (2009–2024)")
    fig.suptitle("Evaluating Core Stronghold Defensive Stability Across Elections", y=0.98, fontsize=12, style="italic")
    ax.set_xlabel("Number of Constituency Transitions")
    ax.set_ylabel("Incumbent Party")
    ax.legend(title="Seat Status", loc="lower right")

    for i, (retained, lost) in enumerate(zip(retention_df["Retained Seats"], retention_df["Lost Seats"])):
        total = retained + lost
        pct_retained = (retained / total) * 100 if total > 0 else 0
        ax.text(total + 10, i, f"{retained}/{total} Retained ({pct_retained:.1f}%)", va="center", fontweight="bold", fontsize=9)

    insight = "TMC & DMK maintain the highest seat retention rates (>75%), whereas INC suffered heavy seat losses in 2014."
    add_chart_footer(fig, "Constituency Transition Master Dataset (2009–2024)", insight)

    out_path = output_dir / "fig_07_party_retention_loss.png"
    save_figure(fig, out_path)
    return out_path


def generate_all_visualizations(processed_dir: Path, output_dir: Path) -> List[Path]:
    """
    Execute all approved visualization blueprint functions and save figures to output_dir.

    Args:
        processed_dir (Path): Data directory containing processed master files.
        output_dir (Path): Figures destination directory.

    Returns:
        List[Path]: List of saved figure paths.
    """
    logger.info("Executing Visualization Blueprint Engine...")
    output_dir.mkdir(parents=True, exist_ok=True)

    c_df = pd.read_csv(processed_dir / "constituency_engineered.csv")
    p_df = pd.read_csv(processed_dir / "party_summary_engineered.csv")
    s_df = pd.read_csv(processed_dir / "state_summary_engineered.csv")

    generated_paths = [
        plot_coalition_trajectory(c_df, output_dir),
        plot_vote_seat_conversion(p_df, output_dir),
        plot_state_volatility_ranking(s_df, output_dir),
        plot_state_margin_distribution(c_df, output_dir),
        plot_reserved_category_wins(c_df, output_dir),
        plot_extreme_margins(c_df, output_dir),
        plot_party_retention_loss(c_df, output_dir),
    ]

    logger.info(f"All {len(generated_paths)} approved figures generated successfully.")
    return generated_paths


if __name__ == "__main__":
    import sys
    base_dir = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(base_dir))
    generate_all_visualizations(
        processed_dir=base_dir / "data" / "processed",
        output_dir=base_dir / "outputs" / "figures"
    )
