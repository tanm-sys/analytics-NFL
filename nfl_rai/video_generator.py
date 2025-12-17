"""
NFL Big Data Bowl 2026 - Video Generator Module

Creates broadcast-quality video animations of plays with RAI overlays.
Suitable for the Broadcast Visualization Track submission.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import imageio
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from tqdm import tqdm

from .visualizations import NFLFieldPlotter


class VideoGenerator:
    """
    Generates broadcast-quality video animations of NFL plays.
    
    Features:
    - Smooth player movement animations
    - Ball trajectory visualization
    - Real-time RAI metric overlays
    - Customizable annotations and captions
    """
    
    def __init__(self, output_dir: Optional[Path] = None, fps: int = 10):
        """
        Initialize video generator.
        
        Args:
            output_dir: Directory for output videos
            fps: Frames per second (tracking data is 10Hz)
        """
        self.output_dir = Path(output_dir) if output_dir else Path('outputs/videos')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.fps = fps
        self.field_plotter = NFLFieldPlotter(figsize=(16, 9))  # 16:9 for broadcast
        
        # Styling
        self.colors = {
            'offense': '#1565C0',
            'defense': '#C62828',
            'ball': '#FFD700',
            'highlight': '#FF6F00',
            'rai_high': '#2E7D32',
            'rai_low': '#D32F2F',
        }
        
    def create_play_video(self,
                          input_df: pd.DataFrame,
                          output_df: pd.DataFrame,
                          ball_x: float,
                          ball_y: float,
                          rai_scores: Optional[pd.DataFrame] = None,
                          title: str = 'NFL Play Animation',
                          filename: str = 'play_animation.mp4') -> Path:
        """
        Create animated video of a single play.
        
        Args:
            input_df: Pre-throw tracking data
            output_df: Post-throw tracking data
            ball_x, ball_y: Ball landing position
            rai_scores: Optional RAI scores for overlay
            title: Video title
            filename: Output filename
            
        Returns:
            Path to created video file
        """
        output_path = self.output_dir / filename
        
        # Get frame range
        frames = sorted(output_df['frame_id'].unique())
        n_frames = len(frames)
        
        # Calculate field bounds
        all_data = pd.concat([input_df, output_df])
        x_min = max(0, all_data['x'].min() - 10)
        x_max = min(120, all_data['x'].max() + 10)
        
        # Store frames as images
        image_frames = []
        
        print(f"Generating {n_frames} frames...")
        for frame_id in tqdm(frames, desc="Rendering"):
            fig = self._create_frame(
                input_df, output_df, frame_id, frames,
                ball_x, ball_y, x_min, x_max,
                rai_scores, title
            )
            
            # Convert figure to image
            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
            image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            image_frames.append(image)
            
            plt.close(fig)
        
        # Create video
        print(f"Writing video to {output_path}...")
        imageio.mimwrite(output_path, image_frames, fps=self.fps)
        print(f"✓ Video saved: {output_path}")
        
        return output_path
    
    def _create_frame(self,
                      input_df: pd.DataFrame,
                      output_df: pd.DataFrame,
                      current_frame: int,
                      all_frames: List[int],
                      ball_x: float,
                      ball_y: float,
                      x_min: float,
                      x_max: float,
                      rai_scores: Optional[pd.DataFrame],
                      title: str) -> plt.Figure:
        """Create a single animation frame."""
        fig, ax = plt.subplots(figsize=(16, 9))
        
        # Create field
        self.field_plotter.create_field(ax, yard_range=(x_min, x_max))
        
        # Get data up to current frame
        frame_data = output_df[output_df['frame_id'] <= current_frame]
        current_positions = frame_data[frame_data['frame_id'] == current_frame]
        
        # Draw player trails
        for nfl_id in frame_data['nfl_id'].unique():
            player_trail = frame_data[frame_data['nfl_id'] == nfl_id].sort_values('frame_id')
            if len(player_trail) > 1:
                player_side = player_trail['player_side'].iloc[0] if 'player_side' in player_trail.columns else 'Defense'
                color = self.colors['offense'] if player_side == 'Offense' else self.colors['defense']
                
                trail = player_trail[['x', 'y']].values
                ax.plot(trail[:, 0], trail[:, 1], c=color, alpha=0.3, linewidth=2)
        
        # Draw current player positions
        for _, player in current_positions.iterrows():
            player_side = player.get('player_side', 'Defense')
            color = self.colors['offense'] if player_side == 'Offense' else self.colors['defense']
            
            # Get RAI score for color intensity if available
            if rai_scores is not None and player['nfl_id'] in rai_scores['nfl_id'].values:
                rai = rai_scores[rai_scores['nfl_id'] == player['nfl_id']]['rai'].iloc[0]
                edge_color = self.colors['rai_high'] if rai > 0 else self.colors['rai_low']
                edge_width = 3
            else:
                edge_color = 'white'
                edge_width = 2
            
            ax.scatter(player['x'], player['y'], c=color, s=300,
                      edgecolors=edge_color, linewidths=edge_width, zorder=5)
            
            # Player label
            if 'player_name' in player:
                label = player['player_name'].split()[-1][:4].upper()
            else:
                label = str(int(player['nfl_id']))[-2:]
            ax.annotate(label, (player['x'], player['y']),
                       ha='center', va='center', fontsize=7,
                       color='white', fontweight='bold', zorder=6)
        
        # Draw ball trajectory and landing
        progress = (current_frame - all_frames[0]) / (all_frames[-1] - all_frames[0])
        
        # Ball in air animation
        qb_data = input_df[input_df['player_role'] == 'Passing'] if 'player_role' in input_df.columns else input_df.iloc[:1]
        if len(qb_data) > 0:
            start_x = qb_data['x'].iloc[0]
            start_y = qb_data['y'].iloc[0]
            
            # Interpolate ball position
            ball_current_x = start_x + progress * (ball_x - start_x)
            ball_current_y = start_y + progress * (ball_y - start_y)
            
            # Draw trajectory line
            ax.plot([start_x, ball_x], [start_y, ball_y],
                   c=self.colors['ball'], linestyle='--', linewidth=1, alpha=0.5)
            
            # Draw current ball position
            ax.scatter(ball_current_x, ball_current_y, c=self.colors['ball'],
                      s=150, marker='o', edgecolors='black', linewidths=2, zorder=10)
            
            # Landing spot indicator
            ax.scatter(ball_x, ball_y, c=self.colors['ball'],
                      s=200, marker='x', linewidths=3, alpha=0.5, zorder=9)
        
        # Add overlays
        self._add_overlays(ax, fig, title, current_frame, all_frames, progress, rai_scores)
        
        return fig
    
    def _add_overlays(self, ax: plt.Axes, fig: plt.Figure,
                      title: str, current_frame: int,
                      all_frames: List[int], progress: float,
                      rai_scores: Optional[pd.DataFrame]):
        """Add broadcast-style overlays to frame."""
        
        # Title bar (top)
        ax.text(0.5, 1.05, title,
               transform=ax.transAxes, ha='center', va='bottom',
               fontsize=16, fontweight='bold', color='white',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a1a', alpha=0.9))
        
        # Frame counter (top right)
        frame_text = f"Frame {current_frame} / {all_frames[-1]}"
        ax.text(0.98, 0.98, frame_text,
               transform=ax.transAxes, ha='right', va='top',
               fontsize=10, color='white',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#333333', alpha=0.8))
        
        # Progress bar (bottom)
        bar_y = -0.05
        ax.axhline(y=-2, xmin=0.1, xmax=0.9, color='gray', linewidth=4, transform=ax.transAxes)
        ax.axhline(y=-2, xmin=0.1, xmax=0.1 + 0.8*progress, color=self.colors['ball'], 
                  linewidth=4, transform=ax.transAxes)
        
        # Time display
        time_sec = (current_frame - all_frames[0]) * 0.1  # 10Hz = 100ms per frame
        ax.text(0.5, -0.08, f"Time: {time_sec:.1f}s",
               transform=ax.transAxes, ha='center', va='top',
               fontsize=10, color='white',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#333333', alpha=0.8))
        
        # RAI legend (bottom left)
        if rai_scores is not None:
            legend_text = "● High RAI (good reaction)\n● Low RAI (slow reaction)"
            ax.text(0.02, 0.02, legend_text,
                   transform=ax.transAxes, ha='left', va='bottom',
                   fontsize=8, color='white',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='#333333', alpha=0.8))
    
    def create_highlight_reel(self,
                               plays: List[Dict],
                               filename: str = 'highlight_reel.mp4') -> Path:
        """
        Create a highlight reel from multiple plays.
        
        Args:
            plays: List of dicts with play data and metadata
            filename: Output filename
            
        Returns:
            Path to created video
        """
        output_path = self.output_dir / filename
        all_frames = []
        
        for i, play in enumerate(tqdm(plays, desc="Processing plays")):
            # Generate frames for each play
            frames = sorted(play['output_df']['frame_id'].unique())
            
            for frame_id in frames:
                fig = self._create_frame(
                    play['input_df'],
                    play['output_df'],
                    frame_id,
                    frames,
                    play['ball_x'],
                    play['ball_y'],
                    play.get('x_min', 20),
                    play.get('x_max', 100),
                    play.get('rai_scores'),
                    play.get('title', f'Play {i+1}')
                )
                
                fig.canvas.draw()
                image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
                image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
                all_frames.append(image)
                
                plt.close(fig)
            
            # Add transition frames (brief pause between plays)
            if i < len(plays) - 1:
                all_frames.extend([all_frames[-1]] * 5)  # 0.5 second pause
        
        # Write video
        imageio.mimwrite(output_path, all_frames, fps=self.fps)
        print(f"✓ Highlight reel saved: {output_path}")
        
        return output_path
    
    def create_comparison_video(self,
                                 play_data: Dict,
                                 fast_player_id: int,
                                 slow_player_id: int,
                                 filename: str = 'reaction_comparison.mp4') -> Path:
        """
        Create side-by-side comparison of fast vs slow reacting players.
        
        Args:
            play_data: Play tracking data
            fast_player_id: NFL ID of fast-reacting player
            slow_player_id: NFL ID of slow-reacting player
            filename: Output filename
            
        Returns:
            Path to video
        """
        output_path = self.output_dir / filename
        
        output_df = play_data['output_df']
        frames = sorted(output_df['frame_id'].unique())
        
        image_frames = []
        
        for frame_id in tqdm(frames, desc="Rendering comparison"):
            fig, axes = plt.subplots(1, 2, figsize=(18, 8))
            
            for ax, player_id, title in zip(
                axes,
                [fast_player_id, slow_player_id],
                ['Fast Reaction', 'Slow Reaction']
            ):
                # Create field
                self.field_plotter.create_field(ax)
                
                # Get player data
                player_data = output_df[output_df['nfl_id'] == player_id]
                current = player_data[player_data['frame_id'] <= frame_id]
                
                if len(current) > 0:
                    # Trail
                    trail = current[['x', 'y']].values
                    ax.plot(trail[:, 0], trail[:, 1], 'b-', linewidth=3, alpha=0.5)
                    
                    # Current position
                    last = current.iloc[-1]
                    ax.scatter(last['x'], last['y'], c='blue', s=400, zorder=5)
                
                ax.set_title(title, fontsize=14, fontweight='bold')
            
            fig.suptitle(f'Reaction Comparison - Frame {frame_id}', 
                        fontsize=16, fontweight='bold')
            
            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
            image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            image_frames.append(image)
            
            plt.close(fig)
        
        imageio.mimwrite(output_path, image_frames, fps=self.fps)
        print(f"✓ Comparison video saved: {output_path}")
        
        return output_path


if __name__ == "__main__":
    print("Video generator module loaded successfully!")
    print("Use VideoGenerator class to create broadcast-quality animations.")
