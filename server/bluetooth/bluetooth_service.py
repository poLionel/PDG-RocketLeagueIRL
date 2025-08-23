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
CHAR_SSID = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f1"
CHAR_PASS = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f2"
CHAR_APPLY = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f3"
CHAR_STATUS = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f4"
CHAR_DEVID = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f9"

# Car device name pattern - updated to match actual format
CAR_DEVICE_PREFIX = "RL-CAR-"

logger = logging.getLogger(__name__)


def dump(label, data):
    """Debug function to dump data in hex and text format."""
    b = bytes(data)
    try:
        txt = b.decode("utf-8")
    except Exception:
        txt = "<invalid-utf8>"
    logger.info(f"{label}: len={len(b)} hex={b.hex()} text={txt!r}")


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
        """Connect to the BLE device using the working approach."""
        try:
            self.client = BleakClient(self.device)
            await self.client.connect()
            logger.info(f"Connected to device: {self.name} ({self.address})")
            
            # Small delay for characteristic setup
            await asyncio.sleep(0.3)
            self.is_connected = True
            
            # Read device ID if not already known
            if not self.device_id:
                try:
                    devid_data = await self.client.read_gatt_char(CHAR_DEVID)
                    self.device_id = devid_data.decode("utf-8", errors="ignore")
                    dump("device_id", devid_data)
                    logger.info(f"Device ID for {self.name}: {self.device_id}")
                except Exception as e:
                    logger.warning(f"Could not read device ID from {self.name}: {e}")
            
            # Read initial status
            try:
                status_data = await self.client.read_gatt_char(CHAR_STATUS)
                dump("STATUS(read)", status_data)
            except Exception as e:
                logger.warning(f"Could not read initial status from {self.name}: {e}")
            
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
            dump("STATUS(notif)", data)
            try:
                status = data.decode("utf-8", errors="ignore")
                logger.info(f"Status from {self.name}: {status}")
                callback(self, status)
            except Exception as e:
                logger.error(f"Error processing status notification: {e}")
        
        self.status_callback = on_status
        await self.client.start_notify(CHAR_STATUS, on_status)
        logger.info(f"Subscribed to status notifications from {self.name}")
    
    async def set_wifi_credentials(self, ssid: str, password: str) -> bool:
        """Set WiFi credentials on the device using the working approach."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        
        try:
            logger.info(f"Setting WiFi credentials on {self.name}: SSID={ssid}")
            
            # Write SSID and password
            await self.client.write_gatt_char(CHAR_SSID, ssid.encode("utf-8"))
            await self.client.write_gatt_char(CHAR_PASS, password.encode("utf-8"))
            logger.info(f"SSID/PASS written to {self.name}")
            
            # Apply the settings
            await self.client.write_gatt_char(CHAR_APPLY, b"\x01")
            logger.info(f"APPLY sent to {self.name}")
            
            # Wait a bit for processing
            await asyncio.sleep(1.0)
            
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
    
    def __init__(self, car_manager=None):
        self.car_manager = car_manager
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
        """Check if a BLE device is a Rocket League car based on its name."""
        if not device.name:
            return False
        return device.name.startswith(CAR_DEVICE_PREFIX)
    
    async def discover_cars(self, timeout: float = 6.0) -> List[PDGCarDevice]:
        """Discover PDG car devices via BLE using the working approach."""
        logger.info(f"Scanning for Rocket League cars with service UUID {SERVICE_UUID} (timeout: {timeout}s)...")
        
        try:
            # Scan for devices with our specific service UUID
            ble_devices = await BleakScanner.discover(
                timeout=timeout, 
                service_uuids=[SERVICE_UUID]
            )
            
            if not ble_devices:
                logger.debug("No BLE devices found with the specified service UUID")
                return []
            
            cars = []
            new_discoveries = 0
            
            for ble_device in ble_devices:
                logger.debug(f"Found BLE device: {ble_device.name} ({ble_device.address})")
                
                # Check if this is a Rocket League car
                if not self.is_car_device(ble_device):
                    logger.debug(f"Skipping non-car device: {ble_device.name}")
                    continue
                
                # Check if we already know about this device
                if ble_device.address in self.discovered_devices:
                    logger.debug(f"Already discovered car: {ble_device.name} ({ble_device.address})")
                    existing_device = self.discovered_devices[ble_device.address]
                    cars.append(existing_device)
                    
                    # Update car manager with latest discovery
                    if self.car_manager:
                        self.car_manager.add_or_update_car_from_ble(ble_device.name, ble_device.address)
                    continue
                
                # New car discovered
                car_device = PDGCarDevice(ble_device)
                cars.append(car_device)
                
                # Update our discovered devices
                self.discovered_devices[ble_device.address] = car_device
                self._notify_device_callbacks(car_device, "discovered")
                
                # Add/update car in CarManager
                if self.car_manager:
                    car = self.car_manager.add_or_update_car_from_ble(ble_device.name, ble_device.address)
                    logger.info(f"Added/updated car in manager: {car}")
                
                new_discoveries += 1
                logger.info(f"Discovered new Rocket League car: {car_device.name} ({car_device.address})")
            
            if new_discoveries > 0:
                logger.info(f"BLE discovery complete. Found {new_discoveries} new cars, {len(cars)} total cars discovered.")
            else:
                logger.debug(f"BLE discovery complete. No new cars found, {len(cars)} total cars known.")
            
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
    
    async def send_command_to_car(self, ble_address: str, command: str, data: str = "") -> bool:
        """Send a command to a specific car via BLE."""
        if ble_address not in self.discovered_devices:
            logger.error(f"Car with address {ble_address} not found in discovered devices")
            return False
        
        device = self.discovered_devices[ble_address]
        
        try:
            # Connect if not already connected
            if not device.is_connected:
                logger.info(f"Connecting to {device.name} to send command...")
                if not await device.connect():
                    logger.error(f"Failed to connect to {device.name}")
                    return False
            
            # For now, we'll send the command as a status update
            # You can modify this to use different characteristics based on your car's BLE service
            
            # Subscribe to status notifications to see responses
            def response_handler(dev, status):
                logger.info(f"Response from {dev.name}: {status}")
            
            await device.subscribe_to_status(response_handler)
            
            # Send command by writing to SSID characteristic (as a test)
            # You should define proper command characteristics in your car firmware
            command_data = f"{command}:{data}".encode("utf-8")
            await device.client.write_gatt_char(CHAR_SSID, command_data)
            
            logger.info(f"Command '{command}' sent to {device.name}")
            
            # Wait a bit for any response
            await asyncio.sleep(1.0)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending command to {device.name}: {e}")
            return False
    
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


# Additional classes for compatibility with existing code
class BluetoothDevice:
    """Simple Bluetooth device representation for compatibility."""
    def __init__(self, address: str, name: str = "Unknown", paired: bool = False):
        self.address = address
        self.name = name
        self.paired = paired
    
    def __str__(self):
        return f"BluetoothDevice({self.name}, {self.address}, paired={self.paired})"


class BluetoothService:
    """Main Bluetooth service class that wraps BLEService for compatibility."""
    
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
        # Note: This is a simplified sync version for compatibility
        # In practice, you'd want to use the async version
        return []
    
    async def start_auto_discovery(self):
        """Start automatic device discovery."""
        if self.is_auto_discovery_running:
            logger.warning("Auto discovery already running")
            return
        
        self.is_auto_discovery_running = True
        await self.ble_service.start_continuous_scan()
    
    def stop_auto_discovery(self):
        """Stop automatic device discovery."""
        if self.is_auto_discovery_running:
            self.is_auto_discovery_running = False
            # Note: BLEService.stop_continuous_scan() is async, but this method needs to be sync
            # In practice, you'd want to handle this properly
    
    def get_device_status(self) -> dict:
        """Get the status of all Bluetooth devices."""
        return self.ble_service.get_status()
    
    def pair_device(self, device: BluetoothDevice) -> bool:
        """Pair with a device (simplified for compatibility)."""
        # This would need to be implemented based on actual pairing logic
        logger.info(f"Pairing request for device: {device}")
        return False
    
    async def send_command_to_car_async(self, ble_address: str, command: str, data: str = "") -> bool:
        """Send a command to a car via BLE (async wrapper)."""
        return await self.ble_service.send_command_to_car(ble_address, command, data)


def check_bluetooth_dependencies() -> bool:
    """Check if Bluetooth dependencies are available."""
    try:
        import bleak
        return True
    except ImportError:
        logger.warning("Bleak library not available - Bluetooth functionality disabled")
        return False


# Global BLE service instance
bluetooth_service = BLEService()
ble_service = bluetooth_service  # Alias for clarity


async def test_ble_functionality():
    """Test function using the working approach."""
    logger.info("=== Testing BLE Functionality (Working Version) ===")
    
    # Simple discovery and connection test
    try:
        devs = await BleakScanner.discover(timeout=6.0, service_uuids=[SERVICE_UUID])
        if not devs:
            logger.warning("No devices found with service UUID")
            logger.info("Make sure your PDG car device is:")
            logger.info("1. Powered on")
            logger.info("2. Has BLE enabled") 
            logger.info("3. Is advertising the service UUID")
            return
        
        dev = devs[0]
        logger.info(f"Target device: {dev.name} {dev.address}")
        
        async with BleakClient(dev) as client:
            logger.info("Connected successfully")
            await asyncio.sleep(0.3)  # Setup delay
            
            # Read device_id and status
            try:
                devid = await client.read_gatt_char(CHAR_DEVID)
                dump("device_id", devid)
            except Exception as e:
                logger.error(f"device_id read error: {e}")
            
            try:
                st = await client.read_gatt_char(CHAR_STATUS)
                dump("STATUS(read)", st)
            except Exception as e:
                logger.error(f"STATUS read error: {e}")
            
            # Subscribe to STATUS notifications
            def on_status(_, data: bytearray):
                dump("STATUS(notif)", data)
            
            await client.start_notify(CHAR_STATUS, on_status)
            
            # Test WiFi credential setting
            test_ssid = "TestWiFi"
            test_password = "TestPassword123"
            
            await client.write_gatt_char(CHAR_SSID, test_ssid.encode("utf-8"))
            await client.write_gatt_char(CHAR_PASS, test_password.encode("utf-8"))
            logger.info("SSID/PASS written")
            
            await client.write_gatt_char(CHAR_APPLY, b"\x01")
            logger.info("APPLY sent")
            
            await asyncio.sleep(3.0)
            logger.info("Test completed successfully")
            
    except Exception as e:
        logger.error(f"Error during BLE test: {e}")
    
    logger.info("=== BLE Test Complete ===")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(test_ble_functionality())
