#!/usr/bin/env python3
"""
NFL Big Data Bowl 2026 - Reactivity Advantage Index (RAI) Analysis

Main analysis script that:
1. Loads all tracking data
2. Calculates RAI for all plays
3. Generates key insights
4. Creates visualizations for the competition submission

Usage:
    python analysis/rai_analysis.py [--weeks 1-18] [--output-figures] [--output-video]
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from nfl_rai.data_loader import NFLDataLoader
from nfl_rai.feature_engineering import FeatureEngineer
from nfl_rai.rai_calculator import RAICalculator
from nfl_rai.visualizations import RAIVisualizer, NFLFieldPlotter, create_summary_dashboard
from nfl_rai.video_generator import VideoGenerator


class RAIAnalysis:
    """
    Complete RAI analysis pipeline for NFL Big Data Bowl 2026.
    """
    
    def __init__(self, data_dir: str = None, output_dir: str = 'outputs'):
        """
        Initialize analysis pipeline.
        
        Args:
            data_dir: Path to analytics-NFL directory
            output_dir: Directory for outputs
        """
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent
        self.output_dir = Path(output_dir)
        
        # Create output directories
        (self.output_dir / 'figures').mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'videos').mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'reports').mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.loader = NFLDataLoader(self.data_dir)
        self.fe = FeatureEngineer()
        self.rai_calc = RAICalculator(self.fe)
        self.visualizer = RAIVisualizer(self.output_dir / 'figures')
        self.video_gen = VideoGenerator(self.output_dir / 'videos')
        
        # Results storage
        self.rai_results = None
        self.play_results = None
        self.insights = {}
        
    def load_data(self, weeks: list = None, verbose: bool = True):
        """Load all data for analysis."""
        print("\n" + "="*60)
        print("STEP 1: Loading Data")
        print("="*60)
        
        self.loader.load_all_weeks(weeks, verbose)
        self.loader.load_supplementary()
        
        stats = self.loader.summary_stats()
        print(f"\nData loaded successfully:")
        print(f"  - Total plays: {stats.get('total_plays', 'N/A'):,}")
        print(f"  - Total games: {stats.get('total_games', 'N/A'):,}")
        print(f"  - Unique players: {stats.get('unique_players', 'N/A'):,}")
        
        return self
    
    def calculate_all_rai(self, sample_size: int = None, verbose: bool = True):
        """
        Calculate RAI for all plays.
        
        Args:
            sample_size: Number of plays to analyze (None = all)
            verbose: Show progress
        """
        print("\n" + "="*60)
        print("STEP 2: Calculating RAI Metrics")
        print("="*60)
        
        # Get unique plays
        plays = self.loader.input_data.groupby(['game_id', 'play_id']).first().reset_index()
        
        if sample_size:
            plays = plays.sample(min(sample_size, len(plays)), random_state=42)
            print(f"Analyzing sample of {len(plays)} plays...")
        else:
            print(f"Analyzing all {len(plays)} plays...")
        
        all_results = []
        
        iterator = tqdm(plays.iterrows(), total=len(plays), desc="Processing") if verbose else plays.iterrows()
        
        for _, play_row in iterator:
            game_id = play_row['game_id']
            play_id = play_row['play_id']
            
            try:
                # Get play data
                input_play, output_play = self.loader.get_play_tracking(game_id, play_id)
                
                if len(output_play) == 0:
                    continue
                
                # Get ball landing position
                ball_x = play_row.get('ball_land_x', output_play['x'].mean())
                ball_y = play_row.get('ball_land_y', output_play['y'].mean())
                
                # Calculate RAI for all players in play
                play_rai = self.rai_calc.calculate_play_rai(
                    input_play, output_play, ball_x, ball_y
                )
                
                # Add play identifiers
                play_rai['game_id'] = game_id
                play_rai['play_id'] = play_id
                
                all_results.append(play_rai)
                
            except Exception as e:
                # Skip problematic plays silently
                continue
        
        # Combine results
        self.rai_results = pd.concat(all_results, ignore_index=True)
        
        print(f"\n✓ Calculated RAI for {len(self.rai_results):,} player-plays")
        print(f"  - Unique players: {self.rai_results['nfl_id'].nunique():,}")
        print(f"  - Unique plays: {self.rai_results.groupby(['game_id', 'play_id']).ngroups:,}")
        
        return self
    
    def generate_insights(self):
        """Extract key insights from RAI analysis."""
        print("\n" + "="*60)
        print("STEP 3: Generating Insights")
        print("="*60)
        
        if self.rai_results is None:
            raise ValueError("Run calculate_all_rai() first")
        
        # Merge with supplementary data
        merged = self.rai_results.merge(
            self.loader.supplementary_data[['game_id', 'play_id', 'team_coverage_type', 
                                           'offense_formation', 'yards_gained', 'pass_result']],
            on=['game_id', 'play_id'],
            how='left'
        )
        
        # 1. Overall statistics
        self.insights['overall'] = {
            'mean_rai': self.rai_results['rai'].mean(),
            'std_rai': self.rai_results['rai'].std(),
            'mean_rtd': self.rai_results['rtd'].mean(),
            'mean_te': self.rai_results['te'].mean(),
        }
        
        # 2. RAI by player role
        role_stats = self.rai_results.groupby('player_role').agg({
            'rai': ['mean', 'std', 'count'],
            'rtd': 'mean',
            'te': 'mean'
        }).round(3)
        self.insights['by_role'] = role_stats
        
        # 3. RAI by coverage type
        if 'team_coverage_type' in merged.columns:
            coverage_stats = merged.groupby('team_coverage_type').agg({
                'rai': 'mean',
                'rtd': 'mean'
            }).round(3)
            self.insights['by_coverage'] = coverage_stats
        
        # 4. Top performers
        player_avg = self.rai_results.groupby('nfl_id').agg({
            'rai': 'mean',
            'rtd': 'mean',
            'te': 'mean',
            'player_role': 'first'
        }).round(3)
        self.insights['top_10'] = player_avg.nlargest(10, 'rai')
        self.insights['bottom_10'] = player_avg.nsmallest(10, 'rai')
        
        # 5. Correlation with play outcomes
        if 'yards_gained' in merged.columns:
            from scipy.stats import pearsonr
            valid = merged.dropna(subset=['rai', 'yards_gained'])
            if len(valid) > 10:
                corr, pval = pearsonr(valid['rai'], valid['yards_gained'])
                self.insights['yards_correlation'] = {'r': corr, 'p': pval}
        
        # Print insights
        print("\n📊 KEY INSIGHTS:")
        print("-" * 40)
        print(f"• Average RAI Score: {self.insights['overall']['mean_rai']:.3f}")
        print(f"• Average Reaction Time: {self.insights['overall']['mean_rtd']:.1f} frames ({self.insights['overall']['mean_rtd']*100:.0f}ms)")
        print(f"• Average Trajectory Efficiency: {self.insights['overall']['mean_te']:.2%}")
        
        print("\n📈 RAI BY ROLE:")
        print(self.insights['by_role'])
        
        if 'yards_correlation' in self.insights:
            corr = self.insights['yards_correlation']
            print(f"\n🏈 RAI-Yards Correlation: r = {corr['r']:.3f} (p = {corr['p']:.4f})")
        
        return self
    
    def create_visualizations(self, save: bool = True):
        """Create all competition visualizations."""
        print("\n" + "="*60)
        print("STEP 4: Creating Visualizations")
        print("="*60)
        
        if self.rai_results is None:
            raise ValueError("Run calculate_all_rai() first")
        
        # 1. RAI Distribution
        print("Creating RAI distribution plot...")
        self.visualizer.plot_rai_distribution(self.rai_results, save=save)
        
        # 2. Component breakdown
        print("Creating component breakdown...")
        self.visualizer.plot_component_breakdown(self.rai_results, save=save)
        
        # 3. Summary dashboard
        print("Creating summary dashboard...")
        create_summary_dashboard(
            self.rai_results,
            self.output_dir / 'figures' / 'summary_dashboard.png'
        )
        
        # 4. Coverage comparison (if data available)
        merged = self.rai_results.merge(
            self.loader.supplementary_data[['game_id', 'play_id', 'team_coverage_type']],
            on=['game_id', 'play_id'],
            how='left'
        )
        if 'team_coverage_type' in merged.columns and merged['team_coverage_type'].notna().any():
            print("Creating coverage comparison...")
            self.visualizer.plot_coverage_comparison(merged, save=save)
        
        print(f"\n✓ Visualizations saved to: {self.output_dir / 'figures'}")
        
        return self
    
    def create_sample_video(self, n_plays: int = 3):
        """Create sample video animations."""
        print("\n" + "="*60)
        print("STEP 5: Creating Video Animation")
        print("="*60)
        
        # Get a few interesting plays (high variance in RAI)
        play_variance = self.rai_results.groupby(['game_id', 'play_id'])['rai'].std()
        top_plays = play_variance.nlargest(n_plays).index.tolist()
        
        for i, (game_id, play_id) in enumerate(top_plays[:n_plays]):
            print(f"\nProcessing play {i+1}/{n_plays}: {game_id}_{play_id}")
            
            input_play, output_play = self.loader.get_play_tracking(game_id, play_id)
            play_meta = self.loader.get_play_metadata(game_id, play_id)
            
            # Get ball position
            ball_x = float(input_play['ball_land_x'].iloc[0])
            ball_y = float(input_play['ball_land_y'].iloc[0])
            
            # Get RAI scores for this play
            play_rai = self.rai_results[
                (self.rai_results['game_id'] == game_id) &
                (self.rai_results['play_id'] == play_id)
            ]
            
            # Create video
            title = f"RAI Analysis: {play_meta.get('play_description', 'NFL Play')[:50]}"
            self.video_gen.create_play_video(
                input_play, output_play,
                ball_x, ball_y,
                rai_scores=play_rai,
                title=title,
                filename=f'play_{game_id}_{play_id}.mp4'
            )
        
        return self
    
    def export_results(self):
        """Export analysis results to files."""
        print("\n" + "="*60)
        print("STEP 6: Exporting Results")
        print("="*60)
        
        # Export RAI results
        results_path = self.output_dir / 'reports' / 'rai_results.csv'
        self.rai_results.to_csv(results_path, index=False)
        print(f"✓ RAI results: {results_path}")
        
        # Export insights
        insights_path = self.output_dir / 'reports' / 'insights.txt'
        with open(insights_path, 'w') as f:
            f.write("="*60 + "\n")
            f.write("NFL BIG DATA BOWL 2026 - RAI ANALYSIS INSIGHTS\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            f.write("OVERALL STATISTICS:\n")
            f.write("-"*40 + "\n")
            for key, value in self.insights['overall'].items():
                f.write(f"  {key}: {value:.4f}\n")
            
            f.write("\n\nRAI BY PLAYER ROLE:\n")
            f.write("-"*40 + "\n")
            f.write(str(self.insights['by_role']))
            
            f.write("\n\n\nTOP 10 PERFORMERS:\n")
            f.write("-"*40 + "\n")
            f.write(str(self.insights['top_10']))
            
            if 'yards_correlation' in self.insights:
                f.write(f"\n\n\nRAI-YARDS CORRELATION:\n")
                f.write(f"  r = {self.insights['yards_correlation']['r']:.4f}\n")
                f.write(f"  p = {self.insights['yards_correlation']['p']:.4f}\n")
        
        print(f"✓ Insights report: {insights_path}")
        
        # Export player aggregates
        player_agg = self.rai_results.groupby('nfl_id').agg({
            'rai': ['mean', 'std', 'count'],
            'rtd': 'mean',
            'te': 'mean',
            'bpq': 'mean',
            'cms': 'mean',
            'sd': 'mean',
            'player_role': 'first'
        }).round(4)
        player_path = self.output_dir / 'reports' / 'player_rai_aggregates.csv'
        player_agg.to_csv(player_path)
        print(f"✓ Player aggregates: {player_path}")
        
        return self
    
    def run_full_analysis(self, weeks: list = None, sample_size: int = None,
                          create_videos: bool = True):
        """Run complete analysis pipeline."""
        print("\n" + "#"*60)
        print("#  NFL BIG DATA BOWL 2026 - RAI ANALYSIS PIPELINE")
        print("#"*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self.load_data(weeks)
        self.calculate_all_rai(sample_size)
        self.generate_insights()
        self.create_visualizations()
        
        if create_videos:
            self.create_sample_video(n_plays=3)
        
        self.export_results()
        
        print("\n" + "#"*60)
        print("#  ANALYSIS COMPLETE!")
        print("#"*60)
        print(f"\nOutputs saved to: {self.output_dir}")
        
        return self


def main():
    parser = argparse.ArgumentParser(description='NFL Big Data Bowl 2026 RAI Analysis')
    parser.add_argument('--weeks', nargs='+', type=int, default=None,
                       help='Weeks to analyze (default: all)')
    parser.add_argument('--sample', type=int, default=None,
                       help='Sample size for testing (default: all plays)')
    parser.add_argument('--no-video', action='store_true',
                       help='Skip video generation')
    parser.add_argument('--output-dir', type=str, default='outputs',
                       help='Output directory')
    
    args = parser.parse_args()
    
    analysis = RAIAnalysis(output_dir=args.output_dir)
    analysis.run_full_analysis(
        weeks=args.weeks,
        sample_size=args.sample,
        create_videos=not args.no_video
    )


if __name__ == "__main__":
    main()
