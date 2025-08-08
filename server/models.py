"""
Data models for the Rocket League IRL server.
"""

class Car:
    """Represents a car in the Rocket League IRL game."""
    
    def __init__(self, car_id, name="Unknown Car"):
        """
        Initialize a new car.
        
        Args:
            car_id (int): Unique identifier for the car
            name (str): Human-readable name for the car
        """
        self.car_id = car_id
        self.name = name
        self.battery_level = 100  # Battery level percentage (0-100)
        self.move = "stopped"     # Current movement: stopped, forward, backward, left, right
        self.boost = False        # Whether boost is currently active
        self.boost_value = 100    # Boost fuel level (0-100)
        self.connected = False    # Whether the car is connected via Bluetooth
        
    def update_status(self, **kwargs):
        """
        Update car status with provided parameters.
        
        Args:
            **kwargs: Key-value pairs for status updates
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_status(self):
        """
        Get current car status as a dictionary.
        
        Returns:
            dict: Current car status
        """
        return {
            "car": self.car_id,
            "name": self.name,
            "battery_level": self.battery_level,
            "move": self.move,
            "boost": str(self.boost).lower(),
            "boost_value": self.boost_value,
            "connected": self.connected
        }
    
    def __str__(self):
        return f"Car {self.car_id} ({self.name}) - Battery: {self.battery_level}%, Move: {self.move}, Boost: {self.boost}"
    
    def __repr__(self):
        return f"Car(car_id={self.car_id}, name='{self.name}')"


class CarManager:
    """Manages a collection of cars."""
    
    def __init__(self):
        """Initialize the car manager with an empty list of cars."""
        self.cars = {}  # Dictionary mapping car_id to Car objects
    
    def add_car(self, car):
        """
        Add a car to the manager.
        
        Args:
            car (Car): Car object to add
        """
        self.cars[car.car_id] = car
    
    def get_car(self, car_id):
        """
        Get a car by its ID.
        
        Args:
            car_id (int): ID of the car to retrieve
            
        Returns:
            Car or None: Car object if found, None otherwise
        """
        return self.cars.get(car_id)
    
    def get_all_cars(self):
        """
        Get all cars.
        
        Returns:
            list: List of all Car objects
        """
        return list(self.cars.values())
    
    def remove_car(self, car_id):
        """
        Remove a car by its ID.
        
        Args:
            car_id (int): ID of the car to remove
            
        Returns:
            bool: True if car was removed, False if not found
        """
        if car_id in self.cars:
            del self.cars[car_id]
            return True
        return False
    
    def update_car_status(self, car_id, **kwargs):
        """
        Update the status of a specific car.
        
        Args:
            car_id (int): ID of the car to update
            **kwargs: Status parameters to update
            
        Returns:
            bool: True if car was found and updated, False otherwise
        """
        car = self.get_car(car_id)
        if car:
            car.update_status(**kwargs)
            return True
        return False
    
    def get_car_count(self):
        """
        Get the total number of cars.
        
        Returns:
            int: Number of cars
        """
        return len(self.cars)
