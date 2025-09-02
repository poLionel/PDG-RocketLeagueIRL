"""
Video Feed Service for fetching camera feeds from cars.

This service manages periodic fetching of video frames from cars' IP cameras
and distributes them to subscribed WebSocket clients.
"""

import asyncio
import logging
import base64
import json
from typing import Dict, Set

# Try to import aiohttp, fallback gracefully if not available
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None

logger = logging.getLogger(__name__)


class VideoFeedService:
    """Service for managing video feeds from cars."""
    
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
        self.fetch_interval = 1.0  # Fetch every 1 second
        self.session = None
        self.running = False
    
    async def start(self):
        """Start the video feed service."""
        if not AIOHTTP_AVAILABLE:
            logger.warning("aiohttp not available, video feed service disabled")
            return
        
        self.running = True
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5))
        logger.info("Video feed service started")
    
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
        if not car or not car.video_feed_url:
            logger.warning(f"Car {car_id} not found or has no video feed URL")
            return
        
        if not car.video_subscribers:
            logger.debug(f"Car {car_id} has no subscribers, not starting feed")
            return
        
        # Start feed task
        task = asyncio.create_task(self._fetch_feed_loop(car_id))
        self.active_feeds[car_id] = task
        logger.info(f"Started video feed for car {car_id} at {car.video_feed_url}")
    
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
            if car.video_subscribers and car.video_feed_url:
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
    
    async def _fetch_feed_loop(self, car_id):
        """
        Main loop for fetching video frames from a car.
        
        Args:
            car_id (int): ID of the car to fetch from
        """
        car = self.car_manager.get_car(car_id)
        if not car:
            return
        
        url = f"http://{car.video_feed_url}/capture"  # Assume endpoint is /capture
        
        while self.running:
            try:
                # Check if car still has subscribers
                if not car.video_subscribers:
                    logger.debug(f"Car {car_id} has no more subscribers, stopping feed")
                    break
                
                # Fetch frame from car's camera
                async with self.session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Convert to base64
                        base64_frame = base64.b64encode(image_data).decode('utf-8')
                        
                        # Update car's last frame
                        car.update_video_frame(base64_frame)
                        
                        # Broadcast to subscribers
                        await self._broadcast_frame(car_id, base64_frame)
                    
                    else:
                        logger.warning(f"Failed to fetch frame from car {car_id}: HTTP {response.status}")
                
            except asyncio.CancelledError:
                logger.debug(f"Feed loop for car {car_id} cancelled")
                break
            except Exception as e:
                logger.error(f"Error fetching frame from car {car_id}: {e}")
            
            # Wait before next fetch
            await asyncio.sleep(self.fetch_interval)
        
        logger.debug(f"Feed loop for car {car_id} ended")
    
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
