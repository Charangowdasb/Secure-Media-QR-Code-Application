"""
Configuration settings for the QR Media Secure application
"""

# Shamir's Secret Sharing Configuration
SHAMIR_TOTAL_SHARES = 3  # N - Total number of shares to create
SHAMIR_REQUIRED_SHARES = 2  # K - Minimum shares needed to reconstruct

# Encryption Configuration
ENCRYPTION_ALGORITHM = "Fernet"  # Fernet for simplicity; can use AES
FERNET_KEY_LENGTH = 32  # 32 bytes for Fernet

# QR Code Configuration
QR_VERSION = None  # None = auto-detect optimal version based on data size (1-40)
QR_ERROR_CORRECTION = "L"  # Error correction level: L, M, Q, H (L allows more data)
QR_BOX_SIZE = 10  # Size of each box in pixels
QR_BORDER = 4  # Border size in boxes
QR_FILL_COLOR = "black"  # QR code color
QR_BACK_COLOR = "white"  # Background color

# 3D Visual Effects Configuration
ENABLE_3D_EFFECTS = True
GRADIENT_ENABLED = True
SHADOW_ENABLED = True
DEPTH_EFFECT_ENABLED = True
SHADOW_OFFSET = 2  # pixels
SHADOW_COLOR = (128, 128, 128)  # RGB gray

# File Paths
OUTPUT_QR_PATH = "generated_qr.png"
OUTPUT_QR_3D_PATH = "generated_qr_3d.png"
SHARED_SECRETS_FILE = "shared_secrets.json"

# Media Player Configuration
USE_DEFAULT_BROWSER = True
MEDIA_PLAYER_PATH = None  # Set to custom media player path if needed
# Examples: "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe" for VLC
#           "C:\\Program Files\\Windows Media Player\\wmplayer.exe" for Windows Media Player

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Validation
MIN_URL_LENGTH = 10
MAX_URL_LENGTH = 1000
VALID_MEDIA_EXTENSIONS = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm", ".m3u8", ".mp3", ".wav", ".flac"]
