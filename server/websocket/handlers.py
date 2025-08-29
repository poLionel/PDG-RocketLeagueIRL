"""
WebSocket message handlers for the Rocket League IRL server.

This module contains all the handler functions for processing incoming WebSocket
messages from client applications. It bridges the WebSocket communication layer
with the car management system and Bluetooth services.

Handler categories:
- Car management: select, free, status operations
- Movement control: translate UI commands to motor parameters  
- Bluetooth integration: device discovery and pairing
- System status: health checks and configuration
"""

import asyncio
import logging

# Bluetooth functionality with graceful degradation
try:
    from bluetooth.handlers import BLUETOOTH_HANDLERS, get_bluetooth_service
    BLUETOOTH_AVAILABLE = True
except ImportError:
    # Fallback when Bluetooth dependencies are unavailable
    BLUETOOTH_HANDLERS = {}
    BLUETOOTH_AVAILABLE = False
    def get_bluetooth_service():
        return None

logger = logging.getLogger(__name__)

def translate_move_to_drive_params(move, x, boost):
    """
    Convert high-level movement commands to low-level motor control parameters.
    
    Translates user-friendly movement commands from the mobile app/web interface
    into the specific motor control values expected by the car's BLE firmware.
    This includes coordinate system mapping and boost behavior.
    
    Args:
        move (str): Movement direction ("forward", "backward", "stopped")
        x (int): Steering value (-100 to 100, left to right)
        boost (bool): Whether boost mode is enabled
        
    Returns:
        tuple: (drive_x, drive_y, speed, decay_mode) for BLE characteristic writes
            - drive_x: Steering direction (-100 to 100)
            - drive_y: Forward/backward direction (-100 to 100) 
            - speed: Motor speed magnitude (0 to 100)
            - decay_mode: Braking behavior (0=normal, 1=fast/boost)
    """
    # Initialize with safe default values
    drive_x = x  # Direct steering mapping from UI
    drive_y = 0  # Forward/backward component
    speed = 0    # Motor speed magnitude
    decay_mode = 0  # Normal braking behavior
    
    # Map movement commands to motor directions
    if move == "forward":
        drive_y = 50   # Positive Y-axis for forward motion
        speed = 50     # Moderate base speed for control
    elif move == "backward":
        drive_y = -50  # Negative Y-axis for reverse motion
        speed = 50     # Same speed for consistent feel
    elif move == "stopped":
        drive_y = 0    # No directional movement
        speed = 0      # Complete stop
    
    # Boost mode increases speed and changes braking characteristics
    if boost:
        speed = 100    # Maximum speed for boost
        decay_mode = 1 # boost decay mode
        
    return drive_x, drive_y, speed, decay_mode

async def send_drive_command_to_car(car, move, x, boost):
    """
    Send drive commands to a car via Bluetooth based on move parameters.
    
    Args:
        car: Car object with BLE address
        move (str): Movement direction
        x (int): Steering value
        boost (bool): Boost enabled
        
    Returns:
        bool: True if command was sent successfully, False otherwise
    """
    try:
        # Get the Bluetooth service
        bluetooth_service = get_bluetooth_service()
        if not bluetooth_service:
            logger.warning("Bluetooth service not available for drive command")
            return False
        
        # Check if car has BLE address
        if not car.ble_address:
            logger.warning(f"Car {car.car_id} has no BLE address")
            return False
        
        # Check if BLE service is in control phase
        if not bluetooth_service.ble_service.is_in_control_phase():
            logger.warning("Cannot send drive command: BLE service is in scan phase")
            return False
        
        # Check if car device is discovered
        ble_devices = bluetooth_service.ble_service.discovered_devices
        if car.ble_address not in ble_devices:
            logger.warning(f"Car {car.car_id} BLE device not found in discovered devices")
            return False
        
        # Translate move command to drive parameters
        drive_x, drive_y, speed, decay_mode = translate_move_to_drive_params(move, x, boost)
        
        logger.info(f"Sending drive command to car {car.car_id}: move={move}, x={x}, boost={boost}")
        logger.info(f"BLE drive params: X={drive_x}, Y={drive_y}, Speed={speed}, Decay={decay_mode}")
        
        # Send the drive command via BLE
        success = await bluetooth_service.ble_service.set_drive_on_car(
            car.ble_address, drive_x, drive_y, speed, decay_mode
        )
        
        if success:
            logger.info(f"Drive command successfully sent to car {car.car_id}")
            return True
        else:
            logger.error(f"Failed to send drive command to car {car.car_id}")
            return False
        
    except Exception as e:
        logger.error(f"Error sending drive command to car {car.car_id}: {e}")
        return False

__all__ = [
    'handle_move_car',
    'handle_get_car_status',
    'handle_get_all_cars',
    'handle_get_free_cars',
    'handle_select_car',
    'handle_free_car',
    'handle_send_to_car',
    'handle_connect_to_car',
    'handle_unknown_action', 
    'handle_invalid_json',
    # Game management handlers
    'handle_start_game',
    'handle_stop_game',
    'handle_resume_game',
    'handle_end_game',
    'handle_get_game_status',
    'handle_goal_scored',
    'handle_score_goal',
    'handle_add_car_to_team',
    'handle_remove_car_from_teams',
    'handle_add_team',
    'ACTION_HANDLERS'
]

def handle_move_car(data, car_manager=None, websocket_id=None):
    """Handle car movement commands with automatic Bluetooth drive command integration."""
    car_id = data.get("car")
    move = data.get("move")  # forward, backward, stopped
    x = data.get("x", 0)     # steering: -100 (full left) to 100 (full right)
    boost = data.get("boost", "false")
    
    # Validate x parameter
    try:
        x = int(x)
        if x < -100 or x > 100:
            return {
                "status": "error",
                "action": "move_car",
                "message": f"Invalid x parameter: {x}. Must be between -100 and 100"
            }
    except (ValueError, TypeError):
        return {
            "status": "error",
            "action": "move_car",
            "message": f"Invalid x parameter: {x}. Must be an integer between -100 and 100"
        }
    
    print(f"Car {car_id} moving {move} with x={x} and boost: {boost}")
    
    # Update car status if car manager is available
    if car_manager and car_id is not None:
        car = car_manager.get_car(car_id)
        if car:
            # Check if this websocket has permission to control this car
            if websocket_id and car.websocket_id is not None and car.websocket_id != websocket_id:
                return {
                    "status": "error",
                    "action": "move_car",
                    "message": f"Car {car_id} is controlled by another client. Select the car first."
                }
            
            # Convert boost string to boolean
            boost_bool = boost.lower() == "true" if isinstance(boost, str) else bool(boost)
            
            # Update car status
            car_manager.update_car_status(
                car_id=car_id,
                move=move,
                x=x,
                boost=boost_bool
            )
            
            # Try to send Bluetooth drive command asynchronously
            async def send_bluetooth_command():
                try:
                    ble_success = await send_drive_command_to_car(car, move, x, boost_bool)
                    if ble_success:
                        # Update car connection status
                        car_manager.update_car_status(car_id, connected=True)
                        logger.info(f"Bluetooth drive command sent successfully to car {car_id}")
                    else:
                        logger.warning(f"Bluetooth drive command failed for car {car_id}")
                except Exception as e:
                    logger.error(f"Error in Bluetooth drive command for car {car_id}: {e}")
            
            # Schedule the async task (fire and forget) if event loop is available
            bluetooth_command_sent = False
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(send_bluetooth_command())
                bluetooth_command_sent = True
            except RuntimeError:
                # No event loop running, can't send BLE command
                logger.warning(f"No event loop available to send Bluetooth command for car {car_id}")
            
            return {
                "status": "success",
                "action": "move_car",
                "message": f"Car {car_id} command received and executed" + (" and Bluetooth drive command initiated" if bluetooth_command_sent else ""),
                "car_status": car.get_status(),
                "bluetooth_command_sent": bluetooth_command_sent
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
            car_status = car.get_status()
            # Flatten the response to match documented format
            return {
                "status": "success",
                "action": "get_car_status",
                "car": car_status["car"],
                "battery_level": car_status["battery_level"],
                "move": car_status["move"],
                "x": car_status["x"],
                "boost": car_status["boost"],
                "boost_value": car_status["boost_value"]
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

def handle_connect_to_car(data, car_manager=None, websocket_id=None):
    """Handle connect to car via Bluetooth requests."""
    car_id = data.get("car")
    ble_address = data.get("ble_address")
    
    print(f"Connecting to car {car_id} via Bluetooth")
    
    # Check car ownership if car_manager is available
    if car_manager and car_id is not None:
        car = car_manager.get_car(car_id)
        if car and websocket_id and car.websocket_id is not None and car.websocket_id != websocket_id:
            return {
                "status": "error",
                "action": "connect_to_car",
                "message": f"Car {car_id} is controlled by another client. Select the car first."
            }
    
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

def handle_send_to_car(data, car_manager=None, websocket_id=None):
    """Handle sending commands/data to car via Bluetooth."""
    car_id = data.get("car")
    command = data.get("command", "test")
    message = data.get("message", "Hello from server!")
    
    print(f"Sending to car {car_id}: command={command}, message={message}")
    
    # Check car ownership if car_manager is available
    if car_manager and car_id is not None:
        car = car_manager.get_car(car_id)
        if car and websocket_id and car.websocket_id is not None and car.websocket_id != websocket_id:
            return {
                "status": "error",
                "action": "send_to_car",
                "message": f"Car {car_id} is controlled by another client. Select the car first."
            }
    
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

def handle_invalid_json():
    """Handle invalid JSON requests."""
    return {
        "status": "error",
        "message": "Invalid JSON format"
    }

def handle_get_free_cars(data, car_manager=None):
    """Handle get free cars requests."""
    if not car_manager:
        return {
            "status": "error",
            "action": "get_free_cars",
            "message": "Car manager not available"
        }
    
    free_cars = car_manager.get_free_cars()
    free_car_ids = [car.car_id for car in free_cars]
    
    return {
        "status": "success",
        "action": "get_free_cars",
        "free_cars": free_car_ids,
        "message": f"Found {len(free_car_ids)} available cars"
    }

def handle_select_car(data, car_manager=None, websocket_id=None):
    """Handle car selection requests."""
    car_id = data.get("car")
    
    if car_id is None:
        return {
            "status": "error",
            "action": "select_car",
            "message": "Car ID is required"
        }
    
    if not car_manager:
        return {
            "status": "error",
            "action": "select_car",
            "message": "Car manager not available"
        }
    
    if not websocket_id:
        return {
            "status": "error",
            "action": "select_car",
            "message": "WebSocket ID not available"
        }
    
    success, message, car = car_manager.select_car(car_id, websocket_id)
    
    if success:
        return {
            "status": "success",
            "action": "select_car",
            "car": car_id
        }
    else:
        return {
            "status": "error",
            "action": "select_car",
            "message": message
        }

def handle_free_car(data, car_manager=None, websocket_id=None):
    """Handle car freeing requests."""
    car_id = data.get("car")
    
    if car_id is None:
        return {
            "status": "error",
            "action": "free_car",
            "message": "Car ID is required"
        }
    
    if not car_manager:
        return {
            "status": "error",
            "action": "free_car", 
            "message": "Car manager not available"
        }
    
    success, message = car_manager.free_car(car_id, websocket_id)
    
    return {
        "status": "success" if success else "error",
        "action": "free_car",
        "message": message,
        "car": car_id
    }

# ============================================================================
# Game Management Handlers
# ============================================================================

def handle_get_game_status(data, game_manager=None):
    """Handle get game status requests."""
    if not game_manager:
        return {
            "status": "error",
            "action": "get_game_status",
            "message": "Game manager not available"
        }
    
    current_game = game_manager.get_current_game()
    
    return {
        "status": "success",
        "action": "get_game_status",
        "game_status": current_game.to_dict()
    }

def handle_resume_game(data, game_manager=None):
    """Handle resume game requests."""
    if not game_manager:
        return {
            "status": "error",
            "action": "resume_game",
            "message": "Game manager not available"
        }
    
    success = game_manager.resume_game()
    
    if success:
        return {
            "status": "success",
            "action": "resume_game",
            "message": "Game resumed!"
        }
    else:
        return {
            "status": "error",
            "action": "resume_game",
            "message": "Cannot resume game. Game may not be paused or may be finished."
        }

def handle_start_game(data, game_manager=None):
    """Handle start game requests. This resets and starts the game."""
    if not game_manager:
        return {
            "status": "error",
            "action": "start_game",
            "message": "Game manager not available"
        }
    
    match_length = data.get("match_length_seconds")
    
    # Validate match length if provided
    if match_length is not None:
        try:
            match_length = int(match_length)
            if match_length <= 0:
                raise ValueError("Match length must be positive")
        except (ValueError, TypeError):
            return {
                "status": "error",
                "action": "start_game",
                "message": "Invalid match length. Must be a positive integer."
            }
    
    success = game_manager.start_game(match_length)
    
    if success:
        return {
            "status": "success",
            "action": "start_game",
            "message": "Game started!"
        }
    else:
        return {
            "status": "error",
            "action": "start_game",
            "message": "Failed to start game"
        }

def handle_end_game(data, game_manager=None):
    """Handle end game requests."""
    if not game_manager:
        return {
            "status": "error",
            "action": "end_game",
            "message": "Game manager not available"
        }
    
    success = game_manager.end_game()
    
    if success:
        return {
            "status": "success",
            "action": "end_game",
            "message": "Game ended!"
        }
    else:
        return {
            "status": "error",
            "action": "end_game",
            "message": "Failed to end game"
        }

def handle_score_goal(data, game_manager=None):
    """Handle goal scoring requests."""
    if not game_manager:
        return {
            "status": "error",
            "action": "score_goal",
            "message": "Game manager not available"
        }
    
    team_color = data.get("team")
    player_id = data.get("player_id")
    car_id = data.get("car_id")
    
    if not team_color:
        return {
            "status": "error",
            "action": "score_goal",
            "message": "Team color is required"
        }
    
    success = game_manager.score_goal(team_color, player_id, car_id)
    
    if success:
        current_game = game_manager.get_current_game()
        return {
            "status": "success",
            "action": "score_goal",
            "message": f"Goal scored by {team_color} team!",
            "game_status": current_game.to_dict() if current_game else None
        }
    else:
        return {
            "status": "error",
            "action": "score_goal",
            "message": f"Failed to score goal. Invalid team '{team_color}' or no active game."
        }

def handle_add_car_to_team(data, game_manager=None):
    """Handle adding car to team requests."""
    if not game_manager:
        return {
            "status": "error",
            "action": "add_car_to_team",
            "message": "Game manager not available"
        }
    
    car_id = data.get("car_id")
    team_color = data.get("team")
    
    if car_id is None:
        return {
            "status": "error",
            "action": "add_car_to_team",
            "message": "Car ID is required"
        }
    
    if not team_color:
        return {
            "status": "error",
            "action": "add_car_to_team",
            "message": "Team color is required"
        }
    
    try:
        car_id = int(car_id)
    except (ValueError, TypeError):
        return {
            "status": "error",
            "action": "add_car_to_team",
            "message": "Invalid car ID. Must be an integer."
        }
    
    success = game_manager.add_car_to_team(car_id, team_color)
    
    if success:
        current_game = game_manager.get_current_game()
        return {
            "status": "success",
            "action": "add_car_to_team",
            "message": f"Car {car_id} added to {team_color} team",
            "game_status": current_game.to_dict() if current_game else None
        }
    else:
        return {
            "status": "error",
            "action": "add_car_to_team",
            "message": f"Failed to add car {car_id} to team. Car not found or invalid team '{team_color}'."
        }

def handle_remove_car_from_teams(data, game_manager=None):
    """Handle removing car from all teams requests."""
    if not game_manager:
        return {
            "status": "error",
            "action": "remove_car_from_teams",
            "message": "Game manager not available"
        }
    
    car_id = data.get("car_id")
    
    if car_id is None:
        return {
            "status": "error",
            "action": "remove_car_from_teams",
            "message": "Car ID is required"
        }
    
    try:
        car_id = int(car_id)
    except (ValueError, TypeError):
        return {
            "status": "error",
            "action": "remove_car_from_teams",
            "message": "Invalid car ID. Must be an integer."
        }
    
    current_game = game_manager.get_current_game()
    if current_game:
        current_game.remove_car_from_teams(car_id)
        return {
            "status": "success",
            "action": "remove_car_from_teams",
            "message": f"Car {car_id} removed from all teams",
            "game_status": current_game.to_dict()
        }
    else:
        return {
            "status": "error",
            "action": "remove_car_from_teams",
            "message": "No active game"
        }

def handle_add_team(data, game_manager=None):
    """Handle adding new team requests."""
    if not game_manager:
        return {
            "status": "error",
            "action": "add_team",
            "message": "Game manager not available"
        }
    
    color = data.get("color")
    name = data.get("name")
    
    if not color:
        return {
            "status": "error",
            "action": "add_team",
            "message": "Team color is required"
        }
    
    current_game = game_manager.get_current_game()
    if current_game:
        team = current_game.add_team(color, name)
        return {
            "status": "success",
            "action": "add_team",
            "message": f"Team '{team.name}' added successfully",
            "game_status": current_game.to_dict()
        }
    else:
        return {
            "status": "error",
            "action": "add_team",
            "message": "No active game. Create a game first."
        }

def handle_stop_game(data, game_manager=None):
    """Handle stop game requests. This pauses the game."""
    if not game_manager:
        return {
            "status": "error",
            "action": "stop_game",
            "message": "Game manager not available"
        }
    
    success = game_manager.stop_game()
    
    if success:
        return {
            "status": "success",
            "action": "stop_game",
            "message": "Game stopped!"
        }
    else:
        return {
            "status": "error",
            "action": "stop_game",
            "message": "No active game to stop"
        }

def handle_goal_scored(data, game_manager=None):
    """Handle goal scored requests (maps to score_goal functionality)."""
    if not game_manager:
        return {
            "status": "error",
            "action": "goal_scored",
            "message": "Game manager not available"
        }
    
    team_color = data.get("team")
    player_id = data.get("player_id")
    car_id = data.get("car_id")
    
    if not team_color:
        return {
            "status": "error",
            "action": "goal_scored",
            "message": "Team color is required"
        }
    
    success = game_manager.score_goal(team_color, player_id, car_id)
    
    if success:
        return {
            "status": "success",
            "action": "goal_scored",
            "message": f"Goal scored by {team_color} team!"
        }
    else:
        return {
            "status": "error",
            "action": "goal_scored",
            "message": f"Failed to score goal. Invalid team '{team_color}' or no active game."
        }


# Action dispatch dictionary
ACTION_HANDLERS = {
    "move_car": handle_move_car,
    "get_car_status": handle_get_car_status,
    "get_all_cars": handle_get_all_cars,
    "get_free_cars": handle_get_free_cars,
    "select_car": handle_select_car,
    "free_car": handle_free_car,
    "send_to_car": handle_send_to_car,
    "connect_to_car": handle_connect_to_car,
    "switch_to_scan_phase": handle_switch_to_scan_phase,
    "switch_to_control_phase": handle_switch_to_control_phase,
    "get_phase_status": handle_get_phase_status,
    # Game management actions
    "start_game": handle_start_game,
    "stop_game": handle_stop_game,
    "resume_game": handle_resume_game,
    "end_game": handle_end_game,
    "get_game_status": handle_get_game_status,
    "goal_scored": handle_goal_scored,
    "score_goal": handle_score_goal,
    "add_car_to_team": handle_add_car_to_team,
    "remove_car_from_teams": handle_remove_car_from_teams,
    "add_team": handle_add_team,
}

# Add Bluetooth handlers if available
if BLUETOOTH_AVAILABLE:
    ACTION_HANDLERS.update(BLUETOOTH_HANDLERS)
