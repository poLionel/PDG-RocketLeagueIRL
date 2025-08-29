"""
Asynchronous WebSocket handlers for real-time Bluetooth communication.

This module contains async handlers that require awaiting operations, primarily
for Bluetooth Low Energy communication with cars. These handlers are separated
from the synchronous handlers to enable proper async/await patterns for BLE
operations which can take significant time to complete.

Key functions:
- Car command transmission via BLE
- WiFi provisioning for car setup
- Real-time motor control with feedback
- Asynchronous device discovery and pairing
"""

import asyncio
import logging
from bluetooth.handlers import get_bluetooth_service

logger = logging.getLogger(__name__)

async def handle_send_to_car_async(data, car_manager=None):
    """
    Send commands and data to a specific car via Bluetooth Low Energy.
    
    This async handler manages the complete process of transmitting commands
    to a physical car, including device lookup, BLE connection validation,
    and command execution with proper error handling.
    
    Args:
        data (dict): WebSocket message containing car ID, command, and parameters
        car_manager (CarManager): Car registry for device lookup
        
    Returns:
        dict: Response with operation status and any error messages
    """
    car_id = data.get("car")
    command = data.get("command", "test")
    message = data.get("message", "Hello from server!")
    
    logger.info(f"Sending to car {car_id}: command={command}, message={message}")
    
    try:
        # Validate car exists in the management system
        car = None
        if car_manager and car_id is not None:
            car = car_manager.get_car(car_id)
        
        if not car:
            return {
                "status": "error",
                "message": f"Car {car_id} not found"
            }
        
        if not car.ble_address:
            return {
                "status": "error",
                "message": f"Car {car_id} has no BLE address"
            }
        
        # Access the Bluetooth service for BLE operations
        bluetooth_service = get_bluetooth_service()
        if not bluetooth_service:
            return {
                "status": "error",
                "message": "Bluetooth service not initialized"
            }
        
        # Locate the BLE device in the discovered devices registry
        ble_devices = bluetooth_service.ble_service.discovered_devices
        ble_device = ble_devices.get(car.ble_address)
        
        if not ble_device:
            return {
                "status": "error",
                "message": f"Car {car_id} BLE device not found. Try discovering cars first."
            }
        
        # Connect to the device if not already connected
        if not ble_device.is_connected:
            logger.info(f"Connecting to {ble_device.name} to send command...")
            connected = await ble_device.connect()
            if not connected:
                return {
                    "status": "error",
                    "message": f"Failed to connect to car {car.name} via BLE"
                }
        
        # Send the command via BLE
        success = await bluetooth_service.send_command_to_car_async(
            car.ble_address, 
            command, 
            message
        )
        
        if success:
            # Update car status to show communication
            if car_manager:
                car_manager.update_car_status(car_id, connected=True)
            
            return {
                "status": "success",
                "message": f"Command '{command}' sent to car {car.name}",
                "sent_data": {
                    "command": command,
                    "message": message,
                    "car_id": car_id,
                    "ble_address": car.ble_address
                },
                "car": car.get_status()
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to send command to car {car.name}"
            }
        
    except Exception as e:
        logger.error(f"Error in handle_send_to_car_async: {e}")
        return {
            "status": "error",
            "message": f"Error sending to car: {str(e)}"
        }

async def handle_set_wifi_credentials_async(data, car_manager=None):
    """Handle setting WiFi credentials on a car via Bluetooth (async version)."""
    car_id = data.get("car")
    ssid = data.get("ssid", "TestWiFi")
    password = data.get("password", "TestPassword123")
    
    logger.info(f"Setting WiFi credentials on car {car_id}: SSID={ssid}")
    
    try:
        # Find the car
        car = None
        if car_manager and car_id is not None:
            car = car_manager.get_car(car_id)
        
        if not car:
            return {
                "status": "error",
                "message": f"Car {car_id} not found"
            }
        
        if not car.ble_address:
            return {
                "status": "error",
                "message": f"Car {car_id} has no BLE address"
            }
        
        # Get the Bluetooth service
        bluetooth_service = get_bluetooth_service()
        if not bluetooth_service:
            return {
                "status": "error",
                "message": "Bluetooth service not initialized"
            }
        
        # Get the BLE device
        ble_devices = bluetooth_service.ble_service.discovered_devices
        ble_device = ble_devices.get(car.ble_address)
        
        if not ble_device:
            return {
                "status": "error",
                "message": f"Car {car_id} BLE device not found. Try discovering cars first."
            }
        
        # Connect to the device if not already connected
        if not ble_device.is_connected:
            logger.info(f"Connecting to {ble_device.name} to set WiFi credentials...")
            connected_device = await bluetooth_service.ble_service.connect_to_device(car.ble_address)
            if not connected_device:
                return {
                    "status": "error",
                    "message": f"Failed to connect to car {car.name} via BLE"
                }
        
        # Set WiFi credentials using the new BLE service method
        success = await bluetooth_service.ble_service.set_wifi_on_car(car.ble_address, ssid, password)
        
        if success:
            # Update car status to show communication
            if car_manager:
                car_manager.update_car_status(car_id, connected=True)
            
            return {
                "status": "success",
                "message": f"WiFi credentials set on car {car.name}",
                "wifi_data": {
                    "ssid": ssid,
                    "car_id": car_id,
                    "ble_address": car.ble_address
                },
                "car": car.get_status()
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to set WiFi credentials on car {car.name}"
            }
        
    except Exception as e:
        logger.error(f"Error in handle_set_wifi_credentials_async: {e}")
        return {
            "status": "error",
            "message": f"Error setting WiFi credentials: {str(e)}"
        }

async def handle_connect_to_car_async(data, car_manager=None):
    """Handle connecting to a car via Bluetooth (async version)."""
    car_id = data.get("car")
    
    logger.info(f"Connecting to car {car_id} via BLE...")
    
    try:
        # Find the car
        car = None
        if car_manager and car_id is not None:
            car = car_manager.get_car(car_id)
        
        if not car:
            return {
                "status": "error",
                "message": f"Car {car_id} not found"
            }
        
        if not car.ble_address:
            return {
                "status": "error",
                "message": f"Car {car_id} has no BLE address"
            }
        
        # Get the Bluetooth service
        bluetooth_service = get_bluetooth_service()
        if not bluetooth_service:
            return {
                "status": "error",
                "message": "Bluetooth service not initialized"
            }
        
        # Get the BLE device
        ble_devices = bluetooth_service.ble_service.discovered_devices
        ble_device = ble_devices.get(car.ble_address)
        
        if not ble_device:
            return {
                "status": "error",
                "message": f"Car {car_id} BLE device not found. Try discovering cars first."
            }
        
        # Connect to the device
        if ble_device.is_connected:
            return {
                "status": "success",
                "message": f"Car {car.name} is already connected",
                "car": car.get_status()
            }
        
        logger.info(f"Connecting to {ble_device.name}...")
        connected_device = await bluetooth_service.ble_service.connect_to_device(car.ble_address)
        
        if connected_device:
            # Update car status
            if car_manager:
                car_manager.update_car_status(car_id, connected=True)
            
            return {
                "status": "success",
                "message": f"Successfully connected to car {car.name}",
                "car": car.get_status()
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to connect to car {car.name}"
            }
        
    except Exception as e:
        logger.error(f"Error in handle_connect_to_car_async: {e}")
        return {
            "status": "error",
            "message": f"Error connecting to car: {str(e)}"
        }

async def handle_switch_to_scan_phase_async(data, car_manager=None):
    """Handle switching to scan phase (async version)."""
    logger.info("Switching to scan phase...")
    
    try:
        # Get the Bluetooth service
        bluetooth_service = get_bluetooth_service()
        if not bluetooth_service:
            return {
                "status": "error",
                "message": "Bluetooth service not initialized"
            }
        
        # Switch to scan phase and discover cars
        discovered_cars = await bluetooth_service.ble_service.start_scan_phase()
        
        return {
            "status": "success",
            "message": f"Switched to scan phase. Found {len(discovered_cars)} cars.",
            "phase": "scan",
            "discovered_cars": [car.to_dict() for car in discovered_cars]
        }
        
    except Exception as e:
        logger.error(f"Error in handle_switch_to_scan_phase_async: {e}")
        return {
            "status": "error",
            "message": f"Error switching to scan phase: {str(e)}"
        }

async def handle_switch_to_control_phase_async(data, car_manager=None):
    """Handle switching to control phase (async version)."""
    logger.info("Switching to control phase...")
    
    try:
        # Get the Bluetooth service
        bluetooth_service = get_bluetooth_service()
        if not bluetooth_service:
            return {
                "status": "error",
                "message": "Bluetooth service not initialized"
            }
        
        # Switch to control phase
        await bluetooth_service.ble_service.switch_to_control_phase()
        
        return {
            "status": "success",
            "message": "Switched to control phase. You can now send commands to cars.",
            "phase": "control",
            "discovered_cars": [car.to_dict() for car in bluetooth_service.ble_service.discovered_devices.values()]
        }
        
    except Exception as e:
        logger.error(f"Error in handle_switch_to_control_phase_async: {e}")
        return {
            "status": "error",
            "message": f"Error switching to control phase: {str(e)}"
        }

# Export the async handler
ASYNC_HANDLERS = {
    "send_to_car": handle_send_to_car_async,
    "set_wifi_credentials": handle_set_wifi_credentials_async,
    "connect_to_car": handle_connect_to_car_async,
    "switch_to_scan_phase": handle_switch_to_scan_phase_async,
    "switch_to_control_phase": handle_switch_to_control_phase_async,
}
