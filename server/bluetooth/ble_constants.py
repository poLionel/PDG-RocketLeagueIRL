"""
BLE constants, UUIDs, and utility functions for PDG-RocketLeagueIRL car communication.
"""

import logging

# BLE Service and Characteristic UUIDs for PDG cars
SERVICE_UUID = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f0"  # Main service for car communication

# WiFi provisioning characteristics
CHAR_SSID = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f1"     # WiFi SSID
CHAR_PASS = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f2"     # WiFi password
CHAR_APPLY = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f3"    # Apply WiFi settings

# Status and identification characteristics
CHAR_STATUS = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f4"   # Device status updates
CHAR_DEVID = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f9"    # Device ID
CHAR_BATTERY = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f5"  # Battery level

# Motor control characteristics
CHAR_DIR_X = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f6"    # X-axis direction
CHAR_DIR_Y = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f7"    # Y-axis direction
CHAR_DIR_SPEED = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f8" # Speed control
CHAR_DECAY_MODE = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1fa" # Motor decay mode

# Device identification
CAR_DEVICE_PREFIX = "RL-CAR-"  # Expected prefix for Rocket League car device names

# Get logger for this module
logger = logging.getLogger(__name__)


def dump(label, data):
    """Debug function to dump data in hex and text format."""
    b = bytes(data)
    try:
        txt = b.decode("utf-8")
    except Exception:
        txt = "<invalid-utf8>"
    logger.info(f"{label}: len={len(b)} hex={b.hex()} text={txt!r}")


def clamp(v: int, lo: int, hi: int) -> int:
    """Clamp an integer value between lo and hi."""
    return max(lo, min(hi, v))


def check_bluetooth_dependencies() -> bool:
    """Check if Bluetooth dependencies are available."""
    try:
        import bleak
        return True
    except ImportError:
        logger.warning("Bleak library not available - Bluetooth functionality disabled")
        return False
