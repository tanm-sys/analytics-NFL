"""
NFL Big Data Bowl 2026 - Feature Engineering Module

Calculates physics-based features from tracking data:
- Velocity vectors (vx, vy, speed, direction)
- Acceleration (ax, ay, magnitude)
- Jerk (rate of acceleration change)
- Path curvature and efficiency
- Distance and separation metrics
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple, List
from scipy.ndimage import gaussian_filter1d


class FeatureEngineer:
    """
    Calculates derived physics and movement features from tracking data.
    
    All calculations assume 10Hz sampling rate (100ms between frames).
    """
    
    FRAME_RATE = 10  # Hz
    FRAME_INTERVAL = 0.1  # seconds
    
    def __init__(self, smooth_sigma: float = 1.0):
        """
        Initialize feature engineer.
        
        Args:
            smooth_sigma: Gaussian smoothing sigma for velocity/acceleration
        """
        self.smooth_sigma = smooth_sigma
        
    def calculate_velocity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate velocity vectors from position data.
        
        Args:
            df: DataFrame with x, y columns, sorted by frame_id
            
        Returns:
            DataFrame with added vx, vy, speed, direction_calc columns
        """
        df = df.copy()
        
        # Calculate position differences
        df['dx'] = df['x'].diff()
        df['dy'] = df['y'].diff()
        
        # Convert to velocity (yards per second)
        df['vx'] = df['dx'] / self.FRAME_INTERVAL
        df['vy'] = df['dy'] / self.FRAME_INTERVAL
        
        # Smooth velocities
        if len(df) > 3:
            df['vx'] = gaussian_filter1d(df['vx'].fillna(0), sigma=self.smooth_sigma)
            df['vy'] = gaussian_filter1d(df['vy'].fillna(0), sigma=self.smooth_sigma)
        
        # Calculate speed magnitude
        df['speed_calc'] = np.sqrt(df['vx']**2 + df['vy']**2)
        
        # Calculate direction (in degrees, 0 = right, 90 = up)
        df['direction_calc'] = np.degrees(np.arctan2(df['vy'], df['vx'])) % 360
        
        return df
    
    def calculate_acceleration(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate acceleration from velocity data.
        
        Args:
            df: DataFrame with vx, vy columns
            
        Returns:
            DataFrame with added ax, ay, accel_magnitude columns
        """
        df = df.copy()
        
        # Calculate velocity differences
        df['dvx'] = df['vx'].diff()
        df['dvy'] = df['vy'].diff()
        
        # Convert to acceleration (yards per second^2)
        df['ax'] = df['dvx'] / self.FRAME_INTERVAL
        df['ay'] = df['dvy'] / self.FRAME_INTERVAL
        
        # Smooth accelerations
        if len(df) > 3:
            df['ax'] = gaussian_filter1d(df['ax'].fillna(0), sigma=self.smooth_sigma)
            df['ay'] = gaussian_filter1d(df['ay'].fillna(0), sigma=self.smooth_sigma)
        
        # Calculate acceleration magnitude
        df['accel_magnitude'] = np.sqrt(df['ax']**2 + df['ay']**2)
        
        return df
    
    def calculate_jerk(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate jerk (rate of acceleration change) - key reaction indicator.
        
        High jerk indicates sudden changes in motion (reactions).
        
        Args:
            df: DataFrame with ax, ay columns
            
        Returns:
            DataFrame with added jx, jy, jerk_magnitude columns
        """
        df = df.copy()
        
        # Calculate acceleration differences
        df['dax'] = df['ax'].diff()
        df['day'] = df['ay'].diff()
        
        # Convert to jerk (yards per second^3)
        df['jx'] = df['dax'] / self.FRAME_INTERVAL
        df['jy'] = df['day'] / self.FRAME_INTERVAL
        
        # Calculate jerk magnitude
        df['jerk_magnitude'] = np.sqrt(df['jx']**2 + df['jy']**2)
        
        return df
    
    def calculate_path_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate path efficiency and curvature metrics.
        
        Args:
            df: DataFrame with x, y columns
            
        Returns:
            DataFrame with added path_length, straight_line_dist, path_efficiency, curvature
        """
        df = df.copy()
        
        if len(df) < 2:
            df['path_length'] = 0
            df['straight_line_dist'] = 0
            df['path_efficiency'] = 1.0
            df['curvature'] = 0
            return df
        
        # Calculate frame-to-frame distances
        df['frame_dist'] = np.sqrt(df['x'].diff()**2 + df['y'].diff()**2)
        
        # Cumulative path length
        df['path_length'] = df['frame_dist'].cumsum()
        
        # Straight-line distance from start
        start_x, start_y = df['x'].iloc[0], df['y'].iloc[0]
        df['straight_line_dist'] = np.sqrt((df['x'] - start_x)**2 + (df['y'] - start_y)**2)
        
        # Path efficiency (1.0 = perfectly straight)
        df['path_efficiency'] = np.where(
            df['path_length'] > 0.1,  # Avoid division by zero
            df['straight_line_dist'] / df['path_length'],
            1.0
        )
        
        # Curvature (change in direction per unit distance)
        if 'direction_calc' in df.columns:
            dir_diff = df['direction_calc'].diff()
            # Handle wrap-around at 360/0
            dir_diff = ((dir_diff + 180) % 360) - 180
            df['curvature'] = np.abs(dir_diff) / (df['frame_dist'] + 0.01)
        else:
            df['curvature'] = 0
            
        return df
    
    def calculate_distance_to_point(self, df: pd.DataFrame, 
                                     target_x: float, target_y: float,
                                     col_name: str = 'dist_to_target') -> pd.DataFrame:
        """
        Calculate distance from player to a target point (e.g., ball landing).
        
        Args:
            df: DataFrame with x, y columns
            target_x, target_y: Target coordinates
            col_name: Name for the distance column
            
        Returns:
            DataFrame with added distance column
        """
        df = df.copy()
        df[col_name] = np.sqrt((df['x'] - target_x)**2 + (df['y'] - target_y)**2)
        return df
    
    def calculate_player_separation(self, df1: pd.DataFrame, df2: pd.DataFrame,
                                     merge_on: str = 'frame_id') -> pd.DataFrame:
        """
        Calculate separation distance between two players.
        
        Args:
            df1, df2: DataFrames for two different players with x, y, frame_id
            merge_on: Column to merge on (typically frame_id)
            
        Returns:
            DataFrame with frame_id and separation distance
        """
        merged = df1[[merge_on, 'x', 'y']].merge(
            df2[[merge_on, 'x', 'y']],
            on=merge_on,
            suffixes=('_1', '_2')
        )
        
        merged['separation'] = np.sqrt(
            (merged['x_1'] - merged['x_2'])**2 + 
            (merged['y_1'] - merged['y_2'])**2
        )
        
        return merged[[merge_on, 'separation']]
    
    def calculate_closing_speed(self, df1: pd.DataFrame, df2: pd.DataFrame,
                                 merge_on: str = 'frame_id') -> pd.DataFrame:
        """
        Calculate closing speed between two players.
        
        Positive = players getting closer, Negative = separating
        
        Args:
            df1, df2: DataFrames for two players
            merge_on: Column to merge on
            
        Returns:
            DataFrame with frame_id and closing_speed
        """
        separation = self.calculate_player_separation(df1, df2, merge_on)
        separation['closing_speed'] = -separation['separation'].diff() / self.FRAME_INTERVAL
        
        return separation[[merge_on, 'separation', 'closing_speed']]
    
    def process_player_tracking(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature calculations to player tracking data.
        
        Args:
            df: Raw tracking DataFrame for a single player, sorted by frame_id
            
        Returns:
            DataFrame with all derived features
        """
        df = df.sort_values('frame_id').copy()
        
        # Calculate all features in sequence
        df = self.calculate_velocity(df)
        df = self.calculate_acceleration(df)
        df = self.calculate_jerk(df)
        df = self.calculate_path_metrics(df)
        
        return df
    
    def detect_reaction_frame(self, df: pd.DataFrame, 
                               threshold: float = 5.0,
                               min_frames: int = 2) -> Optional[int]:
        """
        Detect the frame where player shows significant reaction.
        
        Reaction defined as sustained jerk or acceleration above threshold.
        
        Args:
            df: DataFrame with jerk_magnitude column
            threshold: Jerk threshold for reaction detection
            min_frames: Minimum consecutive frames above threshold
            
        Returns:
            Frame number of detected reaction, or None
        """
        if 'jerk_magnitude' not in df.columns:
            df = self.process_player_tracking(df)
            
        jerk = df['jerk_magnitude'].values
        frames = df['frame_id'].values
        
        # Find first sustained region above threshold
        above_thresh = jerk > threshold
        
        for i in range(len(above_thresh) - min_frames + 1):
            if all(above_thresh[i:i + min_frames]):
                return int(frames[i])
                
        return None
    
    def calculate_break_quality(self, df: pd.DataFrame,
                                 break_frame: Optional[int] = None) -> float:
        """
        Calculate route break quality for receivers.
        
        Measures angle sharpness × speed maintenance at break point.
        
        Args:
            df: Player tracking DataFrame
            break_frame: Known break frame, or auto-detect
            
        Returns:
            Break quality score (0-1, higher is better)
        """
        if 'curvature' not in df.columns:
            df = self.process_player_tracking(df)
        
        if len(df) < 3:
            return 0.5
            
        # Handle NaN in curvature
        curvature_valid = df['curvature'].dropna()
        if len(curvature_valid) == 0:
            return 0.5
            
        if break_frame is None:
            # Detect break as max curvature point
            break_idx = curvature_valid.idxmax()
        else:
            break_idx = df[df['frame_id'] == break_frame].index
            if len(break_idx) == 0:
                return 0.5
            break_idx = break_idx[0]
        
        # Get position in dataframe
        df_reset = df.reset_index(drop=True)
        try:
            pos = df.index.get_loc(break_idx)
        except KeyError:
            return 0.5
            
        # Get speed before and after break
        window = 3  # frames
        pre_start = max(0, pos - window)
        post_end = min(len(df_reset), pos + window + 1)
        
        pre_speeds = df_reset.iloc[pre_start:pos]['speed_calc'].dropna()
        post_speeds = df_reset.iloc[pos:post_end]['speed_calc'].dropna()
        
        pre_speed = pre_speeds.mean() if len(pre_speeds) > 0 else 0.0
        post_speed = post_speeds.mean() if len(post_speeds) > 0 else 0.0
        
        # Speed maintenance ratio (capped at 1.0)
        if pre_speed < 0.1:
            speed_maintenance = 0.5  # Default if not moving
        else:
            speed_maintenance = min(post_speed / (pre_speed + 0.1), 1.0)
        
        # Curvature at break (normalized)
        try:
            curvature = df.loc[break_idx, 'curvature']
            if pd.isna(curvature):
                curvature = 0.0
        except (KeyError, IndexError):
            curvature = 0.0
            
        curvature_score = min(curvature / 50, 1.0)  # Normalize to 0-1
        
        # Combined score
        break_quality = 0.6 * speed_maintenance + 0.4 * curvature_score
        
        return float(break_quality)


def run_unit_tests():
    """Run unit tests on feature engineering calculations."""
    print("Running feature engineering unit tests...")
    
    fe = FeatureEngineer()
    
    # Test 1: Basic velocity calculation
    test_df = pd.DataFrame({
        'frame_id': [1, 2, 3, 4, 5],
        'x': [0, 1, 2, 3, 4],
        'y': [0, 0, 0, 0, 0]
    })
    result = fe.calculate_velocity(test_df)
    
    # Speed should be ~10 yards/second for 1 yard per 0.1 seconds
    assert 'speed_calc' in result.columns, "Speed column not found"
    assert result['speed_calc'].iloc[2] > 9 and result['speed_calc'].iloc[2] < 11, \
        f"Speed calculation incorrect: {result['speed_calc'].iloc[2]}"
    
    # Test 2: Path efficiency for straight line
    result = fe.process_player_tracking(test_df)
    assert result['path_efficiency'].iloc[-1] > 0.99, \
        f"Path efficiency for straight line should be ~1.0, got {result['path_efficiency'].iloc[-1]}"
    
    # Test 3: Path efficiency for curved path
    curved_df = pd.DataFrame({
        'frame_id': [1, 2, 3, 4, 5],
        'x': [0, 1, 2, 2, 2],
        'y': [0, 0, 0, 1, 2]
    })
    result = fe.process_player_tracking(curved_df)
    assert result['path_efficiency'].iloc[-1] < 0.95, \
        f"Path efficiency for curved path should be < 0.95, got {result['path_efficiency'].iloc[-1]}"
    
    print("✓ All unit tests passed!")
    return True


if __name__ == "__main__":
    run_unit_tests()
