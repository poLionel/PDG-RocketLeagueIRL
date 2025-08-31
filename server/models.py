"""
Backward compatibility module for models.

This module re-exports all models from the models package to maintain
backward compatibility with existing imports.
"""

# Re-export everything from the models package
from models.car import Car
from models.car_manager import CarManager
from models.game import Goal, Team
from models.game_status import GameStatus
from models.game_manager import GameManager

# Ensure all exports are available
__all__ = [
    'Car',
    'CarManager',
    'Goal',
    'Team',
    'GameStatus',
    'GameManager'
]
