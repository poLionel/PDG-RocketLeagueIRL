"""
Bluetooth module for Rocket League IRL server.
Provides automatic device discovery and pairing functionality.
"""

from .ble_constants import check_bluetooth_dependencies
from .bluetooth_service import BluetoothService, BluetoothDevice
from .ble_service import BLEService
from .ble_device import PDGCarDevice
from .handlers import (
    BLUETOOTH_HANDLERS,
    set_bluetooth_service,
    get_bluetooth_service,
    handle_get_bluetooth_status,
    handle_start_bluetooth_scan,
    handle_stop_bluetooth_scan,
    handle_pair_bluetooth_device
)

__all__ = [
    'BluetoothService', 
    'BluetoothDevice', 
    'BLEService',
    'PDGCarDevice',
    'check_bluetooth_dependencies',
    'BLUETOOTH_HANDLERS',
    'set_bluetooth_service',
    'get_bluetooth_service',
    'handle_get_bluetooth_status',
    'handle_start_bluetooth_scan',
    'handle_stop_bluetooth_scan',
    'handle_pair_bluetooth_device'
]
