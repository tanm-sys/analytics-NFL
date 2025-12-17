"""
📊 Overview Dashboard
KPI metrics, 3D visualizations, and RAI distribution analysis
Enhanced with more filters, insights, and statistical data
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.themes import apply_theme, COLORS, get_plotly_layout
from components.data_loader import (
    load_rai_results, 
    get_summary_stats, 
    get_top_performers,
    get_rai_distribution_data,
)
from components.charts import (
    create_rai_distribution_chart,
    create_3d_scatter,
    create_bar_chart,
)

# Apply theme
apply_theme()

st.markdown("""
<div style="margin-bottom: 24px;">
    <h1 style="font-size: 2rem; font-weight: 700; margin: 0;">📊 Overview Dashboard</h1>
    <p style="color: #9CA3AF; margin: 8px 0 0 0;">Comprehensive RAI analytics with interactive filters and insights</p>
</div>
""", unsafe_allow_html=True)

# Load data with spinner
with st.spinner("Loading analytics data..."):
    try:
        stats = get_summary_stats()
        rai_df = load_rai_results()
        data_loaded = True
    except Exception as e:
        st.error(f"Error loading data: {e}")
        data_loaded = False
        stats = {}
        rai_df = None

if data_loaded and rai_df is not None and not rai_df.empty:
    
    # ============== SIDEBAR FILTERS ==============
    st.sidebar.markdown("### 🎚️ Data Filters")
    
    # Role filter
    role_options = ["All Players"] + list(rai_df['player_role'].unique())
    selected_role = st.sidebar.selectbox("Player Role", role_options, index=0)
    
    # RTD range filter
    rtd_min, rtd_max = float(rai_df['rtd'].min()), float(rai_df['rtd'].max())
    rtd_range = st.sidebar.slider(
        "Reaction Time (RTD) Range",
        min_value=rtd_min,
        max_value=rtd_max,
        value=(rtd_min, rtd_max),
        step=0.5
    )
    
    # TE range filter
    te_min, te_max = float(rai_df['te'].min()), float(rai_df['te'].max())
    te_range = st.sidebar.slider(
        "Trajectory Efficiency (TE) Range",
        min_value=te_min,
        max_value=te_max,
        value=(te_min, te_max),
        step=0.01
    )
    
    # RAI range filter
    rai_min, rai_max = float(rai_df['rai'].min()), float(rai_df['rai'].max())
    rai_range = st.sidebar.slider(
        "RAI Score Range",
        min_value=rai_min,
        max_value=rai_max,
        value=(rai_min, rai_max),
        step=0.1
    )
    
    # Sample size for 3D chart
    st.sidebar.markdown("### ⚙️ Visualization")
    sample_size = st.sidebar.slider(
        "3D Chart Data Points",
        min_value=500,
        max_value=min(10000, len(rai_df)),
        value=min(3000, len(rai_df)),
        step=500,
        help="More points = richer visualization but slower"
    )
    
    # Apply filters
    filtered_df = rai_df.copy()
    if selected_role != "All Players":
        filtered_df = filtered_df[filtered_df['player_role'] == selected_role]
    filtered_df = filtered_df[
        (filtered_df['rtd'] >= rtd_range[0]) & (filtered_df['rtd'] <= rtd_range[1]) &
        (filtered_df['te'] >= te_range[0]) & (filtered_df['te'] <= te_range[1]) &
        (filtered_df['rai'] >= rai_range[0]) & (filtered_df['rai'] <= rai_range[1])
    ]
    
    # Show filter summary
    st.sidebar.markdown(f"""
    <div style="background: rgba(255,184,28,0.1); padding: 12px; border-radius: 8px; margin-top: 16px;">
        <div style="color: #FFB81C; font-weight: 600;">📊 Filtered Data</div>
        <div style="color: #9CA3AF; font-size: 0.875rem; margin-top: 8px;">
            {len(filtered_df):,} of {len(rai_df):,} records<br>
            {filtered_df['nfl_id'].nunique()} players
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ============== KPI CARDS ==============
    st.markdown("### 🎯 Key Performance Metrics")
    
    # Row 1: 3 main metrics
    row1 = st.columns(3)
    with row1[0]:
        st.metric(
            label="📊 Average RAI",
            value=f"{filtered_df['rai'].mean():.3f}",
            delta=f"Median: {filtered_df['rai'].median():.3f}",
            delta_color="off"
        )
    with row1[1]:
        st.metric(
            label="⚡ Avg Reaction Time",
            value=f"{filtered_df['rtd'].mean():.1f} frames",
            delta=f"Best: {filtered_df['rtd'].min():.0f}f",
            delta_color="off"
        )
    with row1[2]:
        st.metric(
            label="🎯 Trajectory Efficiency",
            value=f"{filtered_df['te'].mean():.1%}",
            delta=f"Best: {filtered_df['te'].max():.1%}",
            delta_color="off"
        )
    
    # Row 2: 3 count metrics
    row2 = st.columns(3)
    with row2[0]:
        st.metric(
            label="👥 Players Analyzed",
            value=f"{filtered_df['nfl_id'].nunique():,}",
        )
    with row2[1]:
        st.metric(
            label="🏈 Total Plays",
            value=f"{filtered_df[['game_id', 'play_id']].drop_duplicates().shape[0]:,}",
        )
    with row2[2]:
        st.metric(
            label="📈 Total Observations", 
            value=f"{len(filtered_df):,}",
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============== QUICK INSIGHTS ==============
    st.markdown("### 💡 Quick Insights")
    
    # Check if we have enough data for insights
    player_groups = filtered_df.groupby('nfl_id')['rai'].mean()
    
    if len(player_groups) > 0:
        # Row 1: Top performer and Fastest reactor
        insight_row1 = st.columns(2)
        
        # Top performer
        top_player = player_groups.idxmax()
        top_player_rai = player_groups.max()
        
        with insight_row1[0]:
            st.metric(
                label="🏆 Top Performer",
                value=f"Player #{top_player}",
                delta=f"RAI: {top_player_rai:.3f}",
                delta_color="off"
            )
        
        # Fastest reactor
        rtd_groups = filtered_df.groupby('nfl_id')['rtd'].mean()
        fastest_player = rtd_groups.idxmin()
        fastest_rtd = rtd_groups.min()
        
        with insight_row1[1]:
            st.metric(
                label="⚡ Fastest Reactor",
                value=f"Player #{fastest_player}",
                delta=f"RTD: {fastest_rtd:.1f} frames",
                delta_color="off"
            )
        
        # Row 2: Most efficient and Most consistent
        insight_row2 = st.columns(2)
        
        # Most efficient
        te_groups = filtered_df.groupby('nfl_id')['te'].mean()
        efficient_player = te_groups.idxmax()
        efficient_te = te_groups.max()
        
        with insight_row2[0]:
            st.metric(
                label="🎯 Most Efficient",
                value=f"Player #{efficient_player}",
                delta=f"TE: {efficient_te:.1%}",
                delta_color="off"
            )
        
        # Most consistent
        consistency = filtered_df.groupby('nfl_id')['rai'].agg(['mean', 'std', 'count'])
        consistency = consistency[consistency['count'] >= 5]  # Min 5 plays
        if not consistency.empty:
            most_consistent = consistency['std'].idxmin()
            consist_std = consistency.loc[most_consistent, 'std']
            with insight_row2[1]:
                st.metric(
                    label="📊 Most Consistent",
                    value=f"Player #{most_consistent}",
                    delta=f"Std Dev: {consist_std:.3f}",
                    delta_color="off"
                )
        else:
            with insight_row2[1]:
                st.info("Need 5+ plays per player for consistency calculation")
    else:
        st.info("Adjust filters to see Quick Insights - no data matches current filter criteria.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============== 3D VISUALIZATION ==============
    st.markdown("### 🌐 3D RAI Performance Space")
    st.markdown("*Drag to rotate • Scroll to zoom • Double-click to reset • Click legend to filter*")
    
    # 3D Axis selector
    axis_cols = st.columns(4)
    with axis_cols[0]:
        x_axis = st.selectbox("X-Axis", ['rtd', 'te', 'rai', 'bpq', 'cms'], index=0)
    with axis_cols[1]:
        y_axis = st.selectbox("Y-Axis", ['te', 'rtd', 'rai', 'bpq', 'cms'], index=0)
    with axis_cols[2]:
        z_axis = st.selectbox("Z-Axis", ['rai', 'rtd', 'te', 'bpq', 'cms'], index=0)
    with axis_cols[3]:
        color_by = st.selectbox("Color By", ['player_role', 'rai', 'rtd', 'te'], index=0)
    
    # Sample data
    sample_df = filtered_df.sample(n=min(sample_size, len(filtered_df)), random_state=42)
    
    fig_3d = create_3d_scatter(
        sample_df, 
        x=x_axis, 
        y=y_axis, 
        z=z_axis,
        color=color_by,
        hover_data=['nfl_id']
    )
    fig_3d.update_layout(
        title="",
        height=700,
        margin=dict(l=0, r=0, t=20, b=0),
    )
    st.plotly_chart(fig_3d, use_container_width=True, key="overview_3d_scatter")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============== DISTRIBUTION ANALYSIS ==============
    st.markdown("### 📈 Distribution Analysis")
    
    dist_tabs = st.tabs(["RAI Distribution", "Component Comparison", "Percentile Ranking"])
    
    with dist_tabs[0]:
        dist_data = filtered_df[['rai', 'player_role', 'nfl_id']].dropna()
        fig_dist = create_rai_distribution_chart(dist_data)
        fig_dist.update_layout(title="", height=500)
        st.plotly_chart(fig_dist, use_container_width=True, key="overview_dist")
    
    with dist_tabs[1]:
        # Side-by-side component comparison
        layout = get_plotly_layout()
        
        # Aggregate by role
        role_stats = filtered_df.groupby('player_role').agg({
            'rtd': 'mean',
            'te': 'mean',
            'bpq': 'mean',
            'cms': 'mean',
            'rai': 'mean'
        }).reset_index()
        
        fig_compare = go.Figure()
        
        for _, row in role_stats.iterrows():
            color = COLORS['receiver'] if 'Receiver' in row['player_role'] else COLORS['defender']
            fig_compare.add_trace(go.Bar(
                name=row['player_role'],
                x=['RTD (inv)', 'TE', 'BPQ', 'CMS', 'RAI'],
                y=[1 - row['rtd']/5, row['te'], row['bpq'], row['cms'], (row['rai'] + 1) / 2],
                marker_color=color,
            ))
        
        fig_compare.update_layout(
            **layout,
            title="Normalized Component Comparison by Role",
            barmode='group',
            height=450,
            yaxis_title="Normalized Score (0-1)",
        )
        st.plotly_chart(fig_compare, use_container_width=True)
    
    with dist_tabs[2]:
        # Percentile ranking table
        st.markdown("**Player Percentile Rankings** (higher = better)")
        
        player_agg = filtered_df.groupby('nfl_id').agg({
            'rai': 'mean',
            'rtd': 'mean',
            'te': 'mean',
            'player_role': 'first'
        }).reset_index()
        
        # Calculate percentiles
        player_agg['RAI Percentile'] = player_agg['rai'].rank(pct=True) * 100
        player_agg['RTD Percentile'] = (1 - player_agg['rtd'].rank(pct=True)) * 100  # Lower RTD is better
        player_agg['TE Percentile'] = player_agg['te'].rank(pct=True) * 100
        
        # Round and format
        display_agg = player_agg[['nfl_id', 'player_role', 'rai', 'RAI Percentile', 'rtd', 'RTD Percentile', 'te', 'TE Percentile']]
        display_agg = display_agg.round(2)
        display_agg = display_agg.sort_values('RAI Percentile', ascending=False).head(50)
        
        st.dataframe(
            display_agg,
            use_container_width=True,
            height=400,
            column_config={
                "nfl_id": st.column_config.NumberColumn("Player ID", format="%d"),
                "player_role": "Role",
                "rai": st.column_config.NumberColumn("Avg RAI", format="%.3f"),
                "RAI Percentile": st.column_config.ProgressColumn("RAI %ile", min_value=0, max_value=100, format="%.0f"),
                "rtd": st.column_config.NumberColumn("Avg RTD", format="%.1f"),
                "RTD Percentile": st.column_config.ProgressColumn("RTD %ile", min_value=0, max_value=100, format="%.0f"),
                "te": st.column_config.NumberColumn("Avg TE", format="%.3f"),
                "TE Percentile": st.column_config.ProgressColumn("TE %ile", min_value=0, max_value=100, format="%.0f"),
            },
            hide_index=True,
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============== STATISTICAL SUMMARY ==============
    st.markdown("### 📊 Statistical Summary")
    
    stat_cols = st.columns(2)
    
    with stat_cols[0]:
        st.markdown("#### Descriptive Statistics")
        desc_stats = filtered_df[['rai', 'rtd', 'te', 'bpq', 'cms']].describe()
        desc_stats = desc_stats.round(4)
        st.dataframe(desc_stats, use_container_width=True)
    
    with stat_cols[1]:
        st.markdown("#### Correlation Matrix")
        corr_cols = ['rtd', 'te', 'bpq', 'cms', 'rai']
        available_cols = [c for c in corr_cols if c in filtered_df.columns]
        corr_matrix = filtered_df[available_cols].corr()
        
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale=[
                [0, COLORS['defender']],
                [0.5, COLORS['neutral']],
                [1, COLORS['primary']],
            ],
            text=[[f"{v:.2f}" for v in row] for row in corr_matrix.values],
            texttemplate="%{text}",
            textfont={"size": 12, "color": "white"},
        ))
        layout = get_plotly_layout()
        fig_corr.update_layout(**layout, height=350, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_corr, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============== ROLE COMPARISON ==============
    st.markdown("### 🆚 Receivers vs Defenders Deep Dive")
    
    receiver_stats = filtered_df[filtered_df['player_role'] == 'Targeted Receiver']
    defender_stats = filtered_df[filtered_df['player_role'] == 'Defensive Coverage']
    
    role_cols = st.columns(2)
    
    # Receivers Card
    with role_cols[0]:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1C2541 0%, #0B132B 100%); 
                    border-radius: 16px; padding: 20px; border-left: 4px solid #3B82F6;">
            <h3 style="color: #3B82F6; margin: 0 0 16px 0;">🏃 Targeted Receivers</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not receiver_stats.empty:
            m1, m2 = st.columns(2)
            with m1:
                st.metric("Avg RAI", f"{receiver_stats['rai'].mean():.3f}")
                st.metric("Avg TE", f"{receiver_stats['te'].mean():.1%}")
            with m2:
                st.metric("Avg RTD", f"{receiver_stats['rtd'].mean():.1f}")
                st.metric("Players", f"{receiver_stats['nfl_id'].nunique()}")
            
            st.caption(f"📊 {len(receiver_stats):,} observations | Best RAI: {receiver_stats['rai'].max():.3f}")
        else:
            st.info("No receiver data available")
    
    # Defenders Card
    with role_cols[1]:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1C2541 0%, #0B132B 100%); 
                    border-radius: 16px; padding: 20px; border-left: 4px solid #EF4444;">
            <h3 style="color: #EF4444; margin: 0 0 16px 0;">🛡️ Defensive Coverage</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not defender_stats.empty:
            m3, m4 = st.columns(2)
            with m3:
                st.metric("Avg RAI", f"{defender_stats['rai'].mean():.3f}")
                st.metric("Avg TE", f"{defender_stats['te'].mean():.1%}")
            with m4:
                st.metric("Avg RTD", f"{defender_stats['rtd'].mean():.1f}")
                st.metric("Players", f"{defender_stats['nfl_id'].nunique()}")
            
            st.caption(f"📊 {len(defender_stats):,} observations | Best RAI: {defender_stats['rai'].max():.3f}")
        else:
            st.info("No defender data available")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============== DATA EXPORT ==============
    st.markdown("### 💾 Export Data")
    
    export_cols = st.columns(3)
    
    with export_cols[0]:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name="rai_filtered_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with export_cols[1]:
        # Summary stats export
        summary_stats = filtered_df.describe().to_csv()
        st.download_button(
            label="📊 Download Statistics (CSV)",
            data=summary_stats,
            file_name="rai_statistics.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with export_cols[2]:
        # Player aggregates
        player_export = filtered_df.groupby('nfl_id').agg({
            'rai': ['mean', 'std', 'count'],
            'rtd': 'mean',
            'te': 'mean',
            'bpq': 'mean',
            'cms': 'mean',
            'player_role': 'first'
        }).reset_index()
        player_export.columns = ['nfl_id', 'avg_rai', 'std_rai', 'play_count', 'avg_rtd', 'avg_te', 'avg_bpq', 'avg_cms', 'role']
        player_csv = player_export.to_csv(index=False)
        st.download_button(
            label="👤 Download Player Aggregates (CSV)",
            data=player_csv,
            file_name="rai_player_aggregates.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    st.info("📁 Please ensure RAI results are available in `outputs/reports/`")
    st.markdown("""
    To generate RAI results, run the analysis pipeline:
    ```bash
    python -m nfl_rai.rai_calculator
    ```
    """)
