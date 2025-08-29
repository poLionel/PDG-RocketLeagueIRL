"""
Game manager for the Rocket League IRL server.
"""

from typing import Optional, TYPE_CHECKING
from .game_status import GameStatus

if TYPE_CHECKING:
    from .car_manager import CarManager


class GameManager:
    """Manages game state and operations."""
    
    def __init__(self, car_manager: 'CarManager'):
        """
        Initialize game manager with a default game always available.
        
        Args:
            car_manager (CarManager): Reference to the car manager
        """
        self.car_manager = car_manager
        self.match_length_seconds = 300  # Default 5 minutes
        # Always create a default game
        self.current_game = GameStatus(self.match_length_seconds)
    
    def get_current_game(self) -> GameStatus:
        """Get the current game status. Always returns a game."""
        return self.current_game
    
    def start_game(self, match_length_seconds: int = None) -> bool:
        """
        Start or restart the game. This resets the game state.
        
        Args:
            match_length_seconds (int, optional): New match length, uses current if not provided
            
        Returns:
            bool: Always True since game is always available
        """
        if match_length_seconds:
            self.match_length_seconds = match_length_seconds
        
        # Reset the game with current match length
        self.current_game = GameStatus(self.match_length_seconds)
        self.current_game.start_game()
        return True
    
    def stop_game(self) -> bool:
        """
        Stop (pause) the current game without ending it.
        
        Returns:
            bool: True if game was paused, False if game was not active
        """
        if self.current_game.is_active:
            self.current_game.stop_game()  # This will set pause_date and is_active = False
            return True
        return False
    
    def resume_game(self) -> bool:
        """
        Resume a paused game.
        
        Returns:
            bool: True if game was resumed, False if game was finished or not started
        """
        if not self.current_game.is_finished and self.current_game.start_date:
            self.current_game.resume_game()  # This will handle pause_date and is_active = True
            return True
        return False
    
    def end_game(self) -> bool:
        """
        End the current game permanently.
        
        Returns:
            bool: Always True since game is always available
        """
        self.current_game.end_game()
        return True
    
    def score_goal(self, team_color: str, player_id: Optional[str] = None, car_id: Optional[int] = None) -> bool:
        """
        Record a goal in the current game.
        
        Args:
            team_color (str): Color of the team that scored
            player_id (str, optional): ID of the player who scored
            car_id (int, optional): ID of the car that scored
            
        Returns:
            bool: True if goal was recorded, False if invalid team
        """
        return self.current_game.score_goal(team_color, player_id, car_id)
    
    def add_car_to_team(self, car_id: int, team_color: str) -> bool:
        """
        Add a car to a team in the current game.
        
        Args:
            car_id (int): ID of the car to add
            team_color (str): Color of the team
            
        Returns:
            bool: True if successful, False if invalid parameters
        """
        # Verify car exists in car manager
        if self.car_manager.get_car(car_id):
            return self.current_game.add_car_to_team(car_id, team_color)
        return False
    
    def check_game_time(self) -> bool:
        """
        Check if the current game should end due to time expiration.
        Automatically ends the game if time has run out.
        
        Returns:
            bool: True if game was ended due to time, False otherwise
        """
        if self.current_game.is_game_over():
            self.current_game.end_game()
            return True
        return False
