"""
Bluetooth Low Energy (BLE) service for PDG-RocketLeagueIRL car detection and communication.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice

# BLE Service and Characteristic UUIDs for PDG cars
SERVICE_UUID = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f0"
CHAR_DEVID = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f9"
CHAR_STATUS = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f4"
CHAR_SSID = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f1"
CHAR_PASS = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f2"
CHAR_APPLY = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f3"

# Car device name pattern
CAR_DEVICE_PREFIX = "pdg-car"

logger = logging.getLogger(__name__)


class PDGCarDevice:
    """Represents a PDG car BLE device with connection capabilities."""
    
    def __init__(self, device: BLEDevice, device_id: str = None):
        self.device = device
        self.device_id = device_id
        self.name = device.name or "Unknown"
        self.address = device.address
        self.rssi = getattr(device, 'rssi', None)
        self.is_connected = False
        self.client: Optional[BleakClient] = None
        self.status_callback: Optional[Callable] = None
    
    async def connect(self) -> bool:
        """Connect to the BLE device."""
        try:
            self.client = BleakClient(self.device)
            await self.client.connect()
            self.is_connected = True
            
            # Read device ID if not already known
            if not self.device_id:
                try:
                    devid_data = await self.client.read_gatt_char(CHAR_DEVID)
                    self.device_id = devid_data.decode(errors="ignore")
                    logger.info(f"Device ID for {self.name}: {self.device_id}")
                except Exception as e:
                    logger.warning(f"Could not read device ID from {self.name}: {e}")
            
            logger.info(f"Connected to PDG car: {self.name} ({self.address})")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to {self.name}: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from the BLE device."""
        if self.client and self.is_connected:
            try:
                if self.status_callback:
                    await self.client.stop_notify(CHAR_STATUS)
                    self.status_callback = None
                await self.client.disconnect()
                self.is_connected = False
                logger.info(f"Disconnected from {self.name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {self.name}: {e}")
    
    async def subscribe_to_status(self, callback: Callable):
        """Subscribe to status notifications from the device."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        
        def on_status(_, data: bytearray):
            status = data.decode(errors="ignore")
            logger.info(f"Status from {self.name}: {status}")
            callback(self, status)
        
        self.status_callback = on_status
        await self.client.start_notify(CHAR_STATUS, on_status)
        logger.info(f"Subscribed to status notifications from {self.name}")
    
    async def set_wifi_credentials(self, ssid: str, password: str) -> bool:
        """Set WiFi credentials on the device."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        
        try:
            logger.info(f"Setting WiFi credentials on {self.name}: SSID={ssid}")
            
            # Write SSID and password
            await self.client.write_gatt_char(CHAR_SSID, ssid.encode())
            await self.client.write_gatt_char(CHAR_PASS, password.encode())
            
            # Apply the settings
            await self.client.write_gatt_char(CHAR_APPLY, b"\x01")
            
            logger.info(f"WiFi credentials successfully set on {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to set WiFi credentials on {self.name}: {e}")
            return False
    
    def to_dict(self) -> dict:
        """Convert device to dictionary representation."""
        return {
            "name": self.name,
            "address": self.address,
            "device_id": self.device_id,
            "rssi": self.rssi,
            "is_connected": self.is_connected
        }


class BLEService:
    """Service for managing BLE car device discovery and communication."""
    
    def __init__(self):
        self.discovered_devices: Dict[str, PDGCarDevice] = {}
        self.is_scanning = False
        self.scan_task: Optional[asyncio.Task] = None
        self.device_callbacks: List[Callable] = []
    
    def add_device_callback(self, callback: Callable):
        """Add a callback to be called when devices are discovered."""
        self.device_callbacks.append(callback)
    
    def remove_device_callback(self, callback: Callable):
        """Remove a device callback."""
        if callback in self.device_callbacks:
            self.device_callbacks.remove(callback)
    
    def _notify_device_callbacks(self, device: PDGCarDevice, event_type: str):
        """Notify all callbacks about device events."""
        for callback in self.device_callbacks:
            try:
                callback(device, event_type)
            except Exception as e:
                logger.error(f"Error in device callback: {e}")
    
    def is_car_device(self, device: BLEDevice) -> bool:
        """Check if a BLE device is a PDG car based on its name."""
        if not device.name:
            return False
        return device.name.lower().startswith(CAR_DEVICE_PREFIX.lower())
    
    async def discover_cars(self, timeout: float = 10.0) -> List[PDGCarDevice]:
        """Discover PDG car devices via BLE."""
        logger.info(f"Scanning for PDG cars with service UUID {SERVICE_UUID} (timeout: {timeout}s)...")
        
        try:
            # Scan for devices with our specific service UUID
            ble_devices = await BleakScanner.discover(
                timeout=timeout, 
                service_uuids=[SERVICE_UUID]
            )
            
            cars = []
            for ble_device in ble_devices:
                logger.debug(f"Found BLE device: {ble_device.name} ({ble_device.address})")
                
                if self.is_car_device(ble_device):
                    car_device = PDGCarDevice(ble_device)
                    cars.append(car_device)
                    
                    # Update our discovered devices
                    self.discovered_devices[ble_device.address] = car_device
                    self._notify_device_callbacks(car_device, "discovered")
                    
                    logger.info(f"Found PDG car: {car_device.name} ({car_device.address})")
            
            logger.info(f"BLE discovery complete. Found {len(cars)} PDG cars out of {len(ble_devices)} total devices.")
            return cars
            
        except Exception as e:
            logger.error(f"Error during BLE discovery: {e}")
            return []
    
    async def start_continuous_scan(self, scan_interval: float = 10.0):
        """Start continuous scanning for PDG cars."""
        if self.is_scanning:
            logger.warning("Continuous scan already running")
            return
        
        self.is_scanning = True
        logger.info(f"Starting continuous BLE scan for PDG cars (interval: {scan_interval}s)...")
        
        async def scan_loop():
            while self.is_scanning:
                try:
                    await self.discover_cars(timeout=scan_interval)
                    await asyncio.sleep(1.0)  # Brief pause between scans
                except Exception as e:
                    logger.error(f"Error in continuous scan: {e}")
                    await asyncio.sleep(5.0)  # Longer pause on error
        
        self.scan_task = asyncio.create_task(scan_loop())
    
    async def stop_continuous_scan(self):
        """Stop continuous scanning."""
        if not self.is_scanning:
            return
        
        self.is_scanning = False
        if self.scan_task:
            self.scan_task.cancel()
            try:
                await self.scan_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped continuous BLE scan")
    
    async def connect_to_device(self, address: str) -> Optional[PDGCarDevice]:
        """Connect to a specific device by address."""
        if address not in self.discovered_devices:
            logger.error(f"Device {address} not found in discovered devices")
            return None
        
        device = self.discovered_devices[address]
        if await device.connect():
            self._notify_device_callbacks(device, "connected")
            return device
        return None
    
    async def disconnect_from_device(self, address: str):
        """Disconnect from a specific device."""
        if address in self.discovered_devices:
            device = self.discovered_devices[address]
            await device.disconnect()
            self._notify_device_callbacks(device, "disconnected")
    
    async def disconnect_all(self):
        """Disconnect from all connected devices."""
        disconnection_tasks = []
        for device in self.discovered_devices.values():
            if device.is_connected:
                disconnection_tasks.append(device.disconnect())
        
        if disconnection_tasks:
            await asyncio.gather(*disconnection_tasks, return_exceptions=True)
            logger.info("Disconnected from all devices")
    
    async def set_wifi_on_all_cars(self, ssid: str, password: str) -> Dict[str, bool]:
        """Set WiFi credentials on all discovered cars."""
        results = {}
        
        for address, device in self.discovered_devices.items():
            try:
                if not device.is_connected:
                    logger.info(f"Connecting to {device.name} to set WiFi credentials...")
                    if not await device.connect():
                        logger.error(f"Failed to connect to {device.name}")
                        results[address] = False
                        continue
                
                results[address] = await device.set_wifi_credentials(ssid, password)
                
            except Exception as e:
                logger.error(f"Error setting WiFi on {device.name} ({address}): {e}")
                results[address] = False
        
        return results
    
    def get_discovered_devices(self) -> Dict[str, dict]:
        """Get all discovered devices as dictionaries."""
        return {addr: device.to_dict() for addr, device in self.discovered_devices.items()}
    
    def get_connected_devices(self) -> Dict[str, dict]:
        """Get all connected devices as dictionaries."""
        return {
            addr: device.to_dict() 
            for addr, device in self.discovered_devices.items() 
            if device.is_connected
        }
    
    def get_status(self) -> dict:
        """Get the current status of the BLE service."""
        return {
            "is_scanning": self.is_scanning,
            "total_discovered": len(self.discovered_devices),
            "total_connected": len([d for d in self.discovered_devices.values() if d.is_connected]),
            "devices": self.get_discovered_devices()
        }


# Global BLE service instance (maintains compatibility with existing code)
bluetooth_service = BLEService()
ble_service = bluetooth_service  # Alias for clarity


async def test_ble_functionality():
    """Test function to demonstrate BLE functionality."""
    logger.info("=== Testing BLE Functionality ===")
    
    # Test device discovery
    logger.info("Starting device discovery...")
    cars = await ble_service.discover_cars(timeout=15.0)
    
    if not cars:
        logger.info("No PDG cars found during test")
        logger.info("Make sure your PDG car device is:")
        logger.info("1. Powered on")
        logger.info("2. Has BLE enabled")
        logger.info("3. Is advertising the service UUID")
        logger.info("4. Has a name starting with 'pdg-car'")
        return
    
    # Show discovered cars
    logger.info(f"Found {len(cars)} PDG cars:")
    for car in cars:
        logger.info(f"  - {car.name} ({car.address}) RSSI: {car.rssi}")
    
    # Connect to the first car found
    first_car = cars[0]
    logger.info(f"Testing connection to {first_car.name}...")
    
    if await first_car.connect():
        # Subscribe to status updates
        def status_handler(device, status):
            logger.info(f"Status update from {device.name}: {status}")
        
        try:
            await first_car.subscribe_to_status(status_handler)
            
            # Test WiFi credential setting
            test_ssid = "TestWiFi"
            test_password = "TestPassword123"
            
            logger.info(f"Setting WiFi credentials (SSID: {test_ssid})...")
            success = await first_car.set_wifi_credentials(test_ssid, test_password)
            
            if success:
                logger.info("WiFi credentials set successfully")
                # Wait a bit for status updates
                await asyncio.sleep(3.0)
            else:
                logger.error("Failed to set WiFi credentials")
                
        except Exception as e:
            logger.error(f"Error during testing: {e}")
        
        await first_car.disconnect()
    else:
        logger.error(f"Failed to connect to {first_car.name}")
    
    # Test service status
    status = ble_service.get_status()
    logger.info(f"Service status: {status}")
    
    logger.info("=== BLE Test Complete ===")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(test_ble_functionality())
