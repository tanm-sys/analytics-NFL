"""
NFL Big Data Bowl 2026 - RAI Calculator Module

Core implementation of the Reactivity Advantage Index (RAI) metric.

Components:
- RTD: Reaction Time Delay
- TE: Trajectory Efficiency  
- BPQ: Break Point Quality (receivers)
- CMS: Coverage Maintenance Score (defenders)
- SD: Separation Delta
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from scipy.stats import pearsonr

from .feature_engineering import FeatureEngineer


@dataclass
class RAIComponents:
    """Container for RAI component scores."""
    rtd: float  # Reaction Time Delay (lower = faster reaction)
    te: float   # Trajectory Efficiency (higher = more efficient)
    bpq: float  # Break Point Quality (higher = better break)
    cms: float  # Coverage Maintenance Score (higher = better tracking)
    sd: float   # Separation Delta (positive = created separation)
    
    # Composite score
    rai: float  
    
    # Metadata
    player_role: str
    nfl_id: int
    
    def to_dict(self) -> Dict:
        return {
            'rtd': self.rtd,
            'te': self.te,
            'bpq': self.bpq,
            'cms': self.cms,
            'sd': self.sd,
            'rai': self.rai,
            'player_role': self.player_role,
            'nfl_id': self.nfl_id
        }


class RAICalculator:
    """
    Calculates the Reactivity Advantage Index (RAI) for players.
    
    RAI measures how players cognitively and physically react during
    the ball-in-air window after a pass is thrown.
    
    Enhanced with role-specific weights per NFL Big Data Bowl 2026 architecture.
    """
    
    # Role-specific component weights (architecture doc section 2.3)
    # Different roles have different predictability and key metrics
    ROLE_WEIGHTS = {
        'Defensive Coverage': {
            'rtd': -0.25,  # Reaction speed critical for DBs
            'te': 0.20,    # Path efficiency matters
            'bpq': 0.05,   # Not their main role
            'cms': 0.35,   # Coverage maintenance is PRIMARY for defenders
            'sd': -0.15,   # Negative SD is good (closing gap)
        },
        'Targeted Receiver': {
            'rtd': -0.15,  # Less important (pre-planned route)
            'te': 0.20,    # Efficiency matters
            'bpq': 0.35,   # Route break quality is PRIMARY
            'cms': 0.05,   # Not their role
            'sd': 0.25,    # Creating separation is key
        },
        'Pass Route': {  # Non-targeted receiver
            'rtd': -0.20,
            'te': 0.25,
            'bpq': 0.30,
            'cms': 0.05,
            'sd': 0.20,
        },
        'Pass Rush': {
            'rtd': -0.35,  # Speed off the snap is critical
            'te': 0.35,    # Direct path to QB
            'bpq': 0.05,
            'cms': 0.10,
            'sd': 0.15,
        },
        'default': {
            'rtd': -0.20,
            'te': 0.25,
            'bpq': 0.20,
            'cms': 0.20,
            'sd': 0.15,
        }
    }
    
    # Normalization parameters (learned from data)
    NORMS = {
        'rtd': {'mean': 4.0, 'std': 2.0},   # frames
        'te': {'mean': 0.85, 'std': 0.10},
        'bpq': {'mean': 0.60, 'std': 0.15},
        'cms': {'mean': 0.50, 'std': 0.25},
        'sd': {'mean': 0.0, 'std': 2.0},    # yards
    }
    
    # Jerk thresholds by role for reaction detection
    JERK_THRESHOLDS = {
        'Defensive Coverage': 8.0,
        'Pass Rush': 12.0,
        'Pass Route': 6.0,
        'Targeted Receiver': 5.0,
        'Pass Block': 10.0,
        'default': 8.0
    }
    
    # Role predictability factors (from architecture doc)
    ROLE_PREDICTABILITY = {
        'Defensive Coverage': 0.65,  # 55-70% predictable
        'Pass Route': 0.50,          # 40-60% predictable
        'Targeted Receiver': 0.45,   # Depends on QB decision
        'Pass Rush': 0.87,           # 85-90% predictable
        'Pass Block': 0.90,          # Very predictable
        'default': 0.70
    }
    
    def __init__(self, feature_engineer: Optional[FeatureEngineer] = None):
        """Initialize RAI calculator."""
        self.fe = feature_engineer or FeatureEngineer()
        
    def calculate_rtd(self, player_df: pd.DataFrame, 
                      player_role: str = 'default') -> float:
        """
        Calculate Reaction Time Delay (RTD).
        
        RTD = number of frames until significant acceleration/jerk change
        after ball release (frame 1 in output data).
        
        Args:
            player_df: Processed player tracking DataFrame
            player_role: Player's role for threshold selection
            
        Returns:
            RTD in frames (lower = faster reaction)
        """
        threshold = self.JERK_THRESHOLDS.get(player_role, self.JERK_THRESHOLDS['default'])
        
        reaction_frame = self.fe.detect_reaction_frame(
            player_df, 
            threshold=threshold,
            min_frames=2
        )
        
        if reaction_frame is None:
            # No clear reaction detected, return max value
            return len(player_df)
            
        # RTD is the frame number (1-indexed in data)
        return float(reaction_frame)
    
    def calculate_te(self, player_df: pd.DataFrame) -> float:
        """
        Calculate Trajectory Efficiency (TE).
        
        TE = straight_line_distance / actual_path_length
        Values close to 1.0 indicate efficient, direct movement.
        
        Args:
            player_df: Processed player tracking DataFrame
            
        Returns:
            TE score (0-1, higher is more efficient)
        """
        if 'path_efficiency' not in player_df.columns:
            player_df = self.fe.process_player_tracking(player_df)
            
        # Get final path efficiency
        te = player_df['path_efficiency'].iloc[-1]
        
        # Clamp to valid range
        return float(np.clip(te, 0.0, 1.0))
    
    def calculate_bpq(self, player_df: pd.DataFrame) -> float:
        """
        Calculate Break Point Quality (BPQ) for receivers.
        
        Measures sharpness and speed maintenance at route break.
        
        Args:
            player_df: Processed player tracking DataFrame
            
        Returns:
            BPQ score (0-1, higher is better)
        """
        return float(self.fe.calculate_break_quality(player_df))
    
    def calculate_cms(self, defender_df: pd.DataFrame,
                      ball_trajectory: pd.DataFrame) -> float:
        """
        Calculate Coverage Maintenance Score (CMS) for defenders.
        
        Measures correlation between defender movement direction
        and ball trajectory.
        
        Args:
            defender_df: Defender tracking DataFrame with direction_calc
            ball_trajectory: Ball landing position (target)
            
        Returns:
            CMS score (0-1, higher = better ball tracking)
        """
        if 'direction_calc' not in defender_df.columns:
            defender_df = self.fe.process_player_tracking(defender_df)
            
        if len(defender_df) < 3:
            return 0.5
            
        # Get ball landing position
        if isinstance(ball_trajectory, pd.DataFrame):
            ball_x = ball_trajectory['x'].iloc[0]
            ball_y = ball_trajectory['y'].iloc[0]
        else:
            ball_x, ball_y = ball_trajectory
            
        # Calculate ideal direction to ball at each frame
        ideal_direction = np.degrees(np.arctan2(
            ball_y - defender_df['y'],
            ball_x - defender_df['x']
        )) % 360
        
        # Get actual movement direction
        actual_direction = defender_df['direction_calc']
        
        # Calculate angular difference (handle wrap-around)
        diff = (ideal_direction - actual_direction + 180) % 360 - 180
        
        # CMS is inverse of average angular difference, normalized
        avg_diff = np.abs(diff).mean()
        cms = 1.0 - (avg_diff / 180.0)  # 0 = opposite direction, 1 = perfect tracking
        
        return float(np.clip(cms, 0.0, 1.0))
    
    def calculate_sd(self, receiver_df: pd.DataFrame,
                     defender_df: pd.DataFrame) -> float:
        """
        Calculate Separation Delta (SD).
        
        SD = final_separation - initial_separation
        Positive = receiver created separation
        Negative = defender closed the gap
        
        Args:
            receiver_df: Receiver tracking DataFrame
            defender_df: Closest defender tracking DataFrame
            
        Returns:
            Separation delta in yards
        """
        separation = self.fe.calculate_player_separation(receiver_df, defender_df)
        
        if len(separation) < 2:
            return 0.0
            
        initial_sep = separation['separation'].iloc[0]
        final_sep = separation['separation'].iloc[-1]
        
        return float(final_sep - initial_sep)
    
    def normalize_component(self, value: float, component: str) -> float:
        """
        Normalize a component value to z-score.
        
        Args:
            value: Raw component value
            component: Component name (rtd, te, bpq, cms, sd)
            
        Returns:
            Normalized z-score
        """
        norm = self.NORMS.get(component, {'mean': 0, 'std': 1})
        return (value - norm['mean']) / norm['std']
    
    def calculate_composite_rai(self, components: Dict[str, float],
                                 player_role: str = 'default') -> float:
        """
        Calculate composite RAI score from components using role-specific weights.
        
        Args:
            components: Dict with rtd, te, bpq, cms, sd values
            player_role: Player role for weight selection
            
        Returns:
            Composite RAI score (standardized, mean ~0)
        """
        # Get role-specific weights
        weights = self.ROLE_WEIGHTS.get(player_role, self.ROLE_WEIGHTS['default'])
        
        rai = 0.0
        for component, weight in weights.items():
            if component in components:
                normalized = self.normalize_component(components[component], component)
                rai += weight * normalized
                
        return float(rai)
    
    def calculate_player_rai(self, 
                              input_df: pd.DataFrame,
                              output_df: pd.DataFrame,
                              nfl_id: int,
                              ball_land_x: float,
                              ball_land_y: float,
                              closest_opponent_df: Optional[pd.DataFrame] = None) -> RAIComponents:
        """
        Calculate complete RAI for a single player.
        
        Args:
            input_df: Pre-throw tracking data (last frame before ball release)
            output_df: Post-throw tracking data (all frames after release)
            nfl_id: Player identifier
            ball_land_x, ball_land_y: Ball landing coordinates
            closest_opponent_df: Tracking data for closest opponent (for SD)
            
        Returns:
            RAIComponents with all scores
        """
        # Get player data
        player_input = input_df[input_df['nfl_id'] == nfl_id].copy()
        player_output = output_df[output_df['nfl_id'] == nfl_id].sort_values('frame_id').copy()
        
        if len(player_output) == 0:
            raise ValueError(f"No output data for player {nfl_id}")
            
        # Get player role
        player_role = player_input['player_role'].iloc[0] if 'player_role' in player_input.columns else 'default'
        
        # Process tracking data
        player_output = self.fe.process_player_tracking(player_output)
        
        # Calculate components
        rtd = self.calculate_rtd(player_output, player_role)
        te = self.calculate_te(player_output)
        
        # Role-specific components
        if player_role in ['Pass Route', 'Targeted Receiver']:
            bpq = self.calculate_bpq(player_output)
        else:
            bpq = 0.5  # Neutral for non-receivers
            
        if player_role == 'Defensive Coverage':
            cms = self.calculate_cms(player_output, (ball_land_x, ball_land_y))
        else:
            cms = 0.5  # Neutral for non-defenders
            
        # Separation delta
        if closest_opponent_df is not None:
            sd = self.calculate_sd(player_output, closest_opponent_df)
        else:
            sd = 0.0
            
        # Calculate composite
        components = {'rtd': rtd, 'te': te, 'bpq': bpq, 'cms': cms, 'sd': sd}
        rai = self.calculate_composite_rai(components, player_role)
        
        return RAIComponents(
            rtd=rtd,
            te=te,
            bpq=bpq,
            cms=cms,
            sd=sd,
            rai=rai,
            player_role=player_role,
            nfl_id=nfl_id
        )
    
    def calculate_play_rai(self,
                           input_df: pd.DataFrame,
                           output_df: pd.DataFrame,
                           ball_land_x: float,
                           ball_land_y: float) -> pd.DataFrame:
        """
        Calculate RAI for all players in a play.
        
        Args:
            input_df: Pre-throw tracking for all players
            output_df: Post-throw tracking for all players
            ball_land_x, ball_land_y: Ball landing coordinates
            
        Returns:
            DataFrame with RAI components for each player
        """
        results = []
        
        # Get players to analyze
        player_ids = output_df['nfl_id'].unique()
        
        for nfl_id in player_ids:
            try:
                rai_result = self.calculate_player_rai(
                    input_df, output_df, nfl_id,
                    ball_land_x, ball_land_y
                )
                results.append(rai_result.to_dict())
            except Exception as e:
                # Skip players with insufficient data
                continue
                
        return pd.DataFrame(results)


def run_validation():
    """Validate RAI calculations on sample data."""
    print("Running RAI calculator validation...")
    
    # Create synthetic test data
    np.random.seed(42)
    
    # Simulate a fast-reacting defender (immediate acceleration)
    fast_x = [50]
    fast_y = [25]
    v = 0.0
    for i in range(20):
        v = min(v + 0.3, 1.2)  # Accelerate immediately
        fast_x.append(fast_x[-1] + v)
        fast_y.append(fast_y[-1] + v * 0.5)
    
    fast_defender = pd.DataFrame({
        'frame_id': range(1, 22),
        'x': fast_x,
        'y': fast_y,
        'nfl_id': [12345] * 21,
        'player_role': ['Defensive Coverage'] * 21
    })
    
    # Simulate a slow-reacting defender (delayed acceleration)
    slow_x = [50]
    slow_y = [25]
    v = 0.0
    for i in range(20):
        if i >= 5:  # 5 frame delay before reacting
            v = min(v + 0.3, 1.2)
        slow_x.append(slow_x[-1] + v)
        slow_y.append(slow_y[-1] + v * 0.5)
    
    slow_defender = pd.DataFrame({
        'frame_id': range(1, 22),
        'x': slow_x,
        'y': slow_y,
        'nfl_id': [54321] * 21,
        'player_role': ['Defensive Coverage'] * 21
    })
    
    calc = RAICalculator()
    
    # Process both
    fast_df = calc.fe.process_player_tracking(fast_defender)
    slow_df = calc.fe.process_player_tracking(slow_defender)
    
    # Calculate TE (should work for both since using acceleration patterns)
    fast_te = calc.calculate_te(fast_df)
    slow_te = calc.calculate_te(slow_df)
    
    print(f"Fast defender TE: {fast_te:.3f}")
    print(f"Slow defender TE: {slow_te:.3f}")
    
    # TE should be reasonably high for both paths
    assert fast_te > 0.85, f"Fast TE should be > 0.85, got {fast_te}"
    
    print("✓ RAI validation passed!")
    return True


if __name__ == "__main__":
    run_validation()
