"""
BLE constants, UUIDs, and utility functions for PDG-RocketLeagueIRL car communication.

This module defines the Bluetooth Low Energy protocol specification for communicating
with physical Rocket League cars, including service UUIDs, characteristic definitions,
and utility functions for data handling and validation.
"""

import logging

# BLE Service and Characteristic UUIDs for PDG cars
# These UUIDs must match the firmware implementation on the car's ESP32 controller
SERVICE_UUID = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f0"  # Main service for car communication

# WiFi provisioning characteristics - used for initial car network setup
CHAR_SSID = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f1"     # WiFi network name
CHAR_PASS = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f2"     # WiFi network password
CHAR_APPLY = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f3"    # Trigger WiFi configuration apply

# Status and identification characteristics - for monitoring and device discovery
CHAR_STATUS = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f4"   # Real-time device status updates
CHAR_DEVID = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f9"    # Unique device identifier
CHAR_BATTERY = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f5"  # Battery level (0-100%)

# Motor control characteristics - primary vehicle movement commands
CHAR_DIR_X = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f6"    # Steering (-100 to +100)
CHAR_DIR_Y = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f7"    # Throttle (-100 to +100)
CHAR_DIR_SPEED = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f8" # Motor speed control
CHAR_DECAY_MODE = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1fa" # Motor braking behavior

# Device identification constants
CAR_DEVICE_PREFIX = "RL-CAR-"  # BLE advertisement name prefix for car discovery

# Module logger for debugging BLE operations
logger = logging.getLogger(__name__)


def dump(label, data):
    """
    Debug utility to log binary data in both hexadecimal and text formats.
    
    Useful for analyzing BLE characteristic data during development and debugging.
    
    Args:
        label (str): Descriptive label for the data dump
        data (bytes): Binary data to analyze
    """
    b = bytes(data)
    try:
        txt = b.decode("utf-8")
    except Exception:
        txt = "<invalid-utf8>"
    logger.info(f"{label}: len={len(b)} hex={b.hex()} text={txt!r}")


def clamp(v: int, lo: int, hi: int) -> int:
    """
    Constrain an integer value within specified bounds.
    
    Essential for ensuring motor control values stay within safe operational ranges.
    
    Args:
        v (int): Value to constrain
        lo (int): Minimum allowed value
        hi (int): Maximum allowed value
        
    Returns:
        int: Clamped value between lo and hi (inclusive)
    """
    return max(lo, min(hi, v))


def check_bluetooth_dependencies() -> bool:
    """
    Verify that required Bluetooth libraries are available for import.
    
    Gracefully handles environments where Bluetooth support is not installed,
    allowing the server to continue operation with reduced functionality.
    
    Returns:
        bool: True if Bluetooth dependencies are available, False otherwise
    """
    try:
        import bleak
        return True
    except ImportError:
        logger.warning("Bleak library not available - Bluetooth functionality disabled")
        return False
