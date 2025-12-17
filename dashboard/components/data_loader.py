"""
NFL RAI Dashboard - Data Loader
Cached data loading for optimal performance
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any

# Base path for data files
DATA_DIR = Path(__file__).parent.parent.parent / "outputs" / "reports"
SUPPLEMENTARY_PATH = Path(__file__).parent.parent.parent / "supplementary_data.csv"


@st.cache_data(ttl=3600, show_spinner=False)
def load_rai_results() -> pd.DataFrame:
    """Load detailed RAI results for all plays."""
    path = DATA_DIR / "rai_results.csv"
    if not path.exists():
        st.error(f"RAI results not found at {path}")
        return pd.DataFrame()
    
    df = pd.read_csv(path)
    # Ensure numeric columns
    numeric_cols = ['rtd', 'te', 'bpq', 'cms', 'sd', 'rai']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def load_player_aggregates() -> pd.DataFrame:
    """Load aggregated player RAI statistics."""
    path = DATA_DIR / "player_rai_aggregates.csv"
    if not path.exists():
        st.error(f"Player aggregates not found at {path}")
        return pd.DataFrame()
    
    df = pd.read_csv(path)
    
    # Handle multi-level columns if present
    if df.columns[0] == 'Unnamed: 0':
        df = df.rename(columns={'Unnamed: 0': 'nfl_id'})
    
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def load_supplementary_data() -> pd.DataFrame:
    """Load supplementary game/play data."""
    if not SUPPLEMENTARY_PATH.exists():
        st.warning(f"Supplementary data not found at {SUPPLEMENTARY_PATH}")
        return pd.DataFrame()
    
    return pd.read_csv(SUPPLEMENTARY_PATH)


@st.cache_data(ttl=3600, show_spinner=False)
def get_unique_games() -> list:
    """Get list of unique game IDs."""
    df = load_rai_results()
    if 'game_id' in df.columns:
        return sorted(df['game_id'].unique().tolist())
    return []


@st.cache_data(ttl=3600, show_spinner=False)
def get_plays_for_game(game_id: int) -> list:
    """Get list of play IDs for a specific game."""
    df = load_rai_results()
    if 'game_id' in df.columns and 'play_id' in df.columns:
        plays = df[df['game_id'] == game_id]['play_id'].unique().tolist()
        return sorted(plays)
    return []


@st.cache_data(ttl=3600, show_spinner=False)
def get_play_data(game_id: int, play_id: int) -> pd.DataFrame:
    """Get RAI data for a specific play."""
    df = load_rai_results()
    return df[(df['game_id'] == game_id) & (df['play_id'] == play_id)]


@st.cache_data(ttl=3600, show_spinner=False)
def get_player_stats(nfl_id: int) -> Dict[str, Any]:
    """Get aggregated stats for a specific player."""
    df = load_rai_results()
    player_df = df[df['nfl_id'] == nfl_id]
    
    if player_df.empty:
        return {}
    
    return {
        'nfl_id': nfl_id,
        'total_plays': len(player_df),
        'avg_rai': player_df['rai'].mean(),
        'avg_rtd': player_df['rtd'].mean(),
        'avg_te': player_df['te'].mean(),
        'avg_bpq': player_df['bpq'].mean(),
        'avg_cms': player_df['cms'].mean(),
        'primary_role': player_df['player_role'].mode().iloc[0] if not player_df['player_role'].mode().empty else 'Unknown',
    }


@st.cache_data(ttl=3600, show_spinner=False)
def get_top_performers(n: int = 25, role: Optional[str] = None) -> pd.DataFrame:
    """Get top N performers by average RAI."""
    df = load_rai_results()
    
    if role:
        df = df[df['player_role'] == role]
    
    # Aggregate by player
    agg = df.groupby('nfl_id').agg({
        'rai': ['mean', 'std', 'count'],
        'rtd': 'mean',
        'te': 'mean',
        'player_role': 'first'
    }).reset_index()
    
    agg.columns = ['nfl_id', 'avg_rai', 'std_rai', 'play_count', 'avg_rtd', 'avg_te', 'player_role']
    
    # Filter to players with sufficient plays
    agg = agg[agg['play_count'] >= 5]
    
    return agg.nlargest(n, 'avg_rai')


@st.cache_data(ttl=3600, show_spinner=False)
def get_rai_distribution_data() -> pd.DataFrame:
    """Get RAI distribution by player role."""
    df = load_rai_results()
    return df[['rai', 'player_role', 'nfl_id']].dropna()


@st.cache_data(ttl=3600, show_spinner=False)
def get_coverage_analysis() -> pd.DataFrame:
    """Get RAI metrics merged with coverage data."""
    rai_df = load_rai_results()
    supp_df = load_supplementary_data()
    
    if supp_df.empty or 'game_id' not in supp_df.columns:
        return rai_df
    
    # Check which coverage columns exist
    coverage_cols = []
    for col in ['pff_passCoverage', 'pff_passCoverageType']:
        if col in supp_df.columns:
            coverage_cols.append(col)
    
    if not coverage_cols:
        # No coverage columns available, return RAI data only
        return rai_df
    
    # Merge with supplementary for coverage info
    merge_cols = ['game_id', 'play_id'] + coverage_cols
    merged = rai_df.merge(
        supp_df[merge_cols].drop_duplicates(),
        on=['game_id', 'play_id'],
        how='left'
    )
    return merged


def get_summary_stats() -> Dict[str, Any]:
    """Get overall summary statistics."""
    df = load_rai_results()
    
    return {
        'total_plays': df[['game_id', 'play_id']].drop_duplicates().shape[0],
        'total_players': df['nfl_id'].nunique(),
        'avg_rai': df['rai'].mean(),
        'avg_rtd': df['rtd'].mean(),
        'avg_te': df['te'].mean(),
        'receivers_analyzed': df[df['player_role'] == 'Targeted Receiver']['nfl_id'].nunique(),
        'defenders_analyzed': df[df['player_role'] == 'Defensive Coverage']['nfl_id'].nunique(),
    }
