"""
WebSocket communication module for Rocket League IRL server.

This module provides real-time bidirectional communication between the server
and client applications (mobile app, web interface) via WebSocket protocol.
It handles client connections, message routing, and integration with the
car management and Bluetooth systems.

Main entry points:
- start_server_with_cars: Primary server function with car management integration
- start_server_async: Async server without car dependencies  
- start_server: Legacy synchronous server interface
"""

from .websocket import start_server, start_server_async, start_server_with_cars

__all__ = ['start_server', 'start_server_async', 'start_server_with_cars']
