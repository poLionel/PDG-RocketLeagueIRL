"""
Car model for the Rocket League IRL server.
"""

from datetime import datetime
from typing import Optional


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
