"""
NFL Big Data Bowl 2026 - Visualization Module

Creates publication-quality visualizations for RAI analysis:
- Field plots with player positions and trajectories
- Reaction heatmaps
- RAI distribution charts
- Player comparison dashboards
- Animated play sequences
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle
from matplotlib.collections import LineCollection
import seaborn as sns
from typing import Optional, List, Dict, Tuple
from pathlib import Path


# NFL field dimensions (in yards)
FIELD_LENGTH = 120  # Including end zones
FIELD_WIDTH = 53.3
YARD_NUMBERS = [10, 20, 30, 40, 50, 40, 30, 20, 10]
HASH_WIDTH = 0.5


class NFLFieldPlotter:
    """Creates NFL field visualizations with player tracking."""
    
    def __init__(self, figsize: Tuple[int, int] = (14, 7)):
        self.figsize = figsize
        self.colors = {
            'field': '#2E7D32',  # Green turf
            'lines': 'white',
            'offense': '#1565C0',  # Blue
            'defense': '#C62828',  # Red
            'ball': '#FFD700',  # Gold
            'highlight': '#FF6F00',  # Orange
        }
        
    def create_field(self, ax: Optional[plt.Axes] = None,
                     yard_range: Tuple[int, int] = (0, 120)) -> plt.Axes:
        """
        Create a football field visualization.
        
        Args:
            ax: Existing axes to draw on, or None to create new
            yard_range: (start, end) yard lines to show
            
        Returns:
            Matplotlib axes with field drawn
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
            
        # Set field boundaries
        ax.set_xlim(yard_range)
        ax.set_ylim(0, FIELD_WIDTH)
        
        # Fill field color
        ax.set_facecolor(self.colors['field'])
        
        # Draw yard lines
        for yard in range(0, 121, 5):
            if yard_range[0] <= yard <= yard_range[1]:
                lw = 2 if yard % 10 == 0 else 0.5
                ax.axvline(x=yard, color=self.colors['lines'], 
                          linewidth=lw, alpha=0.7)
        
        # Draw end zones
        if yard_range[0] <= 10:
            ax.add_patch(mpatches.Rectangle((0, 0), 10, FIELD_WIDTH,
                                           facecolor='#1B5E20', alpha=0.5))
        if yard_range[1] >= 110:
            ax.add_patch(mpatches.Rectangle((110, 0), 10, FIELD_WIDTH,
                                           facecolor='#1B5E20', alpha=0.5))
        
        # Draw sidelines
        ax.axhline(y=0, color=self.colors['lines'], linewidth=2)
        ax.axhline(y=FIELD_WIDTH, color=self.colors['lines'], linewidth=2)
        
        # Draw hash marks
        for yard in range(10, 111):
            for y in [18.5, 34.8]:  # NFL hash positions
                ax.plot([yard-0.3, yard+0.3], [y, y], 
                       color=self.colors['lines'], linewidth=0.5)
        
        # Add yard numbers
        for i, yard in enumerate(range(10, 100, 10)):
            number = YARD_NUMBERS[i] if i < len(YARD_NUMBERS) else ''
            ax.text(yard + 10, 5, str(number), fontsize=14, 
                   color=self.colors['lines'], alpha=0.5,
                   ha='center', va='center', fontweight='bold')
            ax.text(yard + 10, FIELD_WIDTH - 5, str(number), fontsize=14,
                   color=self.colors['lines'], alpha=0.5,
                   ha='center', va='center', fontweight='bold')
        
        ax.set_aspect('equal')
        ax.axis('off')
        
        return ax
    
    def plot_players(self, ax: plt.Axes, player_data: pd.DataFrame,
                     show_trails: bool = True,
                     frame: Optional[int] = None) -> plt.Axes:
        """
        Plot player positions on the field.
        
        Args:
            ax: Axes with field drawn
            player_data: DataFrame with x, y, player_side, nfl_id, frame_id
            show_trails: Whether to show movement trails
            frame: Specific frame to show, or None for latest
            
        Returns:
            Axes with players plotted
        """
        if frame is not None:
            current_data = player_data[player_data['frame_id'] == frame]
        else:
            current_data = player_data.drop_duplicates(subset='nfl_id', keep='last')
        
        # Plot each player
        for _, player in current_data.iterrows():
            color = self.colors['offense'] if player.get('player_side') == 'Offense' else self.colors['defense']
            
            # Player marker
            ax.scatter(player['x'], player['y'], c=color, s=200, 
                      edgecolors='white', linewidths=2, zorder=5)
            
            # Player number/label
            if 'player_name' in player:
                label = player['player_name'].split()[-1][:3].upper()
            else:
                label = str(int(player['nfl_id']))[-2:]
            ax.annotate(label, (player['x'], player['y']),
                       ha='center', va='center', fontsize=7,
                       color='white', fontweight='bold', zorder=6)
            
            # Movement trail
            if show_trails:
                player_trail = player_data[player_data['nfl_id'] == player['nfl_id']]
                if len(player_trail) > 1:
                    trail = player_trail.sort_values('frame_id')[['x', 'y']].values
                    ax.plot(trail[:, 0], trail[:, 1], c=color, 
                           alpha=0.4, linewidth=1.5, zorder=3)
                    
        return ax
    
    def plot_trajectories(self, ax: plt.Axes,
                          predicted: pd.DataFrame,
                          actual: pd.DataFrame,
                          nfl_id: int) -> plt.Axes:
        """
        Plot predicted vs actual trajectories for a player.
        
        Args:
            ax: Axes with field
            predicted: Predicted trajectory DataFrame
            actual: Actual trajectory DataFrame
            nfl_id: Player to highlight
            
        Returns:
            Axes with trajectories
        """
        pred_player = predicted[predicted['nfl_id'] == nfl_id].sort_values('frame_id')
        actual_player = actual[actual['nfl_id'] == nfl_id].sort_values('frame_id')
        
        # Plot actual trajectory
        if len(actual_player) > 1:
            ax.plot(actual_player['x'], actual_player['y'],
                   c='green', linewidth=3, label='Actual', zorder=4)
            ax.scatter(actual_player['x'].iloc[-1], actual_player['y'].iloc[-1],
                      c='green', s=150, marker='*', zorder=5)
        
        # Plot predicted trajectory
        if len(pred_player) > 1:
            ax.plot(pred_player['x'], pred_player['y'],
                   c='orange', linewidth=2, linestyle='--', label='Predicted', zorder=4)
            ax.scatter(pred_player['x'].iloc[-1], pred_player['y'].iloc[-1],
                      c='orange', s=100, marker='d', zorder=5)
        
        ax.legend(loc='upper right')
        
        return ax
    
    def plot_ball_trajectory(self, ax: plt.Axes,
                              start_x: float, start_y: float,
                              end_x: float, end_y: float) -> plt.Axes:
        """Plot ball trajectory from throw to landing."""
        ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                   arrowprops=dict(arrowstyle='->', color=self.colors['ball'],
                                  lw=2, connectionstyle='arc3,rad=0.2'))
        
        # Ball landing spot
        ax.scatter(end_x, end_y, c=self.colors['ball'], s=300, 
                  marker='o', zorder=10, edgecolors='black', linewidths=2)
        ax.annotate('BALL', (end_x, end_y), ha='center', va='center',
                   fontsize=6, fontweight='bold', zorder=11)
        
        return ax


class RAIVisualizer:
    """Creates RAI-specific visualizations."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = Path(output_dir) if output_dir else Path('outputs/figures')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.field_plotter = NFLFieldPlotter()
        
        # Custom color palette
        self.rai_cmap = plt.cm.RdYlGn  # Red (low) to Green (high)
        
    def plot_rai_distribution(self, rai_df: pd.DataFrame,
                               group_by: str = 'player_role',
                               save: bool = True) -> plt.Figure:
        """
        Plot RAI score distribution by group.
        
        Args:
            rai_df: DataFrame with RAI scores and group columns
            group_by: Column to group by
            save: Whether to save the figure
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Distribution plot
        ax1 = axes[0]
        groups = rai_df[group_by].unique()
        colors = plt.cm.Set2(np.linspace(0, 1, len(groups)))
        
        for group, color in zip(groups, colors):
            data = rai_df[rai_df[group_by] == group]['rai'].dropna()  # Filter NaN
            if len(data) > 0:
                ax1.hist(data, bins=30, alpha=0.6, label=group, color=color)
        
        ax1.set_xlabel('RAI Score', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.set_title('RAI Distribution by Role', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.axvline(x=0, color='black', linestyle='--', alpha=0.5)
        
        # Box plot
        ax2 = axes[1]
        rai_df.boxplot(column='rai', by=group_by, ax=ax2)
        ax2.set_xlabel(group_by.replace('_', ' ').title(), fontsize=12)
        ax2.set_ylabel('RAI Score', fontsize=12)
        ax2.set_title('RAI by Role', fontsize=14, fontweight='bold')
        plt.suptitle('')  # Remove automatic title
        
        plt.tight_layout()
        
        if save:
            filepath = self.output_dir / 'rai_distribution.png'
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"Saved: {filepath}")
            
        return fig
    
    def plot_component_breakdown(self, rai_components: pd.DataFrame,
                                  top_n: int = 10,
                                  save: bool = True) -> plt.Figure:
        """
        Plot RAI component breakdown for top players.
        
        Args:
            rai_components: DataFrame with all RAI components
            top_n: Number of top players to show
            save: Whether to save figure
            
        Returns:
            Matplotlib figure
        """
        # Get top players by RAI
        top_players = rai_components.nlargest(top_n, 'rai')
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        components = ['rtd', 'te', 'bpq', 'cms', 'sd']
        x = np.arange(len(top_players))
        width = 0.15
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(components)))
        
        for i, (comp, color) in enumerate(zip(components, colors)):
            # Normalize for visualization
            values = (top_players[comp] - top_players[comp].mean()) / top_players[comp].std()
            ax.bar(x + i*width, values, width, label=comp.upper(), color=color)
        
        ax.set_xlabel('Player', fontsize=12)
        ax.set_ylabel('Normalized Component Value', fontsize=12)
        ax.set_title('RAI Component Breakdown (Top Players)', fontsize=14, fontweight='bold')
        ax.set_xticks(x + width * 2)
        ax.set_xticklabels([str(int(p)) for p in top_players['nfl_id']], rotation=45)
        ax.legend(loc='upper right')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filepath = self.output_dir / 'rai_components.png'
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"Saved: {filepath}")
            
        return fig
    
    def plot_reaction_heatmap(self, player_data: pd.DataFrame,
                               rai_scores: pd.DataFrame,
                               save: bool = True) -> plt.Figure:
        """
        Create field heatmap showing reaction quality by position.
        
        Args:
            player_data: Tracking data with positions
            rai_scores: RAI scores for players
            save: Whether to save
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # Create field
        self.field_plotter.create_field(ax, yard_range=(10, 110))
        
        # Merge positions with RAI
        merged = player_data.merge(rai_scores[['nfl_id', 'rai']], on='nfl_id', how='left')
        
        # Get unique player positions (first frame)
        positions = merged.drop_duplicates(subset='nfl_id', keep='first')
        
        # Color by RAI score
        scatter = ax.scatter(positions['x'], positions['y'],
                            c=positions['rai'], cmap=self.rai_cmap,
                            s=200, vmin=-2, vmax=2,
                            edgecolors='white', linewidths=2, zorder=5)
        
        # Colorbar
        cbar = plt.colorbar(scatter, ax=ax, shrink=0.7, pad=0.02)
        cbar.set_label('RAI Score', fontsize=12)
        
        ax.set_title('Reaction Quality by Field Position', fontsize=14, fontweight='bold')
        
        if save:
            filepath = self.output_dir / 'reaction_heatmap.png'
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"Saved: {filepath}")
            
        return fig
    
    def plot_coverage_comparison(self, rai_by_coverage: pd.DataFrame,
                                  save: bool = True) -> plt.Figure:
        """
        Compare RAI metrics across coverage types.
        
        Args:
            rai_by_coverage: RAI data with coverage_type column
            save: Whether to save
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Average RAI by coverage
        ax1 = axes[0]
        coverage_means = rai_by_coverage.groupby('team_coverage_type')['rai'].mean().sort_values()
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(coverage_means)))
        coverage_means.plot(kind='barh', ax=ax1, color=colors)
        ax1.set_xlabel('Average RAI Score', fontsize=12)
        ax1.set_ylabel('Coverage Type', fontsize=12)
        ax1.set_title('Defensive Reactivity by Coverage Scheme', fontsize=14, fontweight='bold')
        ax1.axvline(x=0, color='black', linestyle='--', alpha=0.5)
        
        # RTD by coverage
        ax2 = axes[1]
        rtd_means = rai_by_coverage.groupby('team_coverage_type')['rtd'].mean().sort_values()
        colors2 = plt.cm.Blues(np.linspace(0.3, 0.9, len(rtd_means)))
        rtd_means.plot(kind='barh', ax=ax2, color=colors2)
        ax2.set_xlabel('Average Reaction Time (frames)', fontsize=12)
        ax2.set_ylabel('Coverage Type', fontsize=12)
        ax2.set_title('Reaction Speed by Coverage Scheme', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save:
            filepath = self.output_dir / 'coverage_comparison.png'
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"Saved: {filepath}")
            
        return fig
    
    def create_play_animation_frames(self, input_df: pd.DataFrame,
                                      output_df: pd.DataFrame,
                                      ball_x: float, ball_y: float,
                                      rai_scores: Optional[pd.DataFrame] = None) -> List[plt.Figure]:
        """
        Create frames for play animation.
        
        Args:
            input_df: Pre-throw tracking
            output_df: Post-throw tracking
            ball_x, ball_y: Ball landing position
            rai_scores: Optional RAI scores for coloring
            
        Returns:
            List of matplotlib figures (one per frame)
        """
        frames = sorted(output_df['frame_id'].unique())
        figures = []
        
        for frame_id in frames:
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # Get field bounds from data
            all_data = pd.concat([input_df, output_df])
            x_min = max(0, all_data['x'].min() - 10)
            x_max = min(120, all_data['x'].max() + 10)
            
            # Create field
            self.field_plotter.create_field(ax, yard_range=(x_min, x_max))
            
            # Get current frame data
            frame_data = output_df[output_df['frame_id'] <= frame_id]
            
            # Plot players
            self.field_plotter.plot_players(ax, frame_data, show_trails=True, frame=frame_id)
            
            # Plot ball trajectory
            qb_data = input_df[input_df['player_role'] == 'Passing']
            if len(qb_data) > 0:
                start_x = qb_data['x'].iloc[0]
                start_y = qb_data['y'].iloc[0]
                self.field_plotter.plot_ball_trajectory(ax, start_x, start_y, ball_x, ball_y)
            
            # Add frame info
            ax.text(0.02, 0.98, f'Frame: {frame_id}', transform=ax.transAxes,
                   fontsize=12, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            figures.append(fig)
            plt.close(fig)  # Close to save memory
            
        return figures


def create_summary_dashboard(rai_df: pd.DataFrame,
                              output_path: Path) -> plt.Figure:
    """
    Create a comprehensive summary dashboard.
    
    Args:
        rai_df: Complete RAI analysis results
        output_path: Where to save the dashboard
        
    Returns:
        Dashboard figure
    """
    fig = plt.figure(figsize=(16, 12))
    
    # Title
    fig.suptitle('NFL Big Data Bowl 2026: Reactivity Advantage Index Analysis',
                fontsize=18, fontweight='bold', y=0.98)
    
    # Create grid
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Overall RAI distribution
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.hist(rai_df['rai'], bins=40, color='steelblue', edgecolor='white', alpha=0.8)
    ax1.axvline(x=0, color='red', linestyle='--', linewidth=2)
    ax1.set_xlabel('RAI Score')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Overall RAI Distribution')
    
    # 2. RAI by role
    ax2 = fig.add_subplot(gs[0, 1])
    role_means = rai_df.groupby('player_role')['rai'].mean().sort_values()
    role_means.plot(kind='barh', ax=ax2, color='teal')
    ax2.set_xlabel('Average RAI')
    ax2.set_title('RAI by Player Role')
    
    # 3. Top performers
    ax3 = fig.add_subplot(gs[0, 2])
    top_10 = rai_df.nlargest(10, 'rai')[['nfl_id', 'rai', 'player_role']]
    y_pos = np.arange(len(top_10))
    ax3.barh(y_pos, top_10['rai'], color='green', alpha=0.7)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels([f"{int(row['nfl_id'])} ({row['player_role'][:8]})" 
                        for _, row in top_10.iterrows()])
    ax3.set_xlabel('RAI Score')
    ax3.set_title('Top 10 Performers')
    
    # 4. Component correlations
    ax4 = fig.add_subplot(gs[1, :2])
    components = ['rtd', 'te', 'bpq', 'cms', 'sd', 'rai']
    corr_matrix = rai_df[components].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
               ax=ax4, fmt='.2f', square=True)
    ax4.set_title('Component Correlations')
    
    # 5. RTD vs TE scatter
    ax5 = fig.add_subplot(gs[1, 2])
    scatter = ax5.scatter(rai_df['rtd'], rai_df['te'], c=rai_df['rai'],
                         cmap='RdYlGn', alpha=0.6, s=30)
    ax5.set_xlabel('Reaction Time Delay (frames)')
    ax5.set_ylabel('Trajectory Efficiency')
    ax5.set_title('RTD vs TE (colored by RAI)')
    plt.colorbar(scatter, ax=ax5, label='RAI')
    
    # 6. Key insights text box
    ax6 = fig.add_subplot(gs[2, :])
    ax6.axis('off')
    
    # Calculate insights
    avg_rai = rai_df['rai'].mean()
    std_rai = rai_df['rai'].std()
    best_role = rai_df.groupby('player_role')['rai'].mean().idxmax()
    avg_rtd = rai_df['rtd'].mean()
    
    insights = f"""
    KEY INSIGHTS:
    
    • Average RAI Score: {avg_rai:.3f} (σ = {std_rai:.3f})
    • Best Performing Role: {best_role}
    • Average Reaction Time: {avg_rtd:.1f} frames ({avg_rtd * 100:.0f}ms)
    • Trajectory Efficiency Range: {rai_df['te'].min():.2f} - {rai_df['te'].max():.2f}
    • Total Players Analyzed: {rai_df['nfl_id'].nunique():,}
    • Total Plays Analyzed: {len(rai_df):,}
    """
    
    ax6.text(0.1, 0.5, insights, fontsize=12, family='monospace',
            verticalalignment='center', transform=ax6.transAxes,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved dashboard: {output_path}")
    
    return fig


if __name__ == "__main__":
    # Test visualization module
    print("Testing visualization module...")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'nfl_id': [1, 1, 1, 2, 2, 2],
        'frame_id': [1, 2, 3, 1, 2, 3],
        'x': [50, 51, 52, 45, 44, 43],
        'y': [25, 25, 25, 30, 30, 30],
        'player_side': ['Offense', 'Offense', 'Offense', 'Defense', 'Defense', 'Defense'],
        'player_name': ['John Smith', 'John Smith', 'John Smith', 'Jane Doe', 'Jane Doe', 'Jane Doe']
    })
    
    # Test field plotter
    plotter = NFLFieldPlotter()
    fig, ax = plt.subplots(figsize=(14, 7))
    plotter.create_field(ax, yard_range=(30, 70))
    plotter.plot_players(ax, sample_data)
    plt.savefig('outputs/figures/test_field.png', dpi=100)
    plt.close()
    
    print("✓ Visualization tests passed!")
