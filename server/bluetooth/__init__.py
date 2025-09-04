"""
Bluetooth module for Rocket League IRL server.
Provides BLE device discovery and communication functionality.
"""

from .ble_constants import check_bluetooth_dependencies
from .ble_service import BLEService, get_bluetooth_service
from .ble_device import PDGCarDevice, BluetoothDevice
from .handlers import (
    BLUETOOTH_HANDLERS,
    set_bluetooth_service
)

__all__ = [
    'BLEService',
    'PDGCarDevice',
    'BluetoothDevice',
    'check_bluetooth_dependencies',
    'BLUETOOTH_HANDLERS',
    'set_bluetooth_service',
    'get_bluetooth_service'
]
