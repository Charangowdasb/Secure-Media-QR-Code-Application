"""
Encryption and Decryption Module

Provides secure encryption/decryption using Fernet (symmetric encryption)
from the cryptography library. Fernet guarantees that a message encrypted
using it cannot be manipulated or read without the key.
"""

from cryptography.fernet import Fernet, InvalidToken
import base64
import os
import hashlib
from typing import Tuple
from utils import get_logger, bytes_to_hex, hex_to_bytes

logger = get_logger(__name__)


class EncryptionManager:
    """Manages encryption and decryption of data"""
    
    def __init__(self, key: bytes = None):
        """
        Initialize encryption manager with optional key
        
        Args:
            key: 32-byte key for Fernet (if None, generates new key)
        """
        if key is None:
            self.key = Fernet.generate_key()
            logger.info("Generated new encryption key")
        else:
            self.key = key
        
        self.cipher = Fernet(self.key)
        logger.debug("EncryptionManager initialized")

    def get_key(self) -> bytes:
        """Get the encryption key"""
        return self.key

    def get_key_hex(self) -> str:
        """Get the encryption key as hex string"""
        return bytes_to_hex(self.key)

    @staticmethod
    def generate_key() -> bytes:
        """Generate a new random encryption key"""
        key = Fernet.generate_key()
        logger.info("New encryption key generated")
        return key

    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None, iterations: int = 100000) -> Tuple[bytes, bytes]:
        """
        Derive an encryption key from a password using PBKDF2-like approach
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation (generated if None)
            iterations: Number of iterations for key derivation
            
        Returns:
            Tuple of (key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        # Simple PBKDF2-like implementation using hashlib
        key = password.encode('utf-8')
        for _ in range(iterations):
            key = hashlib.sha256(key + salt).digest()
        
        # Fernet key must be URL-safe base64 encoded 32 bytes
        key = base64.urlsafe_b64encode(key[:32])
        logger.info("Key derived from password")
        return key, salt

    def encrypt(self, data: str) -> str:
        """
        Encrypt plaintext string
        
        Args:
            data: Plaintext string to encrypt
            
        Returns:
            Encrypted data as hex string
        """
        try:
            plaintext_bytes = data.encode('utf-8')
            ciphertext = self.cipher.encrypt(plaintext_bytes)
            return bytes_to_hex(ciphertext)
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt(self, encrypted_hex: str) -> str:
        """
        Decrypt ciphertext
        
        Args:
            encrypted_hex: Encrypted data as hex string
            
        Returns:
            Decrypted plaintext string
        """
        try:
            ciphertext = hex_to_bytes(encrypted_hex)
            plaintext_bytes = self.cipher.decrypt(ciphertext)
            return plaintext_bytes.decode('utf-8')
        except InvalidToken:
            logger.error("Decryption failed: Invalid token or corrupted data")
            raise ValueError("Decryption failed: Invalid or corrupted data")
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

    def encrypt_bytes(self, data: bytes) -> str:
        """
        Encrypt bytes
        
        Args:
            data: Bytes to encrypt
            
        Returns:
            Encrypted data as hex string
        """
        try:
            ciphertext = self.cipher.encrypt(data)
            return bytes_to_hex(ciphertext)
        except Exception as e:
            logger.error(f"Bytes encryption failed: {e}")
            raise

    def decrypt_bytes(self, encrypted_hex: str) -> bytes:
        """
        Decrypt ciphertext to bytes
        
        Args:
            encrypted_hex: Encrypted data as hex string
            
        Returns:
            Decrypted bytes
        """
        try:
            ciphertext = hex_to_bytes(encrypted_hex)
            plaintext_bytes = self.cipher.decrypt(ciphertext)
            return plaintext_bytes
        except InvalidToken:
            logger.error("Decryption failed: Invalid token or corrupted data")
            raise ValueError("Decryption failed: Invalid or corrupted data")
        except Exception as e:
            logger.error(f"Bytes decryption failed: {e}")
            raise


class SecureDataContainer:
    """
    Secure container for storing encrypted data with metadata
    """
    
    def __init__(self, encryption_manager: EncryptionManager):
        """
        Initialize with encryption manager
        
        Args:
            encryption_manager: EncryptionManager instance
        """
        self.encryption_manager = encryption_manager
        self.data = {}

    def store(self, key: str, value: str) -> None:
        """Store encrypted data"""
        encrypted = self.encryption_manager.encrypt(value)
        self.data[key] = encrypted
        logger.debug(f"Data stored for key: {key}")

    def retrieve(self, key: str) -> str:
        """Retrieve and decrypt data"""
        if key not in self.data:
            raise KeyError(f"Key not found: {key}")
        encrypted = self.data[key]
        return self.encryption_manager.decrypt(encrypted)

    def get_encrypted(self, key: str) -> str:
        """Get encrypted data without decryption"""
        if key not in self.data:
            raise KeyError(f"Key not found: {key}")
        return self.data[key]
