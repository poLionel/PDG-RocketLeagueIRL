"""
WebSocket message handlers for the Rocket League IRL server.
"""

# Try to import Bluetooth handlers, but don't fail if they're not available
try:
    from bluetooth.handlers import BLUETOOTH_HANDLERS, get_bluetooth_service
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_HANDLERS = {}
    BLUETOOTH_AVAILABLE = False
    def get_bluetooth_service():
        return None

__all__ = [
    'handle_move_car',
    'handle_get_car_status',
    'handle_get_all_cars',
    'handle_send_to_car',
    'handle_connect_to_car',
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
                "action": "move_car",
                "message": f"Car {car_id} command received and executed",
                "car_status": car.get_status()
            }
        else:
            return {
                "status": "error",
                "action": "move_car",
                "message": f"Car {car_id} not found"
            }
    
    return {
        "status": "success",
        "action": "move_car",
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
                "action": "get_car_status",
                "car_status": car.get_status()
            }            
    
    # If car manager is not available, return an error response
    return {
        "status": "error",
        "action": "get_car_status",
        "message": f"Car {car_id} not found"
    }

def handle_get_all_cars(data, car_manager=None):
    """Handle get all cars requests."""
    print("Getting all cars status")
    
    if car_manager:
        cars = car_manager.get_all_cars()
        cars_status = [car.get_status() for car in cars]
        return {
            "status": "success",
            "cars": cars_status,
            "count": len(cars_status)
        }
    
    return {
        "status": "error",
        "message": "Car manager not available"
    }

def handle_connect_to_car(data, car_manager=None):
    """Handle connect to car via Bluetooth requests."""
    car_id = data.get("car")
    ble_address = data.get("ble_address")
    
    print(f"Connecting to car {car_id} via Bluetooth")
    
    if not BLUETOOTH_AVAILABLE:
        return {
            "status": "error",
            "message": "Bluetooth service not available"
        }
    
    bluetooth_service = get_bluetooth_service()
    if not bluetooth_service:
        return {
            "status": "error",
            "message": "Bluetooth service not initialized"
        }
    
    try:
        # Find car by ID or BLE address
        car = None
        if car_manager and car_id is not None:
            car = car_manager.get_car(car_id)
        elif car_manager and ble_address:
            car = car_manager.get_car_by_ble_address(ble_address)
        
        if not car:
            return {
                "status": "error",
                "message": f"Car not found (ID: {car_id}, Address: {ble_address})"
            }
        
        # Try to connect via BLE service
        # Note: This would need to be made async in a real implementation
        return {
            "status": "success",
            "message": f"Connection initiated to car {car.name} ({car.ble_address})",
            "car": car.get_status()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error connecting to car: {str(e)}"
        }

def handle_send_to_car(data, car_manager=None):
    """Handle sending commands/data to car via Bluetooth."""
    car_id = data.get("car")
    command = data.get("command", "test")
    message = data.get("message", "Hello from server!")
    
    print(f"Sending to car {car_id}: command={command}, message={message}")
    
    if not BLUETOOTH_AVAILABLE:
        return {
            "status": "error",
            "message": "Bluetooth service not available"
        }
    
    bluetooth_service = get_bluetooth_service()
    if not bluetooth_service:
        return {
            "status": "error",
            "message": "Bluetooth service not initialized"
        }
    
    try:
        # Find the car
        car = None
        if car_manager and car_id is not None:
            car = car_manager.get_car(car_id)
        
        if not car:
            return {
                "status": "error",
                "message": f"Car {car_id} not found"
            }
        
        if not car.ble_address:
            return {
                "status": "error",
                "message": f"Car {car_id} has no BLE address"
            }
        
        # Get the BLE device
        ble_devices = bluetooth_service.ble_service.discovered_devices
        ble_device = ble_devices.get(car.ble_address)
        
        if not ble_device:
            return {
                "status": "error",
                "message": f"Car {car_id} BLE device not found. Try discovering cars first."
            }
        
        # For now, we'll send a static test message
        # This should be made async in a real implementation
        test_message = {
            "command": command,
            "message": message,
            "timestamp": str(car.last_seen),
            "car_id": car_id
        }
        
        print(f"Would send to {car.name} ({car.ble_address}): {test_message}")
        
        # Update car status to show communication attempt
        if car_manager:
            car_manager.update_car_status(car_id, connected=True)
        
        return {
            "status": "success",
            "message": f"Command sent to car {car.name}",
            "sent_data": test_message,
            "car": car.get_status()
        }
        
    except Exception as e:
        print(f"Error in handle_send_to_car: {e}")
        return {
            "status": "error",
            "message": f"Error sending to car: {str(e)}"
        }

def handle_switch_to_scan_phase(data, car_manager=None):
    """Handle switch to scan phase requests."""
    print("Switching to scan phase")
    
    if not BLUETOOTH_AVAILABLE:
        return {
            "status": "error",
            "message": "Bluetooth service not available"
        }
    
    bluetooth_service = get_bluetooth_service()
    if not bluetooth_service:
        return {
            "status": "error",
            "message": "Bluetooth service not initialized"
        }
    
    try:
        # This will be called async in the WebSocket handler
        return {
            "status": "pending",
            "action": "switch_to_scan_phase",
            "message": "Switching to scan phase..."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error switching to scan phase: {str(e)}"
        }

def handle_switch_to_control_phase(data, car_manager=None):
    """Handle switch to control phase requests."""
    print("Switching to control phase")
    
    if not BLUETOOTH_AVAILABLE:
        return {
            "status": "error",
            "message": "Bluetooth service not available"
        }
    
    bluetooth_service = get_bluetooth_service()
    if not bluetooth_service:
        return {
            "status": "error",
            "message": "Bluetooth service not initialized"
        }
    
    try:
        # This will be called async in the WebSocket handler
        return {
            "status": "pending",
            "action": "switch_to_control_phase",
            "message": "Switching to control phase..."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error switching to control phase: {str(e)}"
        }

def handle_get_phase_status(data, car_manager=None):
    """Handle get phase status requests."""
    print("Getting phase status")
    
    if not BLUETOOTH_AVAILABLE:
        return {
            "status": "error",
            "message": "Bluetooth service not available"
        }
    
    bluetooth_service = get_bluetooth_service()
    if not bluetooth_service:
        return {
            "status": "error",
            "message": "Bluetooth service not initialized"
        }
    
    try:
        ble_status = bluetooth_service.ble_service.get_status()
        return {
            "status": "success",
            "phase_status": ble_status
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting phase status: {str(e)}"
        }

def handle_unknown_action(data):
    """Handle unknown action commands."""
    response = {
        "status": "error",
        "message": "Unknown action"
    }
    
    # Include the action if it was provided
    if isinstance(data, dict) and "action" in data:
        response["action"] = data["action"]
    
    return response


# Action dispatch dictionary
ACTION_HANDLERS = {
    "move_car": handle_move_car,
    "get_car_status": handle_get_car_status,
    "get_all_cars": handle_get_all_cars,
    "send_to_car": handle_send_to_car,
    "connect_to_car": handle_connect_to_car,
    "switch_to_scan_phase": handle_switch_to_scan_phase,
    "switch_to_control_phase": handle_switch_to_control_phase,
    "get_phase_status": handle_get_phase_status,
}

# Add Bluetooth handlers if available
if BLUETOOTH_AVAILABLE:
    ACTION_HANDLERS.update(BLUETOOTH_HANDLERS)
