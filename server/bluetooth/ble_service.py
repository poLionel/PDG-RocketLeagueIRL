"""
BLE service for managing car device discovery and communication.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable
from bleak import BleakScanner
from bleak.backends.device import BLEDevice

from .ble_constants import SERVICE_UUID, CAR_DEVICE_PREFIX
from .ble_device import PDGCarDevice

logger = logging.getLogger(__name__)


class BLEService:
    """Service for managing BLE car device discovery and communication."""
    
    ble_operation_lock = asyncio.Lock()  # Prevents concurrent BLE operations that can cause conflicts

    def __init__(self, car_manager=None, adapter: str = None):
        self.car_manager = car_manager
        self.discovered_devices: Dict[str, PDGCarDevice] = {}
        self.is_scanning = False
        self.scan_task: Optional[asyncio.Task] = None
        self.device_callbacks: List[Callable] = []
        self.adapter = adapter or "hci1"  # Default Bluetooth adapter for Raspberry Pi
        # Phase management for scan/control workflow
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
        """Discover PDG car devices via BLE with Raspberry Pi optimizations."""
        logger.info(f"Scanning for Rocket League cars with service UUID {SERVICE_UUID} (timeout: {timeout}s)...")
        async with BLEService.ble_operation_lock:
            try:
                await self.cleanup_stale_connections()
                
                # Store discovered devices with RSSI data
                discovered_devices_with_rssi = {}
                
                def detection_callback(device: BLEDevice, advertisement_data):
                    if self.is_car_device(device):
                        discovered_devices_with_rssi[device.address] = {
                            'device': device,
                            'rssi': advertisement_data.rssi
                        }
                
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
                    
                    # Update existing device or create new one
                    if ble_device.address in self.discovered_devices:
                        logger.debug(f"Already discovered car: {ble_device.name} ({ble_device.address})")
                        existing_device = self.discovered_devices[ble_device.address]
                        existing_device.device = ble_device
                        existing_device.rssi = rssi_value
                        cars.append(existing_device)
                        
                        if self.car_manager:
                            self.car_manager.add_or_update_car_from_ble(ble_device.name, ble_device.address)
                        continue
                    
                    # New car discovered
                    car_device = PDGCarDevice(ble_device, adapter=self.adapter)
                    car_device.rssi = rssi_value
                    cars.append(car_device)
                    
                    self.discovered_devices[ble_device.address] = car_device
                    self._notify_device_callbacks(car_device, "discovered")
                    
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
        """Check and clear existing connections to prevent conflicts (Raspberry Pi optimized)."""
        try:
            import subprocess
            
            # Check for existing connections using multiple methods
            result = subprocess.run(['hcitool', 'con'], capture_output=True, text=True, timeout=5)
            address_found = False
            if address.upper() in result.stdout or address.lower() in result.stdout:
                address_found = True
                logger.warning(f"Found existing hcitool connection to {address}")
                
                subprocess.run(['sudo', 'hcitool', 'dc', address], 
                             capture_output=True, text=True, timeout=5)
                await asyncio.sleep(1.0)
            
            # Check bluetoothctl connections
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
                await asyncio.sleep(1.5)  # Ensure disconnection completes
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
        """Reset the Bluetooth adapter to clear stuck connections (Raspberry Pi optimized)."""
        try:
            logger.info("Resetting Bluetooth adapter...")
            import subprocess
            
            # Disconnect all active car connections
            try:
                result = subprocess.run(['hcitool', 'con'], capture_output=True, text=True, timeout=5)
                if result.stdout and 'RL-CAR' in result.stdout:
                    logger.info("Disconnecting active car connections...")
                    subprocess.run(['sudo', 'hcitool', 'cc'], capture_output=True, text=True, timeout=5)
                    await asyncio.sleep(1.0)
            except Exception as e:
                logger.debug(f"Could not disconnect active connections: {e}")
            
            # Reset the adapter
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
            
            # Reset via bluetoothctl
            try:
                subprocess.run(['bluetoothctl', 'power', 'off'], 
                             capture_output=True, text=True, timeout=5)
                await asyncio.sleep(1.0)
                subprocess.run(['bluetoothctl', 'power', 'on'], 
                             capture_output=True, text=True, timeout=5)
                await asyncio.sleep(1.5)
            except Exception as e:
                logger.debug(f"Could not reset via bluetoothctl: {e}")
            
            # Verify adapter status
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
        """Connect to a specific device by address with enhanced Raspberry Pi logic."""
        if address not in self.discovered_devices:
            logger.error(f"Device {address} not found in discovered devices")
            return None
        
        # Verify we're in control phase
        if not self.is_in_control_phase():
            logger.warning("Connection blocked: currently in scan phase. Switch to control phase first.")
            return None
        
        async with BLEService.ble_operation_lock:
            device = self.discovered_devices[address]
            
            # Check if already connected and responsive
            if device.is_connected and device.client:
                try:
                    await device.client.read_gatt_char("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f4")  # CHAR_STATUS
                    logger.debug(f"Device {device.name} is already connected and responsive")
                    return device
                except Exception as e:
                    logger.warning(f"Existing connection to {device.name} is stale: {e}")
                    await device.disconnect()
            
            # Get fresh device reference for better reliability
            fresh_device_found = False
            try:
                logger.info(f"Getting fresh device reference for {address}...")
                
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
                await asyncio.sleep(5.0)
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
            
            await asyncio.sleep(0.5)  # Let Bluetooth stack settle
            
            # Connection strategies
            connection_success = False
            
            # Strategy 1: Direct connection
            logger.info(f"Attempting direct connection to {device.name}...")
            if await device.connect(retries=3):
                connection_success = True
            
            # Strategy 2: Connection with Bluetooth reset
            if not connection_success:
                logger.warning(f"Direct connection failed, trying with Bluetooth reset...")
                await self.reset_bluetooth_adapter()
                await asyncio.sleep(3.0)
                
                # Refresh device reference after reset
                if fresh_device_found:
                    try:
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
            # Ensure device is connected
            if not device.is_connected:
                logger.info(f"Connecting to {device.name} to send command...")
                if not await device.connect():
                    logger.error(f"Failed to connect to {device.name}")
                    return False
            
            # TODO: Define proper command characteristics in car firmware
            # Currently using SSID characteristic as test
            command_data = f"{command}:{data}".encode("utf-8")
            await device.client.write_gatt_char("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f1", command_data)  # CHAR_SSID
            
            logger.info(f"Command '{command}' sent to {device.name}")
            
            await asyncio.sleep(1.0)  # Wait for response
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending command to {device.name}: {e}")
            return False
    
    async def set_wifi_on_car(self, ble_address: str, ssid: str, password: str) -> bool:
        """Set WiFi credentials on a specific car."""
        if ble_address not in self.discovered_devices:
            logger.error(f"Car with address {ble_address} not found in discovered devices")
            return False
        
        # Verify we're in control phase
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

    # Motor control methods
    async def set_drive_on_car(self, ble_address: str, x: int, y: int, speed: int, decay_mode: int) -> bool:
        """Send drive parameters to a car."""
        if ble_address not in self.discovered_devices:
            logger.error(f"Car with address {ble_address} not found in discovered devices")
            return False
        
        # Verify we're in control phase
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
        
        # Verify we're in control phase
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

    async def read_car_state(self, ble_address: str) -> Optional[dict]:
        """Read complete car state from a car."""
        if ble_address not in self.discovered_devices:
            logger.error(f"Car with address {ble_address} not found in discovered devices")
            return None
        
        # Verify we're in control phase
        if not self.is_in_control_phase():
            logger.warning("Car state read blocked: currently in scan phase. Switch to control phase first.")
            return None
        
        device = self.discovered_devices[ble_address]
        
        try:
            if not device.is_connected:
                logger.info(f"Connecting to {device.name} to read car state...")
                if not await self.connect_to_device(ble_address):
                    logger.error(f"Failed to connect to {device.name}")
                    return None
            return await device.get_car_state()
        except Exception as e:
            logger.error(f"Error reading car state from {device.name}: {e}")
            return None

    async def read_motor_control_state(self, ble_address: str) -> Optional[dict]:
        """Read motor control state from a car."""
        if ble_address not in self.discovered_devices:
            logger.error(f"Car with address {ble_address} not found in discovered devices")
            return None
        
        # Verify we're in control phase
        if not self.is_in_control_phase():
            logger.warning("Motor control read blocked: currently in scan phase. Switch to control phase first.")
            return None
        
        device = self.discovered_devices[ble_address]
        
        try:
            if not device.is_connected:
                logger.info(f"Connecting to {device.name} to read motor state...")
                if not await self.connect_to_device(ble_address):
                    logger.error(f"Failed to connect to {device.name}")
                    return None
            
            motor_state = {
                "x_direction": await device.read_x_direction(),
                "y_direction": await device.read_y_direction(),
                "speed": await device.read_speed_direction(),
                "decay_mode": await device.read_decay_mode()
            }
            
            logger.info(f"Read motor control state from {device.name}: {motor_state}")
            return motor_state
            
        except Exception as e:
            logger.error(f"Error reading motor control state from {device.name}: {e}")
            return None
