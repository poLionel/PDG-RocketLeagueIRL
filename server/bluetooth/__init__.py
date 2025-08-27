"""
Bluetooth module for Rocket League IRL server.
Provides automatic device discovery and pairing functionality.
"""

from .bluetooth_service import BluetoothService, BluetoothDevice, check_bluetooth_dependencies
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
    'check_bluetooth_dependencies',
    'BLUETOOTH_HANDLERS',
    'set_bluetooth_service',
    'get_bluetooth_service',
    'handle_get_bluetooth_status',
    'handle_start_bluetooth_scan',
    'handle_stop_bluetooth_scan',
    'handle_pair_bluetooth_device'
]
