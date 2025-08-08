"""
WebSocket message handlers for the Rocket League IRL server.
"""

__all__ = [
    'handle_move_car',
    'handle_unknown_action', 
    'handle_invalid_json',
    'ACTION_HANDLERS'
]

def handle_move_car(data):
    """Handle car movement commands."""
    car_id = data.get("car")
    move = data.get("move")
    boost = data.get("boost", "false")
    
    print(f"Car {car_id} moving {move} with boost: {boost}")
    
    return {
        "status": "success",
        "message": f"Car {car_id} command received"
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
}
