"""
🏈 Play Analysis
3D interactive field visualization with player trajectories
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.themes import apply_theme, COLORS, get_plotly_layout
from components.data_loader import (
    load_rai_results,
    get_unique_games,
    get_plays_for_game,
    get_play_data,
    load_supplementary_data,
)
from components.field_3d import create_3d_field

apply_theme()

st.markdown("""
<div style="margin-bottom: 24px;">
    <h1 style="font-size: 2rem; font-weight: 700; margin: 0;">🏈 Play Analysis</h1>
    <p style="color: #9CA3AF; margin: 8px 0 0 0;">3D interactive field visualization with RAI breakdown</p>
</div>
""", unsafe_allow_html=True)

# Load data
rai_df = load_rai_results()
supp_df = load_supplementary_data()

if rai_df is not None and not rai_df.empty:
    # Sidebar controls
    st.sidebar.markdown("### 🎮 Play Controls")
    
    # Game selection
    games = get_unique_games()
    selected_game = st.sidebar.selectbox(
        "Select Game",
        games,
        index=0 if games else None,
        format_func=lambda x: f"Game {x}"
    )
    
    # Play selection
    if selected_game:
        plays = get_plays_for_game(selected_game)
        selected_play = st.sidebar.selectbox(
            "Select Play",
            plays,
            index=0 if plays else None,
            format_func=lambda x: f"Play {x}"
        )
    else:
        selected_play = None
    
    st.sidebar.markdown("---")
    
    # Camera controls
    st.sidebar.markdown("### 📷 Camera View")
    camera_preset = st.sidebar.radio(
        "Angle",
        ["Broadcast", "Endzone", "Overhead", "Sideline"],
        index=0,
        horizontal=True
    )
    
    # Display options
    st.sidebar.markdown("### ⚙️ Display Options")
    show_yard_lines = st.sidebar.checkbox("Show Yard Lines", value=True)
    show_rai_colors = st.sidebar.checkbox("Color by RAI Score", value=True)
    
    # Main content
    if selected_game and selected_play:
        # Get play data
        play_data = get_play_data(selected_game, selected_play)
        
        # Get play description from supplementary data
        play_desc = ""
        if supp_df is not None and not supp_df.empty:
            play_info = supp_df[(supp_df['game_id'] == selected_game) & 
                                (supp_df['play_id'] == selected_play)]
            if not play_info.empty:
                play_desc = play_info.iloc[0].get('playDescription', '')
        
        # Play info header
        st.markdown(f"""
        <div class="glass-card" style="margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; color: #FFB81C;">Game {selected_game} - Play {selected_play}</h3>
                    <p style="margin: 8px 0 0 0; color: #9CA3AF; max-width: 600px;">{play_desc[:200] if play_desc else 'No description available'}{'...' if len(play_desc) > 200 else ''}</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.5rem; color: #FFB81C;">{len(play_data)} players</div>
                    <div style="color: #9CA3AF; font-size: 0.875rem;">in play</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 3D Field Visualization
        st.markdown("### 🌐 3D Field View")
        st.markdown("*Drag to rotate, scroll to zoom, double-click to reset*")
        
        # Create sample player positions for visualization
        # In production, this would come from tracking data
        if not play_data.empty:
            # Create synthetic positions based on play data
            np.random.seed(int(selected_play))
            
            player_positions = []
            for idx, row in play_data.iterrows():
                # Generate semi-random positions on field
                if 'Receiver' in row.get('player_role', ''):
                    x = 50 + np.random.randn() * 15
                    y = 26.65 + np.random.randn() * 10
                else:
                    x = 55 + np.random.randn() * 10
                    y = 26.65 + np.random.randn() * 12
                
                player_positions.append({
                    'nfl_id': row['nfl_id'],
                    'player_role': row['player_role'],
                    'x': x,
                    'y': y,
                    'rai': row['rai'],
                })
            
            positions_df = pd.DataFrame(player_positions)
            
            # Create 3D field
            fig_field = create_3d_field(
                players_df=positions_df,
                ball_position=(60, 26.65),
                camera_preset=camera_preset.lower(),
                show_yard_lines=show_yard_lines,
            )
            
            st.plotly_chart(fig_field, use_container_width=True, key="play_3d_field")
        else:
            st.info("No tracking data available for this play")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # RAI Component Breakdown for this play
        st.markdown("### 📊 Player RAI Breakdown")
        
        if not play_data.empty:
            # Split by role
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="glass-card" style="border-left: 4px solid #3B82F6;">
                    <h4 style="color: #3B82F6; margin: 0 0 16px 0;">🏃 Receivers</h4>
                </div>
                """, unsafe_allow_html=True)
                
                receivers = play_data[play_data['player_role'].str.contains('Receiver', na=False)]
                if not receivers.empty:
                    for _, row in receivers.iterrows():
                        rai_color = COLORS['success'] if row['rai'] > 0.5 else (
                            COLORS['warning'] if row['rai'] > 0 else COLORS['error']
                        )
                        st.markdown(f"""
                        <div style="background: rgba(59, 130, 246, 0.1); padding: 12px; 
                                    border-radius: 8px; margin: 8px 0;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>Player #{int(row['nfl_id'])}</span>
                                <span style="color: {rai_color}; font-weight: 600;">
                                    RAI: {row['rai']:.3f}
                                </span>
                            </div>
                            <div style="display: flex; gap: 16px; margin-top: 8px; 
                                        font-size: 0.8rem; color: #9CA3AF;">
                                <span>RTD: {row['rtd']:.0f}</span>
                                <span>TE: {row['te']:.2f}</span>
                                <span>BPQ: {row['bpq']:.2f}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No receivers in this play")
            
            with col2:
                st.markdown("""
                <div class="glass-card" style="border-left: 4px solid #EF4444;">
                    <h4 style="color: #EF4444; margin: 0 0 16px 0;">🛡️ Defenders</h4>
                </div>
                """, unsafe_allow_html=True)
                
                defenders = play_data[play_data['player_role'].str.contains('Defensive', na=False)]
                if not defenders.empty:
                    for _, row in defenders.iterrows():
                        rai_color = COLORS['success'] if row['rai'] > 0.5 else (
                            COLORS['warning'] if row['rai'] > 0 else COLORS['error']
                        )
                        st.markdown(f"""
                        <div style="background: rgba(239, 68, 68, 0.1); padding: 12px; 
                                    border-radius: 8px; margin: 8px 0;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>Player #{int(row['nfl_id'])}</span>
                                <span style="color: {rai_color}; font-weight: 600;">
                                    RAI: {row['rai']:.3f}
                                </span>
                            </div>
                            <div style="display: flex; gap: 16px; margin-top: 8px; 
                                        font-size: 0.8rem; color: #9CA3AF;">
                                <span>RTD: {row['rtd']:.0f}</span>
                                <span>TE: {row['te']:.2f}</span>
                                <span>CMS: {row['cms']:.2f}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No defenders in this play")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Summary bar chart
            st.markdown("### 📊 RAI Comparison")
            
            layout = get_plotly_layout()
            
            fig_bar = go.Figure()
            
            # Sort by RAI
            sorted_data = play_data.sort_values('rai', ascending=True)
            
            colors = [COLORS['receiver'] if 'Receiver' in r else COLORS['defender'] 
                     for r in sorted_data['player_role']]
            
            fig_bar.add_trace(go.Bar(
                y=[f"Player {int(x)}" for x in sorted_data['nfl_id']],
                x=sorted_data['rai'],
                orientation='h',
                marker=dict(color=colors),
                text=[f"{x:.3f}" for x in sorted_data['rai']],
                textposition='outside',
            ))
            
            fig_bar.add_vline(x=0, line_dash="dash", line_color=COLORS['text_muted'])
            
            fig_bar.update_layout(
                **layout,
                title="",
                xaxis_title="RAI Score",
                yaxis_title="",
                height=max(300, len(play_data) * 40),
                showlegend=False,
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
    
    else:
        # No play selected - show summary
        st.info("👈 Select a game and play from the sidebar to view the analysis")
        
        # Show some aggregate stats
        st.markdown("### 📈 Overall Statistics")
        
        avg_players_per_play = rai_df.groupby(['game_id', 'play_id']).size().mean()
        total_games = rai_df['game_id'].nunique()
        
        stats_cols = st.columns(3)
        with stats_cols[0]:
            st.metric("Total Games", f"{total_games:,}")
        with stats_cols[1]:
            st.metric("Total Plays", f"{len(games) if games else 0:,}")
        with stats_cols[2]:
            st.metric("Avg Players/Play", f"{avg_players_per_play:.1f}")

else:
    st.warning("No RAI data available. Please run the analysis first.")
