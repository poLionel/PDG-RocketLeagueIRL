"""
Data models for the Rocket League IRL server.
"""

class Car:
    """Represents a car in the Rocket League IRL game."""
    
    def __init__(self, car_id, name="Unknown Car", ble_name=None, ble_address=None):
        """
        Initialize a new car.
        
        Args:
            car_id (int): Unique identifier for the car
            name (str): Human-readable name for the car
            ble_name (str): BLE device name (e.g., "RL-CAR-cc:ba:97:0d:8c:b5")
            ble_address (str): BLE MAC address
        """
        self.car_id = car_id
        self.name = name
        self.ble_name = ble_name  # BLE device name
        self.ble_address = ble_address  # BLE MAC address
        self.battery_level = 100  # Battery level percentage (0-100)
        self.move = "stopped"     # Current movement: stopped, forward, backward, left, right
        self.x = 0                # Steering direction (-100 to 100, left to right)
        self.boost = False        # Whether boost is currently active
        self.boost_value = 100    # Boost fuel level (0-100)
        self.connected = False    # Whether the car is connected via Bluetooth
        self.last_seen = None     # Timestamp of last BLE discovery
        self.websocket_id = None  # WebSocket connection identifier that controls this car
        
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
            "ble_name": self.ble_name,
            "ble_address": self.ble_address,
            "battery_level": self.battery_level,
            "move": self.move,
            "x": self.x,
            "boost": str(self.boost).lower(),
            "boost_value": self.boost_value,
            "connected": self.connected,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "websocket_id": self.websocket_id,
            "selected": self.websocket_id is not None
        }
    
    def __str__(self):
        selected_status = f" [Selected by {self.websocket_id}]" if self.websocket_id else " [Available]"
        return f"Car {self.car_id} ({self.name}) - BLE: {self.ble_name} - Battery: {self.battery_level}%, Move: {self.move}, Boost: {self.boost}{selected_status}"
    
    def __repr__(self):
        return f"Car(car_id={self.car_id}, name='{self.name}', ble_name='{self.ble_name}')"


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
    
    def get_car_by_ble_name(self, ble_name):
        """
        Get a car by its BLE device name.
        
        Args:
            ble_name (str): BLE device name (e.g., "RL-CAR-cc:ba:97:0d:8c:b5")
            
        Returns:
            Car or None: Car object if found, None otherwise
        """
        for car in self.cars.values():
            if car.ble_name == ble_name:
                return car
        return None
    
    def get_car_by_ble_address(self, ble_address):
        """
        Get a car by its BLE MAC address.
        
        Args:
            ble_address (str): BLE MAC address
            
        Returns:
            Car or None: Car object if found, None otherwise
        """
        for car in self.cars.values():
            if car.ble_address == ble_address:
                return car
        return None
    
    def add_or_update_car_from_ble(self, ble_name, ble_address):
        """
        Add a new car or update existing car based on BLE discovery.
        
        Args:
            ble_name (str): BLE device name (e.g., "RL-CAR-cc:ba:97:0d:8c:b5")
            ble_address (str): BLE MAC address
            
        Returns:
            Car: The car object (new or existing)
        """
        from datetime import datetime
        
        # Check if car already exists by BLE name or address
        existing_car = self.get_car_by_ble_name(ble_name) or self.get_car_by_ble_address(ble_address)
        
        if existing_car:
            # Update existing car
            existing_car.ble_name = ble_name
            existing_car.ble_address = ble_address
            existing_car.last_seen = datetime.now()
            return existing_car
        else:
            # Create new car
            # Generate car_id from the MAC address in the BLE name
            car_id = self._generate_car_id_from_ble_name(ble_name)
            
            # Extract a readable name from BLE name
            readable_name = self._extract_car_name_from_ble_name(ble_name)
            
            new_car = Car(
                car_id=car_id,
                name=readable_name,
                ble_name=ble_name,
                ble_address=ble_address
            )
            new_car.last_seen = datetime.now()
            
            self.add_car(new_car)
            return new_car
    
    def _generate_car_id_from_ble_name(self, ble_name):
        """
        Generate a unique car ID from BLE name.
        
        Args:
            ble_name (str): BLE device name (e.g., "RL-CAR-cc:ba:97:0d:8c:b5")
            
        Returns:
            int: Generated car ID
        """
        if ble_name and "RL-CAR-" in ble_name:
            # Extract MAC address and convert to a hash for car ID
            mac_part = ble_name.replace("RL-CAR-", "").replace(":", "")
            # Use last 4 characters of MAC as car ID to keep it simple
            try:
                return int(mac_part[-4:], 16)  # Convert hex to int
            except ValueError:
                pass
        
        # Fallback: use hash of the BLE name
        return abs(hash(ble_name)) % 10000
    
    def _extract_car_name_from_ble_name(self, ble_name):
        """
        Extract a readable car name from BLE device name.
        
        Args:
            ble_name (str): BLE device name (e.g., "RL-CAR-cc:ba:97:0d:8c:b5")
            
        Returns:
            str: Readable car name
        """
        if ble_name and "RL-CAR-" in ble_name:
            mac_part = ble_name.replace("RL-CAR-", "")
            return f"Rocket League Car ({mac_part[-8:]})"  # Use last 8 chars of MAC
        return f"Unknown Car ({ble_name})"
    
    def select_car(self, car_id, websocket_id):
        """
        Select/assign a car to a websocket connection.
        
        Args:
            car_id (int): ID of the car to select
            websocket_id (str): Unique identifier for the websocket connection
            
        Returns:
            tuple: (success: bool, message: str, car: Car or None)
        """
        car = self.get_car(car_id)
        if not car:
            return False, f"Car {car_id} not found", None
        
        if car.websocket_id is not None:
            if car.websocket_id == websocket_id:
                return True, f"Car {car_id} is already selected by this client", car
            else:
                return False, f"Car {car_id} is already selected by another client", None
        
        car.websocket_id = websocket_id
        return True, f"Car {car_id} successfully selected", car
    
    def free_car(self, car_id, websocket_id=None):
        """
        Free/release a car from its websocket connection.
        
        Args:
            car_id (int): ID of the car to free
            websocket_id (str, optional): WebSocket ID that should own the car (for verification)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        car = self.get_car(car_id)
        if not car:
            return False, f"Car {car_id} not found"
        
        if car.websocket_id is None:
            return True, f"Car {car_id} is already free"
        
        # If websocket_id is provided, verify ownership
        if websocket_id is not None and car.websocket_id != websocket_id:
            return False, f"Car {car_id} is not selected by this client"
        
        car.websocket_id = None
        return True, f"Car {car_id} has been freed"
    
    def free_cars_by_websocket(self, websocket_id):
        """
        Free all cars assigned to a specific websocket connection.
        
        Args:
            websocket_id (str): WebSocket connection identifier
            
        Returns:
            list: List of car IDs that were freed
        """
        freed_cars = []
        for car in self.cars.values():
            if car.websocket_id == websocket_id:
                car.websocket_id = None
                freed_cars.append(car.car_id)
        return freed_cars
    
    def get_free_cars(self):
        """
        Get all cars that are not currently selected by any websocket.
        
        Returns:
            list: List of Car objects that are available
        """
        return [car for car in self.cars.values() if car.websocket_id is None]
    
    def get_cars_by_websocket(self, websocket_id):
        """
        Get all cars assigned to a specific websocket connection.
        
        Args:
            websocket_id (str): WebSocket connection identifier
            
        Returns:
            list: List of Car objects assigned to the websocket
        """
        return [car for car in self.cars.values() if car.websocket_id == websocket_id]
