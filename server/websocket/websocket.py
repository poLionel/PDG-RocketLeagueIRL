import asyncio
import websockets
import websockets.exceptions
import json
import uuid
import logging
from .handlers import *
from .async_handlers import ASYNC_HANDLERS

# Global car manager reference
car_manager = None

# Track active websocket connections
active_connections = {}

logger = logging.getLogger(__name__)

def set_car_manager(manager):
    """Set the global car manager reference."""
    global car_manager
    car_manager = manager

def get_car_manager():
    """Get the global car manager reference."""
    return car_manager

async def handle_message(websocket, path=None):
    """Handle WebSocket messages. Path parameter for compatibility with websockets library."""
    # Generate unique ID for this websocket connection
    websocket_id = str(uuid.uuid4())
    active_connections[websocket_id] = websocket
    
    logger.info(f"New WebSocket connection established: {websocket_id}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"Reçu: {data}")
                
                action = data.get("action")
                
                # Check if this is an async action first
                if action in ASYNC_HANDLERS:
                    response = await ASYNC_HANDLERS[action](data, car_manager)
                # Check regular handlers
                elif action in ACTION_HANDLERS:
                    # For certain actions, pass the websocket_id
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
