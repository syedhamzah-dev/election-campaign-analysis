"""
Visualization Facade Module for Election Campaign Analysis (2004-2024).

Re-exports all utilities and plotting functions from the modular `src.visualizations` package.
Ensures 100% backward compatibility for legacy imports across all scripts and dashboard pages.
"""

import logging
import sys
from pathlib import Path
from typing import List

base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from src.visualizations import (
    COALITION_COLORS,
    PARTY_COLORS,
    add_chart_footer,
    find_constituency_col,
    find_party_col,
    find_vote_col,
    get_party_color,
    plot_coalition_trajectory,
    plot_evm_postal_by_party,
    plot_evm_vs_postal_scatter,
    plot_extreme_margins,
    plot_margins_hist,
    plot_party_retention_loss,
    plot_postal_vote_share,
    plot_reserved_category_wins,
    plot_seats_by_party,
    plot_state_margin_distribution,
    plot_state_volatility_ranking,
    plot_turnout_top20,
    plot_vote_seat_conversion,
    plot_votes_by_party,
    save_figure,
    setup_matplotlib_style,
)

logger = logging.getLogger(__name__)


def generate_all_visualizations(processed_dir: Path, output_dir: Path) -> List[Path]:
    """
    Execute all approved visualization blueprint functions and save figures to output_dir.

    Args:
        processed_dir (Path): Data directory containing processed master files.
        output_dir (Path): Figures destination directory.

    Returns:
        List[Path]: List of saved figure paths.
    """
    logger.info("Executing Visualization Blueprint Engine via facade...")
    output_dir.mkdir(parents=True, exist_ok=True)

    import pandas as pd
    c_df = pd.read_csv(processed_dir / "constituency_engineered.csv")
    p_df = pd.read_csv(processed_dir / "party_summary_engineered.csv")
    s_df = pd.read_csv(processed_dir / "state_summary_engineered.csv")

    # Load 2024 raw file if available for specialized plots
    raw_2024_path = processed_dir.parent / "raw" / "election_results_2024.csv"
    if raw_2024_path.exists():
        e24_df = pd.read_csv(raw_2024_path, na_values=["-"])
        e24_df.columns = [c.strip() for c in e24_df.columns]
        for col in ["EVM Votes", "Postal Votes", "Total Votes"]:
            if col in e24_df.columns:
                e24_df[col] = pd.to_numeric(e24_df[col], errors="coerce")
    else:
        e24_df = c_df

    generated_paths = [
        plot_coalition_trajectory(c_df, output_dir),
        plot_vote_seat_conversion(p_df, output_dir),
        plot_state_volatility_ranking(s_df, output_dir),
        plot_state_margin_distribution(c_df, output_dir),
        plot_reserved_category_wins(c_df, output_dir),
        plot_extreme_margins(c_df, output_dir),
        plot_party_retention_loss(c_df, output_dir),
        plot_seats_by_party(e24_df, output_dir),
        plot_votes_by_party(e24_df, output_dir),
        plot_postal_vote_share(e24_df, output_dir),
        plot_turnout_top20(e24_df, output_dir),
        plot_margins_hist(e24_df, output_dir),
        plot_evm_vs_postal_scatter(e24_df, output_dir),
    ]

    logger.info(f"All {len(generated_paths)} approved figures generated successfully.")
    return generated_paths


if __name__ == "__main__":
    generate_all_visualizations(
        processed_dir=base_dir / "data" / "processed",
        output_dir=base_dir / "outputs" / "figures"
    )
