"""Components package for NFL RAI Dashboard."""

from .themes import COLORS, apply_theme, get_plotly_layout
from .data_loader import (
    load_rai_results,
    load_player_aggregates,
    load_supplementary_data,
    get_summary_stats,
    get_top_performers,
    get_play_data,
)

__all__ = [
    'COLORS',
    'apply_theme',
    'get_plotly_layout',
    'load_rai_results',
    'load_player_aggregates',
    'load_supplementary_data',
    'get_summary_stats',
    'get_top_performers',
    'get_play_data',
]
