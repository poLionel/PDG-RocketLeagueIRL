"""
Game-related models for the Rocket League IRL server.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any


class Goal:
    """Represents a goal scored in the game."""
    
    def __init__(self, team_color: str, player_id: Optional[str] = None, car_id: Optional[int] = None, timestamp: Optional[datetime] = None):
        """
        Initialize a goal record.
        
        Args:
            team_color (str): Color of the team that scored (e.g., "red", "blue")
            player_id (str, optional): ID of the player who scored
            car_id (int, optional): ID of the car that scored
            timestamp (datetime, optional): When the goal was scored (defaults to now)
        """
        self.team_color = team_color
        self.player_id = player_id
        self.car_id = car_id
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert goal to dictionary representation."""
        return {
            "team_color": self.team_color,
            "player_id": self.player_id,
            "car_id": self.car_id,
            "timestamp": self.timestamp.isoformat()
        }


class Team:
    """Represents a team in the game."""
    
    def __init__(self, color: str, name: Optional[str] = None):
        """
        Initialize a team.
        
        Args:
            color (str): Team color identifier (e.g., "red", "blue")
            name (str, optional): Team name (defaults to color)
        """
        self.color = color
        self.name = name or color.capitalize()
        self.car_ids: List[int] = []  # List of car IDs in this team
        self.score = 0
    
    def add_car(self, car_id: int):
        """Add a car to the team."""
        if car_id not in self.car_ids:
            self.car_ids.append(car_id)
    
    def remove_car(self, car_id: int):
        """Remove a car from the team."""
        if car_id in self.car_ids:
            self.car_ids.remove(car_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert team to dictionary representation."""
        return {
            "color": self.color,
            "name": self.name,
            "car_ids": self.car_ids,
            "score": self.score
        }
