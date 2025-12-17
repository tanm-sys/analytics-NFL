"""
NFL Big Data Bowl 2026 - Reactivity Advantage Index (RAI) Package

A novel metric for analyzing player movement during the ball-in-air window.

Components:
- data_loader: Load and preprocess tracking data
- feature_engineering: Physics-based feature calculations
- rai_calculator: Core RAI metric computation
- baseline: Kalman filter expected trajectory
- visualizations: Publication-quality plots
- video_generator: Broadcast-ready animations
"""

__version__ = "1.0.0"
__author__ = "NFL BDB 2026 Entry"

from .data_loader import NFLDataLoader
from .feature_engineering import FeatureEngineer
from .rai_calculator import RAICalculator

__all__ = [
    "NFLDataLoader",
    "FeatureEngineer", 
    "RAICalculator",
]
