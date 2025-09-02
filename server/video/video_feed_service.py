"""
Video Feed Service for fetching camera feeds from cars.

This service manages periodic fetching of video frames from cars' IP cameras
and distributes them to subscribed WebSocket clients. The server acts as a
proxy to prevent overloading the cars with multiple direct connections.

Architecture:
- Cars stream video to their IP:81/stream endpoint
- Server fetches frames from each car
- Server redistributes frames to WebSocket subscribers
- Supports both MJPEG streams and single JPEG capture endpoints
"""

import asyncio
import logging
import base64
import json
import re
from typing import Dict, Set, Optional

# Try to import aiohttp, fallback gracefully if not available
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None

logger = logging.getLogger(__name__)


class VideoFeedService:
    """Service for managing video feeds from cars with IP-based streaming."""
    
    def __init__(self, car_manager, websocket_module):
        """
        Initialize the video feed service.
        
        Args:
            car_manager: CarManager instance for accessing car information
            websocket_module: WebSocket module for broadcasting frames
        """
        self.car_manager = car_manager
        self.websocket_module = websocket_module
        self.active_feeds: Dict[int, asyncio.Task] = {}  # car_id -> task
        self.fetch_interval = 0.5  # Fetch every 500ms for smoother video
        self.session = None
        self.running = False
        
        # IP-based video feed configuration
        self.stream_timeout = 10.0  # Timeout for stream connections
        self.capture_timeout = 3.0  # Timeout for single frame capture
    
    async def start(self):
        """Start the video feed service."""
        if not AIOHTTP_AVAILABLE:
            logger.warning("aiohttp not available, video feed service disabled")
            return
        
        self.running = True
        # Create session with longer timeout for video streams
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.stream_timeout, connect=5.0)
        )
        logger.info("Video feed service started with IP streaming support")
    
    async def stop(self):
        """Stop the video feed service and clean up resources."""
        self.running = False
        
        # Cancel all active feed tasks
        for task in self.active_feeds.values():
            task.cancel()
        
        # Wait for all tasks to complete
        if self.active_feeds:
            await asyncio.gather(*self.active_feeds.values(), return_exceptions=True)
        
        self.active_feeds.clear()
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        logger.info("Video feed service stopped")
    
    async def start_feed_for_car(self, car_id):
        """
        Start fetching video feed for a specific car.
        
        Args:
            car_id (int): ID of the car to start feeding
        """
        if car_id in self.active_feeds:
            logger.debug(f"Video feed for car {car_id} already active")
            return
        
        car = self.car_manager.get_car(car_id)
        if not car:
            logger.warning(f"Car {car_id} not found")
            return
            
        if not car.video_subscribers:
            logger.debug(f"Car {car_id} has no subscribers, not starting feed")
            return
        
        # Check if we can get the IP address via BLE to auto-configure video feed
        if not car.video_feed_url:
            logger.info(f"Car {car_id} has no video feed URL, attempting to auto-configure from BLE...")
            if await self._auto_configure_video_feed(car_id):
                car = self.car_manager.get_car(car_id)  # Refresh car object
            else:
                logger.warning(f"Could not auto-configure video feed for car {car_id}")
                return
        
        # Start feed task
        task = asyncio.create_task(self._fetch_feed_loop(car_id))
        self.active_feeds[car_id] = task
        logger.info(f"Started video feed for car {car_id} from {car.video_feed_url}")
    
    async def stop_feed_for_car(self, car_id):
        """
        Stop fetching video feed for a specific car.
        
        Args:
            car_id (int): ID of the car to stop feeding
        """
        if car_id not in self.active_feeds:
            return
        
        task = self.active_feeds.pop(car_id)
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        logger.info(f"Stopped video feed for car {car_id}")
    
    async def update_car_feeds(self):
        """Update active feeds based on current car subscriptions."""
        if not self.running:
            return
        
        cars_with_subscribers = []
        cars_without_subscribers = []
        
        for car in self.car_manager.get_all_cars():
            if car.video_subscribers:
                cars_with_subscribers.append(car.car_id)
            else:
                cars_without_subscribers.append(car.car_id)
        
        # Start feeds for cars with subscribers
        for car_id in cars_with_subscribers:
            if car_id not in self.active_feeds:
                await self.start_feed_for_car(car_id)
        
        # Stop feeds for cars without subscribers
        for car_id in cars_without_subscribers:
            if car_id in self.active_feeds:
                await self.stop_feed_for_car(car_id)
    
    async def _auto_configure_video_feed(self, car_id) -> bool:
        """
        Auto-configure video feed URL by reading IP address from car via BLE.
        
        Args:
            car_id (int): ID of the car to configure
            
        Returns:
            bool: True if configuration successful, False otherwise
        """
        try:
            # Try to get Bluetooth service
            from bluetooth.handlers import get_bluetooth_service
            
            bluetooth_service = get_bluetooth_service()
            if not bluetooth_service:
                logger.debug("Bluetooth service not available for auto-configuration")
                return False
            
            car = self.car_manager.get_car(car_id)
            if not car or not car.ble_address:
                logger.debug(f"Car {car_id} has no BLE address for auto-configuration")
                return False
            
            # Check if we're in control phase
            if not bluetooth_service.ble_service.is_in_control_phase():
                logger.debug("Cannot auto-configure: BLE service is in scan phase")
                return False
            
            # Get IP address via BLE
            ip_address = await bluetooth_service.ble_service.get_car_ip_address(car.ble_address)
            
            if ip_address and ip_address.strip():
                # Configure video feed URL in format http://IP:81/stream
                video_url = f"http://{ip_address.strip()}:81/stream"
                success = self.car_manager.update_car_video_feed(car_id, ip_address.strip(), 81)
                
                if success:
                    logger.info(f"Auto-configured video feed for car {car_id}: {video_url}")
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error during auto-configuration for car {car_id}: {e}")
            return False
    
    def _parse_video_url(self, video_feed_url: str) -> tuple:
        """
        Parse video feed URL to extract base URL and determine stream type.
        
        Args:
            video_feed_url (str): Full video feed URL
            
        Returns:
            tuple: (base_url, stream_endpoint, capture_endpoint, is_stream)
        """
        # Expected format: "http://IP:PORT" or "IP:PORT"
        if not video_feed_url.startswith('http'):
            video_feed_url = f"http://{video_feed_url}"
        
        # Remove any existing path
        base_url = re.match(r'(https?://[^/]+)', video_feed_url)
        if base_url:
            base_url = base_url.group(1)
        else:
            base_url = video_feed_url
        
        # Define endpoints for car camera streams
        stream_endpoint = f"{base_url}/stream"      # MJPEG stream endpoint
        capture_endpoint = f"{base_url}/capture"    # Single JPEG capture endpoint
        
        return base_url, stream_endpoint, capture_endpoint, True
    
    async def _fetch_feed_loop(self, car_id):
        """
        Main loop for fetching video frames from a car's IP camera.
        
        Args:
            car_id (int): ID of the car to fetch from
        """
        car = self.car_manager.get_car(car_id)
        if not car:
            return
        
        base_url, stream_endpoint, capture_endpoint, is_stream = self._parse_video_url(car.video_feed_url)
        logger.info(f"Starting video feed loop for car {car_id}")
        logger.debug(f"Stream endpoint: {stream_endpoint}")
        logger.debug(f"Capture endpoint: {capture_endpoint}")
        
        consecutive_failures = 0
        max_failures = 5
        
        while self.running:
            try:
                # Check if car still has subscribers
                if not car.video_subscribers:
                    logger.debug(f"Car {car_id} has no more subscribers, stopping feed")
                    break
                
                # Try MJPEG stream first, fall back to single captures
                frame_data = None
                
                if is_stream and consecutive_failures < 3:
                    frame_data = await self._fetch_from_mjpeg_stream(stream_endpoint)
                
                # Fall back to single frame capture if stream fails
                if frame_data is None:
                    frame_data = await self._fetch_single_frame(capture_endpoint)
                
                if frame_data:
                    # Convert to base64
                    base64_frame = base64.b64encode(frame_data).decode('utf-8')
                    
                    # Update car's last frame
                    car.update_video_frame(base64_frame)
                    
                    # Broadcast to subscribers
                    await self._broadcast_frame(car_id, base64_frame)
                    
                    consecutive_failures = 0
                    logger.debug(f"Successfully fetched and broadcast frame for car {car_id}")
                else:
                    consecutive_failures += 1
                    logger.warning(f"Failed to fetch frame from car {car_id} (failure #{consecutive_failures})")
                    
                    if consecutive_failures >= max_failures:
                        logger.error(f"Too many consecutive failures for car {car_id}, stopping feed")
                        break
                
            except asyncio.CancelledError:
                logger.debug(f"Feed loop for car {car_id} cancelled")
                break
            except Exception as e:
                consecutive_failures += 1
                logger.error(f"Error in feed loop for car {car_id}: {e}")
                
                if consecutive_failures >= max_failures:
                    logger.error(f"Too many errors for car {car_id}, stopping feed")
                    break
            
            # Wait before next fetch
            await asyncio.sleep(self.fetch_interval)
        
        logger.debug(f"Feed loop for car {car_id} ended")
    
    async def _fetch_from_mjpeg_stream(self, stream_url: str) -> Optional[bytes]:
        """
        Fetch a single frame from an MJPEG stream.
        
        Args:
            stream_url (str): URL of the MJPEG stream
            
        Returns:
            Optional[bytes]: JPEG frame data or None if failed
        """
        try:
            async with self.session.get(stream_url) as response:
                if response.status != 200:
                    return None
                
                # Read stream data to find JPEG frame boundaries
                boundary = None
                content_type = response.headers.get('content-type', '')
                
                if 'multipart' in content_type:
                    # Extract boundary from content type
                    boundary_match = re.search(r'boundary=([^;]+)', content_type)
                    if boundary_match:
                        boundary = boundary_match.group(1).strip()
                
                if boundary:
                    # Read multipart stream
                    async for chunk in response.content.iter_chunked(1024):
                        # TODO: Implement proper MJPEG boundary parsing
                        # For now, just take the chunk as a frame
                        if len(chunk) > 1000:  # Assume it's a frame if reasonably sized
                            return chunk
                else:
                    # Treat entire response as single JPEG
                    data = await response.read()
                    if len(data) > 1000:
                        return data
                
        except Exception as e:
            logger.debug(f"MJPEG stream fetch failed: {e}")
        
        return None
    
    async def _fetch_single_frame(self, capture_url: str) -> Optional[bytes]:
        """
        Fetch a single JPEG frame from the capture endpoint.
        
        Args:
            capture_url (str): URL of the capture endpoint
            
        Returns:
            Optional[bytes]: JPEG frame data or None if failed
        """
        try:
            timeout = aiohttp.ClientTimeout(total=self.capture_timeout)
            async with self.session.get(capture_url, timeout=timeout) as response:
                if response.status == 200:
                    frame_data = await response.read()
                    
                    # Verify it's a valid JPEG by checking header
                    if len(frame_data) > 10 and frame_data[:2] == b'\xff\xd8':
                        return frame_data
                    else:
                        logger.debug(f"Invalid JPEG data from {capture_url}")
                
        except Exception as e:
            logger.debug(f"Single frame fetch failed from {capture_url}: {e}")
        
        return None
    
    async def _broadcast_frame(self, car_id, base64_frame):
        """
        Broadcast a video frame to all subscribers.
        
        Args:
            car_id (int): ID of the car
            base64_frame (str): Base64 encoded JPEG frame
        """
        car = self.car_manager.get_car(car_id)
        if not car or not car.video_subscribers:
            return
        
        # Create video frame message
        video_message = {
            "action": "video_frame_update",
            "car": car_id,
            "video_frame": base64_frame,
            "timestamp": str(asyncio.get_event_loop().time())
        }
        
        # Send to each subscriber individually
        disconnected_subscribers = []
        
        for websocket_id in car.video_subscribers.copy():
            if websocket_id in self.websocket_module.active_connections:
                websocket = self.websocket_module.active_connections[websocket_id]
                try:
                    await websocket.send(json.dumps(video_message))
                except Exception as e:
                    logger.warning(f"Failed to send video frame to {websocket_id}: {e}")
                    disconnected_subscribers.append(websocket_id)
            else:
                disconnected_subscribers.append(websocket_id)
        
        # Clean up disconnected subscribers
        for websocket_id in disconnected_subscribers:
            car.remove_video_subscriber(websocket_id)
        
        logger.debug(f"Broadcasted frame for car {car_id} to {len(car.video_subscribers)} subscribers")


# Global video feed service instance
video_feed_service = None


def get_video_feed_service():
    """Get the global video feed service instance."""
    return video_feed_service


def set_video_feed_service(service):
    """Set the global video feed service instance."""
    global video_feed_service
    video_feed_service = service
