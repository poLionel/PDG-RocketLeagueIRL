"""
Bluetooth Low Energy (BLE) service for PDG-RocketLeagueIRL car detection and communication.
"""

import asyncio
import logging
import struct
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
CHAR_BATTERY = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f5"
CHAR_DIR_X = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f6"
CHAR_DIR_Y = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f7"
CHAR_DIR_SPEED = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f8"
CHAR_DECAY_MODE = "7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1fa"

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


def clamp(v: int, lo: int, hi: int) -> int:
    """Clamp an integer value between lo and hi."""
    return max(lo, min(hi, v))


class PDGCarDevice:
    """Represents a PDG car BLE device with connection capabilities."""
    
    def __init__(self, device: BLEDevice, device_id: str = None, adapter: str = None):
        self.device = device
        self.device_id = device_id
        self.name = device.name or "Unknown"
        self.address = device.address
        self.rssi = getattr(device, 'rssi', None)
        self.is_connected = False
        self.client: Optional[BleakClient] = None
        self.status_callback: Optional[Callable] = None
        self.adapter = adapter or "hci0"

    async def connect(self, retries: int = 3) -> bool:
        """Connect to the BLE device with retry logic and adapter support."""
        # Ensure any previous client is properly closed
        if self.client:
            try:
                await self.client.__aexit__(None, None, None)
            except:
                pass
            self.client = None
            self.is_connected = False
        
        for attempt in range(1, retries + 1):
            try:
                # Create a fresh client for each attempt
                self.client = BleakClient(self.device.address, adapter=self.adapter)
                await self.client.__aenter__()
                logger.info(f"Connected to device: {self.name} ({self.address}) [adapter={self.adapter}]")
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
                logger.error(f"Attempt {attempt}/{retries} failed to connect to {self.name}: {e}")
                
                # Clean up failed client
                if self.client:
                    try:
                        await self.client.__aexit__(None, None, None)
                    except:
                        pass
                    self.client = None
                
                # If the error is 'InProgress', wait longer before retrying
                if "InProgress" in str(e):
                    await asyncio.sleep(2.5)
                elif "connection abort" in str(e).lower() or "failed" in str(e).lower():
                    # Device reference may be stale, wait a bit longer
                    await asyncio.sleep(3.0)
                elif attempt < retries:
                    await asyncio.sleep(1.0)
                if attempt < retries:
                    logger.info("Retrying BLE connection...")
                else:
                    self.is_connected = False
                    return False
    
    async def disconnect(self):
        """Disconnect from the BLE device."""
        if self.client and self.is_connected:
            try:
                if self.status_callback:
                    await self.client.stop_notify(CHAR_STATUS)
                    self.status_callback = None
                await self.client.__aexit__(None, None, None)
                self.is_connected = False
                logger.info(f"Disconnected from {self.name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {self.name}: {e}")
    
    # --- BLE helpers ---
    async def write_string(self, char_uuid: str, s: str):
        """Write a string value to a characteristic."""
        await self.client.write_gatt_char(char_uuid, s.encode("utf-8"), response=True)

    async def write_bool(self, char_uuid: str, value: bool):
        """Write a boolean value to a characteristic."""
        await self.client.write_gatt_char(char_uuid, b"\x01" if value else b"\x00", response=True)

    async def write_i8(self, char_uuid: str, v: int):
        """Write an 8-bit signed integer to a characteristic."""
        await self.client.write_gatt_char(char_uuid, struct.pack("b", clamp(v, -128, 127)), response=True)

    async def write_u8(self, char_uuid: str, v: int):
        """Write an 8-bit unsigned integer to a characteristic."""
        await self.client.write_gatt_char(char_uuid, struct.pack("B", clamp(v, 0, 255)), response=True)

    async def read_battery(self) -> Optional[int]:
        """Read the battery level from the device."""
        try:
            raw = await self.client.read_gatt_char(CHAR_BATTERY)
            if raw and len(raw) >= 1:
                return raw[0]
        except Exception as e:
            logger.warning(f"Battery read error: {e}")
        return None

    async def set_drive(self, x: int, y: int, speed: int, decay_mode: int):
        """Set drive parameters (x, y, speed, decay_mode) on the car."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        await self.write_i8(CHAR_DIR_X, x)
        await self.write_i8(CHAR_DIR_Y, y)
        await self.write_i8(CHAR_DIR_SPEED, speed)
        await self.write_i8(CHAR_DECAY_MODE, decay_mode)
        logger.info(f"Drive params sent to {self.name}: x={x}, y={y}, speed={speed}, decay_mode={decay_mode}")

    async def set_wifi_credentials(self, ssid: str, password: str) -> bool:
        """Set WiFi credentials on the device using the robust approach."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        try:
            logger.info(f"Setting WiFi credentials on {self.name}: SSID={ssid}")
            await self.write_string(CHAR_SSID, ssid)
            await self.write_string(CHAR_PASS, password)
            await self.write_bool(CHAR_APPLY, True)
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
    
    ble_operation_lock = asyncio.Lock()  # Global lock for BLE operations

    def __init__(self, car_manager=None, adapter: str = None):
        self.car_manager = car_manager
        self.discovered_devices: Dict[str, PDGCarDevice] = {}
        self.is_scanning = False
        self.scan_task: Optional[asyncio.Task] = None
        self.device_callbacks: List[Callable] = []
        self.adapter = adapter or "hci0"
        # Scan/Send window separation
        self.in_scan_window = False
        self.scan_window_duration = 10.0  # 10 seconds for scanning
        self.send_window_duration = 60.0  # 60 seconds for operations
        self.cycle_task: Optional[asyncio.Task] = None
        self.is_cycling = False

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
        async with BLEService.ble_operation_lock:
            try:
                # Scan for devices with our specific service UUID
                ble_devices = await BleakScanner.discover(
                    timeout=timeout, 
                    service_uuids=[SERVICE_UUID],
                    adapter=self.adapter
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
                    car_device = PDGCarDevice(ble_device, adapter=self.adapter)
                    cars.append(car_device)
                    # Update our discovered devices
                    self.discovered_devices[ble_device.address] = car_device
                    self._notify_device_callbacks(car_device, "discovered")
                    
                    # Try to connect immediately while device reference is fresh
                    logger.info(f"Attempting immediate connection to fresh device: {car_device.name}")
                    try:
                        if await car_device.connect(retries=1):
                            logger.info(f"Successfully connected to {car_device.name} during discovery")
                            self._notify_device_callbacks(car_device, "connected")
                        else:
                            logger.info(f"Immediate connection failed for {car_device.name}, will retry later")
                    except Exception as e:
                        logger.warning(f"Immediate connection attempt failed for {car_device.name}: {e}")
                    
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
    
    async def start_scan_send_cycle(self, scan_duration: float = 10.0, send_duration: float = 60.0):
        """Start the scan/send cycle: scan for cars, then allow operations for a window."""
        if self.is_cycling:
            logger.warning("Scan/send cycle already running")
            return
        
        self.scan_window_duration = scan_duration
        self.send_window_duration = send_duration
        self.is_cycling = True
        
        logger.info(f"Starting scan/send cycle: {scan_duration}s scan + {send_duration}s send windows")
        
        async def cycle_loop():
            while self.is_cycling:
                try:
                    # SCAN WINDOW
                    logger.info("=== SCAN WINDOW STARTED ===")
                    self.in_scan_window = True
                    await self.discover_cars(timeout=self.scan_window_duration)
                    self.in_scan_window = False
                    logger.info("=== SCAN WINDOW ENDED ===")
                    
                    # SEND WINDOW
                    logger.info(f"=== SEND WINDOW STARTED ({self.send_window_duration}s) ===")
                    await asyncio.sleep(self.send_window_duration)
                    logger.info("=== SEND WINDOW ENDED ===")
                    
                except Exception as e:
                    logger.error(f"Error in scan/send cycle: {e}")
                    await asyncio.sleep(5.0)  # Brief pause on error
        
        self.cycle_task = asyncio.create_task(cycle_loop())
    
    async def stop_scan_send_cycle(self):
        """Stop the scan/send cycle."""
        if not self.is_cycling:
            return
        
        self.is_cycling = False
        self.in_scan_window = False
        
        if self.cycle_task:
            self.cycle_task.cancel()
            try:
                await self.cycle_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped scan/send cycle")
    
    def is_in_send_window(self) -> bool:
        """Check if we're currently in a send window (operations allowed)."""
        return self.is_cycling and not self.in_scan_window
    
    def is_in_scan_window(self) -> bool:
        """Check if we're currently in a scan window (no operations allowed)."""
        return self.in_scan_window
    
    async def check_existing_connections(self, address: str):
        """Check if device already has active connections and disconnect them."""
        try:
            import subprocess
            # Check for existing connections
            result = subprocess.run(['hcitool', 'con'], capture_output=True, text=True)
            if address.upper() in result.stdout:
                logger.warning(f"Found existing connection to {address}, disconnecting...")
                subprocess.run(['sudo', 'hcitool', 'dc', address], capture_output=True, text=True)
                await asyncio.sleep(1.0)
                return True
        except Exception as e:
            logger.debug(f"Could not check existing connections: {e}")
        return False

    async def reset_bluetooth_adapter(self):
        """Reset the Bluetooth adapter to clear any stuck connections."""
        try:
            logger.info("Resetting Bluetooth adapter...")
            import subprocess
            # Reset the Bluetooth adapter
            result = subprocess.run(['sudo', 'hciconfig', self.adapter, 'down'], 
                                  capture_output=True, text=True, timeout=5)
            await asyncio.sleep(1.0)
            result = subprocess.run(['sudo', 'hciconfig', self.adapter, 'up'], 
                                  capture_output=True, text=True, timeout=5)
            await asyncio.sleep(2.0)
            logger.info("Bluetooth adapter reset complete")
            return True
        except Exception as e:
            logger.warning(f"Failed to reset Bluetooth adapter: {e}")
            return False

    async def connect_to_device(self, address: str) -> Optional[PDGCarDevice]:
        """Connect to a specific device by address using robust logic."""
        if address not in self.discovered_devices:
            logger.error(f"Device {address} not found in discovered devices")
            return None
        
        # Check if we're in a send window (operations allowed)
        if self.is_cycling and self.in_scan_window:
            logger.warning("Connection blocked: currently in scan window. Wait for send window.")
            return None
        
        # Ensure no scan is running before connecting
        async with BLEService.ble_operation_lock:
            device = self.discovered_devices[address]
            
            # If device is already connected, return it
            if device.is_connected:
                return device
            
            # Check for and clear any existing connections
            await self.check_existing_connections(address)
            
            # Try to get a fresh device reference before connecting
            try:
                logger.info(f"Getting fresh device reference for {address}...")
                fresh_devices = await BleakScanner.discover(
                    timeout=3.0, 
                    service_uuids=[SERVICE_UUID],
                    adapter=self.adapter
                )
                
                # Find our specific device in the fresh scan
                fresh_device = None
                for ble_dev in fresh_devices:
                    if ble_dev.address == address:
                        fresh_device = ble_dev
                        break
                
                if fresh_device:
                    # Update our device with the fresh reference
                    device.device = fresh_device
                    logger.info(f"Updated device reference for {device.name}")
                else:
                    logger.warning(f"Device {address} not found in fresh scan, using cached reference")
                    
            except Exception as e:
                logger.warning(f"Failed to get fresh device reference: {e}, using cached reference")
            
            # Now try to connect
            connection_success = False
            for connect_attempt in range(2):  # Try twice, with reset if first fails
                if await device.connect():
                    connection_success = True
                    break
                elif connect_attempt == 0:  # First attempt failed
                    logger.warning(f"Connection failed, resetting Bluetooth adapter...")
                    await self.reset_bluetooth_adapter()
                    await asyncio.sleep(2.0)
            
            if connection_success:
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
    
    async def set_wifi_on_car(self, ble_address: str, ssid: str, password: str) -> bool:
        """Set WiFi credentials on a specific car."""
        if ble_address not in self.discovered_devices:
            logger.error(f"Car with address {ble_address} not found in discovered devices")
            return False
        
        # Check if we're in a send window (operations allowed)
        if self.is_cycling and self.in_scan_window:
            logger.warning("WiFi operation blocked: currently in scan window. Wait for send window.")
            return False
        
        device = self.discovered_devices[ble_address]
        
        try:
            if not device.is_connected:
                logger.info(f"Connecting to {device.name} to set WiFi credentials...")
                if not await self.connect_to_device(ble_address):
                    logger.error(f"Failed to connect to {device.name}")
                    return False
            
            return await device.set_wifi_credentials(ssid, password)
            
        except Exception as e:
            logger.error(f"Error setting WiFi on {device.name} ({ble_address}): {e}")
            return False
    
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
            "is_cycling": self.is_cycling,
            "in_scan_window": self.in_scan_window,
            "in_send_window": self.is_in_send_window(),
            "scan_window_duration": self.scan_window_duration,
            "send_window_duration": self.send_window_duration,
            "total_discovered": len(self.discovered_devices),
            "total_connected": len([d for d in self.discovered_devices.values() if d.is_connected]),
            "devices": self.get_discovered_devices()
        }

    # --- New: drive control API ---
    async def set_drive_on_car(self, ble_address: str, x: int, y: int, speed: int, decay_mode: int) -> bool:
        """Send drive parameters to a car."""
        if ble_address not in self.discovered_devices:
            logger.error(f"Car with address {ble_address} not found in discovered devices")
            return False
        
        # Check if we're in a send window (operations allowed)
        if self.is_cycling and self.in_scan_window:
            logger.warning("Drive operation blocked: currently in scan window. Wait for send window.")
            return False
        
        device = self.discovered_devices[ble_address]
        
        try:
            if not device.is_connected:
                logger.info(f"Connecting to {device.name} to send drive params...")
                if not await self.connect_to_device(ble_address):
                    logger.error(f"Failed to connect to {device.name}")
                    return False
            await device.set_drive(x, y, speed, decay_mode)
            return True
        except Exception as e:
            logger.error(f"Error sending drive params to {device.name}: {e}")
            return False

    async def read_battery_on_car(self, ble_address: str) -> Optional[int]:
        """Read battery level from a car."""
        if ble_address not in self.discovered_devices:
            logger.error(f"Car with address {ble_address} not found in discovered devices")
            return None
        
        # Check if we're in a send window (operations allowed)
        if self.is_cycling and self.in_scan_window:
            logger.warning("Battery read blocked: currently in scan window. Wait for send window.")
            return None
        
        device = self.discovered_devices[ble_address]
        
        try:
            if not device.is_connected:
                logger.info(f"Connecting to {device.name} to read battery...")
                if not await self.connect_to_device(ble_address):
                    logger.error(f"Failed to connect to {device.name}")
                    return None
            return await device.read_battery()
        except Exception as e:
            logger.error(f"Error reading battery from {device.name}: {e}")
            return None


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
        """Start automatic device discovery using scan/send cycles."""
        if self.is_auto_discovery_running:
            logger.warning("Auto discovery already running")
            return
        
        self.is_auto_discovery_running = True
        await self.ble_service.start_scan_send_cycle()
    
    async def stop_auto_discovery(self):
        """Stop automatic device discovery."""
        if self.is_auto_discovery_running:
            self.is_auto_discovery_running = False
            await self.ble_service.stop_scan_send_cycle()
    
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
    logger.info("=== Testing BLE Functionality ===")
    
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
