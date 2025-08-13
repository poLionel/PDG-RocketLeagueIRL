#!/usr/bin/env python3
"""
Windows-compatible Bluetooth test script for pairing headsets.
This version uses Windows Bluetooth APIs instead of Linux tools.
"""

import asyncio
import sys
import logging
import os
import time

# Add the current directory and server directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, server_dir)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WindowsBluetoothDevice:
    """Simple Windows Bluetooth device representation."""
    
    def __init__(self, address: str, name: str = None):
        self.address = address
        self.name = name or "Unknown Device"
        self.paired = False
        self.connected = False
        self.last_seen = time.time()
    
    def __str__(self):
        return f"BluetoothDevice({self.address}, {self.name}, paired={self.paired})"

def is_headset_device(device_name: str) -> bool:
    """Check if a device name indicates it's a headset."""
    headset_patterns = ["headset", "headphone", "speaker", "airpods", "buds", "beats", "sony", "bose"]
    device_name_lower = device_name.lower()
    return any(pattern.lower() in device_name_lower for pattern in headset_patterns)

async def windows_headset_test():
    """Windows-compatible headset discovery and pairing simulation."""
    print("=== Windows Headset Pairing Test ===")
    print("This is a simulation for Windows systems.")
    print("For actual Bluetooth functionality, this needs to be run on a Raspberry Pi.")
    print("Press Ctrl+C to stop\n")
    
    # Simulate discovering devices
    simulated_devices = [
        WindowsBluetoothDevice("AA:BB:CC:DD:EE:FF", "Your Headset"),
        WindowsBluetoothDevice("11:22:33:44:55:66", "Sony WH-1000XM4"),
        WindowsBluetoothDevice("77:88:99:AA:BB:CC", "AirPods Pro"),
    ]
    
    scan_count = 0
    
    try:
        while True:
            scan_count += 1
            print(f"\nSimulation Scan #{scan_count}")
            
            # Simulate random device discovery
            import random
            if random.random() > 0.3:  # 70% chance to find devices
                found_devices = random.sample(simulated_devices, random.randint(1, len(simulated_devices)))
                
                for device in found_devices:
                    if is_headset_device(device.name):
                        print(f"   HEADSET FOUND: {device}")
                        
                        # Simulate pairing attempt
                        print(f"   SIMULATING PAIR: Simulating pairing with {device.name}...")
                        await asyncio.sleep(2)  # Simulate pairing time
                        
                        if random.random() > 0.2:  # 80% success rate
                            device.paired = True
                            print(f"   SUCCESS: Successfully paired with {device.name}!")
                            print("   Headset pairing completed!")
                            return
                        else:
                            print(f"   FAILED: Failed to pair with {device.name}")
            else:
                print("   No devices found in this scan...")
            
            print("   Waiting 5 seconds before next scan...")
            await asyncio.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n\nSTOPPED: Simulation stopped by user after {scan_count} scans")

def print_usage():
    """Print usage information."""
    print("Windows Bluetooth Test Usage:")
    print("  python windows_bluetooth_test.py        - Run headset pairing simulation")

async def main():
    """Main test function."""
    await windows_headset_test()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
