"""
Secure Media QR Code Application

A comprehensive Python application for generating secure QR codes with embedded
media URLs using Shamir's Secret Sharing and encryption.

Features:
- Shamir's Secret Sharing for URL protection
- Fernet encryption for shares
- 3D visual effects on QR codes
- QR scanning and automatic reconstruction
- Media playback integration

Author: Cryptography & Security Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Security Team"

from orchestrator import SecureMediaQROrchestrator, create_orchestrator
from shamir_sharing import ShamirSecretSharing, create_secret_sharer
from encryption import EncryptionManager, SecureDataContainer
from qr_generator import QRCodeGenerator, QRCodeWithCustomColors
from qr_scanner import QRCodeScanner, create_scanner
from media_player import MediaPlayer, StreamingMediaPlayer, MediaValidation

__all__ = [
    'SecureMediaQROrchestrator',
    'create_orchestrator',
    'ShamirSecretSharing',
    'create_secret_sharer',
    'EncryptionManager',
    'SecureDataContainer',
    'QRCodeGenerator',
    'QRCodeWithCustomColors',
    'QRCodeScanner',
    'create_scanner',
    'MediaPlayer',
    'StreamingMediaPlayer',
    'MediaValidation',
]
