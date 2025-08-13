import asyncio
import websockets
import websockets.exceptions
import json
from .handlers import *

# Global car manager reference
car_manager = None

def set_car_manager(manager):
    """Set the global car manager reference."""
    global car_manager
    car_manager = manager

def get_car_manager():
    """Get the global car manager reference."""
    return car_manager

async def handle_message(websocket, path=None):
    """Handle WebSocket messages. Path parameter for compatibility with websockets library."""
    async for message in websocket:
        try:
            data = json.loads(message)
            print(f"Reçu: {data}")
            
            action = data.get("action")
            
            if action in ACTION_HANDLERS:
                response = ACTION_HANDLERS[action](data, car_manager)
            else:
                response = handle_unknown_action(data)
                
            await websocket.send(json.dumps(response))
            
        except json.JSONDecodeError:
            error_response = handle_invalid_json()
            await websocket.send(json.dumps(error_response))
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
            break
        except Exception as e:
            print(f"Error handling message: {e}")
            error_response = {
                "status": "error",
                "message": "Internal server error"
            }
            try:
                await websocket.send(json.dumps(error_response))
            except:
                pass

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
