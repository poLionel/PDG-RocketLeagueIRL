import asyncio
import websockets
import json
from .handlers import *

async def handle_message(websocket, path):
    async for message in websocket:
        try:
            data = json.loads(message)
            print(f"Reçu: {data}")
            
            action = data.get("action")
            
            if action in ACTION_HANDLERS:
                response = ACTION_HANDLERS[action](data)
            else:
                response = handle_unknown_action(data)
                
            await websocket.send(json.dumps(response))
            
        except json.JSONDecodeError:
            error_response = handle_invalid_json()
            await websocket.send(json.dumps(error_response))

async def start_server_async(port=8000):
    print(f"Serveur WebSocket en écoute sur le port {port}...")
    async with websockets.serve(handle_message, "0.0.0.0", port):
        await asyncio.Future()  # Run forever

def start_server(port=8000):
    asyncio.run(start_server_async(port))

if __name__ == "__main__":
    start_server()
