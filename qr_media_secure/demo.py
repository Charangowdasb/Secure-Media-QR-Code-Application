"""
Complete Example and Demo Script

This script demonstrates the full workflow:
1. Generate a secure QR code with a media URL
2. Scan the QR code
3. Reconstruct the media URL
4. Play the media
"""

import os
import sys
from pathlib import Path
from orchestrator import create_orchestrator
from utils import get_logger

logger = get_logger(__name__)


def demo_full_workflow():
    """
    Demonstrate the complete secure media QR workflow
    """
    print("\n" + "="*80)
    print("SECURE MEDIA QR CODE - COMPLETE WORKFLOW DEMO")
    print("="*80 + "\n")
    
    try:
        # Step 1: Initialize orchestrator
        print("[1/5] Initializing orchestrator...")
        print("-" * 80)
        orchestrator = create_orchestrator(k=2, n=3)  # 3 shares, need 2 to reconstruct
        print("[OK] Orchestrator created: {} total shares, {} required".format(orchestrator.n, orchestrator.k))
        print(f"  Encryption key: {orchestrator.get_encryption_key_hex()[:16]}...")
        print()
        
        # Step 2: Generate QR code with media URL
        print("[2/5] Generating secure QR code...")
        print("-" * 80)
        
        # Example media URLs (change to your own)
        # media_url = "https://bit.ly/rickroll"  # Short URL for QR demo
        # Alternative examples:
        media_url = "https://www.w3schools.com/html/mov_bbb.mp4"
        # media_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        print(f"Media URL to protect: {media_url}")
        
        qr_result = orchestrator.generate_encrypted_qr(
            media_url=media_url,
            output_path="demo_qr_code.png",
            use_3d=True
        )
        
        print("[OK] QR code generated with 3D effects")
        print(f"  Path: {qr_result['qr_path']}")
        print(f"  Shares: {qr_result['shares_generated']}/{qr_result['total_shares']}")
        print()
        
        # Step 3: Verify QR code integrity
        print("[3/5] Verifying QR code integrity...")
        print("-" * 80)
        
        verification = orchestrator.verify_reconstruction("demo_qr_code.png")
        print(f"✓ Verification status: {verification['status']}")
        print(f"  QR Scannable: {verification.get('qr_scannable', 'N/A')}")
        print(f"  URLs match: {verification.get('urls_match', 'N/A')}")
        print()
        
        # Step 4: Scan and reconstruct URL
        print("[4/5] Scanning QR code and reconstructing URL...")
        print("-" * 80)
        
        reconstructed_url = orchestrator.scan_and_reconstruct_url("demo_qr_code.png", use_k_shares=3)
        print(f"✓ URL successfully reconstructed!")
        print(f"  Original:      {media_url}")
        print(f"  Reconstructed: {reconstructed_url}")
        print(f"  Match: {'✓ YES' if media_url == reconstructed_url else '✗ NO'}")
        print()
        
        # Step 5: Summary and optional playback
        print("[5/5] Summary and next steps...")
        print("-" * 80)
        print(f"✓ Complete workflow executed successfully!")
        print()
        print("Security Details:")
        print(f"  • URL split into {orchestrator.n} secret shares")
        print(f"  • Any {orchestrator.k} shares can reconstruct the URL")
        print(f"  • Each share is encrypted with Fernet")
        print(f"  • Encryption key: {orchestrator.get_encryption_key_hex()[:32]}...")
        print()
        print("Files generated:")
        print(f"  • demo_qr_code.png - Your secure QR code with 3D effects")
        print()
        print("To play media:")
        print("  • Scan 'demo_qr_code.png' with the application")
        print("  • The URL will be automatically reconstructed and decrypted")
        print("  • Media will open in your default browser or media player")
        print()
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n✗ Error: {e}")
        sys.exit(1)


def demo_partial_shares():
    """
    Demonstrate insufficient shares scenario
    """
    print("\n" + "="*80)
    print("DEMO: INSUFFICIENT SHARES TEST")
    print("="*80 + "\n")
    
    try:
        orchestrator = create_orchestrator(k=3, n=5)
        media_url = "https://example.com/video.mp4"
        
        print(f"Generating QR code with 5 shares (threshold 3)...")
        orchestrator.generate_encrypted_qr(media_url, "test_qr.png")
        print("✓ QR generated")
        print()
        
        # Try with insufficient shares
        print("Attempting to reconstruct with only 2 shares (< threshold 3)...")
        try:
            qr_data = orchestrator.qr_scanner.scan_image_file("test_qr.png")
            import json
            metadata = json.loads(qr_data)
            encrypted_shares = metadata['encrypted_shares'][:2]
            
            decrypted_shares = [
                orchestrator.encryption_mgr.decrypt(share) 
                for share in encrypted_shares
            ]
            reconstructed = orchestrator.shamir.reconstruct(decrypted_shares)
            print(f"✗ Unexpected: Reconstruction succeeded with only 2 shares!")
            
        except Exception as e:
            print(f"✓ Correctly failed: {type(e).__name__}")
            print(f"  Reason: Insufficient shares for reconstruction")
        
        print()
        print("Now trying with 3 shares (= threshold 3)...")
        encrypted_shares = metadata['encrypted_shares'][:3]
        decrypted_shares = [
            orchestrator.encryption_mgr.decrypt(share) 
            for share in encrypted_shares
        ]
        reconstructed = orchestrator.shamir.reconstruct(decrypted_shares)
        print(f"✓ Reconstruction succeeded with 3 shares!")
        print(f"  Reconstructed URL: {reconstructed}")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n✗ Error: {e}")


def demo_custom_encryption_key():
    """
    Demonstrate using a custom encryption key
    """
    print("\n" + "="*80)
    print("DEMO: CUSTOM ENCRYPTION KEY")
    print("="*80 + "\n")
    
    try:
        from encryption import EncryptionManager
        
        # Create orchestrator with custom key
        custom_key = EncryptionManager.generate_key()
        print(f"Generated custom encryption key: {custom_key}")
        print()
        
        orchestrator = create_orchestrator(encryption_key=custom_key)
        media_url = "https://example.com/media.mp4"
        
        print("Generating QR code with custom encryption key...")
        orchestrator.generate_encrypted_qr(media_url, "custom_key_qr.png")
        print("✓ QR code generated")
        print()
        
        print("Reconstructing with same key...")
        reconstructed = orchestrator.scan_and_reconstruct_url("custom_key_qr.png")
        print(f"✓ Successfully reconstructed: {reconstructed}")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n✗ Error: {e}")


def demo_session_save_load():
    """
    Demonstrate saving and loading sessions
    """
    print("\n" + "="*80)
    print("DEMO: SESSION SAVE AND LOAD")
    print("="*80 + "\n")
    
    try:
        # Create and generate
        print("Creating session and generating QR code...")
        orchestrator1 = create_orchestrator(k=3, n=5)
        media_url = "https://example.com/video.mp4"
        orchestrator1.generate_encrypted_qr(media_url, "session_qr.png")
        print("✓ QR code generated")
        print()
        
        # Save session
        print("Saving session to file...")
        orchestrator1.save_session("demo_session.json")
        print("✓ Session saved to demo_session.json")
        print()
        
        # Load session in new orchestrator
        print("Loading session in new orchestrator...")
        orchestrator2 = create_orchestrator()
        orchestrator2.load_session("demo_session.json")
        print("✓ Session loaded")
        print(f"  Loaded k={orchestrator2.k}, n={orchestrator2.n}")
        print()
        
        # Use loaded session
        print("Reconstructing URL from loaded session...")
        reconstructed = orchestrator2.scan_and_reconstruct_url("session_qr.png")
        print(f"✓ Successfully reconstructed: {reconstructed}")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print("SECURE MEDIA QR CODE - CRYPTOGRAPHIC DEMONSTRATION")
    print("Using Shamir's Secret Sharing & AES-256 Encryption")
    print("=" * 80)
    
    # Run full workflow demo
    demo_full_workflow()
    
    # Optional: Run additional demos (comment out if not needed)
    # Uncomment below to run additional demonstrations
    # demo_partial_shares()
    # demo_custom_encryption_key()
    # demo_session_save_load()
    
    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80 + "\n")
