"""
Media Player Module

Handles opening and playing media content (videos, audio, etc.)
Supports various playback options and media types.
"""

import webbrowser
import subprocess
import os
import sys
from typing import Optional
from urllib.parse import urlparse
from utils import get_logger, validate_url

logger = get_logger(__name__)


class MediaPlayer:
    """Handle media playback from URLs or local files"""
    
    def __init__(self, media_player_path: str = None, use_browser: bool = True):
        """
        Initialize media player
        
        Args:
            media_player_path: Path to custom media player executable
            use_browser: Use default browser for URLs
        """
        self.media_player_path = media_player_path
        self.use_browser = use_browser
        logger.info(f"MediaPlayer initialized: browser={use_browser}, custom_player={media_player_path}")

    def play_url(self, url: str) -> bool:
        """
        Play media from URL
        
        Args:
            url: URL to media content
            
        Returns:
            True if playback initiated successfully
        """
        if not validate_url(url):
            logger.error(f"Invalid URL: {url}")
            raise ValueError(f"Invalid URL: {url}")
        
        logger.info(f"Attempting to play URL: {url}")
        
        try:
            if self.use_browser:
                logger.debug("Opening URL in default browser")
                webbrowser.open(url)
                return True
            elif self.media_player_path:
                logger.debug(f"Opening URL with custom player: {self.media_player_path}")
                subprocess.Popen([self.media_player_path, url])
                return True
            else:
                logger.error("No media player configured")
                return False
        
        except Exception as e:
            logger.error(f"Error playing URL {url}: {e}")
            raise

    def play_file(self, filepath: str) -> bool:
        """
        Play media from local file
        
        Args:
            filepath: Path to media file
            
        Returns:
            True if playback initiated successfully
        """
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Convert to absolute path
        filepath = os.path.abspath(filepath)
        logger.info(f"Attempting to play file: {filepath}")
        
        try:
            if self.media_player_path and os.path.exists(self.media_player_path):
                logger.debug(f"Playing with custom player: {self.media_player_path}")
                subprocess.Popen([self.media_player_path, filepath])
                return True
            elif sys.platform == 'win32':
                logger.debug("Playing with Windows default player")
                os.startfile(filepath)
                return True
            elif sys.platform == 'darwin':  # macOS
                logger.debug("Playing with macOS default player")
                subprocess.Popen(['open', filepath])
                return True
            else:  # Linux
                logger.debug("Playing with xdg-open")
                subprocess.Popen(['xdg-open', filepath])
                return True
        
        except Exception as e:
            logger.error(f"Error playing file {filepath}: {e}")
            raise

    def play_media(self, media_path: str) -> bool:
        """
        Play media from URL or file (auto-detects)
        
        Args:
            media_path: URL or file path
            
        Returns:
            True if playback initiated successfully
        """
        if media_path.startswith(('http://', 'https://', 'file://')):
            logger.debug("Detected as URL")
            return self.play_url(media_path)
        elif os.path.exists(media_path):
            logger.debug("Detected as local file")
            return self.play_file(media_path)
        else:
            logger.error(f"Invalid media path (not URL or existing file): {media_path}")
            raise ValueError(f"Invalid media path: {media_path}")

    def set_custom_player(self, player_path: str) -> None:
        """
        Set custom media player
        
        Args:
            player_path: Path to media player executable
        """
        if not os.path.exists(player_path):
            logger.warning(f"Media player not found: {player_path}")
        self.media_player_path = player_path
        logger.info(f"Custom media player set to: {player_path}")

    def disable_browser(self) -> None:
        """Disable browser-based playback"""
        self.use_browser = False
        logger.info("Browser-based playback disabled")

    def enable_browser(self) -> None:
        """Enable browser-based playback"""
        self.use_browser = True
        logger.info("Browser-based playback enabled")


class StreamingMediaPlayer(MediaPlayer):
    """Enhanced media player for streaming content"""
    
    def __init__(self, media_player_path: str = None):
        """Initialize streaming media player"""
        super().__init__(media_player_path, use_browser=True)
        self.supported_protocols = [
            'http', 'https', 'rtmp', 'rtsp', 'hls', 'dash'
        ]
        logger.info("StreamingMediaPlayer initialized")

    def is_streaming_url(self, url: str) -> bool:
        """
        Check if URL is a streaming URL
        
        Args:
            url: URL to check
            
        Returns:
            True if URL appears to be streaming content
        """
        parsed = urlparse(url)
        return parsed.scheme in self.supported_protocols

    def play_streaming_content(self, url: str) -> bool:
        """
        Play streaming content
        
        Args:
            url: Streaming URL
            
        Returns:
            True if playback initiated successfully
        """
        if not self.is_streaming_url(url):
            logger.warning(f"URL may not be streaming content: {url}")
        
        logger.info(f"Playing streaming content from: {url}")
        return self.play_url(url)


class MediaValidation:
    """Validate media content"""
    
    VALID_VIDEO_EXTENSIONS = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm', '.m3u8']
    VALID_AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']
    VALID_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    @staticmethod
    def is_valid_media_file(filepath: str) -> bool:
        """Check if file has valid media extension"""
        if not os.path.exists(filepath):
            return False
        
        _, ext = os.path.splitext(filepath.lower())
        valid_extensions = (
            MediaValidation.VALID_VIDEO_EXTENSIONS +
            MediaValidation.VALID_AUDIO_EXTENSIONS +
            MediaValidation.VALID_IMAGE_EXTENSIONS
        )
        return ext in valid_extensions

    @staticmethod
    def get_media_type(filepath: str) -> Optional[str]:
        """Get media type from file extension"""
        _, ext = os.path.splitext(filepath.lower())
        
        if ext in MediaValidation.VALID_VIDEO_EXTENSIONS:
            return 'video'
        elif ext in MediaValidation.VALID_AUDIO_EXTENSIONS:
            return 'audio'
        elif ext in MediaValidation.VALID_IMAGE_EXTENSIONS:
            return 'image'
        return None

    @staticmethod
    def validate_url_format(url: str) -> bool:
        """Validate URL format"""
        return validate_url(url)


def create_media_player(player_path: str = None) -> MediaPlayer:
    """Factory function to create media player"""
    return MediaPlayer(player_path)


def create_streaming_player(player_path: str = None) -> StreamingMediaPlayer:
    """Factory function to create streaming player"""
    return StreamingMediaPlayer(player_path)
