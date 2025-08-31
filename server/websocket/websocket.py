import asyncio
import websockets
import websockets.exceptions
import json
import uuid
import logging
from .handlers import *
from .async_handlers import ASYNC_HANDLERS

# Global car manager for WebSocket handler access
car_manager = None

# Global game manager for WebSocket handler access
game_manager = None

# Active WebSocket connections registry for broadcast and management
active_connections = {}

logger = logging.getLogger(__name__)

def initialize_handlers():
    """Initialize handlers with broadcast functionality."""
    from .async_handlers import set_broadcast_function
    set_broadcast_function(broadcast_to_all_clients)

def set_car_manager(manager):
    """
    Configure the global car manager for WebSocket handler access.
    
    Args:
        manager: CarManager instance for vehicle operations
    """
    global car_manager
    car_manager = manager

def set_game_manager(manager):
    """
    Configure the global game manager for WebSocket handler access.
    
    Args:
        manager: GameManager instance for game operations
    """
    global game_manager
    game_manager = manager

def get_car_manager():
    """
    Retrieve the global car manager instance.
    
    Returns:
        CarManager: Active car manager or None if not initialized
    """
    return car_manager

def get_game_manager():
    """
    Retrieve the global game manager instance.
    
    Returns:
        GameManager: Active game manager or None if not initialized
    """
    return game_manager

async def handle_message(websocket, path=None):
    """
    Process incoming WebSocket messages and route to appropriate handlers.
    
    Manages the complete lifecycle of a WebSocket connection including:
    - Connection registration and unique ID assignment
    - Message parsing and validation
    - Action routing to sync/async handlers
    - Error handling and response formatting
    - Connection cleanup on disconnect
    
    Args:
        websocket: WebSocket connection object
        path: URL path (for websockets library compatibility)
    """
    # Assign unique identifier for connection tracking and car assignment
    websocket_id = str(uuid.uuid4())
    active_connections[websocket_id] = websocket
    
    logger.info(f"New WebSocket connection established: {websocket_id}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"Reçu: {data}")
                
                action = data.get("action")
                
                # Route to async handlers first (for operations requiring await)
                if action in ASYNC_HANDLERS:
                    # Pass game_manager to async game handlers
                    if action in ["start_game", "stop_game", "resume_game", "end_game", "goal_scored"]:
                        response = await ASYNC_HANDLERS[action](data, game_manager=game_manager)
                    else:
                        response = await ASYNC_HANDLERS[action](data, car_manager)
                # Route to synchronous handlers for immediate operations
                elif action in ACTION_HANDLERS:
                    # Synchronous game management actions
                    if action in ["get_game_status", "score_goal", "add_car_to_team", "remove_car_from_teams", "add_team"]:
                        response = ACTION_HANDLERS[action](data, game_manager=game_manager)
                    # Pass websocket_id for car assignment and ownership tracking
                    elif action in ["select_car", "free_car", "move_car", "send_to_car", "connect_to_car"]:
                        response = ACTION_HANDLERS[action](data, car_manager, websocket_id)
                    else:
                        response = ACTION_HANDLERS[action](data, car_manager)
                else:
                    response = handle_unknown_action(data)
                    
                await websocket.send(json.dumps(response))
                
            except json.JSONDecodeError:
                error_response = handle_invalid_json()
                await websocket.send(json.dumps(error_response))
            except websockets.exceptions.ConnectionClosed:
                print(f"Client {websocket_id} disconnected")
                break
            except Exception as e:
                print(f"Error handling message from {websocket_id}: {e}")
                error_response = {
                    "status": "error",
                    "message": "Internal server error"
                }
                try:
                    await websocket.send(json.dumps(error_response))
                except:
                    pass
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {websocket_id} disconnected during message handling")
    finally:
        # Cleanup: free all cars assigned to this websocket
        await cleanup_websocket_connection(websocket_id)

async def cleanup_websocket_connection(websocket_id):
    """Clean up resources when a websocket connection closes."""
    if websocket_id in active_connections:
        del active_connections[websocket_id]
    
    if car_manager:
        freed_cars = car_manager.free_cars_by_websocket(websocket_id)
        if freed_cars:
            logger.info(f"Freed cars {freed_cars} from disconnected websocket {websocket_id}")
            print(f"Freed cars {freed_cars} from disconnected websocket {websocket_id}")
    
    logger.info(f"WebSocket connection {websocket_id} cleaned up")

async def broadcast_to_all_clients(message):
    """
    Broadcast a message to all connected WebSocket clients.
    
    Args:
        message (dict): Message to broadcast to all clients
    """
    if not active_connections:
        logger.info("No active connections for broadcast")
        return
    
    # Convert message to JSON string
    message_str = json.dumps(message)
    
    # Keep track of connections to remove if they're closed
    disconnected_connections = []
    
    # Send to all active connections
    for websocket_id, websocket in active_connections.items():
        try:
            await websocket.send(message_str)
            logger.debug(f"Broadcast sent to {websocket_id}")
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection {websocket_id} closed during broadcast")
            disconnected_connections.append(websocket_id)
        except Exception as e:
            logger.error(f"Error broadcasting to {websocket_id}: {e}")
            disconnected_connections.append(websocket_id)
    
    # Clean up disconnected connections
    for websocket_id in disconnected_connections:
        await cleanup_websocket_connection(websocket_id)
    
    logger.info(f"Broadcast sent to {len(active_connections) - len(disconnected_connections)} clients")

async def game_time_monitor():
    """Monitor game time and broadcast when game ends due to time expiration."""
    while True:
        try:
            if game_manager:
                # Check if game should end due to time
                if game_manager.check_game_time():
                    # Game was ended due to time expiration
                    current_game = game_manager.get_current_game()
                    final_status = current_game.to_dict()
                    
                    # Import broadcast function from async_handlers
                    from .async_handlers import broadcast_game_event
                    await broadcast_game_event(
                        "game_ended",
                        "⏰ Game ended - Time expired!",
                        final_status
                    )
                    
                    logger.info("Game ended due to time expiration - broadcast sent")
            
            # Check every second
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Error in game time monitor: {e}")
            await asyncio.sleep(5)  # Wait longer if there's an error

async def start_server_async(port=8000):
    print(f"Serveur WebSocket en écoute sur le port {port}...")
    async with websockets.serve(handle_message, "0.0.0.0", port):
        await asyncio.Future()  # Run forever

def start_server(port=8000):
    asyncio.run(start_server_async(port))

async def start_server_with_cars(manager, port=8000):
    """Start the WebSocket server with a car manager (async version)."""
    set_car_manager(manager)
    print(f"Serveur WebSocket en écoute sur le port {port}...")
    async with websockets.serve(handle_message, "0.0.0.0", port):
        await asyncio.Future()  # Run forever

async def start_server_with_managers(car_mgr, game_mgr, port=8000):
    """Start the WebSocket server with both car and game managers (async version)."""
    set_car_manager(car_mgr)
    set_game_manager(game_mgr)
    initialize_handlers()  # Initialize broadcast functionality
    
    # Start the game time monitor as a background task
    asyncio.create_task(game_time_monitor())
    
    print(f"Serveur WebSocket en écoute sur le port {port}...")
    async with websockets.serve(handle_message, "0.0.0.0", port):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    start_server()
