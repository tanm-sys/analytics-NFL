"""
🏆 Leaderboards
Top performers, rankings, and exportable data
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.themes import apply_theme, COLORS, get_plotly_layout
from components.data_loader import (
    load_rai_results,
    get_top_performers,
)

apply_theme()

st.markdown("""
<div style="margin-bottom: 24px;">
    <h1 style="font-size: 2rem; font-weight: 700; margin: 0;">🏆 Leaderboards</h1>
    <p style="color: #9CA3AF; margin: 8px 0 0 0;">Top performers and exportable rankings</p>
</div>
""", unsafe_allow_html=True)

# Load data
rai_df = load_rai_results()

if rai_df is not None and not rai_df.empty:
    # Filters
    st.sidebar.markdown("### 🔍 Filters")
    
    role_filter = st.sidebar.selectbox(
        "Player Role",
        ["All Players", "Targeted Receiver", "Defensive Coverage"],
        index=0
    )
    
    min_plays = st.sidebar.slider(
        "Minimum Plays",
        min_value=1,
        max_value=50,
        value=5,
        help="Filter players with at least this many plays"
    )
    
    top_n = st.sidebar.slider(
        "Top N Players",
        min_value=10,
        max_value=100,
        value=25,
    )
    
    # Get filtered top performers
    role = None if role_filter == "All Players" else role_filter
    top_players = get_top_performers(n=top_n, role=role)
    top_players = top_players[top_players['play_count'] >= min_plays]
    
    # Trophy podium for top 3
    st.markdown("### 🥇 Top Performers")
    
    if len(top_players) >= 3:
        podium_cols = st.columns([1, 1.2, 1])
        
        # Second place
        with podium_cols[0]:
            player = top_players.iloc[1]
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; margin-top: 40px;">
                <div style="font-size: 3rem;">🥈</div>
                <h3 style="color: #C0C0C0; margin: 8px 0;">#{int(player['nfl_id'])}</h3>
                <div class="metric-value" style="font-size: 1.5rem;">{player['avg_rai']:.3f}</div>
                <div style="color: #9CA3AF; font-size: 0.8rem;">{player['player_role']}</div>
                <div style="color: #9CA3AF; font-size: 0.75rem; margin-top: 8px;">
                    {int(player['play_count'])} plays
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # First place
        with podium_cols[1]:
            player = top_players.iloc[0]
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; border: 2px solid #FFB81C;">
                <div style="font-size: 4rem;">🥇</div>
                <h2 style="color: #FFB81C; margin: 8px 0;">#{int(player['nfl_id'])}</h2>
                <div class="metric-value">{player['avg_rai']:.3f}</div>
                <div style="color: #9CA3AF;">{player['player_role']}</div>
                <div style="color: #9CA3AF; font-size: 0.875rem; margin-top: 8px;">
                    {int(player['play_count'])} plays
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Third place
        with podium_cols[2]:
            player = top_players.iloc[2]
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; margin-top: 60px;">
                <div style="font-size: 2.5rem;">🥉</div>
                <h3 style="color: #CD7F32; margin: 8px 0;">#{int(player['nfl_id'])}</h3>
                <div class="metric-value" style="font-size: 1.25rem;">{player['avg_rai']:.3f}</div>
                <div style="color: #9CA3AF; font-size: 0.75rem;">{player['player_role']}</div>
                <div style="color: #9CA3AF; font-size: 0.7rem; margin-top: 8px;">
                    {int(player['play_count'])} plays
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Full leaderboard
    st.markdown("### 📋 Complete Rankings")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["All Players", "Receivers Only", "Defenders Only"])
    
    with tab1:
        display_df = top_players.copy()
        display_df['Rank'] = range(1, len(display_df) + 1)
        display_df = display_df[['Rank', 'nfl_id', 'avg_rai', 'std_rai', 'play_count', 'avg_rtd', 'avg_te', 'player_role']]
        display_df.columns = ['Rank', 'NFL ID', 'Avg RAI', 'Std RAI', 'Plays', 'Avg RTD', 'Avg TE', 'Role']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=500,
            column_config={
                "Rank": st.column_config.NumberColumn("🏆 Rank", format="%d"),
                "NFL ID": st.column_config.NumberColumn("Player", format="%d"),
                "Avg RAI": st.column_config.ProgressColumn(
                    "Avg RAI", 
                    min_value=0, 
                    max_value=1.5,
                    format="%.3f"
                ),
                "Std RAI": st.column_config.NumberColumn("Std", format="%.3f"),
                "Plays": st.column_config.NumberColumn("Plays", format="%d"),
                "Avg RTD": st.column_config.NumberColumn("RTD", format="%.1f"),
                "Avg TE": st.column_config.ProgressColumn("TE", min_value=0, max_value=1, format="%.2f"),
                "Role": st.column_config.TextColumn("Role"),
            },
            hide_index=True,
        )
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Leaderboard CSV",
            data=csv,
            file_name="rai_leaderboard.csv",
            mime="text/csv",
        )
    
    with tab2:
        receivers = get_top_performers(n=top_n, role="Targeted Receiver")
        receivers = receivers[receivers['play_count'] >= min_plays]
        
        if not receivers.empty:
            receivers['Rank'] = range(1, len(receivers) + 1)
            receivers = receivers[['Rank', 'nfl_id', 'avg_rai', 'play_count', 'avg_rtd', 'avg_te']]
            receivers.columns = ['Rank', 'NFL ID', 'Avg RAI', 'Plays', 'Avg RTD', 'Avg TE']
            
            st.dataframe(
                receivers,
                use_container_width=True,
                height=400,
                column_config={
                    "Avg RAI": st.column_config.ProgressColumn(
                        "Avg RAI", min_value=0, max_value=1.5, format="%.3f"
                    ),
                },
                hide_index=True,
            )
        else:
            st.info("No receivers meet the filter criteria")
    
    with tab3:
        defenders = get_top_performers(n=top_n, role="Defensive Coverage")
        defenders = defenders[defenders['play_count'] >= min_plays]
        
        if not defenders.empty:
            defenders['Rank'] = range(1, len(defenders) + 1)
            defenders = defenders[['Rank', 'nfl_id', 'avg_rai', 'play_count', 'avg_rtd', 'avg_te']]
            defenders.columns = ['Rank', 'NFL ID', 'Avg RAI', 'Plays', 'Avg RTD', 'Avg TE']
            
            st.dataframe(
                defenders,
                use_container_width=True,
                height=400,
                column_config={
                    "Avg RAI": st.column_config.ProgressColumn(
                        "Avg RAI", min_value=0, max_value=1.5, format="%.3f"
                    ),
                },
                hide_index=True,
            )
        else:
            st.info("No defenders meet the filter criteria")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Visualization
    st.markdown("### 📊 RAI Distribution of Top Performers")
    
    layout = get_plotly_layout()
    
    fig = go.Figure()
    
    # Add bar chart with gradient
    fig.add_trace(go.Bar(
        x=[f"#{int(x)}" for x in top_players['nfl_id'].head(20)],
        y=top_players['avg_rai'].head(20),
        marker=dict(
            color=top_players['avg_rai'].head(20),
            colorscale=[
                [0, COLORS['warning']],
                [0.5, COLORS['primary']],
                [1, COLORS['success']],
            ],
        ),
        text=[f"{x:.3f}" for x in top_players['avg_rai'].head(20)],
        textposition='outside',
        error_y=dict(
            type='data',
            array=top_players['std_rai'].head(20),
            visible=True,
            color=COLORS['text_muted'],
        ),
    ))
    
    fig.update_layout(
        **layout,
        title="Top 20 Players by Average RAI",
        xaxis_title="Player ID",
        yaxis_title="Average RAI",
        height=450,
        showlegend=False,
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary stats
    st.markdown("### 📈 Summary Statistics")
    
    summary_cols = st.columns(4)
    
    with summary_cols[0]:
        st.metric("Highest RAI", f"{top_players['avg_rai'].max():.3f}")
    
    with summary_cols[1]:
        st.metric("Median RAI", f"{top_players['avg_rai'].median():.3f}")
    
    with summary_cols[2]:
        st.metric("Players Ranked", f"{len(top_players)}")
    
    with summary_cols[3]:
        total_plays = top_players['play_count'].sum()
        st.metric("Total Plays", f"{int(total_plays):,}")

else:
    st.warning("No data available for leaderboards.")
