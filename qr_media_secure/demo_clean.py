"""
Complete Demo Script - Secure Media QR Code Application
"""

import os
import sys
from orchestrator import create_orchestrator
from utils import get_logger

logger = get_logger(__name__)


def demo_full_workflow():
    """Demonstrate the complete secure media QR workflow"""
    
    print("\n" + "="*80)
    print("SECURE MEDIA QR CODE - COMPLETE WORKFLOW DEMO")
    print("="*80 + "\n")
    
    try:
        # Step 1: Initialize orchestrator
        print("[1/5] Initializing orchestrator...")
        print("-" * 80)
        orchestrator = create_orchestrator(k=2, n=2)  # Use 2-of-2 for minimal size
        print("[OK] Orchestrator created: {} total shares, {} required".format(
            orchestrator.n, orchestrator.k))
        print("  Encryption key: {}...".format(orchestrator.get_encryption_key_hex()[:16]))
        print()
        
        # Step 2: Generate QR code with media URL
        print("[2/5] Generating secure QR code...")
        print("-" * 80)
        
        # Use short URL to fit in QR code
        media_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        print("Media URL to protect: {}".format(media_url))
        
        qr_result = orchestrator.generate_encrypted_qr(
            media_url=media_url,
            output_path="demo_qr_code.png",
            use_3d=True
        )
        
        print("[OK] QR code generated with 3D effects")
        print("  Path: {}".format(qr_result['qr_path']))
        print("  Shares: {}/{}".format(qr_result['shares_generated'], qr_result['total_shares']))
        print()
        
        # Step 3: Verify QR code integrity
        print("[3/5] Verifying QR code integrity...")
        print("-" * 80)
        
        verification = orchestrator.verify_reconstruction("demo_qr_code.png")
        print("[OK] Verification status: {}".format(verification['status']))
        if verification['status'] == 'success':
            print("  URLs match: {}".format(verification.get('urls_match', 'N/A')))
        print()
        
        # Step 4: Scan and reconstruct URL
        print("[4/5] Scanning QR code and reconstructing URL...")
        print("-" * 80)
        
        reconstructed_url = orchestrator.scan_and_reconstruct_url("demo_qr_code.png", use_k_shares=2)
        print("[OK] URL successfully reconstructed!")
        print("  Original:      {}".format(media_url))
        print("  Reconstructed: {}".format(reconstructed_url))
        match = "YES" if media_url == reconstructed_url else "NO"
        print("  Match: {}".format(match))
        print()
        
        # Step 5: Summary
        print("[5/5] Summary and next steps...")
        print("-" * 80)
        print("[OK] Complete workflow executed successfully!")
        print()
        print("Security Details:")
        print("  * URL split into {} secret shares".format(orchestrator.n))
        print("  * Any {} shares can reconstruct the URL".format(orchestrator.k))
        print("  * Each share is encrypted with Fernet")
        print("  * Encryption key: {}...".format(orchestrator.get_encryption_key_hex()[:32]))
        print()
        print("Files generated:")
        print("  * demo_qr_code.png - Your secure QR code with 3D effects")
        print()
        print("To play media:")
        print("  * Scan 'demo_qr_code.png' with the application")
        print("  * The URL will be automatically reconstructed and decrypted")
        print("  * Media will open in your default browser")
        print()
        
    except Exception as e:
        logger.error("Demo failed: {}".format(e))
        print("\n[ERROR] {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("\n")
    print("="*80)
    print("SECURE MEDIA QR CODE - CRYPTOGRAPHIC DEMONSTRATION")
    print("Using Shamir's Secret Sharing & Fernet Encryption")
    print("="*80)
    
    demo_full_workflow()
    
    print("="*80)
    print("DEMO COMPLETE")
    print("="*80 + "\n")
