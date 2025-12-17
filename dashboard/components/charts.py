"""
NFL RAI Dashboard - Reusable Chart Components
Premium visualizations with Plotly
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any

from .themes import COLORS, get_plotly_layout


def create_kpi_card(label: str, value: float, delta: Optional[float] = None, 
                    format_str: str = ".2f", icon: str = "📊") -> str:
    """Create an HTML KPI card with glassmorphism styling."""
    formatted_value = f"{value:{format_str}}" if isinstance(value, (int, float)) else str(value)
    
    delta_html = ""
    if delta is not None:
        delta_color = COLORS['success'] if delta >= 0 else COLORS['error']
        delta_arrow = "↑" if delta >= 0 else "↓"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.875rem;">{delta_arrow} {abs(delta):.1%}</div>'
    
    return f"""
    <div class="metric-container" style="text-align: center;">
        <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{formatted_value}</div>
        {delta_html}
    </div>
    """


def create_rai_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Create violin plot of RAI distribution by player role."""
    layout = get_plotly_layout()
    
    fig = go.Figure()
    
    colors = {
        'Targeted Receiver': COLORS['receiver'],
        'Defensive Coverage': COLORS['defender'],
    }
    
    for role in df['player_role'].unique():
        role_data = df[df['player_role'] == role]['rai']
        fig.add_trace(go.Violin(
            y=role_data,
            name=role,
            box_visible=True,
            meanline_visible=True,
            fillcolor=colors.get(role, COLORS['neutral']),
            line_color=COLORS['text'],
            opacity=0.8,
        ))
    
    fig.update_layout(
        **layout,
        title="RAI Distribution by Player Role",
        yaxis_title="RAI Score",
        showlegend=True,
        height=400,
    )
    
    return fig


def create_3d_scatter(df: pd.DataFrame, x: str, y: str, z: str, 
                      color: str = 'player_role', hover_data: List[str] = None) -> go.Figure:
    """Create 3D scatter plot for multi-dimensional analysis."""
    layout = get_plotly_layout()
    
    color_map = {
        'Targeted Receiver': COLORS['receiver'],
        'Defensive Coverage': COLORS['defender'],
    }
    
    fig = px.scatter_3d(
        df,
        x=x,
        y=y,
        z=z,
        color=color,
        color_discrete_map=color_map,
        hover_data=hover_data or [],
        opacity=0.7,
    )
    
    fig.update_layout(
        **layout,
        scene=dict(
            xaxis=dict(
                title=x.upper(),
                backgroundcolor='rgba(0,0,0,0)',
                gridcolor='rgba(255,255,255,0.1)',
            ),
            yaxis=dict(
                title=y.upper(),
                backgroundcolor='rgba(0,0,0,0)',
                gridcolor='rgba(255,255,255,0.1)',
            ),
            zaxis=dict(
                title=z.upper(),
                backgroundcolor='rgba(0,0,0,0)',
                gridcolor='rgba(255,255,255,0.1)',
            ),
            bgcolor='rgba(0,0,0,0)',
        ),
        height=600,
        margin=dict(l=0, r=0, t=40, b=0),
    )
    
    return fig


def create_radar_chart(player_data: Dict[str, float], 
                       comparison_data: Optional[Dict[str, float]] = None,
                       player_name: str = "Player",
                       comparison_name: str = "Average") -> go.Figure:
    """Create radar chart for player component comparison."""
    layout = get_plotly_layout()
    
    categories = ['Reaction Time (RTD)', 'Trajectory Efficiency', 
                  'Break Point Quality', 'Coverage Maintenance', 'Separation Delta']
    keys = ['rtd', 'te', 'bpq', 'cms', 'sd']
    
    # Normalize RTD (lower is better, so invert)
    def normalize(data):
        values = []
        for i, key in enumerate(keys):
            val = data.get(key, 0.5)
            if key == 'rtd':
                # Invert RTD: lower is better, scale to 0-1 where 1 is best
                val = max(0, 1 - (val / 5))  # Assuming max RTD of 5
            values.append(val)
        return values
    
    fig = go.Figure()
    
    # Player trace
    fig.add_trace(go.Scatterpolar(
        r=normalize(player_data),
        theta=categories,
        fill='toself',
        fillcolor=f'rgba(255, 184, 28, 0.3)',
        line=dict(color=COLORS['primary'], width=2),
        name=player_name,
    ))
    
    # Comparison trace
    if comparison_data:
        fig.add_trace(go.Scatterpolar(
            r=normalize(comparison_data),
            theta=categories,
            fill='toself',
            fillcolor='rgba(156, 163, 175, 0.2)',
            line=dict(color=COLORS['text_muted'], width=2, dash='dash'),
            name=comparison_name,
        ))
    
    fig.update_layout(
        **layout,
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor='rgba(255,255,255,0.1)',
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
            ),
        ),
        showlegend=True,
        height=400,
    )
    
    return fig


def create_bar_chart(df: pd.DataFrame, x: str, y: str, 
                     color: Optional[str] = None, title: str = "") -> go.Figure:
    """Create styled bar chart."""
    layout = get_plotly_layout()
    
    color_map = {
        'Targeted Receiver': COLORS['receiver'],
        'Defensive Coverage': COLORS['defender'],
    }
    
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        color_discrete_map=color_map if color else None,
        title=title,
    )
    
    fig.update_layout(
        **layout,
        height=400,
        bargap=0.3,
    )
    
    fig.update_traces(
        marker_line_color=COLORS['primary'],
        marker_line_width=1,
        opacity=0.9,
    )
    
    return fig


def create_line_chart(df: pd.DataFrame, x: str, y: str, 
                      color: Optional[str] = None, title: str = "") -> go.Figure:
    """Create styled line chart with area fill."""
    layout = get_plotly_layout()
    
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        title=title,
    )
    
    fig.update_traces(
        line=dict(width=3),
        fill='tonexty',
        fillcolor='rgba(255, 184, 28, 0.1)',
    )
    
    fig.update_layout(
        **layout,
        height=400,
        hovermode='x unified',
    )
    
    return fig


def create_heatmap(df: pd.DataFrame, x: str, y: str, z: str, 
                   title: str = "") -> go.Figure:
    """Create styled heatmap."""
    layout = get_plotly_layout()
    
    # Pivot data for heatmap
    pivot = df.pivot_table(values=z, index=y, columns=x, aggfunc='mean')
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale=[
            [0, COLORS['defender']],
            [0.5, COLORS['neutral']],
            [1, COLORS['primary']],
        ],
        hovertemplate=f'{x}: %{{x}}<br>{y}: %{{y}}<br>{z}: %{{z:.3f}}<extra></extra>',
    ))
    
    fig.update_layout(
        **layout,
        title=title,
        height=500,
    )
    
    return fig


def create_top_performers_table(df: pd.DataFrame) -> go.Figure:
    """Create a styled table for top performers."""
    layout = get_plotly_layout()
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Rank</b>', '<b>NFL ID</b>', '<b>Avg RAI</b>', 
                    '<b>Plays</b>', '<b>Role</b>'],
            fill_color=COLORS['surface'],
            align='left',
            font=dict(color=COLORS['text'], size=12),
            height=40,
        ),
        cells=dict(
            values=[
                list(range(1, len(df) + 1)),
                df['nfl_id'].tolist(),
                [f"{x:.3f}" for x in df['avg_rai']],
                df['play_count'].tolist(),
                df['player_role'].tolist(),
            ],
            fill_color=[
                [COLORS['background'] if i % 2 == 0 else COLORS['surface'] 
                 for i in range(len(df))]
            ],
            align='left',
            font=dict(color=COLORS['text'], size=11),
            height=35,
        ),
    )])
    
    fig.update_layout(
        **layout,
        height=max(400, 50 + len(df) * 35),
        margin=dict(l=0, r=0, t=0, b=0),
    )
    
    return fig
