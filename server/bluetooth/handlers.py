"""
Bluetooth WebSocket handlers for the Rocket League IRL server.
These handlers provide WebSocket endpoints for Bluetooth device management.
"""

# Global reference to Bluetooth service (set by main.py)
bluetooth_service = None

def set_bluetooth_service(service):
    """Set the global Bluetooth service reference."""
    global bluetooth_service
    bluetooth_service = service

def get_bluetooth_service():
    """Get the global Bluetooth service reference."""
    return bluetooth_service

def handle_get_bluetooth_status(data, car_manager=None):
    """Handle get Bluetooth status requests."""
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
    """Handle start Bluetooth scan requests."""
    print("Starting Bluetooth scan")
    
    if bluetooth_service:
        try:
            # Discover devices
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
