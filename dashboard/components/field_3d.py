"""
NFL RAI Dashboard - 3D Field Visualization
Interactive NFL field with player positions
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from typing import Optional, List, Tuple

from .themes import COLORS, get_plotly_layout


# NFL Field Dimensions (in yards)
FIELD_LENGTH = 120  # Including end zones
FIELD_WIDTH = 53.3
ENDZONE_LENGTH = 10


def create_field_surface() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create 3D surface mesh for NFL field."""
    # Create grid
    x = np.linspace(0, FIELD_LENGTH, 100)
    y = np.linspace(0, FIELD_WIDTH, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    
    return X, Y, Z


def create_3d_field(
    players_df: Optional[pd.DataFrame] = None,
    ball_position: Optional[Tuple[float, float]] = None,
    highlighted_players: Optional[List[int]] = None,
    camera_preset: str = 'broadcast',
    show_yard_lines: bool = True,
    animate: bool = False,
) -> go.Figure:
    """
    Create interactive 3D NFL field visualization.
    
    Args:
        players_df: DataFrame with x, y, player_role, nfl_id columns
        ball_position: (x, y) tuple for ball location
        highlighted_players: List of nfl_ids to highlight
        camera_preset: 'broadcast', 'endzone', 'overhead', 'sideline'
        show_yard_lines: Whether to show yard lines
        animate: Whether to enable animation
    
    Returns:
        Plotly figure
    """
    layout = get_plotly_layout()
    fig = go.Figure()
    
    # Create field surface
    X, Y, Z = create_field_surface()
    
    # Field color - darker green for 3D effect
    field_color = np.ones_like(X) * 0.4
    
    # Add endzone coloring
    field_color[X < ENDZONE_LENGTH] = 0.6
    field_color[X > (FIELD_LENGTH - ENDZONE_LENGTH)] = 0.6
    
    # Add field surface
    fig.add_trace(go.Surface(
        x=X,
        y=Y,
        z=Z,
        surfacecolor=field_color,
        colorscale=[
            [0, '#1a472a'],  # Dark green
            [0.4, '#2E7D32'],  # Normal field
            [0.6, '#1B5E20'],  # Endzone darker
            [1, '#1B5E20'],
        ],
        showscale=False,
        opacity=0.95,
        lighting=dict(
            ambient=0.8,
            diffuse=0.5,
            specular=0.2,
        ),
        hoverinfo='none',
    ))
    
    # Add yard lines
    if show_yard_lines:
        for yard in range(10, 110, 10):
            # Main yard line
            fig.add_trace(go.Scatter3d(
                x=[yard, yard],
                y=[0, FIELD_WIDTH],
                z=[0.01, 0.01],
                mode='lines',
                line=dict(color='white', width=3),
                hoverinfo='none',
                showlegend=False,
            ))
        
        # Hash marks
        for yard in range(10, 110, 1):
            if yard % 10 != 0:
                for y_pos in [FIELD_WIDTH/3, 2*FIELD_WIDTH/3]:
                    fig.add_trace(go.Scatter3d(
                        x=[yard, yard],
                        y=[y_pos - 0.5, y_pos + 0.5],
                        z=[0.01, 0.01],
                        mode='lines',
                        line=dict(color='white', width=1),
                        hoverinfo='none',
                        showlegend=False,
                    ))
    
    # Add sidelines
    fig.add_trace(go.Scatter3d(
        x=[0, FIELD_LENGTH, FIELD_LENGTH, 0, 0],
        y=[0, 0, FIELD_WIDTH, FIELD_WIDTH, 0],
        z=[0.02] * 5,
        mode='lines',
        line=dict(color='white', width=5),
        hoverinfo='none',
        showlegend=False,
    ))
    
    # Add players
    if players_df is not None and not players_df.empty:
        # Separate by role
        for role in players_df['player_role'].unique():
            role_df = players_df[players_df['player_role'] == role]
            
            color = COLORS['receiver'] if 'Receiver' in role else COLORS['defender']
            symbol = 'circle' if 'Receiver' in role else 'diamond'
            
            # Check if any players are highlighted
            sizes = []
            for nfl_id in role_df['nfl_id']:
                if highlighted_players and nfl_id in highlighted_players:
                    sizes.append(15)
                else:
                    sizes.append(10)
            
            fig.add_trace(go.Scatter3d(
                x=role_df['x'] if 'x' in role_df.columns else role_df.index,
                y=role_df['y'] if 'y' in role_df.columns else [FIELD_WIDTH/2] * len(role_df),
                z=[1.5] * len(role_df),  # Player height
                mode='markers',
                marker=dict(
                    size=sizes,
                    color=color,
                    symbol=symbol,
                    opacity=0.9,
                    line=dict(color='white', width=1),
                ),
                name=role,
                hovertemplate=(
                    '<b>Player %{customdata}</b><br>'
                    'Position: (%{x:.1f}, %{y:.1f})<br>'
                    '<extra></extra>'
                ),
                customdata=role_df['nfl_id'] if 'nfl_id' in role_df.columns else range(len(role_df)),
            ))
    
    # Add ball
    if ball_position:
        fig.add_trace(go.Scatter3d(
            x=[ball_position[0]],
            y=[ball_position[1]],
            z=[2],
            mode='markers',
            marker=dict(
                size=8,
                color='#8B4513',  # Football brown
                symbol='circle',
                line=dict(color='white', width=2),
            ),
            name='Football',
            hoverinfo='name',
        ))
    
    # Camera presets
    camera_settings = {
        'broadcast': dict(
            eye=dict(x=1.5, y=0.8, z=0.6),
            center=dict(x=0, y=0, z=0),
            up=dict(x=0, y=0, z=1),
        ),
        'endzone': dict(
            eye=dict(x=2.5, y=0, z=0.5),
            center=dict(x=0, y=0, z=0),
            up=dict(x=0, y=0, z=1),
        ),
        'overhead': dict(
            eye=dict(x=0, y=0, z=2.5),
            center=dict(x=0, y=0, z=0),
            up=dict(x=0, y=1, z=0),
        ),
        'sideline': dict(
            eye=dict(x=0, y=2, z=0.5),
            center=dict(x=0, y=0, z=0),
            up=dict(x=0, y=0, z=1),
        ),
    }
    
    camera = camera_settings.get(camera_preset, camera_settings['broadcast'])
    
    # Update layout
    fig.update_layout(
        **layout,
        scene=dict(
            xaxis=dict(
                title='',
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                range=[0, FIELD_LENGTH],
                backgroundcolor='rgba(0,0,0,0)',
            ),
            yaxis=dict(
                title='',
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                range=[0, FIELD_WIDTH],
                backgroundcolor='rgba(0,0,0,0)',
            ),
            zaxis=dict(
                title='',
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                range=[0, 10],
                backgroundcolor='rgba(0,0,0,0)',
            ),
            bgcolor='rgba(0,0,0,0)',
            camera=camera,
            aspectmode='manual',
            aspectratio=dict(x=2, y=1, z=0.3),
        ),
        height=600,
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(28, 37, 65, 0.8)',
        ),
    )
    
    return fig


def create_play_trajectory(
    tracking_df: pd.DataFrame,
    ball_start: Tuple[float, float],
    ball_end: Tuple[float, float],
    camera_preset: str = 'broadcast',
) -> go.Figure:
    """
    Create 3D visualization with player trajectories for a play.
    
    Args:
        tracking_df: DataFrame with frame_id, x, y, player_role, nfl_id
        ball_start: Starting position (x, y)
        ball_end: Landing position (x, y)
        camera_preset: Camera angle preset
    
    Returns:
        Plotly figure with trajectories
    """
    fig = create_3d_field(camera_preset=camera_preset)
    
    if tracking_df.empty:
        return fig
    
    # Add trajectory lines for each player
    for nfl_id in tracking_df['nfl_id'].unique():
        player_df = tracking_df[tracking_df['nfl_id'] == nfl_id].sort_values('frame_id')
        
        if len(player_df) < 2:
            continue
        
        role = player_df['player_role'].iloc[0]
        color = COLORS['receiver'] if 'Receiver' in role else COLORS['defender']
        
        # Add trajectory line
        fig.add_trace(go.Scatter3d(
            x=player_df['x'],
            y=player_df['y'],
            z=[0.5] * len(player_df),
            mode='lines',
            line=dict(color=color, width=4),
            opacity=0.6,
            name=f'Player {nfl_id}',
            showlegend=False,
        ))
        
        # Add end position marker
        final_pos = player_df.iloc[-1]
        fig.add_trace(go.Scatter3d(
            x=[final_pos['x']],
            y=[final_pos['y']],
            z=[1.5],
            mode='markers',
            marker=dict(size=10, color=color, symbol='circle'),
            name=f'{role} ({nfl_id})',
        ))
    
    # Add ball trajectory arc
    if ball_start and ball_end:
        # Create parabolic arc
        t = np.linspace(0, 1, 30)
        ball_x = ball_start[0] + t * (ball_end[0] - ball_start[0])
        ball_y = ball_start[1] + t * (ball_end[1] - ball_start[1])
        # Parabolic height (peaks in middle)
        max_height = 10 + np.sqrt((ball_end[0] - ball_start[0])**2 + 
                                   (ball_end[1] - ball_start[1])**2) / 5
        ball_z = 2 + 4 * t * (1 - t) * max_height
        
        fig.add_trace(go.Scatter3d(
            x=ball_x,
            y=ball_y,
            z=ball_z,
            mode='lines',
            line=dict(color='#8B4513', width=5, dash='dash'),
            name='Ball Trajectory',
        ))
        
        # Ball at target
        fig.add_trace(go.Scatter3d(
            x=[ball_end[0]],
            y=[ball_end[1]],
            z=[1],
            mode='markers',
            marker=dict(size=12, color=COLORS['primary'], symbol='circle'),
            name='Target',
        ))
    
    return fig
