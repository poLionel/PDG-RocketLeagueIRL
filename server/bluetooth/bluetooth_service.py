"""
Bluetooth Low Energy (BLE) service for PDG-RocketLeagueIRL car detection and communication.

This module provides the high-level BluetoothService interface that integrates BLE
functionality with the car management system. It serves as a compatibility layer
and orchestrates device discovery, connection management, and car registration.

The service handles:
- Automatic car discovery via BLE scanning
- Device pairing and connection management  
- Integration with the CarManager for vehicle tracking
- Event callbacks for UI updates and logging
- Graceful error handling for missing Bluetooth dependencies
"""

import asyncio
import logging
import sys
import os
from typing import List, Callable, Optional

# Import handling for both script and module execution
if __name__ == "__main__":
    # Script mode: adjust Python path for standalone execution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    
    from bluetooth.ble_constants import SERVICE_UUID, check_bluetooth_dependencies
    from bluetooth.ble_device import PDGCarDevice
    from bluetooth.ble_service import BLEService
else:
    # Module mode: use standard relative imports
    from .ble_constants import SERVICE_UUID, check_bluetooth_dependencies
    from .ble_device import PDGCarDevice
    from .ble_service import BLEService

logger = logging.getLogger(__name__)


class BluetoothDevice:
    """
    Legacy compatibility wrapper for simple Bluetooth device representation.
    
    Provides a basic interface for representing discovered Bluetooth devices
    without the full BLE connection capabilities of PDGCarDevice.
    """
    def __init__(self, address: str, name: str = "Unknown", paired: bool = False):
        self.address = address
        self.name = name
        self.paired = paired
    
    def __str__(self):
        return f"BluetoothDevice({self.name}, {self.address}, paired={self.paired})"


class BluetoothService:
    """
    High-level Bluetooth service orchestrator for car discovery and management.
    
    This class provides the main interface for Bluetooth functionality in the
    Rocket League IRL system. It wraps the lower-level BLEService and integrates
    with the CarManager to provide seamless device discovery and car registration.
    
    Key responsibilities:
    - Coordinating BLE device scanning and discovery
    - Managing automatic discovery tasks and scheduling
    - Providing event callbacks for UI updates
    - Handling graceful degradation when Bluetooth is unavailable
    """
    
    def __init__(self, car_manager=None):
        self.car_manager = car_manager
        self.ble_service = BLEService(car_manager)
        self.auto_discovery_task = None
        self.is_auto_discovery_running = False
    
    def add_device_callback(self, callback: Callable):
        """Add a callback for device events."""
        self.ble_service.add_device_callback(callback)
    
    def get_paired_devices(self) -> List[BluetoothDevice]:
        """Get currently paired/connected devices."""
        paired_devices = []
        for device in self.ble_service.discovered_devices.values():
            if device.is_connected:
                bt_device = BluetoothDevice(
                    address=device.address,
                    name=device.name,
                    paired=True
                )
                paired_devices.append(bt_device)
        return paired_devices
    
    def discover_devices(self) -> List[BluetoothDevice]:
        """Discover Bluetooth devices synchronously (for compatibility)."""
        # Simplified sync version for compatibility
        return []
    
    async def start_auto_discovery(self):
        """Start automatic device discovery using scan phase."""
        if self.is_auto_discovery_running:
            logger.warning("Auto discovery already running")
            return
        
        self.is_auto_discovery_running = True
        await self.ble_service.start_scan_phase()
    
    async def stop_auto_discovery(self):
        """Stop automatic device discovery."""
        if self.is_auto_discovery_running:
            self.is_auto_discovery_running = False
    
    def get_device_status(self) -> dict:
        """Get the status of all Bluetooth devices."""
        return self.ble_service.get_status()
    
    def pair_device(self, device: BluetoothDevice) -> bool:
        """Pair with a device (simplified for compatibility)."""
        logger.info(f"Pairing request for device: {device}")
        return False
    
    async def send_command_to_car_async(self, ble_address: str, command: str, data: str = "") -> bool:
        """Send a command to a car via BLE (async wrapper)."""
        return await self.ble_service.send_command_to_car(ble_address, command, data)


# Test function for quick BLE testing
async def test_ble_scan():
    """Quick test function to scan for cars."""
    if not check_bluetooth_dependencies():
        print("Bluetooth dependencies not available")
        return
    
    print("Starting BLE test scan...")
    ble_service = BLEService()
    
    try:
        # Test discovery
        cars = await ble_service.discover_cars(timeout=10.0)
        
        if cars:
            print(f"\nFound {len(cars)} cars:")
            for car in cars:
                print(f"  - {car.name} ({car.address}) RSSI: {car.rssi}")
            
            # Test connection to first car
            print(f"\nTesting connection to {cars[0].name}...")
            if await ble_service.connect_to_device(cars[0].address):
                print("Connection successful!")
                
                # Test reading battery
                battery = await ble_service.read_battery_on_car(cars[0].address)
                if battery is not None:
                    print(f"Battery level: {battery}%")
                
                # Test reading car state
                car_state = await ble_service.read_car_state(cars[0].address)
                if car_state:
                    print(f"Car state: {car_state}")
                
                await ble_service.disconnect_from_device(cars[0].address)
            else:
                print("Connection failed")
        else:
            print("No cars found")
    
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()


# Global service instances for easy access
bluetooth_service = None  # Will be initialized on first use
ble_service = None


def get_bluetooth_service(car_manager=None) -> BLEService:
    """Get global BLE service instance."""
    global bluetooth_service, ble_service
    if bluetooth_service is None:
        bluetooth_service = BLEService(car_manager)
        ble_service = bluetooth_service
    return bluetooth_service


def get_legacy_bluetooth_service(car_manager=None) -> BluetoothService:
    """Get legacy Bluetooth service wrapper."""
    return BluetoothService(car_manager)


if __name__ == "__main__":
    asyncio.run(test_ble_scan())
