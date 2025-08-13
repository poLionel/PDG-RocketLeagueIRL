"""
Bluetooth service for automatic device discovery and pairing.
Handles finding and connecting to cars (and test devices like headsets).
"""

import asyncio
import bluetooth
import subprocess
import sys
import logging
import time
import os
from typing import Dict, List, Optional, Callable

# Add parent directory to path for imports when run directly
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

try:
    from models import Car, CarManager
except ImportError:
    # Try relative import if absolute import fails
    from ..models import Car, CarManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BluetoothDevice:
    """Represents a discovered Bluetooth device."""
    
    def __init__(self, address: str, name: str = None):
        self.address = address
        self.name = name or "Unknown Device"
        self.paired = False
        self.connected = False
        self.last_seen = time.time()
    
    def __str__(self):
        return f"BluetoothDevice({self.address}, {self.name}, paired={self.paired})"

class BluetoothService:
    """Service for managing Bluetooth device discovery and pairing."""
    
    def __init__(self, car_manager: CarManager):
        self.car_manager = car_manager
        self.discovered_devices: Dict[str, BluetoothDevice] = {}
        self.paired_devices: Dict[str, BluetoothDevice] = {}
        self.is_scanning = False
        self.scan_interval = 10  # seconds between scans
        self.device_callbacks: List[Callable] = []
        
        # Device name patterns that identify cars vs test devices
        self.car_patterns = ["RLIRL", "RocketLeague", "Car"]
        self.test_device_patterns = ["headset", "headphone", "speaker", "airpods"]
    
    def add_device_callback(self, callback: Callable):
        """Add a callback that gets called when a new device is discovered."""
        self.device_callbacks.append(callback)
    
    def _notify_device_callbacks(self, device: BluetoothDevice, event: str):
        """Notify all registered callbacks about device events."""
        for callback in self.device_callbacks:
            try:
                callback(device, event)
            except Exception as e:
                logger.error(f"Error in device callback: {e}")
    
    def is_car_device(self, device_name: str) -> bool:
        """Check if a device name indicates it's a car."""
        device_name_lower = device_name.lower()
        return any(pattern.lower() in device_name_lower for pattern in self.car_patterns)
    
    def is_test_device(self, device_name: str) -> bool:
        """Check if a device name indicates it's a test device (like headset)."""
        device_name_lower = device_name.lower()
        return any(pattern.lower() in device_name_lower for pattern in self.test_device_patterns)
    
    def discover_devices(self, duration: int = 8) -> List[BluetoothDevice]:
        """
        Discover nearby Bluetooth devices.
        
        Args:
            duration (int): Duration in seconds to scan for devices
            
        Returns:
            List[BluetoothDevice]: List of discovered devices
        """
        logger.info(f"Starting Bluetooth device discovery (duration: {duration}s)")
        discovered = []
        
        try:
            # Discover devices using PyBluez
            nearby_devices = bluetooth.discover_devices(duration=duration, lookup_names=True)
            
            for address, name in nearby_devices:
                device = BluetoothDevice(address, name)
                discovered.append(device)
                
                # Update our discovered devices cache
                self.discovered_devices[address] = device
                
                logger.info(f"Discovered device: {device}")
                self._notify_device_callbacks(device, "discovered")
                
        except Exception as e:
            logger.error(f"Error during device discovery: {e}")
        
        return discovered
    
    def get_paired_devices(self) -> List[BluetoothDevice]:
        """Get list of already paired devices from the system."""
        paired = []
        
        try:
            # Use bluetoothctl to get paired devices
            result = subprocess.run(
                ["bluetoothctl", "paired-devices"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith("Device "):
                        parts = line.split(' ', 2)
                        if len(parts) >= 3:
                            address = parts[1]
                            name = parts[2] if len(parts) > 2 else "Unknown"
                            device = BluetoothDevice(address, name)
                            device.paired = True
                            paired.append(device)
                            self.paired_devices[address] = device
                            
        except Exception as e:
            logger.error(f"Error getting paired devices: {e}")
        
        return paired
    
    def pair_device(self, device: BluetoothDevice) -> bool:
        """
        Attempt to pair with a Bluetooth device.
        
        Args:
            device (BluetoothDevice): Device to pair with
            
        Returns:
            bool: True if pairing successful, False otherwise
        """
        logger.info(f"Attempting to pair with device: {device}")
        
        try:
            # Use bluetoothctl for pairing
            commands = [
                f"scan on",
                f"pair {device.address}",
                f"trust {device.address}",
                f"connect {device.address}"
            ]
            
            for command in commands:
                logger.info(f"Executing: bluetoothctl {command}")
                result = subprocess.run(
                    ["bluetoothctl", command],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    logger.warning(f"Command failed: {command}, output: {result.stderr}")
                    # Continue with next command as some might fail but pairing could still work
                
                time.sleep(2)  # Wait between commands
            
            # Check if pairing was successful
            time.sleep(3)
            paired_devices = self.get_paired_devices()
            
            for paired_device in paired_devices:
                if paired_device.address == device.address:
                    device.paired = True
                    device.connected = True
                    self.paired_devices[device.address] = device
                    logger.info(f"Successfully paired with {device}")
                    self._notify_device_callbacks(device, "paired")
                    
                    # If this is a car device, add it to car manager
                    if self.is_car_device(device.name):
                        self._add_car_from_device(device)
                    
                    return True
            
            logger.warning(f"Pairing with {device} may have failed")
            return False
            
        except Exception as e:
            logger.error(f"Error pairing with device {device}: {e}")
            return False
    
    def _add_car_from_device(self, device: BluetoothDevice):
        """Add a car to the car manager based on a paired Bluetooth device."""
        # Generate a car ID based on the device address
        car_id = hash(device.address) % 1000  # Simple ID generation
        if car_id < 0:
            car_id = abs(car_id)
        
        # Check if car already exists
        existing_car = self.car_manager.get_car(car_id)
        if existing_car:
            # Update existing car connection status
            existing_car.connected = device.connected
            logger.info(f"Updated existing car {car_id} connection status")
        else:
            # Create new car
            car = Car(car_id=car_id, name=device.name)
            car.connected = device.connected
            self.car_manager.add_car(car)
            logger.info(f"Added new car from Bluetooth device: {car}")
    
    async def start_auto_discovery(self):
        """Start automatic device discovery and pairing."""
        logger.info("Starting automatic Bluetooth discovery and pairing service")
        self.is_scanning = True
        
        while self.is_scanning:
            try:
                logger.info("Scanning for Bluetooth devices...")
                
                # Discover new devices
                discovered = self.discover_devices()
                
                # Try to pair with new devices that look like cars or test devices
                for device in discovered:
                    if device.address not in self.paired_devices:
                        if self.is_car_device(device.name) or self.is_test_device(device.name):
                            logger.info(f"Attempting to pair with potential car/test device: {device}")
                            success = self.pair_device(device)
                            if success:
                                logger.info(f"Successfully paired with {device}")
                            else:
                                logger.warning(f"Failed to pair with {device}")
                        else:
                            logger.info(f"Skipping device (not a car or test device): {device}")
                
                # Wait before next scan
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"Error in auto discovery loop: {e}")
                await asyncio.sleep(5)  # Wait a bit before retrying
    
    def stop_auto_discovery(self):
        """Stop automatic device discovery."""
        logger.info("Stopping automatic Bluetooth discovery")
        self.is_scanning = False
    
    def get_device_status(self) -> Dict:
        """Get status of all discovered and paired devices."""
        return {
            "discovered_devices": [
                {
                    "address": device.address,
                    "name": device.name,
                    "paired": device.paired,
                    "connected": device.connected,
                    "last_seen": device.last_seen
                }
                for device in self.discovered_devices.values()
            ],
            "paired_devices": [
                {
                    "address": device.address,
                    "name": device.name,
                    "paired": device.paired,
                    "connected": device.connected
                }
                for device in self.paired_devices.values()
            ],
            "is_scanning": self.is_scanning
        }

def check_bluetooth_dependencies():
    """Check if required Bluetooth tools are available."""
    required_tools = ["bluetoothctl", "hciconfig"]
    missing_tools = []
    
    for tool in required_tools:
        try:
            result = subprocess.run([tool, "--version"], capture_output=True, timeout=5)
            if result.returncode != 0:
                # Some tools don't support --version, try --help
                result = subprocess.run([tool, "--help"], capture_output=True, timeout=5)
                if result.returncode != 0:
                    missing_tools.append(tool)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            missing_tools.append(tool)
    
    if missing_tools:
        logger.error(f"Missing required Bluetooth tools: {missing_tools}")
        logger.error("Please install bluez and bluez-tools: sudo apt-get install bluez bluez-tools")
        return False
    
    return True

# Test function for development
async def test_bluetooth_service():
    """Test function to verify Bluetooth service functionality."""
    logger.info("Testing Bluetooth service...")
    
    # Check dependencies
    if not check_bluetooth_dependencies():
        logger.error("Bluetooth dependencies not available")
        return
    
    # Create car manager and Bluetooth service
    try:
        from models import CarManager
    except ImportError:
        from ..models import CarManager
    car_manager = CarManager()
    bluetooth_service = BluetoothService(car_manager)
    
    # Add callback to log device events
    def device_callback(device: BluetoothDevice, event: str):
        logger.info(f"Device event: {event} - {device}")
    
    bluetooth_service.add_device_callback(device_callback)
    
    # Get current paired devices
    paired = bluetooth_service.get_paired_devices()
    logger.info(f"Currently paired devices: {paired}")
    
    # Discover devices
    discovered = bluetooth_service.discover_devices()
    logger.info(f"Discovered devices: {discovered}")
    
    # Print status
    status = bluetooth_service.get_device_status()
    logger.info(f"Device status: {status}")

if __name__ == "__main__":
    # Run test when script is executed directly
    asyncio.run(test_bluetooth_service())
