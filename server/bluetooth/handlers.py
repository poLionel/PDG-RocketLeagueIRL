"""
Bluetooth WebSocket handlers for the Rocket League IRL server.

This module provides WebSocket endpoint handlers specifically for Bluetooth
device management operations. It acts as a bridge between WebSocket clients
and the BluetoothService, enabling remote control of device discovery,
pairing, and status monitoring.

Key handler functions:
- Bluetooth adapter status monitoring
- Device discovery and scanning control
- Device pairing and connection management
- Service availability checking with graceful degradation
"""

# Global Bluetooth service instance (injected by main application)
bluetooth_service = None

def set_bluetooth_service(service):
    """
    Configure the global Bluetooth service for handler access.
    
    Args:
        service: BluetoothService instance for device operations
    """
    global bluetooth_service
    bluetooth_service = service

def get_bluetooth_service():
    """
    Retrieve the global Bluetooth service instance.
    
    Returns:
        BluetoothService: Active service instance or None if unavailable
    """
    return bluetooth_service

def handle_get_bluetooth_status(data, car_manager=None):
    """
    Retrieve current Bluetooth adapter and service status.
    
    Provides comprehensive status information about the Bluetooth subsystem
    including adapter state, discovered devices, and connection status.
    
    Args:
        data (dict): WebSocket request data
        car_manager (CarManager): Car registry (unused for status)
        
    Returns:
        dict: Status response with adapter information or error details
    """
    print("Getting Bluetooth status")
    
    if bluetooth_service:
        try:
            bluetooth_status = bluetooth_service.get_device_status()
            return {
                "status": "success",
                "bluetooth_status": bluetooth_status
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error getting Bluetooth status: {str(e)}"
            }
    
    return {
        "status": "error",
        "message": "Bluetooth service not available"
    }

def handle_start_bluetooth_scan(data, car_manager=None):
    """
    Initiate Bluetooth Low Energy device discovery scan.
    
    Starts scanning for nearby BLE devices, particularly looking for
    Rocket League cars with the expected device name prefix. Results
    are returned immediately with discovered devices.
    
    Args:
        data (dict): WebSocket request data
        car_manager (CarManager): Car registry for device registration
        
    Returns:
        dict: Scan results with discovered devices or error information
    """
    print("Starting Bluetooth scan")
    
    if bluetooth_service:
        try:
            # Perform device discovery scan
            devices = bluetooth_service.discover_devices()
            device_list = [
                {
                    "address": device.address,
                    "name": device.name,
                    "paired": device.paired
                }
                for device in devices
            ]
            
            return {
                "status": "success",
                "message": "Bluetooth scan completed",
                "discovered_devices": device_list
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error during Bluetooth scan: {str(e)}"
            }
    
    return {
        "status": "error",
        "message": "Bluetooth service not available"
    }

def handle_stop_bluetooth_scan(data, car_manager=None):
    """Handle stop Bluetooth scan requests."""
    print("Stopping Bluetooth scan")
    
    if bluetooth_service:
        try:
            bluetooth_service.stop_auto_discovery()
            return {
                "status": "success",
                "message": "Bluetooth auto-discovery stopped"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error stopping Bluetooth scan: {str(e)}"
            }
    
    return {
        "status": "error",
        "message": "Bluetooth service not available"
    }

def handle_pair_bluetooth_device(data, car_manager=None):
    """Handle pair Bluetooth device requests."""
    device_address = data.get("address")
    device_name = data.get("name", "Unknown Device")
    
    print(f"Attempting to pair with device: {device_address} ({device_name})")
    
    if not device_address:
        return {
            "status": "error",
            "message": "Device address is required"
        }
    
    if bluetooth_service:
        try:
            from .bluetooth_service import BluetoothDevice
            device = BluetoothDevice(device_address, device_name)
            success = bluetooth_service.pair_device(device)
            
            if success:
                return {
                    "status": "success",
                    "message": f"Successfully paired with {device_name} ({device_address})"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to pair with {device_name} ({device_address})"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error pairing device: {str(e)}"
            }
    
    return {
        "status": "error",
        "message": "Bluetooth service not available"
    }

# Bluetooth handler mappings
BLUETOOTH_HANDLERS = {
    "get_bluetooth_status": handle_get_bluetooth_status,
    "start_bluetooth_scan": handle_start_bluetooth_scan,
    "stop_bluetooth_scan": handle_stop_bluetooth_scan,
    "pair_bluetooth_device": handle_pair_bluetooth_device,
}
