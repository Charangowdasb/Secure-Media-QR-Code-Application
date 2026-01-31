"""
Utility functions for the QR Media Secure application
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from config import LOG_LEVEL

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle bytes and other types"""
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.hex()
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hexadecimal string"""
    return data.hex()


def hex_to_bytes(hex_string: str) -> bytes:
    """Convert hexadecimal string to bytes"""
    return bytes.fromhex(hex_string)


def save_json(data: dict, filepath: str) -> None:
    """Save data to JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4, cls=JSONEncoder)
        logger.info(f"Data saved to {filepath}")
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")
        raise


def load_json(filepath: str) -> dict:
    """Load data from JSON file"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        logger.info(f"Data loaded from {filepath}")
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {filepath}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
        raise


def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted"""
    from config import MIN_URL_LENGTH, MAX_URL_LENGTH
    
    if not isinstance(url, str):
        return False
    if not (MIN_URL_LENGTH <= len(url) <= MAX_URL_LENGTH):
        return False
    if not (url.startswith('http://') or url.startswith('https://')):
        return False
    return True


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
