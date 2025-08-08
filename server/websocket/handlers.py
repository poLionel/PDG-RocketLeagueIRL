"""
WebSocket message handlers for the Rocket League IRL server.
"""

__all__ = [
    'handle_move_car',
    'handle_get_car_status',
    'handle_unknown_action', 
    'handle_invalid_json',
    'ACTION_HANDLERS'
]

def handle_move_car(data, car_manager=None):
    """Handle car movement commands."""
    car_id = data.get("car")
    move = data.get("move")
    boost = data.get("boost", "false")
    
    print(f"Car {car_id} moving {move} with boost: {boost}")
    
    # Update car status if car manager is available
    if car_manager and car_id is not None:
        car = car_manager.get_car(car_id)
        if car:
            # Convert boost string to boolean
            boost_bool = boost.lower() == "true" if isinstance(boost, str) else bool(boost)
            
            # Update car status
            car_manager.update_car_status(
                car_id=car_id,
                move=move,
                boost=boost_bool
            )
            
            return {
                "status": "success",
                "message": f"Car {car_id} command received and executed",
                "car_status": car.get_status()
            }
        else:
            return {
                "status": "error",
                "message": f"Car {car_id} not found"
            }
    
    return {
        "status": "success",
        "message": f"Car {car_id} command received"
    }

def handle_get_car_status(data, car_manager=None):
    """Handle get car status requests."""
    car_id = data.get("car")
    
    print(f"Getting status for car {car_id}")
    
    # Get real car status if car manager is available
    if car_manager and car_id is not None:
        car = car_manager.get_car(car_id)
        if car:
            return {
                "status": "success",
                "car_status": car.get_status()
            }
        else:
            return {
                "status": "error",
                "message": f"Car {car_id} not found"
            }
    
    # Fallback to mock data if no car manager
    return {
        "status": "success",
        "car_status": {
            "car": car_id,
            "battery_level": 85,
            "move": "forward",
            "boost": "false",
            "boost_value": 100
        }
    }

def handle_unknown_action(data):
    """Handle unknown action commands."""
    return {
        "status": "error",
        "message": "Unknown action"
    }

def handle_invalid_json():
    """Handle invalid JSON format errors."""
    return {
        "status": "error",
        "message": "Invalid JSON format"
    }

# Action dispatch dictionary
ACTION_HANDLERS = {
    "move_car": handle_move_car,
    "get_car_status": handle_get_car_status,
}
