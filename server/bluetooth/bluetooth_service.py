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
        self.rssi = None  # Will be set separately from AdvertisementData
        self.is_connected = False
        self.client: Optional[BleakClient] = None
        self.status_callback: Optional[Callable] = None
        self.adapter = adapter or "hci1"

    async def _clear_system_connections(self):
        """Clear any existing system-level connections to this device."""
        try:
            import subprocess
            # Check for existing connections using hcitool
            result = subprocess.run(
                ['hcitool', 'con'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if self.address.upper() in result.stdout or self.address.lower() in result.stdout:
                logger.info(f"Found existing connection to {self.address}, clearing...")
                # Disconnect using hcitool
                subprocess.run(
                    ['sudo', 'hcitool', 'dc', self.address], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                await asyncio.sleep(1.0)
                
                # Also try bluetoothctl disconnect as backup
                subprocess.run(
                    ['bluetoothctl', 'disconnect', self.address], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.debug(f"Could not clear system connections for {self.address}: {e}")

    async def connect(self, retries: int = 5) -> bool:
        """Connect to the BLE device with enhanced retry logic for Raspberry Pi."""
        # Ensure any previous client is properly closed
        if self.client:
            try:
                await self.client.__aexit__(None, None, None)
            except:
                pass
            self.client = None
            self.is_connected = False
        
        # Clear any potential system-level connection conflicts
        await self._clear_system_connections()
        
        for attempt in range(1, retries + 1):
            try:
                # Add a small delay before each attempt to let the Bluetooth stack settle
                if attempt > 1:
                    await asyncio.sleep(0.5)
                
                # Create a fresh client for each attempt with timeout
                self.client = BleakClient(
                    self.device.address, 
                    adapter=self.adapter,
                    timeout=15.0  # Longer timeout for Raspberry Pi
                )
                
                # Try to connect with timeout
                connect_task = asyncio.create_task(self.client.__aenter__())
                try:
                    await asyncio.wait_for(connect_task, timeout=12.0)
                    logger.info(f"Connected to device: {self.name} ({self.address}) [adapter={self.adapter}]")
                except asyncio.TimeoutError:
                    logger.warning(f"Connection timeout for {self.name} on attempt {attempt}")
                    raise Exception("Connection timeout")
                
                # Give the connection time to stabilize
                await asyncio.sleep(0.5)
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
                
                logger.info(f"Successfully connected to {self.name} on attempt {attempt}")
                return True
                
            except Exception as e:
                error_msg = str(e).lower()
                logger.error(f"Attempt {attempt}/{retries} failed to connect to {self.name}: {e}")
                
                # Clean up failed client
                if self.client:
                    try:
                        await self.client.__aexit__(None, None, None)
                    except:
                        pass
                    self.client = None
                
                # Error-specific retry delays for Raspberry Pi
                if "inprogress" in error_msg:
                    # BlueZ operation already in progress
                    delay = 3.0 + (attempt * 0.5)
                    logger.info(f"BlueZ InProgress error, waiting {delay}s before retry...")
                    await asyncio.sleep(delay)
                elif "connection abort" in error_msg or "software caused" in error_msg:
                    # Connection aborted - often due to timing or device state
                    delay = 2.0 + (attempt * 1.0)
                    logger.info(f"Connection abort error, waiting {delay}s before retry...")
                    await asyncio.sleep(delay)
                    # Try to clear any stuck connections
                    await self._clear_system_connections()
                elif "failed" in error_msg or "timeout" in error_msg:
                    # General failure - device may not be responsive
                    delay = 1.5 + (attempt * 0.5)
                    logger.info(f"Connection failed, waiting {delay}s before retry...")
                    await asyncio.sleep(delay)
                elif "device not found" in error_msg or "not available" in error_msg:
                    # Device disappeared - wait longer
                    delay = 4.0
                    logger.info(f"Device not found, waiting {delay}s before retry...")
                    await asyncio.sleep(delay)
                else:
                    # Unknown error - standard delay
                    await asyncio.sleep(1.0 + (attempt * 0.5))
                
                if attempt < retries:
                    logger.info(f"Retrying BLE connection to {self.name}...")
                else:
                    logger.error(f"Failed to connect to {self.name} after {retries} attempts")
                    self.is_connected = False
                    return False
    
    async def disconnect(self):
        """Disconnect from the BLE device with proper cleanup."""
        if self.client and self.is_connected:
            try:
                # Stop any active notifications first
                if self.status_callback:
                    try:
                        await self.client.stop_notify(CHAR_STATUS)
                    except Exception as e:
                        logger.debug(f"Could not stop notifications: {e}")
                    self.status_callback = None
                
                # Disconnect the client
                await self.client.__aexit__(None, None, None)
                self.is_connected = False
                logger.info(f"Disconnected from {self.name}")
                
                # Clear any system-level connections as well
                await self._clear_system_connections()
                
            except Exception as e:
                logger.error(f"Error disconnecting from {self.name}: {e}")
                # Force disconnect regardless of errors
                self.is_connected = False
            finally:
                self.client = None

    async def is_connection_healthy(self) -> bool:
        """Check if the BLE connection is still healthy."""
        if not self.is_connected or not self.client:
            return False
        
        try:
            # Try to read a characteristic to verify connection
            await asyncio.wait_for(
                self.client.read_gatt_char(CHAR_STATUS),
                timeout=3.0
            )
            return True
        except Exception as e:
            logger.debug(f"Connection health check failed for {self.name}: {e}")
            return False
    
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
        self.adapter = adapter or "hci1"
        # Phase management
        self.current_phase = "scan"  # "scan" or "control"
        self.phase_callbacks: List[Callable] = []

    def add_phase_callback(self, callback: Callable):
        """Add a callback to be called when phase changes."""
        self.phase_callbacks.append(callback)
    
    def remove_phase_callback(self, callback: Callable):
        """Remove a phase callback."""
        if callback in self.phase_callbacks:
            self.phase_callbacks.remove(callback)
    
    def _notify_phase_callbacks(self, new_phase: str, discovered_cars: List[PDGCarDevice] = None):
        """Notify all callbacks about phase changes."""
        for callback in self.phase_callbacks:
            try:
                callback(new_phase, discovered_cars or [])
            except Exception as e:
                logger.error(f"Error in phase callback: {e}")

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
    
    async def discover_cars(self, timeout: float = 8.0) -> List[PDGCarDevice]:
        """Discover PDG car devices via BLE using Raspberry Pi optimized approach."""
        logger.info(f"Scanning for Rocket League cars with service UUID {SERVICE_UUID} (timeout: {timeout}s)...")
        async with BLEService.ble_operation_lock:
            try:
                # Clean up any stale connections first
                await self.cleanup_stale_connections()
                
                # Dictionary to store discovered devices with their advertisement data
                discovered_devices_with_rssi = {}
                
                # Use the callback-based scanner to get RSSI values
                def detection_callback(device: BLEDevice, advertisement_data):
                    if self.is_car_device(device):
                        discovered_devices_with_rssi[device.address] = {
                            'device': device,
                            'rssi': advertisement_data.rssi
                        }
                
                # Start scanning with callback
                scanner = BleakScanner(
                    detection_callback=detection_callback,
                    service_uuids=[SERVICE_UUID],
                    adapter=self.adapter
                )
                
                await scanner.start()
                await asyncio.sleep(timeout)
                await scanner.stop()
                
                if not discovered_devices_with_rssi:
                    logger.debug("No BLE devices found with the specified service UUID")
                    return []
                
                cars = []
                new_discoveries = 0
                
                for address, device_info in discovered_devices_with_rssi.items():
                    ble_device = device_info['device']
                    rssi_value = device_info['rssi']
                    
                    logger.debug(f"Found BLE device: {ble_device.name} ({ble_device.address}) RSSI: {rssi_value}")
                    
                    # Check if we already know about this device
                    if ble_device.address in self.discovered_devices:
                        logger.debug(f"Already discovered car: {ble_device.name} ({ble_device.address})")
                        existing_device = self.discovered_devices[ble_device.address]
                        # Update with fresh device reference and RSSI
                        existing_device.device = ble_device
                        existing_device.rssi = rssi_value
                        cars.append(existing_device)
                        
                        # Update car manager with latest discovery
                        if self.car_manager:
                            self.car_manager.add_or_update_car_from_ble(ble_device.name, ble_device.address)
                        continue
                    
                    # New car discovered
                    car_device = PDGCarDevice(ble_device, adapter=self.adapter)
                    car_device.rssi = rssi_value  # Set RSSI from advertisement data
                    cars.append(car_device)
                    
                    # Update our discovered devices
                    self.discovered_devices[ble_device.address] = car_device
                    self._notify_device_callbacks(car_device, "discovered")
                    
                    # Add/update car in CarManager
                    if self.car_manager:
                        car = self.car_manager.add_or_update_car_from_ble(ble_device.name, ble_device.address)
                        logger.info(f"Added/updated car in manager: {car}")
                    
                    new_discoveries += 1
                    logger.info(f"Discovered new Rocket League car: {car_device.name} ({car_device.address}) RSSI: {rssi_value}")
                
                if new_discoveries > 0:
                    logger.info(f"BLE discovery complete. Found {new_discoveries} new cars, {len(cars)} total cars discovered.")
                else:
                    logger.debug(f"BLE discovery complete. No new cars found, {len(cars)} total cars known.")
                
                return cars
                
            except Exception as e:
                logger.error(f"Error during BLE discovery: {e}")
                return []
    
    async def start_scan_phase(self) -> List[PDGCarDevice]:
        """Start scanning phase - discover cars and switch to control phase when found."""
        if self.current_phase == "control":
            logger.info("Switching from control phase to scan phase")
        
        self.current_phase = "scan"
        logger.info("=== SCAN PHASE STARTED ===")
        
        # Discover cars
        discovered_cars = await self.discover_cars(timeout=10.0)
        
        if discovered_cars:
            logger.info(f"Found {len(discovered_cars)} cars, switching to control phase")
            self.current_phase = "control"
            self._notify_phase_callbacks("control", discovered_cars)
            logger.info("=== CONTROL PHASE STARTED ===")
        else:
            logger.info("No cars found, staying in scan phase")
            self._notify_phase_callbacks("scan", [])
        
        return discovered_cars
    
    async def switch_to_control_phase(self):
        """Manually switch to control phase."""
        if self.current_phase != "control":
            self.current_phase = "control"
            logger.info("=== SWITCHED TO CONTROL PHASE ===")
            self._notify_phase_callbacks("control", list(self.discovered_devices.values()))
    
    async def switch_to_scan_phase(self):
        """Manually switch back to scan phase."""
        if self.current_phase != "scan":
            self.current_phase = "scan"
            logger.info("=== SWITCHED TO SCAN PHASE ===")
            self._notify_phase_callbacks("scan", [])
    
    def get_current_phase(self) -> str:
        """Get the current phase."""
        return self.current_phase
    
    def is_in_control_phase(self) -> bool:
        """Check if we're currently in control phase (operations allowed)."""
        return self.current_phase == "control"
    
    def is_in_scan_phase(self) -> bool:
        """Check if we're currently in scan phase."""
        return self.current_phase == "scan"
    
    async def check_existing_connections(self, address: str):
        """Check if device already has active connections and disconnect them (Raspberry Pi optimized)."""
        try:
            import subprocess
            # Check for existing connections using multiple methods
            
            # Method 1: hcitool
            result = subprocess.run(['hcitool', 'con'], capture_output=True, text=True, timeout=5)
            address_found = False
            if address.upper() in result.stdout or address.lower() in result.stdout:
                address_found = True
                logger.warning(f"Found existing hcitool connection to {address}")
                
                # Try multiple disconnect methods
                subprocess.run(['sudo', 'hcitool', 'dc', address], 
                             capture_output=True, text=True, timeout=5)
                await asyncio.sleep(1.0)
            
            # Method 2: bluetoothctl
            result = subprocess.run(['bluetoothctl', 'info', address], 
                                  capture_output=True, text=True, timeout=5)
            if 'Connected: yes' in result.stdout:
                address_found = True
                logger.warning(f"Found existing bluetoothctl connection to {address}")
                subprocess.run(['bluetoothctl', 'disconnect', address], 
                             capture_output=True, text=True, timeout=5)
                await asyncio.sleep(1.0)
            
            if address_found:
                logger.info(f"Cleared existing connections to {address}")
                # Extra wait to ensure disconnection is complete
                await asyncio.sleep(1.5)
                return True
                
        except Exception as e:
            logger.debug(f"Could not check existing connections for {address}: {e}")
        return False

    async def cleanup_stale_connections(self):
        """Clean up any stale connections to discovered devices."""
        logger.info("Cleaning up stale BLE connections...")
        for address, device in self.discovered_devices.items():
            if device.is_connected:
                if not await device.is_connection_healthy():
                    logger.warning(f"Found stale connection to {device.name}, cleaning up...")
                    await device.disconnect()
        logger.info("Stale connection cleanup complete")

    async def reset_bluetooth_adapter(self):
        """Reset the Bluetooth adapter to clear any stuck connections (Raspberry Pi optimized)."""
        try:
            logger.info("Resetting Bluetooth adapter...")
            import subprocess
            
            # Step 1: Disconnect all active connections
            try:
                result = subprocess.run(['hcitool', 'con'], capture_output=True, text=True, timeout=5)
                if result.stdout and 'RL-CAR' in result.stdout:
                    logger.info("Disconnecting active car connections...")
                    subprocess.run(['sudo', 'hcitool', 'cc'], capture_output=True, text=True, timeout=5)
                    await asyncio.sleep(1.0)
            except Exception as e:
                logger.debug(f"Could not disconnect active connections: {e}")
            
            # Step 2: Reset the specific adapter
            logger.info(f"Resetting adapter {self.adapter}...")
            result = subprocess.run(['sudo', 'hciconfig', self.adapter, 'down'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                logger.warning(f"Failed to bring adapter down: {result.stderr}")
            
            await asyncio.sleep(2.0)
            
            result = subprocess.run(['sudo', 'hciconfig', self.adapter, 'up'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                logger.warning(f"Failed to bring adapter up: {result.stderr}")
            
            await asyncio.sleep(2.0)
            
            # Step 3: Clear any cached connections in bluetoothctl
            try:
                subprocess.run(['bluetoothctl', 'power', 'off'], 
                             capture_output=True, text=True, timeout=5)
                await asyncio.sleep(1.0)
                subprocess.run(['bluetoothctl', 'power', 'on'], 
                             capture_output=True, text=True, timeout=5)
                await asyncio.sleep(1.5)
            except Exception as e:
                logger.debug(f"Could not reset via bluetoothctl: {e}")
            
            # Step 4: Verify adapter is working
            result = subprocess.run(['hciconfig', self.adapter], 
                                  capture_output=True, text=True, timeout=5)
            if 'UP RUNNING' in result.stdout:
                logger.info("Bluetooth adapter reset successful")
                return True
            else:
                logger.warning("Bluetooth adapter may not be fully operational after reset")
                return False
                
        except Exception as e:
            logger.error(f"Failed to reset Bluetooth adapter: {e}")
            return False

    async def connect_to_device(self, address: str) -> Optional[PDGCarDevice]:
        """Connect to a specific device by address using enhanced Raspberry Pi logic."""
        if address not in self.discovered_devices:
            logger.error(f"Device {address} not found in discovered devices")
            return None
        
        # Check if we're in control phase (operations allowed)
        if not self.is_in_control_phase():
            logger.warning("Connection blocked: currently in scan phase. Switch to control phase first.")
            return None
        
        # Ensure no scan is running before connecting
        async with BLEService.ble_operation_lock:
            device = self.discovered_devices[address]
            
            # If device is already connected, verify the connection is still valid
            if device.is_connected and device.client:
                try:
                    # Test the connection by trying to read a characteristic
                    await device.client.read_gatt_char(CHAR_STATUS)
                    logger.debug(f"Device {device.name} is already connected and responsive")
                    return device
                except Exception as e:
                    logger.warning(f"Existing connection to {device.name} is stale: {e}")
                    # Connection is stale, disconnect and reconnect
                    await device.disconnect()
            
            # Get a fresh device reference for better reliability
            fresh_device_found = False
            try:
                logger.info(f"Getting fresh device reference for {address}...")
                
                # Use callback-based scanner to get fresh device with RSSI
                fresh_device_with_rssi = None
                
                def detection_callback(device: BLEDevice, advertisement_data):
                    nonlocal fresh_device_with_rssi
                    if device.address.lower() == address.lower():
                        fresh_device_with_rssi = {
                            'device': device,
                            'rssi': advertisement_data.rssi
                        }
                
                scanner = BleakScanner(
                    detection_callback=detection_callback,
                    service_uuids=[SERVICE_UUID],
                    adapter=self.adapter
                )
                
                await scanner.start()
                await asyncio.sleep(5.0)  # Scan for 5 seconds
                await scanner.stop()
                
                if fresh_device_with_rssi:
                    device.device = fresh_device_with_rssi['device']
                    device.rssi = fresh_device_with_rssi['rssi']
                    fresh_device_found = True
                    logger.info(f"Updated device reference for {device.name} (RSSI: {fresh_device_with_rssi['rssi']})")
                else:
                    logger.warning(f"Device {address} not found in fresh scan, using cached reference")
                    
            except Exception as e:
                logger.warning(f"Failed to get fresh device reference: {e}, using cached reference")
            
            # Add a small delay to let the Bluetooth stack settle after scanning
            await asyncio.sleep(0.5)
            
            # Now try to connect with multiple strategies
            connection_success = False
            
            # Strategy 1: Direct connection
            logger.info(f"Attempting direct connection to {device.name}...")
            if await device.connect(retries=3):
                connection_success = True
            
            # Strategy 2: If direct connection failed, try after Bluetooth reset
            if not connection_success:
                logger.warning(f"Direct connection failed, trying with Bluetooth reset...")
                await self.reset_bluetooth_adapter()
                await asyncio.sleep(3.0)  # Longer wait after reset
                
                # Get fresh reference again after reset
                if fresh_device_found:
                    try:
                        # Use callback-based scanner again after reset
                        fresh_device_after_reset = None
                        
                        def reset_detection_callback(device: BLEDevice, advertisement_data):
                            nonlocal fresh_device_after_reset
                            if device.address.lower() == address.lower():
                                fresh_device_after_reset = {
                                    'device': device,
                                    'rssi': advertisement_data.rssi
                                }
                        
                        reset_scanner = BleakScanner(
                            detection_callback=reset_detection_callback,
                            service_uuids=[SERVICE_UUID],
                            adapter=self.adapter
                        )
                        
                        await reset_scanner.start()
                        await asyncio.sleep(3.0)
                        await reset_scanner.stop()
                        
                        if fresh_device_after_reset:
                            device.device = fresh_device_after_reset['device']
                            device.rssi = fresh_device_after_reset['rssi']
                            
                    except Exception as e:
                        logger.debug(f"Could not refresh device after reset: {e}")
                
                if await device.connect(retries=2):
                    connection_success = True
            
            if connection_success:
                self._notify_device_callbacks(device, "connected")
                logger.info(f"Successfully connected to {device.name}")
                return device
            else:
                logger.error(f"All connection attempts failed for {device.name}")
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
        
        # Check if we're in control phase (operations allowed)
        if not self.is_in_control_phase():
            logger.warning("WiFi operation blocked: currently in scan phase. Switch to control phase first.")
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
            "current_phase": self.current_phase,
            "is_in_control_phase": self.is_in_control_phase(),
            "is_in_scan_phase": self.is_in_scan_phase(),
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
        
        # Check if we're in control phase (operations allowed)
        if not self.is_in_control_phase():
            logger.warning("Drive operation blocked: currently in scan phase. Switch to control phase first.")
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
        
        # Check if we're in control phase (operations allowed)
        if not self.is_in_control_phase():
            logger.warning("Battery read blocked: currently in scan phase. Switch to control phase first.")
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
        """Start automatic device discovery using scan phase."""
        if self.is_auto_discovery_running:
            logger.warning("Auto discovery already running")
            return
        
        self.is_auto_discovery_running = True
        # Start with initial scan
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
