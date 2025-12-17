"""
🏃 Player Explorer
Deep-dive into individual player RAI metrics with comparisons
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.themes import apply_theme, COLORS, get_plotly_layout
from components.data_loader import (
    load_rai_results,
    get_player_stats,
    get_top_performers,
)
from components.charts import create_radar_chart

apply_theme()

st.markdown("""
<div style="margin-bottom: 24px;">
    <h1 style="font-size: 2rem; font-weight: 700; margin: 0;">🏃 Player Explorer</h1>
    <p style="color: #9CA3AF; margin: 8px 0 0 0;">Individual player analysis and comparisons</p>
</div>
""", unsafe_allow_html=True)

# Load data
with st.spinner("Loading player data..."):
    rai_df = load_rai_results()

if rai_df is not None and not rai_df.empty:
    # Sidebar filters
    st.sidebar.markdown("### 🔍 Player Selection")
    
    # Get unique players
    players = sorted(rai_df['nfl_id'].unique().tolist())
    
    # Player selection
    selected_player = st.sidebar.selectbox(
        "Select Player (NFL ID)",
        players,
        index=0,
        key="player_select"
    )
    
    # Optional comparison player
    enable_comparison = st.sidebar.checkbox("Compare with another player", value=False)
    comparison_player = None
    if enable_comparison:
        comparison_player = st.sidebar.selectbox(
            "Compare with",
            [p for p in players if p != selected_player],
            index=0,
            key="comparison_select"
        )
    
    # Role filter
    role_filter = st.sidebar.selectbox(
        "Filter by Role",
        ["All", "Targeted Receiver", "Defensive Coverage"],
        index=0
    )
    
    # Get player data
    player_df = rai_df[rai_df['nfl_id'] == selected_player]
    player_role = player_df['player_role'].mode().iloc[0] if not player_df.empty else "Unknown"
    
    # Player Header
    st.markdown(f"""
    <div class="glass-card" style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 24px;">
            <div style="background: {'#3B82F6' if 'Receiver' in player_role else '#EF4444'}; 
                        width: 80px; height: 80px; border-radius: 50%; 
                        display: flex; align-items: center; justify-content: center;
                        font-size: 2rem;">
                {'🏃' if 'Receiver' in player_role else '🛡️'}
            </div>
            <div>
                <h2 style="margin: 0; font-size: 1.75rem;">Player #{selected_player}</h2>
                <p style="margin: 4px 0 0 0; color: #9CA3AF;">{player_role}</p>
                <p style="margin: 4px 0 0 0; color: #FFB81C;">{len(player_df)} plays analyzed</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats row
    if not player_df.empty:
        st.markdown("### 📊 Performance Summary")
        
        avg_rai = player_df['rai'].mean()
        avg_rtd = player_df['rtd'].mean()
        avg_te = player_df['te'].mean()
        avg_bpq = player_df['bpq'].mean()
        avg_cms = player_df['cms'].mean()
        
        # Calculate percentiles relative to all players
        all_avg_rai = rai_df.groupby('nfl_id')['rai'].mean()
        percentile = (all_avg_rai < avg_rai).mean() * 100
        
        # Row 1: Main metrics (3 columns)
        row1 = st.columns(3)
        with row1[0]:
            st.metric("📊 Avg RAI", f"{avg_rai:.3f}", 
                     delta=f"Top {100-percentile:.0f}%", 
                     delta_color="normal")
        with row1[1]:
            st.metric("⚡ Avg Reaction Time", f"{avg_rtd:.1f} frames")
        with row1[2]:
            st.metric("🎯 Trajectory Efficiency", f"{avg_te:.1%}")
        
        # Row 2: Component scores (3 columns)
        row2 = st.columns(3)
        with row2[0]:
            st.metric("💥 Break Point Quality", f"{avg_bpq:.3f}")
        with row2[1]:
            st.metric("🛡️ Coverage Maintenance", f"{avg_cms:.3f}")
        with row2[2]:
            # Show SD if available
            if 'sd' in player_df.columns:
                avg_sd = player_df['sd'].mean()
                st.metric("📐 Separation Differential", f"{avg_sd:.3f}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Radar chart comparison
        col1, col2 = st.columns([1.2, 1])
        
        with col1:
            st.markdown("### 🎯 Component Radar")
            
            player_data = {
                'rtd': avg_rtd,
                'te': avg_te,
                'bpq': avg_bpq,
                'cms': avg_cms,
                'sd': player_df['sd'].mean() if 'sd' in player_df.columns else 0,
            }
            
            # Get comparison data
            comparison_data = None
            comparison_name = "League Average"
            
            if enable_comparison and comparison_player:
                comp_df = rai_df[rai_df['nfl_id'] == comparison_player]
                if not comp_df.empty:
                    comparison_data = {
                        'rtd': comp_df['rtd'].mean(),
                        'te': comp_df['te'].mean(),
                        'bpq': comp_df['bpq'].mean(),
                        'cms': comp_df['cms'].mean(),
                        'sd': comp_df['sd'].mean() if 'sd' in comp_df.columns else 0,
                    }
                    comparison_name = f"Player #{comparison_player}"
            else:
                # Use league average
                comparison_data = {
                    'rtd': rai_df['rtd'].mean(),
                    'te': rai_df['te'].mean(),
                    'bpq': rai_df['bpq'].mean(),
                    'cms': rai_df['cms'].mean(),
                    'sd': rai_df['sd'].mean() if 'sd' in rai_df.columns else 0,
                }
            
            fig_radar = create_radar_chart(
                player_data, 
                comparison_data,
                player_name=f"Player #{selected_player}",
                comparison_name=comparison_name
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 RAI Over Plays")
            
            # Time series of RAI for this player
            layout = get_plotly_layout()
            
            play_history = player_df.reset_index(drop=True)
            play_history['play_num'] = range(1, len(play_history) + 1)
            
            fig_history = go.Figure()
            fig_history.add_trace(go.Scatter(
                x=play_history['play_num'],
                y=play_history['rai'],
                mode='lines+markers',
                line=dict(color=COLORS['primary'], width=2),
                marker=dict(size=6, color=COLORS['primary']),
                fill='tozeroy',
                fillcolor='rgba(255, 184, 28, 0.1)',
                name='RAI',
            ))
            
            # Add average line
            fig_history.add_hline(
                y=avg_rai, 
                line_dash="dash", 
                line_color=COLORS['text_muted'],
                annotation_text=f"Avg: {avg_rai:.3f}",
            )
            
            fig_history.update_layout(
                **layout,
                title="",
                xaxis_title="Play Number",
                yaxis_title="RAI Score",
                height=400,
                showlegend=False,
            )
            st.plotly_chart(fig_history, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Play-by-play table
        st.markdown("### 📋 Play-by-Play Breakdown")
        
        # Prepare display columns
        display_cols = ['game_id', 'play_id', 'rai', 'rtd', 'te', 'bpq', 'cms']
        available_cols = [c for c in display_cols if c in player_df.columns]
        
        display_df = player_df[available_cols].copy()
        display_df = display_df.round(3)
        display_df = display_df.sort_values('rai', ascending=False)
        
        # Use st.dataframe with column config
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            column_config={
                "game_id": st.column_config.NumberColumn("Game ID", format="%d"),
                "play_id": st.column_config.NumberColumn("Play ID", format="%d"),
                "rai": st.column_config.ProgressColumn("RAI", min_value=-1, max_value=2),
                "rtd": st.column_config.NumberColumn("RTD", format="%.1f"),
                "te": st.column_config.ProgressColumn("TE", min_value=0, max_value=1),
                "bpq": st.column_config.ProgressColumn("BPQ", min_value=0, max_value=1),
                "cms": st.column_config.ProgressColumn("CMS", min_value=0, max_value=1),
            },
            hide_index=True,
        )
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Player Data",
            data=csv,
            file_name=f"player_{selected_player}_rai.csv",
            mime="text/csv",
        )

else:
    st.warning("No player data available. Please run the RAI analysis first.")
