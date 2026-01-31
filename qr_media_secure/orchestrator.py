"""
Main Application Orchestrator

Coordinates the entire workflow:
1. Generate QR code with encrypted secret shares
2. Scan and decode QR code
3. Reconstruct secret
4. Decrypt and play media
"""

import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from config import (
    SHAMIR_TOTAL_SHARES, SHAMIR_REQUIRED_SHARES,
    OUTPUT_QR_PATH, OUTPUT_QR_3D_PATH, SHARED_SECRETS_FILE
)
from shamir_sharing import ShamirSecretSharing, create_secret_sharer
from encryption import EncryptionManager
from qr_generator import QRCodeGenerator
from qr_scanner import QRCodeScanner, create_scanner
from media_player import MediaPlayer, StreamingMediaPlayer, MediaValidation
from utils import get_logger, save_json, load_json, validate_url, bytes_to_hex, hex_to_bytes

logger = get_logger(__name__)


class SecureMediaQROrchestrator:
    """
    Main orchestrator for secure media QR code generation and playback
    
    Workflow:
    1. Create encryption key and encryption manager
    2. Split media URL using Shamir's Secret Sharing
    3. Encrypt each share
    4. Encode encrypted shares in QR code
    5. Save QR code with 3D effects
    6. Scan QR code and extract encrypted shares
    7. Decrypt shares
    8. Reconstruct original media URL
    9. Play media content
    """
    
    def __init__(self, k: int = SHAMIR_REQUIRED_SHARES,
                 n: int = SHAMIR_TOTAL_SHARES,
                 encryption_key: bytes = None):
        """
        Initialize orchestrator
        
        Args:
            k: Shamir threshold (minimum shares required)
            n: Total shares to generate
            encryption_key: Optional encryption key (generated if None)
        """
        self.k = k
        self.n = n
        
        # Initialize components
        self.shamir = create_secret_sharer()
        self.encryption_mgr = EncryptionManager(encryption_key)
        self.qr_generator = QRCodeGenerator()
        self.qr_scanner = create_scanner()
        self.media_player = StreamingMediaPlayer()
        
        # Storage for current session
        self.current_shares: List[str] = []
        self.encrypted_shares: List[str] = []
        self.encrypted_shares_hex: List[str] = []
        self.metadata: Dict = {}
        
        logger.info(f"SecureMediaQROrchestrator initialized: k={k}, n={n}")

    def get_encryption_key_hex(self) -> str:
        """Get current encryption key as hex string"""
        return self.encryption_mgr.get_key_hex()

    def generate_encrypted_qr(self, media_url: str, 
                              output_path: str = OUTPUT_QR_3D_PATH,
                              use_3d: bool = True,
                              compress_metadata: bool = True) -> Dict:
        """
        Complete workflow: Encrypt shares and generate QR code
        
        Args:
            media_url: Media URL to protect
            output_path: Path to save QR code
            use_3d: Enable 3D effects
            compress_metadata: Minimize metadata size
            
        Returns:
            Dictionary with metadata about generated QR
        """
        try:
            logger.info(f"Starting QR generation for: {media_url}")
            
            # Validate URL
            if not validate_url(media_url):
                raise ValueError(f"Invalid media URL: {media_url}")
            
            # Step 1: Split URL using Shamir's Secret Sharing
            logger.info(f"Splitting URL into {self.n} shares (threshold {self.k})")
            self.current_shares = self.shamir.split(media_url, self.k, self.n)
            logger.info(f"Successfully created {len(self.current_shares)} shares")
            
            # Step 2: Encrypt each share
            logger.info("Encrypting shares...")
            self.encrypted_shares = [
                self.encryption_mgr.encrypt(share) 
                for share in self.current_shares
            ]
            logger.info(f"Successfully encrypted {len(self.encrypted_shares)} shares")
            
            # Step 3: Create metadata
            self.metadata = {
                'url': media_url,
                'total_shares': self.n,
                'required_shares': self.k,
                'shares_count': len(self.encrypted_shares),
                'encrypted_shares': self.encrypted_shares,
                'encryption_key_hex': self.get_encryption_key_hex(),
            }
            
            # Step 4: Encode encrypted shares as QR code data
            # Compress metadata if enabled
            if compress_metadata:
                qr_data = json.dumps({
                    'u': media_url,  # Short key
                    'n': self.n,
                    'k': self.k,
                    's': self.encrypted_shares,  # Short key
                    'e': self.get_encryption_key_hex(),  # Short key
                })
            else:
                qr_data = json.dumps(self.metadata)
            logger.info(f"QR data size: {len(qr_data)} bytes")
            
            # Step 5: Generate and save QR code
            logger.info(f"Generating {'3D' if use_3d else 'standard'} QR code...")
            self.qr_generator.generate_and_save(qr_data, output_path, use_3d=use_3d)
            
            logger.info(f"QR code saved to {output_path}")
            
            return {
                'status': 'success',
                'qr_path': output_path,
                'total_shares': self.n,
                'required_shares': self.k,
                'shares_generated': len(self.encrypted_shares),
                'encryption_key': self.get_encryption_key_hex(),
                'metadata': self.metadata
            }
        
        except Exception as e:
            logger.error(f"Error generating encrypted QR: {e}")
            raise

    def scan_and_reconstruct_url(self, qr_image_path: str, 
                                 use_k_shares: int = None) -> str:
        """
        Scan QR code and reconstruct media URL
        
        Args:
            qr_image_path: Path to QR code image
            use_k_shares: Number of shares to use (if less than n)
            
        Returns:
            Reconstructed media URL
        """
        try:
            logger.info(f"Scanning QR code from: {qr_image_path}")
            
            # Step 1: Scan QR code
            qr_data = self.qr_scanner.scan_image_file(qr_image_path)
            if not qr_data:
                raise ValueError("Failed to scan QR code")
            
            logger.info("QR code successfully scanned")
            
            # Step 2: Parse metadata
            metadata = json.loads(qr_data)
            logger.info(f"Metadata parsed")
            
            # Handle both compressed and normal formats
            if 'u' in metadata:  # Compressed format
                encrypted_shares = metadata['s']
                k_required = metadata['k']
                original_url = metadata['u']
            else:  # Normal format
                encrypted_shares = metadata['encrypted_shares']
                k_required = metadata['required_shares']
                original_url = metadata['url']
            
            # Step 3: Select shares to use
            if use_k_shares is None:
                use_k_shares = k_required
            elif use_k_shares < k_required:
                raise ValueError(f"Need at least {k_required} shares, requested {use_k_shares}")
            elif use_k_shares > len(encrypted_shares):
                raise ValueError(f"Only {len(encrypted_shares)} shares available")
            
            selected_shares = encrypted_shares[:use_k_shares]
            logger.info(f"Using {use_k_shares} shares out of {len(encrypted_shares)}")
            
            # Step 4: Decrypt shares
            logger.info("Decrypting shares...")
            decrypted_shares = []
            for encrypted_share in selected_shares:
                decrypted = self.encryption_mgr.decrypt(encrypted_share)
                decrypted_shares.append(decrypted)
            
            logger.info(f"Successfully decrypted {len(decrypted_shares)} shares")
            
            # Step 5: Reconstruct original URL
            logger.info(f"Reconstructing URL using {use_k_shares} shares...")
            reconstructed_url = self.shamir.reconstruct(decrypted_shares)
            logger.info("URL successfully reconstructed")
            
            # Verify
            if reconstructed_url == original_url:
                logger.info("✓ Reconstruction verified: URLs match!")
                return reconstructed_url
            else:
                logger.error(f"Reconstruction failed: URLs do not match")
                logger.error(f"Original: {original_url}")
                logger.error(f"Reconstructed: {reconstructed_url}")
                raise ValueError("URL reconstruction failed - mismatch detected")
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing QR data: {e}")
            raise ValueError(f"Invalid QR code data format: {e}")
        except Exception as e:
            logger.error(f"Error during reconstruction: {e}")
            raise

    def play_reconstructed_media(self, qr_image_path: str, 
                                  use_k_shares: int = None) -> bool:
        """
        Complete workflow: Scan, reconstruct, and play media
        
        Args:
            qr_image_path: Path to QR code image
            use_k_shares: Number of shares to use for reconstruction
            
        Returns:
            True if playback initiated successfully
        """
        try:
            logger.info("Starting playback workflow...")
            
            # Scan and reconstruct URL
            media_url = self.scan_and_reconstruct_url(qr_image_path, use_k_shares)
            
            # Play media
            logger.info(f"Playing media: {media_url}")
            success = self.media_player.play_media(media_url)
            
            if success:
                logger.info("✓ Media playback initiated successfully!")
            else:
                logger.warning("Media playback may not have succeeded")
            
            return success
        
        except Exception as e:
            logger.error(f"Error in playback workflow: {e}")
            raise

    def save_session(self, filepath: str) -> None:
        """
        Save current session to file
        
        Args:
            filepath: Path to save session
        """
        session_data = {
            'metadata': self.metadata,
            'current_shares': self.current_shares,
            'encrypted_shares': self.encrypted_shares,
            'encryption_key_hex': self.get_encryption_key_hex(),
            'k': self.k,
            'n': self.n,
        }
        save_json(session_data, filepath)
        logger.info(f"Session saved to {filepath}")

    def load_session(self, filepath: str) -> None:
        """
        Load session from file
        
        Args:
            filepath: Path to session file
        """
        session_data = load_json(filepath)
        self.metadata = session_data.get('metadata', {})
        self.current_shares = session_data.get('current_shares', [])
        self.encrypted_shares = session_data.get('encrypted_shares', [])
        self.k = session_data.get('k', self.k)
        self.n = session_data.get('n', self.n)
        logger.info(f"Session loaded from {filepath}")

    def verify_reconstruction(self, qr_image_path: str) -> Dict:
        """
        Verify that QR code can be properly reconstructed
        
        Args:
            qr_image_path: Path to QR code image
            
        Returns:
            Verification report
        """
        try:
            logger.info("Starting verification...")
            
            # Scan
            qr_data = self.qr_scanner.scan_image_file(qr_image_path)
            if not qr_data:
                return {'status': 'failed', 'reason': 'QR scan failed'}
            
            # Parse
            metadata = json.loads(qr_data)
            
            # Handle both formats
            if 'u' in metadata:  # Compressed
                k_required = metadata['k']
                encrypted_shares = metadata['s']
                original_url = metadata['u']
            else:  # Normal
                k_required = metadata['required_shares']
                encrypted_shares = metadata['encrypted_shares']
                original_url = metadata['url']
            
            # Try reconstruction
            selected_shares = encrypted_shares[:k_required]
            decrypted_shares = [
                self.encryption_mgr.decrypt(share) 
                for share in selected_shares
            ]
            reconstructed_url = self.shamir.reconstruct(decrypted_shares)
            
            # Verify
            match = reconstructed_url == original_url
            
            report = {
                'status': 'success' if match else 'failed',
                'qr_scannable': True,
                'reconstruction_successful': match,
                'shares_available': len(encrypted_shares),
                'shares_required': k_required,
                'original_url': original_url,
                'reconstructed_url': reconstructed_url,
                'urls_match': match,
            }
            
            logger.info(f"Verification complete: {report['status']}")
            return report
        
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return {'status': 'error', 'reason': str(e)}


def create_orchestrator(k: int = SHAMIR_REQUIRED_SHARES,
                       n: int = SHAMIR_TOTAL_SHARES,
                       encryption_key: bytes = None) -> SecureMediaQROrchestrator:
    """Factory function to create orchestrator"""
    return SecureMediaQROrchestrator(k, n, encryption_key)
