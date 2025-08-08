from websocket import start_server_with_cars
from models import Car, CarManager

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

if __name__ == "__main__":
    # Initialize cars
    car_manager = initialize_cars()
    
    # Start the WebSocket server with car manager
    start_server_with_cars(car_manager)
