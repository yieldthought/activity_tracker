"""Activity Tracker - Monitor and analyze your daily work activities."""

__version__ = "0.1.0"

from .tracker import ActivityTracker
from .database import DatabaseHandler

__all__ = ['ActivityTracker', 'DatabaseHandler']
