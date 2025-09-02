"""
Video module for managing video feeds from cars.

This module contains services and utilities for handling video streams
from cars' IP cameras, including fetching, processing, and distributing
video frames to WebSocket clients.
"""

from .video_feed_service import VideoFeedService, get_video_feed_service, set_video_feed_service

__all__ = ['VideoFeedService', 'get_video_feed_service', 'set_video_feed_service']
