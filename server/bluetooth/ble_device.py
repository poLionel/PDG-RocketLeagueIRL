"""
PDG Car BLE device representation and connection management.
"""

import asyncio
import logging
import struct
from typing import Optional, Callable
from bleak import BleakClient
from bleak.backends.device import BLEDevice

from .ble_constants import (
    CHAR_SSID, CHAR_PASS, CHAR_APPLY, CHAR_STATUS, CHAR_DEVID, CHAR_BATTERY,
    CHAR_DIR_X, CHAR_DIR_Y, CHAR_DIR_SPEED, CHAR_DECAY_MODE,
    clamp, dump
)

logger = logging.getLogger(__name__)


class PDGCarDevice:
    """Represents a PDG car BLE device with connection capabilities."""
    
    def __init__(self, device: BLEDevice, device_id: str = None, adapter: str = None):
        self.device = device
        self.device_id = device_id
        self.name = device.name or "Unknown"
        self.address = device.address
        self.rssi = None  # Signal strength from advertisement data
        self.is_connected = False
        self.client: Optional[BleakClient] = None
        self.status_callback: Optional[Callable] = None
        self.adapter = adapter or "hci1"  # Default Bluetooth adapter for Raspberry Pi

    async def _clear_system_connections(self):
        """Clear any existing system-level connections to prevent conflicts."""
        try:
            import subprocess
            result = subprocess.run(
                ['hcitool', 'con'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if self.address.upper() in result.stdout or self.address.lower() in result.stdout:
                logger.info(f"Found existing connection to {self.address}, clearing...")
                subprocess.run(
                    ['sudo', 'hcitool', 'dc', self.address], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                await asyncio.sleep(1.0)
                
                # Backup disconnect method
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
        """Connect to the BLE device with Raspberry Pi optimized retry logic."""
        # Clean up any previous connections
        if self.client:
            try:
                await self.client.__aexit__(None, None, None)
            except:
                pass
            self.client = None
            self.is_connected = False
        
        await self._clear_system_connections()
        
        for attempt in range(1, retries + 1):
            try:
                # Wait between attempts for Bluetooth stack stability
                if attempt > 1:
                    await asyncio.sleep(0.5)
                
                self.client = BleakClient(
                    self.device.address, 
                    adapter=self.adapter,
                    timeout=15.0  # Extended timeout for Raspberry Pi
                )
                
                connect_task = asyncio.create_task(self.client.__aenter__())
                try:
                    await asyncio.wait_for(connect_task, timeout=12.0)
                    logger.info(f"Connected to device: {self.name} ({self.address}) [adapter={self.adapter}]")
                except asyncio.TimeoutError:
                    logger.warning(f"Connection timeout for {self.name} on attempt {attempt}")
                    raise Exception("Connection timeout")
                
                await asyncio.sleep(0.5)  # Connection stabilization delay
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
                
                # Verify connection with status read
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
                
                # Adaptive retry delays based on error type
                if "inprogress" in error_msg:
                    delay = 3.0 + (attempt * 0.5)
                    logger.info(f"BlueZ InProgress error, waiting {delay}s before retry...")
                    await asyncio.sleep(delay)
                elif "connection abort" in error_msg or "software caused" in error_msg:
                    delay = 2.0 + (attempt * 1.0)
                    logger.info(f"Connection abort error, waiting {delay}s before retry...")
                    await asyncio.sleep(delay)
                    await self._clear_system_connections()
                elif "failed" in error_msg or "timeout" in error_msg:
                    delay = 1.5 + (attempt * 0.5)
                    logger.info(f"Connection failed, waiting {delay}s before retry...")
                    await asyncio.sleep(delay)
                elif "device not found" in error_msg or "not available" in error_msg:
                    delay = 4.0
                    logger.info(f"Device not found, waiting {delay}s before retry...")
                    await asyncio.sleep(delay)
                else:
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
                # Stop notifications before disconnecting
                if self.status_callback:
                    try:
                        await self.client.stop_notify(CHAR_STATUS)
                    except Exception as e:
                        logger.debug(f"Could not stop notifications: {e}")
                    self.status_callback = None
                
                await self.client.__aexit__(None, None, None)
                self.is_connected = False
                logger.info(f"Disconnected from {self.name}")
                
                await self._clear_system_connections()
                
            except Exception as e:
                logger.error(f"Error disconnecting from {self.name}: {e}")
                self.is_connected = False
            finally:
                self.client = None

    async def is_connection_healthy(self) -> bool:
        """Check if the BLE connection is still healthy by testing communication."""
        if not self.is_connected or not self.client:
            return False
        
        try:
            # Verify connection with a quick status read
            await asyncio.wait_for(
                self.client.read_gatt_char(CHAR_STATUS),
                timeout=3.0
            )
            return True
        except Exception as e:
            logger.debug(f"Connection health check failed for {self.name}: {e}")
            return False
    
    # BLE characteristic helpers - Write functions
    async def write_string(self, char_uuid: str, s: str):
        """Write a string value to a characteristic (matches firmware gatt_codec<String>)."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        data = s.encode("utf-8")
        await self.client.write_gatt_char(char_uuid, data, response=True)
        logger.debug(f"Wrote string to {char_uuid}: '{s}' ({len(data)} bytes)")

    async def write_bool(self, char_uuid: str, value: bool):
        """Write a boolean value to a characteristic (matches firmware gatt_codec<bool>)."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        data = b"\x01" if value else b"\x00"
        await self.client.write_gatt_char(char_uuid, data, response=True)
        logger.debug(f"Wrote bool to {char_uuid}: {value} (0x{data.hex()})")

    async def write_i8(self, char_uuid: str, v: int):
        """Write an 8-bit signed integer to a characteristic (matches firmware int8_t handling)."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        # Clamp to int8_t range (-128 to 127) as done in firmware
        clamped_value = clamp(v, -128, 127)
        data = struct.pack("b", clamped_value)
        await self.client.write_gatt_char(char_uuid, data, response=True)
        logger.debug(f"Wrote int8 to {char_uuid}: {v} -> {clamped_value} (0x{data.hex()})")

    async def write_u8(self, char_uuid: str, v: int):
        """Write an 8-bit unsigned integer to a characteristic (matches firmware uint8_t handling)."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        # Clamp to uint8_t range (0 to 255)
        clamped_value = clamp(v, 0, 255)
        data = struct.pack("B", clamped_value)
        await self.client.write_gatt_char(char_uuid, data, response=True)
        logger.debug(f"Wrote uint8 to {char_uuid}: {v} -> {clamped_value} (0x{data.hex()})")

    # BLE characteristic helpers - Read functions
    async def read_string(self, char_uuid: str) -> str:
        """Read a string value from a characteristic (matches firmware gatt_codec<String>)."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        data = await self.client.read_gatt_char(char_uuid)
        result = data.decode("utf-8", errors="ignore")
        logger.debug(f"Read string from {char_uuid}: '{result}' ({len(data)} bytes)")
        return result

    async def read_bool(self, char_uuid: str) -> bool:
        """Read a boolean value from a characteristic (matches firmware gatt_codec<bool>)."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        data = await self.client.read_gatt_char(char_uuid)
        result = len(data) > 0 and data[0] != 0
        logger.debug(f"Read bool from {char_uuid}: {result} (0x{data.hex() if data else 'empty'})")
        return result

    async def read_i8(self, char_uuid: str) -> int:
        """Read an 8-bit signed integer from a characteristic (matches firmware int8_t handling)."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        data = await self.client.read_gatt_char(char_uuid)
        if len(data) < 1:
            raise ValueError(f"Invalid data length for int8: {len(data)}")
        result = struct.unpack("b", data[:1])[0]
        logger.debug(f"Read int8 from {char_uuid}: {result} (0x{data.hex()})")
        return result

    async def read_u8(self, char_uuid: str) -> int:
        """Read an 8-bit unsigned integer from a characteristic (matches firmware uint8_t handling)."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        data = await self.client.read_gatt_char(char_uuid)
        if len(data) < 1:
            raise ValueError(f"Invalid data length for uint8: {len(data)}")
        result = struct.unpack("B", data[:1])[0]
        logger.debug(f"Read uint8 from {char_uuid}: {result} (0x{data.hex()})")
        return result

    # High-level characteristic read functions
    async def read_battery(self) -> Optional[int]:
        """Read the battery level from the device (0-100%)."""
        try:
            return await self.read_u8(CHAR_BATTERY)
        except Exception as e:
            logger.warning(f"Battery read error from {self.name}: {e}")
        return None

    async def read_device_id(self) -> Optional[str]:
        """Read the device ID from the device."""
        try:
            return await self.read_string(CHAR_DEVID)
        except Exception as e:
            logger.warning(f"Device ID read error from {self.name}: {e}")
        return None

    async def read_status(self) -> Optional[str]:
        """Read the current status from the device."""
        try:
            return await self.read_string(CHAR_STATUS)
        except Exception as e:
            logger.warning(f"Status read error from {self.name}: {e}")
        return None

    async def read_wifi_ssid(self) -> Optional[str]:
        """Read the current WiFi SSID from the device."""
        try:
            return await self.read_string(CHAR_SSID)
        except Exception as e:
            logger.warning(f"WiFi SSID read error from {self.name}: {e}")
        return None

    async def read_wifi_apply_status(self) -> Optional[bool]:
        """Read whether WiFi credentials should be applied."""
        try:
            return await self.read_bool(CHAR_APPLY)
        except Exception as e:
            logger.warning(f"WiFi apply status read error from {self.name}: {e}")
        return None

    # Motor control characteristic read functions
    async def read_x_direction(self) -> Optional[int]:
        """Read X direction (steering) value (-100 to 100)."""
        try:
            return await self.read_i8(CHAR_DIR_X)
        except Exception as e:
            logger.warning(f"X direction read error from {self.name}: {e}")
        return None

    async def read_y_direction(self) -> Optional[int]:
        """Read Y direction value (-100 to 100)."""
        try:
            return await self.read_i8(CHAR_DIR_Y)
        except Exception as e:
            logger.warning(f"Y direction read error from {self.name}: {e}")
        return None

    async def read_speed_direction(self) -> Optional[int]:
        """Read speed value (0 to 100)."""
        try:
            return await self.read_i8(CHAR_DIR_SPEED)
        except Exception as e:
            logger.warning(f"Speed read error from {self.name}: {e}")
        return None

    async def read_decay_mode(self) -> Optional[int]:
        """Read decay mode value (0 or 1)."""
        try:
            return await self.read_i8(CHAR_DECAY_MODE)
        except Exception as e:
            logger.warning(f"Decay mode read error from {self.name}: {e}")
        return None

    # Enhanced motor control write functions with firmware-matching bounds
    async def write_x_direction(self, value: int):
        """Write X direction (steering) with firmware bounds (-100 to 100)."""
        clamped_value = clamp(value, -100, 100)
        await self.write_i8(CHAR_DIR_X, clamped_value)
        logger.info(f"Set X direction on {self.name}: {value} -> {clamped_value}")

    async def write_y_direction(self, value: int):
        """Write Y direction with firmware bounds (-100 to 100)."""
        clamped_value = clamp(value, -100, 100)
        await self.write_i8(CHAR_DIR_Y, clamped_value)
        logger.info(f"Set Y direction on {self.name}: {value} -> {clamped_value}")

    async def write_speed_direction(self, value: int):
        """Write speed with firmware bounds (0 to 100)."""
        clamped_value = clamp(value, 0, 100)
        await self.write_i8(CHAR_DIR_SPEED, clamped_value)
        logger.info(f"Set speed on {self.name}: {value} -> {clamped_value}")

    async def write_decay_mode(self, value: int):
        """Write decay mode with firmware bounds (0 to 1)."""
        clamped_value = clamp(value, 0, 1)
        await self.write_i8(CHAR_DECAY_MODE, clamped_value)
        logger.info(f"Set decay mode on {self.name}: {value} -> {clamped_value}")

    # Enhanced WiFi functions
    async def write_wifi_ssid(self, ssid: str):
        """Write WiFi SSID to the device."""
        await self.write_string(CHAR_SSID, ssid)
        logger.info(f"Set WiFi SSID on {self.name}: '{ssid}'")

    async def write_wifi_password(self, password: str):
        """Write WiFi password to the device."""
        await self.write_string(CHAR_PASS, password)
        logger.info(f"Set WiFi password on {self.name}: {'*' * len(password)}")

    async def write_wifi_apply(self, apply: bool):
        """Write WiFi apply flag to the device."""
        await self.write_bool(CHAR_APPLY, apply)
        logger.info(f"Set WiFi apply on {self.name}: {apply}")

    async def set_battery_level(self, percent: int):
        """Set battery level on the device (for testing/simulation)."""
        clamped_percent = clamp(percent, 0, 100)
        await self.write_u8(CHAR_BATTERY, clamped_percent)
        logger.info(f"Set battery level on {self.name}: {percent} -> {clamped_percent}%")

    # High-level composite functions
    async def set_drive(self, x: int, y: int, speed: int, decay_mode: int):
        """Set drive parameters (x, y, speed, decay_mode) on the car with firmware-matching bounds."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        
        # Use the enhanced write functions with proper bounds checking
        await self.write_x_direction(x)
        await self.write_y_direction(y) 
        await self.write_speed_direction(speed)
        await self.write_decay_mode(decay_mode)
        
        logger.info(f"Drive params sent to {self.name}: x={x}, y={y}, speed={speed}, decay_mode={decay_mode}")

    async def get_car_state(self) -> dict:
        """Read complete car state from all characteristics."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        
        state = {
            "device_info": {
                "name": self.name,
                "address": self.address,
                "rssi": self.rssi,
                "is_connected": self.is_connected
            }
        }
        
        try:
            # Read device identification
            state["device_id"] = await self.read_device_id()
            state["status"] = await self.read_status()
            
            # Read power state
            state["battery_level"] = await self.read_battery()
            
            # Read WiFi configuration
            state["wifi"] = {
                "ssid": await self.read_wifi_ssid(),
                "apply_pending": await self.read_wifi_apply_status()
            }
            
            # Read motor control state
            state["motor_control"] = {
                "x_direction": await self.read_x_direction(),
                "y_direction": await self.read_y_direction(), 
                "speed": await self.read_speed_direction(),
                "decay_mode": await self.read_decay_mode()
            }
            
            logger.info(f"Read complete car state from {self.name}")
            
        except Exception as e:
            logger.error(f"Error reading car state from {self.name}: {e}")
            state["error"] = str(e)
        
        return state

    async def set_wifi_credentials(self, ssid: str, password: str) -> bool:
        """Set WiFi credentials on the device and apply the configuration (matches firmware protocol)."""
        if not self.is_connected or not self.client:
            raise RuntimeError("Device not connected")
        try:
            logger.info(f"Setting WiFi credentials on {self.name}: SSID={ssid}")
            
            # Use enhanced write functions that match firmware protocol
            await self.write_wifi_ssid(ssid)
            await self.write_wifi_password(password)
            await self.write_wifi_apply(True)  # Trigger the apply process
            
            await asyncio.sleep(1.0)  # Allow device time to process
            
            # Verify the status change (optional)
            try:
                status = await self.read_status()
                if status == "configured":
                    logger.info(f"WiFi credentials successfully configured on {self.name}")
                else:
                    logger.warning(f"WiFi configuration on {self.name} returned status: {status}")
            except Exception as e:
                logger.debug(f"Could not verify WiFi config status on {self.name}: {e}")
            
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
