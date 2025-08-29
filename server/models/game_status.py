"""
Game status model for the Rocket League IRL server.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from .game import Goal, Team


class GameStatus:
    """Represents the current game status and state."""
    
    def __init__(self, match_length_seconds: int = 300):  # Default 5 minutes
        """
        Initialize game status.
        
        Args:
            match_length_seconds (int): Duration of the match in seconds
        """
        self.teams: Dict[str, Team] = {}  # Maps team color to Team object
        self.goals: List[Goal] = []  # List of all goals scored
        self.start_date: Optional[datetime] = None
        self.pause_date: Optional[datetime] = None
        self.end_date: Optional[datetime] = None  # When the game was ended
        self.total_paused_time: int = 0  # Total seconds paused
        self.match_length_seconds = match_length_seconds
        self.is_active = False
        self.is_finished = False
        
        # Initialize default teams
        self.add_team("red")
        self.add_team("blue")
    
    def add_team(self, color: str, name: Optional[str] = None) -> Team:
        """
        Add a new team to the game.
        
        Args:
            color (str): Team color identifier
            name (str, optional): Team name
            
        Returns:
            Team: The created team object
        """
        team = Team(color, name)
        self.teams[color] = team
        return team
    
    def get_team(self, color: str) -> Optional[Team]:
        """Get a team by its color."""
        return self.teams.get(color)
    
    def add_car_to_team(self, car_id: int, team_color: str) -> bool:
        """
        Add a car to a specific team.
        
        Args:
            car_id (int): ID of the car to add
            team_color (str): Color of the team to add to
            
        Returns:
            bool: True if successful, False if team doesn't exist
        """
        team = self.get_team(team_color)
        if team:
            # Remove car from other teams first
            for other_team in self.teams.values():
                if other_team.color != team_color:
                    other_team.remove_car(car_id)
            
            team.add_car(car_id)
            return True
        return False
    
    def remove_car_from_teams(self, car_id: int):
        """Remove a car from all teams."""
        for team in self.teams.values():
            team.remove_car(car_id)
    
    def score_goal(self, team_color: str, player_id: Optional[str] = None, car_id: Optional[int] = None) -> bool:
        """
        Record a goal for a team.
        
        Args:
            team_color (str): Color of the team that scored
            player_id (str, optional): ID of the player who scored
            car_id (int, optional): ID of the car that scored
            
        Returns:
            bool: True if successful, False if team doesn't exist
        """
        team = self.get_team(team_color)
        if team:
            goal = Goal(team_color, player_id, car_id)
            self.goals.append(goal)
            team.score += 1
            return True
        return False
    
    def start_game(self):
        """Start the game."""
        self.start_date = datetime.now()
        self.is_active = True
        self.is_finished = False
        self.pause_date = None
        self.end_date = None  # Reset end date
        self.total_paused_time = 0
    
    def stop_game(self):
        """Stop (pause) the game."""
        if self.is_active:
            self.pause_date = datetime.now()
            self.is_active = False
    
    def resume_game(self):
        """Resume a paused game."""
        if self.pause_date and not self.is_finished:
            # Add paused time to total
            self.total_paused_time += int((datetime.now() - self.pause_date).total_seconds())
            self.pause_date = None
            self.is_active = True
    
    def end_game(self):
        """End the game permanently."""
        if self.pause_date:
            # Add final paused time if game was paused when ended
            self.total_paused_time += int((datetime.now() - self.pause_date).total_seconds())
            self.pause_date = None
        
        # Record when the game was ended
        self.end_date = datetime.now()
        self.is_active = False
        self.is_finished = True
    
    def get_time_remaining(self) -> int:
        """
        Get remaining time in seconds, accounting for paused time.
        
        Returns:
            int: Seconds remaining, full match length if not started, 0 if finished
        """
        if not self.start_date:
            return self.match_length_seconds  # Not started yet
        
        if self.is_finished:
            return 0
        
        # Determine the end time for calculation
        if self.pause_date:
            # Currently paused, calculate from pause time
            end_time = self.pause_date
        elif self.end_date:
            # Game was ended, calculate from end time
            end_time = self.end_date
        else:
            # Game is running, use current time
            end_time = datetime.now()
        
        elapsed = end_time - self.start_date
        total_elapsed = elapsed.total_seconds()
        
        # Subtract total previous paused time
        total_elapsed -= self.total_paused_time
        
        remaining = self.match_length_seconds - total_elapsed
        return max(0, int(remaining))
    
    def get_elapsed_time(self) -> int:
        """
        Get elapsed time in seconds, not counting paused time.
        
        Returns:
            int: Seconds elapsed since game start (excluding paused time), 0 if not started
        """
        if not self.start_date:
            return 0
        
        # Determine the end time for calculation
        if self.pause_date:
            # Currently paused, calculate from pause time
            end_time = self.pause_date
        elif self.end_date:
            # Game was ended, calculate from end time
            end_time = self.end_date
        else:
            # Game is running, use current time
            end_time = datetime.now()
        
        elapsed = end_time - self.start_date
        total_elapsed = elapsed.total_seconds()
        
        # Subtract total previous paused time
        total_elapsed -= self.total_paused_time
        
        return max(0, int(total_elapsed))
    
    def is_game_over(self) -> bool:
        """Check if the game time has expired."""
        return self.get_time_remaining() <= 0 and self.is_active
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert game status to dictionary representation."""
        state = "not_started"
        if self.is_finished:
            state = "ended"
        elif self.is_active:
            state = "active"
        elif self.start_date:
            state = "paused"
        
        return {
            "teams": {color: team.to_dict() for color, team in self.teams.items()},
            "goals": [goal.to_dict() for goal in self.goals],
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "match_length_seconds": self.match_length_seconds,
            "time_remaining": self.get_time_remaining(),
            "elapsed_time": self.get_elapsed_time(),
            "is_active": self.is_active,
            "is_finished": self.is_finished,
            "state": state,
            "total_paused_time": self.total_paused_time
        }
