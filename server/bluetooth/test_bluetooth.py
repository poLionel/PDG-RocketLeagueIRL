#!/usr/bin/env python3
"""
Simple test script for Bluetooth functionality.
This script can be used to test Bluetooth discovery and pairing without the full server.
"""

import asyncio
import sys
import logging
import os

# Add the current directory and server directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)  # For bluetooth_service.py
sys.path.insert(0, server_dir)   # For models.py

# Import from local module in current directory and parent directory
from bluetooth_service import BluetoothService, check_bluetooth_dependencies, test_bluetooth_service
from models import CarManager

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def interactive_bluetooth_test():
    """Interactive test for Bluetooth functionality."""
    print("=== Bluetooth Service Test ===")
    
    # Check dependencies
    if not check_bluetooth_dependencies():
        print("ERROR: Bluetooth dependencies not available")
        print("On Raspberry Pi, install with: sudo apt-get install bluez bluez-tools")
        return
    
    print("SUCCESS: Bluetooth dependencies available")
    
    # Create car manager and Bluetooth service
    car_manager = CarManager()
    bluetooth_service = BluetoothService(car_manager)
    
    # Add callback to log device events
    def device_callback(device, event):
        print(f"DEVICE EVENT: {event} - {device}")
    
    bluetooth_service.add_device_callback(device_callback)
    
    print("\n--- Getting paired devices ---")
    paired = bluetooth_service.get_paired_devices()
    if paired:
        print(f"Found {len(paired)} paired devices:")
        for i, device in enumerate(paired, 1):
            print(f"  {i}. {device}")
    else:
        print("No paired devices found")
    
    print("\n--- Discovering new devices ---")
    discovered = bluetooth_service.discover_devices()
    if discovered:
        print(f"Discovered {len(discovered)} devices:")
        for i, device in enumerate(discovered, 1):
            print(f"  {i}. {device}")
    else:
        print("No devices discovered")
    
    # Interactive pairing
    if discovered:
        print("\n--- Interactive Pairing ---")
        while True:
            try:
                choice = input("\nEnter device number to pair (or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    break
                
                device_num = int(choice)
                if 1 <= device_num <= len(discovered):
                    device = discovered[device_num - 1]
                    print(f"Attempting to pair with {device}...")
                    
                    success = bluetooth_service.pair_device(device)
                    if success:
                        print(f"SUCCESS: Successfully paired with {device}")
                    else:
                        print(f"FAILED: Failed to pair with {device}")
                else:
                    print("Invalid device number")
                    
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                break
    
    # Show final status
    print("\n--- Final Status ---")
    status = bluetooth_service.get_device_status()
    print(f"Discovered devices: {len(status['discovered_devices'])}")
    print(f"Paired devices: {len(status['paired_devices'])}")
    print(f"Cars in manager: {car_manager.get_car_count()}")
    
    if car_manager.get_car_count() > 0:
        print("Cars:")
        for car in car_manager.get_all_cars():
            print(f"  {car}")

async def auto_discovery_test(duration=30):
    """Test automatic discovery for a specified duration."""
    print(f"=== Auto Discovery Test ({duration}s) ===")
    
    if not check_bluetooth_dependencies():
        print("ERROR: Bluetooth dependencies not available")
        return
    
    car_manager = CarManager()
    bluetooth_service = BluetoothService(car_manager)
    
    def device_callback(device, event):
        print(f"DEVICE {event.upper()}: {device}")
    
    bluetooth_service.add_device_callback(device_callback)
    
    print("Starting auto discovery...")
    discovery_task = asyncio.create_task(bluetooth_service.start_auto_discovery())
    
    try:
        # Wait for specified duration
        await asyncio.sleep(duration)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        print("Stopping auto discovery...")
        bluetooth_service.stop_auto_discovery()
        discovery_task.cancel()
        
        try:
            await discovery_task
        except asyncio.CancelledError:
            pass
    
    # Show final results
    status = bluetooth_service.get_device_status()
    print(f"\nResults after {duration}s:")
    print(f"  Discovered devices: {len(status['discovered_devices'])}")
    print(f"  Paired devices: {len(status['paired_devices'])}")
    print(f"  Cars added: {car_manager.get_car_count()}")

async def headset_auto_pair_test():
    """Continuously scan and auto-pair with headsets until one is found and paired."""
    print("=== Headset Auto-Pair Test ===")
    print("This will continuously scan for headsets and automatically pair with them.")
    print("Put your headset in pairing mode and wait...")
    print("Press Ctrl+C to stop\n")
    
    if not check_bluetooth_dependencies():
        print("ERROR: Bluetooth dependencies not available")
        print("On Raspberry Pi, install with: sudo apt-get install bluez bluez-tools")
        return
    
    car_manager = CarManager()
    bluetooth_service = BluetoothService(car_manager)
    
    # Track what we've already tried to pair
    attempted_devices = set()
    successfully_paired = []
    
    def device_callback(device, event):
        print(f"DEVICE {event.upper()}: {device}")
        if event == "paired":
            successfully_paired.append(device)
    
    bluetooth_service.add_device_callback(device_callback)
    
    scan_count = 0
    
    try:
        while True:
            scan_count += 1
            print(f"\nSCAN #{scan_count} - Looking for headsets...")
            
            # Discover devices
            discovered = bluetooth_service.discover_devices(duration=10)
            
            if not discovered:
                print("   No devices found, continuing to scan...")
                await asyncio.sleep(5)
                continue
            
            # Look for headsets
            headsets_found = []
            for device in discovered:
                if bluetooth_service.is_test_device(device.name):
                    headsets_found.append(device)
                    print(f"   HEADSET FOUND: Found potential headset: {device}")
            
            if not headsets_found:
                print("   No headsets found, continuing to scan...")
                await asyncio.sleep(5)
                continue
            
            # Try to pair with new headsets
            for device in headsets_found:
                if device.address not in attempted_devices:
                    print(f"\nATTEMPTING PAIR: Attempting to pair with {device.name} ({device.address})...")
                    attempted_devices.add(device.address)
                    
                    success = bluetooth_service.pair_device(device)
                    
                    if success:
                        print(f"SUCCESS! Paired with {device.name}")
                        print(f"   Address: {device.address}")
                        print("\nHeadset pairing completed!")
                        
                        # Show final status
                        status = bluetooth_service.get_device_status()
                        print(f"\nFinal Status:")
                        print(f"  Total devices discovered: {len(status['discovered_devices'])}")
                        print(f"  Successfully paired devices: {len(status['paired_devices'])}")
                        print(f"  Devices attempted: {len(attempted_devices)}")
                        
                        return  # Exit successfully
                    else:
                        print(f"FAILED: Failed to pair with {device.name}")
                        print("   Continuing to scan for other devices...")
                else:
                    print(f"   Already tried pairing with {device.name}, skipping...")
            
            # Wait before next scan
            print("   Waiting 10 seconds before next scan...")
            await asyncio.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\nSTOPPED: Scanning stopped by user")
        print(f"Scan attempts made: {scan_count}")
        print(f"Devices attempted to pair: {len(attempted_devices)}")
        print(f"Successfully paired: {len(successfully_paired)}")
        
        if successfully_paired:
            print("\nSuccessfully paired devices:")
            for device in successfully_paired:
                print(f"  SUCCESS: {device}")
        else:
            print("\nNo devices were successfully paired.")
            print("\nTips:")
            print("  - Make sure your headset is in pairing mode")
            print("  - Try holding the pairing button longer")
            print("  - Make sure the headset isn't connected to another device")

def print_usage():
    """Print usage information."""
    print("Usage:")
    print("  python test_bluetooth.py interactive    - Interactive testing")
    print("  python test_bluetooth.py auto [time]    - Auto discovery test (default 30s)")
    print("  python test_bluetooth.py headset        - Continuously scan and auto-pair headsets")
    print("  python test_bluetooth.py basic          - Basic functionality test")

async def main():
    """Main test function."""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    mode = sys.argv[1].lower()
    
    if mode == "interactive":
        await interactive_bluetooth_test()
    elif mode == "auto":
        duration = 30
        if len(sys.argv) > 2:
            try:
                duration = int(sys.argv[2])
            except ValueError:
                print("Invalid duration, using default 30s")
        await auto_discovery_test(duration)
    elif mode == "headset":
        await headset_auto_pair_test()
    elif mode == "basic":
        await test_bluetooth_service()
    else:
        print_usage()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
