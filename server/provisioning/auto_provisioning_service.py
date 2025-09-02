"""
Automatic WiFi Provisioning Service

This service automatically provisions cars with WiFi credentials and retrieves their IP addresses
without requiring manual routes. It runs in the background and handles:

1. Sending WiFi credentials to newly discovered cars
2. Waiting for cars to connect to WiFi
3. Reading IP addresses via BLE
4. Retrying failed attempts after 1 minute
5. Auto-configuring video feeds once IP is obtained

The service integrates with the existing car manager and BLE service.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Set, Optional
from bluetooth.handlers import get_bluetooth_service

logger = logging.getLogger(__name__)

class AutoProvisioningService:
    """
    Background service that automatically provisions cars with WiFi and retrieves their IP addresses.
    """
    
    def __init__(self, car_manager, wifi_ssid="RL-Hotspot", wifi_password="rocketleague"):
        self.car_manager = car_manager
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        
        # Track provisioning state for each car
        self.provisioning_states: Dict[str, dict] = {}  # ble_address -> state
        self.retry_queue: Set[str] = set()  # Cars waiting for retry
        
        # Service control
        self.running = False
        self.task = None
        
        # Timing configuration
        self.retry_delay = 60  # 1 minute retry delay
        self.ip_check_delay = 10  # 10 seconds between IP checks after WiFi sent
        self.max_ip_checks = 18  # Max 3 minutes of IP checking (18 * 10s = 180s)
        
    def start(self):
        """Start the automatic provisioning service."""
        if self.running:
            logger.warning("Auto provisioning service is already running")
            return
            
        self.running = True
        self.task = asyncio.create_task(self._run_service())
        logger.info("🚀 Auto provisioning service started")
        
    async def stop(self):
        """Stop the automatic provisioning service."""
        if not self.running:
            return
            
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
                
        logger.info("⏹️ Auto provisioning service stopped")
        
    def add_discovered_car(self, ble_address: str, car_name: str = None):
        """
        Add a newly discovered car to the auto provisioning queue.
        
        Args:
            ble_address: BLE address of the discovered car
            car_name: Optional name of the car
        """
        if ble_address not in self.provisioning_states:
            self.provisioning_states[ble_address] = {
                'name': car_name or f"Car-{ble_address[-5:]}",
                'state': 'discovered',  # discovered -> wifi_sent -> ip_checking -> completed/failed
                'wifi_sent_at': None,
                'ip_check_count': 0,
                'last_retry_at': None,
                'ip_address': None,
                'completed': False,
                'failed': False
            }
            logger.info(f"📱 Added car {car_name or ble_address} to auto provisioning queue")
            
    async def _run_service(self):
        """Main service loop that handles automatic provisioning."""
        logger.info("🔄 Auto provisioning service main loop started")
        
        while self.running:
            try:
                await self._process_provisioning_queue()
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except asyncio.CancelledError:
                logger.info("Auto provisioning service cancelled")
                break
            except Exception as e:
                logger.error(f"Error in auto provisioning service: {e}")
                await asyncio.sleep(10)  # Wait longer on errors
                
    async def _process_provisioning_queue(self):
        """Process all cars in the provisioning queue."""
        bluetooth_service = get_bluetooth_service()
        if not bluetooth_service or not bluetooth_service.ble_service:
            return
            
        current_time = time.time()
        
        for ble_address, state in list(self.provisioning_states.items()):
            if state['completed'] or state['failed']:
                continue
                
            try:
                if state['state'] == 'discovered':
                    await self._send_wifi_credentials(ble_address, state, bluetooth_service)
                    
                elif state['state'] == 'wifi_sent':
                    await self._check_wifi_connection_and_ip(ble_address, state, bluetooth_service)
                    
                elif state['state'] == 'ip_checking':
                    await self._continue_ip_checking(ble_address, state, bluetooth_service)
                    
                elif state['state'] == 'retry_waiting':
                    await self._check_retry_timing(ble_address, state, current_time)
                    
            except Exception as e:
                logger.error(f"Error processing car {ble_address}: {e}")
                await self._schedule_retry(ble_address, state)
                
    async def _send_wifi_credentials(self, ble_address: str, state: dict, bluetooth_service):
        """Send WiFi credentials to a car."""
        logger.info(f"📶 Sending WiFi credentials to {state['name']} ({ble_address})")
        
        try:
            # Check if car is still discoverable
            if ble_address not in bluetooth_service.ble_service.discovered_devices:
                logger.warning(f"Car {ble_address} no longer discoverable, scheduling retry")
                await self._schedule_retry(ble_address, state)
                return
                
            # Send WiFi credentials
            success = await bluetooth_service.ble_service.set_wifi_on_car(
                ble_address, self.wifi_ssid, self.wifi_password
            )
            
            if success:
                state['state'] = 'wifi_sent'
                state['wifi_sent_at'] = time.time()
                state['ip_check_count'] = 0
                logger.info(f"✅ WiFi credentials sent successfully to {state['name']}")
                
                # Update car manager if car exists
                await self._update_car_manager_status(ble_address, connected=True)
                
            else:
                logger.warning(f"❌ Failed to send WiFi credentials to {state['name']}")
                await self._schedule_retry(ble_address, state)
                
        except Exception as e:
            logger.error(f"Error sending WiFi to {state['name']}: {e}")
            await self._schedule_retry(ble_address, state)
            
    async def _check_wifi_connection_and_ip(self, ble_address: str, state: dict, bluetooth_service):
        """Wait a bit after WiFi sent, then start checking for IP."""
        wifi_sent_time = state['wifi_sent_at']
        if time.time() - wifi_sent_time < self.ip_check_delay:
            return  # Wait more before checking IP
            
        # Start IP checking phase
        state['state'] = 'ip_checking'
        logger.info(f"🔍 Starting IP address checking for {state['name']}")
        
    async def _continue_ip_checking(self, ble_address: str, state: dict, bluetooth_service):
        """Continue checking for car's IP address."""
        state['ip_check_count'] += 1
        
        try:
            # Try to read IP address
            ip_address = await bluetooth_service.ble_service.get_car_ip_address(ble_address)
            
            if ip_address and ip_address.strip():
                ip_clean = ip_address.strip()
                state['ip_address'] = ip_clean
                state['completed'] = True
                state['state'] = 'completed'
                
                logger.info(f"🎉 Successfully obtained IP address for {state['name']}: {ip_clean}")
                
                # Update car manager with IP
                await self._configure_car_with_ip(ble_address, ip_clean)
                
            elif state['ip_check_count'] >= self.max_ip_checks:
                # Give up after max attempts
                logger.warning(f"⏰ Max IP check attempts reached for {state['name']}, scheduling retry")
                await self._schedule_retry(ble_address, state)
                
            else:
                # Continue checking
                logger.debug(f"⏳ IP check {state['ip_check_count']}/{self.max_ip_checks} for {state['name']}")
                
        except Exception as e:
            logger.error(f"Error checking IP for {state['name']}: {e}")
            if state['ip_check_count'] >= self.max_ip_checks:
                await self._schedule_retry(ble_address, state)
                
    async def _check_retry_timing(self, ble_address: str, state: dict, current_time: float):
        """Check if it's time to retry a failed provisioning attempt."""
        if state['last_retry_at'] and (current_time - state['last_retry_at']) >= self.retry_delay:
            logger.info(f"🔄 Retrying provisioning for {state['name']} after {self.retry_delay}s delay")
            state['state'] = 'discovered'  # Reset to start over
            state['wifi_sent_at'] = None
            state['ip_check_count'] = 0
            state['last_retry_at'] = None
            
    async def _schedule_retry(self, ble_address: str, state: dict):
        """Schedule a car for retry after delay."""
        state['state'] = 'retry_waiting'
        state['last_retry_at'] = time.time()
        logger.info(f"⏰ Scheduled retry for {state['name']} in {self.retry_delay} seconds")
        
    async def _configure_car_with_ip(self, ble_address: str, ip_address: str):
        """Configure car manager and video feed with obtained IP address."""
        try:
            # Find car in car manager by BLE address
            car = None
            if self.car_manager:
                for c in self.car_manager.get_all_cars():
                    if c.ble_address == ble_address:
                        car = c
                        break
                        
            if car:
                # Update video feed URL
                port = 81  # Standard ESP32 camera port
                success = self.car_manager.update_car_video_feed(car.car_id, ip_address, port)
                
                if success:
                    logger.info(f"📹 Configured video feed for {car.name}: http://{ip_address}:{port}/stream")
                    
                    # Update video feed service
                    try:
                        from video import get_video_feed_service
                        video_service = get_video_feed_service()
                        if video_service:
                            await video_service.update_car_feeds()
                    except ImportError:
                        logger.debug("Video feed service not available")
                        
                # Update car connection status
                self.car_manager.update_car_status(car.car_id, connected=True)
                
            else:
                logger.warning(f"Could not find car with BLE address {ble_address} in car manager")
                
        except Exception as e:
            logger.error(f"Error configuring car with IP {ip_address}: {e}")
            
    async def _update_car_manager_status(self, ble_address: str, **kwargs):
        """Update car status in car manager if car exists."""
        try:
            if self.car_manager:
                for car in self.car_manager.get_all_cars():
                    if car.ble_address == ble_address:
                        self.car_manager.update_car_status(car.car_id, **kwargs)
                        break
        except Exception as e:
            logger.debug(f"Could not update car manager status: {e}")
            
    def get_provisioning_status(self) -> dict:
        """Get current provisioning status for all cars."""
        status = {
            'service_running': self.running,
            'wifi_ssid': self.wifi_ssid,
            'total_cars': len(self.provisioning_states),
            'completed': 0,
            'in_progress': 0,
            'failed': 0,
            'cars': {}
        }
        
        for ble_address, state in self.provisioning_states.items():
            car_status = {
                'name': state['name'],
                'state': state['state'],
                'ip_address': state.get('ip_address'),
                'completed': state['completed'],
                'failed': state['failed']
            }
            
            if state['completed']:
                status['completed'] += 1
            elif state['failed']:
                status['failed'] += 1
            else:
                status['in_progress'] += 1
                
            status['cars'][ble_address] = car_status
            
        return status

# Global service instance
_auto_provisioning_service = None

def get_auto_provisioning_service() -> Optional[AutoProvisioningService]:
    """Get the global auto provisioning service instance."""
    return _auto_provisioning_service

def initialize_auto_provisioning_service(car_manager, wifi_ssid="RL-Hotspot", wifi_password="rocketleague"):
    """Initialize and start the auto provisioning service."""
    global _auto_provisioning_service
    
    if _auto_provisioning_service is None:
        _auto_provisioning_service = AutoProvisioningService(car_manager, wifi_ssid, wifi_password)
        _auto_provisioning_service.start()
        logger.info("🚀 Auto provisioning service initialized and started")
    else:
        logger.warning("Auto provisioning service already initialized")
        
    return _auto_provisioning_service

async def shutdown_auto_provisioning_service():
    """Shutdown the auto provisioning service."""
    global _auto_provisioning_service
    
    if _auto_provisioning_service:
        await _auto_provisioning_service.stop()
        _auto_provisioning_service = None
        logger.info("⏹️ Auto provisioning service shutdown")
