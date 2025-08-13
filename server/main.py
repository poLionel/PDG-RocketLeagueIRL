import asyncio
import logging
from websocket import start_server_with_cars
from models import Car, CarManager
from bluetooth import BluetoothService, check_bluetooth_dependencies, set_bluetooth_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_cars():
    """Initialize static cars for testing purposes."""
    car_manager = CarManager()
    
    # Add some static cars for testing
    car1 = Car(car_id=1, name="Lightning McQueen")
    car1.battery_level = 85
    car1.move = "forward"
    car1.boost = False
    car1.boost_value = 100
    car1.connected = True
    
    car2 = Car(car_id=2, name="Speed Racer")
    car2.battery_level = 72
    car2.move = "stopped"
    car2.boost = False
    car2.boost_value = 85
    car2.connected = True
    
    car3 = Car(car_id=3, name="Knight Rider")
    car3.battery_level = 95
    car3.move = "backward"
    car3.boost = True
    car3.boost_value = 60
    car3.connected = False
    
    car_manager.add_car(car1)
    car_manager.add_car(car2)
    car_manager.add_car(car3)
    
    print(f"Initialized {car_manager.get_car_count()} cars:")
    for car in car_manager.get_all_cars():
        print(f"  {car}")
    
    return car_manager

async def start_bluetooth_service(car_manager: CarManager):
    """Start the Bluetooth discovery and pairing service."""
    # Check if Bluetooth dependencies are available
    if not check_bluetooth_dependencies():
        logger.warning("Bluetooth dependencies not available. Bluetooth service will be disabled.")
        return None
    
    # Create and start Bluetooth service
    bluetooth_service = BluetoothService(car_manager)
    
    # Add callback to log device events
    def device_callback(device, event):
        logger.info(f"Bluetooth event: {event} - {device}")
    
    bluetooth_service.add_device_callback(device_callback)
    
    # Get currently paired devices
    paired_devices = bluetooth_service.get_paired_devices()
    if paired_devices:
        logger.info(f"Found {len(paired_devices)} already paired devices:")
        for device in paired_devices:
            logger.info(f"  {device}")
    
    # Start auto discovery task
    discovery_task = asyncio.create_task(bluetooth_service.start_auto_discovery())
    
    return bluetooth_service, discovery_task

async def main():
    """Main application entry point."""
    logger.info("Starting Rocket League IRL Server")
    
    # Initialize cars
    car_manager = initialize_cars()
    
    # Start Bluetooth service
    bluetooth_result = await start_bluetooth_service(car_manager)
    
    if bluetooth_result:
        bluetooth_service, discovery_task = bluetooth_result
        logger.info("Bluetooth service started successfully")
        # Set the Bluetooth service in handlers so WebSocket clients can access it
        set_bluetooth_service(bluetooth_service)
    else:
        logger.warning("Bluetooth service not available")
        bluetooth_service = None
        discovery_task = None
    
    try:
        # Start the WebSocket server with car manager
        # Note: This will block until the server is stopped
        await start_server_with_cars(car_manager)
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    finally:
        # Clean up Bluetooth service
        if bluetooth_service:
            bluetooth_service.stop_auto_discovery()
        if discovery_task:
            discovery_task.cancel()
            try:
                await discovery_task
            except asyncio.CancelledError:
                pass
        logger.info("Server shutdown complete")

if __name__ == "__main__":
    # Run the main application
    asyncio.run(main())
