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

# Active WebSocket connections registry for broadcast and management
active_connections = {}

logger = logging.getLogger(__name__)

def set_car_manager(manager):
    """
    Configure the global car manager for WebSocket handler access.
    
    Args:
        manager: CarManager instance for vehicle operations
    """
    global car_manager
    car_manager = manager

def get_car_manager():
    """
    Retrieve the global car manager instance.
    
    Returns:
        CarManager: Active car manager or None if not initialized
    """
    return car_manager

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
                    response = await ASYNC_HANDLERS[action](data, car_manager)
                # Route to synchronous handlers for immediate operations
                elif action in ACTION_HANDLERS:
                    # Pass websocket_id for car assignment and ownership tracking
                    if action in ["select_car", "free_car", "move_car", "send_to_car", "connect_to_car"]:
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

if __name__ == "__main__":
    start_server()
