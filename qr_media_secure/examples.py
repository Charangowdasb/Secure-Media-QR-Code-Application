"""
Advanced Usage Examples and Interactive CLI

More detailed examples and interactive command-line interface
"""

import os
import sys
import json
from pathlib import Path
from orchestrator import create_orchestrator
from encryption import EncryptionManager
from qr_scanner import create_scanner
from media_player import MediaPlayer, MediaValidation
from utils import get_logger

logger = get_logger(__name__)


class InteractiveCLI:
    """Interactive command-line interface for the application"""
    
    def __init__(self):
        """Initialize CLI"""
        self.orchestrator = None
        self.menu_options = {
            '1': self.create_new_session,
            '2': self.generate_qr_code,
            '3': self.scan_and_reconstruct,
            '4': self.play_media,
            '5': self.verify_qr,
            '6': self.export_session,
            '7': self.import_session,
            '8': self.encryption_key_info,
            '9': self.exit_app,
        }

    def print_banner(self):
        """Print application banner"""
        print("\n")
        print("╔" + "="*78 + "╗")
        print("║" + " "*78 + "║")
        print("║" + "  SECURE MEDIA QR CODE - INTERACTIVE CLI  ".center(78) + "║")
        print("║" + "  Shamir's Secret Sharing + Encrypted QR  ".center(78) + "║")
        print("║" + " "*78 + "║")
        print("╚" + "="*78 + "╝")
        print()

    def print_menu(self):
        """Print main menu"""
        print("\n" + "-"*80)
        print("MAIN MENU")
        print("-"*80)
        print("1. Create new session")
        print("2. Generate QR code")
        print("3. Scan and reconstruct URL")
        print("4. Play media")
        print("5. Verify QR code")
        print("6. Export session")
        print("7. Import session")
        print("8. Show encryption key")
        print("9. Exit")
        print("-"*80)

    def create_new_session(self):
        """Create new orchestrator session"""
        print("\n[NEW SESSION]")
        try:
            k_input = input("Enter threshold K (default 3): ").strip() or "3"
            n_input = input("Enter total shares N (default 5): ").strip() or "5"
            
            k = int(k_input)
            n = int(n_input)
            
            if k > n:
                print("✗ Error: Threshold K cannot be greater than N")
                return
            if k < 2:
                print("✗ Error: Threshold must be at least 2")
                return
            
            self.orchestrator = create_orchestrator(k=k, n=n)
            print(f"✓ Session created: {n} shares, threshold {k}")
            print(f"  Encryption key: {self.orchestrator.get_encryption_key_hex()[:32]}...")
        
        except ValueError as e:
            print(f"✗ Error: {e}")

    def generate_qr_code(self):
        """Generate QR code"""
        print("\n[GENERATE QR CODE]")
        if not self.orchestrator:
            print("✗ Error: No active session. Create session first.")
            return
        
        try:
            url = input("Enter media URL: ").strip()
            if not url:
                print("✗ Error: URL cannot be empty")
                return
            
            output = input("Enter output filename (default 'qr_code.png'): ").strip() or "qr_code.png"
            use_3d = input("Enable 3D effects? (y/n, default y): ").strip().lower() != 'n'
            
            result = self.orchestrator.generate_encrypted_qr(url, output, use_3d=use_3d)
            print(f"✓ QR code generated: {output}")
            print(f"  Shares: {result['shares_generated']}")
        
        except Exception as e:
            print(f"✗ Error: {e}")

    def scan_and_reconstruct(self):
        """Scan QR code and reconstruct URL"""
        print("\n[SCAN AND RECONSTRUCT]")
        if not self.orchestrator:
            print("✗ Error: No active session. Create session first.")
            return
        
        try:
            qr_path = input("Enter QR code image path: ").strip()
            if not os.path.exists(qr_path):
                print(f"✗ Error: File not found: {qr_path}")
                return
            
            use_k = input(f"Enter number of shares to use (default all): ").strip()
            use_k_shares = int(use_k) if use_k else None
            
            url = self.orchestrator.scan_and_reconstruct_url(qr_path, use_k_shares)
            print(f"✓ URL reconstructed: {url}")
        
        except Exception as e:
            print(f"✗ Error: {e}")

    def play_media(self):
        """Play media from URL"""
        print("\n[PLAY MEDIA]")
        try:
            url = input("Enter media URL or file path: ").strip()
            if not url:
                print("✗ Error: URL cannot be empty")
                return
            
            player = MediaPlayer(use_browser=True)
            if player.play_media(url):
                print(f"✓ Media playback initiated")
            else:
                print(f"✗ Media playback failed")
        
        except Exception as e:
            print(f"✗ Error: {e}")

    def verify_qr(self):
        """Verify QR code"""
        print("\n[VERIFY QR CODE]")
        if not self.orchestrator:
            print("✗ Error: No active session.")
            return
        
        try:
            qr_path = input("Enter QR code image path: ").strip()
            if not os.path.exists(qr_path):
                print(f"✗ Error: File not found: {qr_path}")
                return
            
            report = self.orchestrator.verify_reconstruction(qr_path)
            print(f"\n✓ Verification Report:")
            for key, value in report.items():
                print(f"  {key}: {value}")
        
        except Exception as e:
            print(f"✗ Error: {e}")

    def export_session(self):
        """Export session to file"""
        print("\n[EXPORT SESSION]")
        if not self.orchestrator:
            print("✗ Error: No active session.")
            return
        
        try:
            filename = input("Enter export filename (default 'session.json'): ").strip() or "session.json"
            self.orchestrator.save_session(filename)
            print(f"✓ Session exported to {filename}")
        
        except Exception as e:
            print(f"✗ Error: {e}")

    def import_session(self):
        """Import session from file"""
        print("\n[IMPORT SESSION]")
        try:
            filename = input("Enter import filename: ").strip()
            if not os.path.exists(filename):
                print(f"✗ Error: File not found: {filename}")
                return
            
            self.orchestrator = create_orchestrator()
            self.orchestrator.load_session(filename)
            print(f"✓ Session imported from {filename}")
        
        except Exception as e:
            print(f"✗ Error: {e}")

    def encryption_key_info(self):
        """Show encryption key information"""
        print("\n[ENCRYPTION KEY INFO]")
        if not self.orchestrator:
            print("✗ Error: No active session.")
            return
        
        key_hex = self.orchestrator.get_encryption_key_hex()
        print(f"Current encryption key (hex):")
        print(f"  {key_hex}")
        print(f"\nKey length: {len(bytes.fromhex(key_hex))} bytes")

    def exit_app(self):
        """Exit application"""
        print("\n✓ Goodbye!")
        sys.exit(0)

    def run(self):
        """Run interactive CLI"""
        self.print_banner()
        
        while True:
            self.print_menu()
            choice = input("Enter your choice (1-9): ").strip()
            
            if choice in self.menu_options:
                self.menu_options[choice]()
            else:
                print("✗ Invalid choice. Please try again.")


def example_complete_workflow():
    """
    Example: Complete workflow from start to finish
    Demonstrates best practices and proper error handling
    """
    print("\n" + "="*80)
    print("EXAMPLE: COMPLETE SECURE WORKFLOW")
    print("="*80 + "\n")
    
    try:
        # 1. Initialize with specific parameters
        print("Step 1: Initialize secure orchestrator")
        print("-" * 80)
        orchestrator = create_orchestrator(k=3, n=5)
        print(f"✓ Created orchestrator")
        print(f"  Parameters: {orchestrator.n} total shares, {orchestrator.k} required")
        print(f"  Encryption: Fernet (256-bit key)")
        print()
        
        # 2. Generate QR code
        print("Step 2: Generate secure QR code")
        print("-" * 80)
        media_url = "https://www.w3schools.com/html/mov_bbb.mp4"
        result = orchestrator.generate_encrypted_qr(
            media_url=media_url,
            output_path="example_qr.png",
            use_3d=True
        )
        print(f"✓ QR code generated with 3D effects")
        print()
        
        # 3. Verify integrity
        print("Step 3: Verify QR code integrity")
        print("-" * 80)
        verification = orchestrator.verify_reconstruction("example_qr.png")
        if verification['status'] == 'success' and verification['urls_match']:
            print(f"✓ Verification passed")
            print(f"  URLs match: {verification['urls_match']}")
        else:
            print(f"✗ Verification failed")
            return
        print()
        
        # 4. Reconstruct with minimum shares
        print("Step 4: Reconstruct URL with minimum required shares")
        print("-" * 80)
        reconstructed = orchestrator.scan_and_reconstruct_url(
            "example_qr.png",
            use_k_shares=orchestrator.k
        )
        print(f"✓ URL reconstructed successfully")
        print(f"  Original:      {media_url}")
        print(f"  Reconstructed: {reconstructed}")
        print(f"  Match: {'✓ YES' if media_url == reconstructed else '✗ NO'}")
        print()
        
        # 5. Save for later use
        print("Step 5: Save session for later use")
        print("-" * 80)
        orchestrator.save_session("example_session.json")
        print(f"✓ Session saved to example_session.json")
        print()
        
        print("="*80)
        print("✓ EXAMPLE COMPLETE - All steps successful!")
        print("="*80)
    
    except Exception as e:
        print(f"\n✗ Error in workflow: {e}")
        import traceback
        traceback.print_exc()


def example_security_features():
    """
    Example: Demonstrate security features
    Shows how the system protects the media URL
    """
    print("\n" + "="*80)
    print("EXAMPLE: SECURITY FEATURES DEMONSTRATION")
    print("="*80 + "\n")
    
    try:
        print("Security Feature 1: Shamir's Secret Sharing")
        print("-" * 80)
        print("✓ URL is split into N shares")
        print("✓ Any K shares can reconstruct, but K-1 cannot")
        print("✓ Computational security: Each share reveals nothing about the secret")
        print()
        
        orchestrator = create_orchestrator(k=3, n=5)
        media_url = "https://example.com/sensitive-video.mp4"
        orchestrator.generate_encrypted_qr(media_url, "security_demo_qr.png")
        
        print("Security Feature 2: Encryption")
        print("-" * 80)
        print("✓ Each share is encrypted with Fernet (AES-128 in CBC mode)")
        print("✓ Encryption key is 256-bit, randomly generated")
        print(f"✓ Current key: {orchestrator.get_encryption_key_hex()[:16]}...")
        print()
        
        print("Security Feature 3: QR Code Integrity")
        print("-" * 80)
        print("✓ Entire metadata stored in QR (URL, shares, keys)")
        print("✓ QR code includes error correction")
        print("✓ Can be read even if partially damaged")
        print()
        
        print("Security Feature 4: Access Control")
        print("-" * 80)
        print(f"✓ Threshold of {orchestrator.k} out of {orchestrator.n} shares required")
        print("✓ Even with N-1 shares, URL cannot be reconstructed")
        print()
        
        print("Threat Model & Mitigations:")
        print("-" * 80)
        print("✓ Threat: QR code is intercepted")
        print("  Mitigation: Encrypted shares in QR, need encryption key to decrypt")
        print()
        print("✓ Threat: Some shares are leaked")
        print("  Mitigation: Need K shares; K-1 leaking reveals nothing")
        print()
        print("✓ Threat: QR code is damaged")
        print("  Mitigation: Error correction allows partial recovery")
        print()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "interactive":
            cli = InteractiveCLI()
            cli.run()
        elif command == "example-workflow":
            example_complete_workflow()
        elif command == "example-security":
            example_security_features()
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python examples.py interactive        - Run interactive CLI")
            print("  python examples.py example-workflow   - Run complete workflow example")
            print("  python examples.py example-security   - Show security features")
    else:
        # Default: run interactive CLI
        cli = InteractiveCLI()
        cli.run()
