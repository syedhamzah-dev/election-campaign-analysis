"""
Visualizations Package for Election Campaign Analysis (2004-2024).
Modular submodules for Party, State, Constituency, and Statistical plotting engines.
"""

from src.visualizations.base import (
    COALITION_COLORS,
    PARTY_COLORS,
    add_chart_footer,
    find_constituency_col,
    find_party_col,
    find_vote_col,
    get_party_color,
    save_figure,
    setup_matplotlib_style,
)
from src.visualizations.constituency import (
    plot_extreme_margins,
    plot_reserved_category_wins,
    plot_turnout_top20,
)
from src.visualizations.party import (
    plot_evm_postal_by_party,
    plot_party_retention_loss,
    plot_postal_vote_share,
    plot_seats_by_party,
    plot_vote_seat_conversion,
    plot_votes_by_party,
)
from src.visualizations.state import (
    plot_state_margin_distribution,
    plot_state_volatility_ranking,
)
from src.visualizations.statistical import (
    plot_coalition_trajectory,
    plot_evm_vs_postal_scatter,
    plot_margins_hist,
)

__all__ = [
    "PARTY_COLORS",
    "COALITION_COLORS",
    "get_party_color",
    "setup_matplotlib_style",
    "add_chart_footer",
    "save_figure",
    "find_party_col",
    "find_vote_col",
    "find_constituency_col",
    "plot_seats_by_party",
    "plot_votes_by_party",
    "plot_postal_vote_share",
    "plot_evm_postal_by_party",
    "plot_vote_seat_conversion",
    "plot_party_retention_loss",
    "plot_state_volatility_ranking",
    "plot_state_margin_distribution",
    "plot_turnout_top20",
    "plot_reserved_category_wins",
    "plot_extreme_margins",
    "plot_coalition_trajectory",
    "plot_margins_hist",
    "plot_evm_vs_postal_scatter",
]
