import asyncio
import logging
from websocket import start_server_with_cars
from models import Car, CarManager
from bluetooth import BluetoothService, check_bluetooth_dependencies, set_bluetooth_service

# Configure application-wide logging for debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_cars():
    """
    Initialize the car management system with static test cars.
    
    Creates a CarManager instance and populates it with predefined cars
    for development and testing purposes. In production, cars would be
    dynamically discovered via Bluetooth.
    
    Returns:
        CarManager: Configured car manager with initialized test cars
    """
    car_manager = CarManager()
    
    print(f"Initialized {car_manager.get_car_count()} cars:")
    for car in car_manager.get_all_cars():
        print(f"  {car}")
    
    return car_manager

async def start_bluetooth_service(car_manager: CarManager):
    """
    Initialize and start the Bluetooth service for car discovery and communication.
    
    This function handles the complete Bluetooth service lifecycle including:
    - Dependency validation
    - Service initialization
    - Event callback configuration
    - Auto-discovery task creation
    
    Args:
        car_manager (CarManager): The car manager to associate discovered devices with
        
    Returns:
        tuple: (BluetoothService, asyncio.Task) if successful, None if dependencies unavailable
    """
    if not check_bluetooth_dependencies():
        logger.warning("Bluetooth dependencies not available. Bluetooth service will be disabled.")
        return None
    
    bluetooth_service = BluetoothService(car_manager)
    
    # Configure device event logging and car manager synchronization
    def device_callback(device, event):
        logger.info(f"Bluetooth event: {event} - {device}")
        
        # Log updated car inventory after device state changes
        if event == "discovered":
            logger.info(f"Car manager now has {car_manager.get_car_count()} cars:")
            for car in car_manager.get_all_cars():
                logger.info(f"  {car}")
    
    bluetooth_service.add_device_callback(device_callback)
    
    # Log existing paired devices from previous sessions
    paired_devices = bluetooth_service.get_paired_devices()
    if paired_devices:
        logger.info(f"Found {len(paired_devices)} already paired devices:")
        for device in paired_devices:
            logger.info(f"  {device}")
    
    # Start continuous device discovery using scan/advertise cycles
    discovery_task = asyncio.create_task(bluetooth_service.start_auto_discovery())
    
    return bluetooth_service, discovery_task

async def main():
    """
    Main application entry point and orchestrator.
    
    Coordinates the startup sequence of all system components:
    1. Car management system initialization
    2. Bluetooth service startup (if available)
    3. WebSocket server launch
    4. Graceful shutdown handling
    """
    logger.info("Starting Rocket League IRL Server")
    
    car_manager = initialize_cars()
    
    bluetooth_result = await start_bluetooth_service(car_manager)
    
    if bluetooth_result:
        bluetooth_service, discovery_task = bluetooth_result
        logger.info("Bluetooth service started successfully")
        # Make Bluetooth service globally accessible to WebSocket handlers
        set_bluetooth_service(bluetooth_service)
    else:
        logger.warning("Bluetooth service not available")
        bluetooth_service = None
        discovery_task = None
    
    try:
        # Start WebSocket server - this blocks until server stops
        await start_server_with_cars(car_manager)
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    finally:
        # Ensure clean shutdown of all async resources
        if bluetooth_service:
            await bluetooth_service.stop_auto_discovery()
        if discovery_task:
            discovery_task.cancel()
            try:
                await discovery_task
            except asyncio.CancelledError:
                pass
        logger.info("Server shutdown complete")

if __name__ == "__main__":
    # Entry point: start the async application loop
    asyncio.run(main())
