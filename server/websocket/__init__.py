"""
WebSocket communication module for Rocket League IRL server.

This module provides real-time bidirectional communication between the server
and client applications (mobile app, web interface) via WebSocket protocol.
It handles client connections, message routing, and integration with the
car management and Bluetooth systems.

Main entry point:
- start_server_with_managers: Primary server function with car and game management integration
"""

from .websocket import start_server_with_managers

__all__ = ['start_server_with_managers']
