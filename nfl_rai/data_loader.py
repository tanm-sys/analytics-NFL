"""
NFL Big Data Bowl 2026 - Data Loading Module

Handles loading and preprocessing of tracking data from all weeks.
Creates unified dataset with input (pre-throw) and output (post-throw) data.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict, List
from tqdm import tqdm


class NFLDataLoader:
    """
    Comprehensive data loader for NFL tracking data.
    
    Loads input (pre-throw state), output (post-throw positions),
    and supplementary play-level data.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the data loader.
        
        Args:
            data_dir: Path to the analytics-NFL directory
        """
        if data_dir is None:
            # Default to the directory containing train folder
            data_dir = Path(__file__).parent.parent
        self.data_dir = Path(data_dir)
        self.train_dir = self.data_dir / "train"
        
        # Data containers
        self.input_data: Optional[pd.DataFrame] = None
        self.output_data: Optional[pd.DataFrame] = None
        self.supplementary_data: Optional[pd.DataFrame] = None
        self.merged_data: Optional[pd.DataFrame] = None
        
    def load_all_weeks(self, weeks: List[int] = None, verbose: bool = True) -> pd.DataFrame:
        """
        Load all weeks of tracking data.
        
        Args:
            weeks: List of weeks to load (1-18). None = all weeks.
            verbose: Show progress bar
            
        Returns:
            Merged DataFrame with all tracking data
        """
        if weeks is None:
            weeks = list(range(1, 19))  # Weeks 1-18
            
        input_dfs = []
        output_dfs = []
        
        iterator = tqdm(weeks, desc="Loading weeks") if verbose else weeks
        
        for week in iterator:
            week_str = f"w{week:02d}"
            
            # Load input file
            input_file = self.train_dir / f"input_2023_{week_str}.csv"
            if input_file.exists():
                df_input = pd.read_csv(input_file)
                df_input['week'] = week
                input_dfs.append(df_input)
                
            # Load output file  
            output_file = self.train_dir / f"output_2023_{week_str}.csv"
            if output_file.exists():
                df_output = pd.read_csv(output_file)
                df_output['week'] = week
                output_dfs.append(df_output)
                
        # Concatenate all weeks
        self.input_data = pd.concat(input_dfs, ignore_index=True)
        self.output_data = pd.concat(output_dfs, ignore_index=True)
        
        if verbose:
            print(f"Loaded {len(self.input_data):,} input records from {len(weeks)} weeks")
            print(f"Loaded {len(self.output_data):,} output records")
            
        return self.input_data
    
    def load_supplementary(self) -> pd.DataFrame:
        """Load supplementary play-level data."""
        supp_file = self.data_dir / "supplementary_data.csv"
        
        if supp_file.exists():
            self.supplementary_data = pd.read_csv(supp_file)
            print(f"Loaded {len(self.supplementary_data):,} supplementary records")
        else:
            raise FileNotFoundError(f"Supplementary data not found: {supp_file}")
            
        return self.supplementary_data
    
    def create_play_dataset(self) -> pd.DataFrame:
        """
        Create a comprehensive play-level dataset by merging all sources.
        
        Returns:
            DataFrame with one row per play, containing aggregated metrics
        """
        if self.input_data is None:
            self.load_all_weeks()
        if self.supplementary_data is None:
            self.load_supplementary()
            
        # Get unique plays
        plays = self.input_data.groupby(['game_id', 'play_id']).agg({
            'num_frames_output': 'first',
            'ball_land_x': 'first',
            'ball_land_y': 'first',
            'play_direction': 'first',
            'absolute_yardline_number': 'first',
            'week': 'first'
        }).reset_index()
        
        # Merge with supplementary data
        self.merged_data = plays.merge(
            self.supplementary_data,
            on=['game_id', 'play_id'],
            how='left'
        )
        
        print(f"Created dataset with {len(self.merged_data):,} plays")
        return self.merged_data
    
    def get_play_tracking(self, game_id: int, play_id: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get input and output tracking data for a specific play.
        
        Args:
            game_id: Game identifier
            play_id: Play identifier
            
        Returns:
            Tuple of (input_df, output_df) for the specified play
        """
        if self.input_data is None:
            self.load_all_weeks()
            
        input_play = self.input_data[
            (self.input_data['game_id'] == game_id) & 
            (self.input_data['play_id'] == play_id)
        ].copy()
        
        output_play = self.output_data[
            (self.output_data['game_id'] == game_id) & 
            (self.output_data['play_id'] == play_id)
        ].copy()
        
        return input_play, output_play
    
    def get_player_frames(self, game_id: int, play_id: int, nfl_id: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get frame-by-frame data for a specific player in a play.
        
        Args:
            game_id: Game identifier
            play_id: Play identifier
            nfl_id: Player identifier
            
        Returns:
            Tuple of (input_frames, output_frames) for the player
        """
        input_play, output_play = self.get_play_tracking(game_id, play_id)
        
        input_player = input_play[input_play['nfl_id'] == nfl_id].sort_values('frame_id')
        output_player = output_play[output_play['nfl_id'] == nfl_id].sort_values('frame_id')
        
        return input_player, output_player
    
    def standardize_coordinates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize field coordinates so all plays go left-to-right.
        
        Args:
            df: DataFrame with x, y columns and play_direction
            
        Returns:
            DataFrame with standardized coordinates
        """
        df = df.copy()
        
        # Flip x-coordinate for plays going right-to-left
        mask = df['play_direction'] == 'left'
        df.loc[mask, 'x'] = 120 - df.loc[mask, 'x']
        
        # Flip y-coordinate to maintain player relative positions
        df.loc[mask, 'y'] = 53.3 - df.loc[mask, 'y']
        
        # Adjust direction and orientation
        if 'dir' in df.columns:
            df.loc[mask, 'dir'] = (180 - df.loc[mask, 'dir']) % 360
        if 'o' in df.columns:
            df.loc[mask, 'o'] = (180 - df.loc[mask, 'o']) % 360
            
        return df
    
    def get_players_to_predict(self, game_id: int, play_id: int) -> List[int]:
        """Get list of NFL IDs for players that need predictions."""
        if self.input_data is None:
            self.load_all_weeks()
            
        play_data = self.input_data[
            (self.input_data['game_id'] == game_id) & 
            (self.input_data['play_id'] == play_id) &
            (self.input_data['player_to_predict'] == True)
        ]
        
        return play_data['nfl_id'].unique().tolist()
    
    def get_play_metadata(self, game_id: int, play_id: int) -> Dict:
        """Get metadata for a specific play from supplementary data."""
        if self.supplementary_data is None:
            self.load_supplementary()
            
        play_row = self.supplementary_data[
            (self.supplementary_data['game_id'] == game_id) &
            (self.supplementary_data['play_id'] == play_id)
        ]
        
        if len(play_row) == 0:
            return {}
            
        return play_row.iloc[0].to_dict()
    
    def summary_stats(self) -> Dict:
        """Get summary statistics of loaded data."""
        if self.input_data is None:
            return {"error": "No data loaded. Call load_all_weeks() first."}
            
        stats = {
            "total_input_records": len(self.input_data),
            "total_output_records": len(self.output_data) if self.output_data is not None else 0,
            "total_plays": self.input_data.groupby(['game_id', 'play_id']).ngroups,
            "total_games": self.input_data['game_id'].nunique(),
            "weeks_loaded": sorted(self.input_data['week'].unique().tolist()),
            "unique_players": self.input_data['nfl_id'].nunique(),
            "player_roles": self.input_data['player_role'].value_counts().to_dict() if 'player_role' in self.input_data.columns else {},
        }
        
        if self.supplementary_data is not None:
            stats["coverage_types"] = self.supplementary_data['team_coverage_type'].value_counts().to_dict()
            stats["formations"] = self.supplementary_data['offense_formation'].value_counts().to_dict()
            
        return stats


def load_all_weeks(data_dir: str = None) -> pd.DataFrame:
    """Convenience function to load all weeks."""
    loader = NFLDataLoader(data_dir)
    return loader.load_all_weeks()


if __name__ == "__main__":
    # Test the data loader
    loader = NFLDataLoader()
    loader.load_all_weeks()
    loader.load_supplementary()
    
    stats = loader.summary_stats()
    print("\n=== Data Summary ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
