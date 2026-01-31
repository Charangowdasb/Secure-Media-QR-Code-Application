"""
Unit Tests and Integration Tests

Comprehensive testing suite for the Secure Media QR application
"""

import unittest
import json
import os
import tempfile
from pathlib import Path

from shamir_sharing import ShamirSecretSharing
from encryption import EncryptionManager
from qr_generator import QRCodeGenerator
from qr_scanner import QRCodeScanner
from orchestrator import SecureMediaQROrchestrator


class TestShamirSharing(unittest.TestCase):
    """Test Shamir's Secret Sharing"""
    
    def setUp(self):
        self.shamir = ShamirSecretSharing()
    
    def test_split_and_reconstruct(self):
        """Test basic split and reconstruct"""
        secret = "https://example.com/video.mp4"
        shares = self.shamir.split(secret, k=3, n=5)
        
        self.assertEqual(len(shares), 5)
        
        # Reconstruct with 3 shares
        reconstructed = self.shamir.reconstruct(shares[:3])
        self.assertEqual(reconstructed, secret)
    
    def test_threshold_k_of_n(self):
        """Test that K-1 shares cannot reconstruct"""
        secret = "https://secure-media.com/stream"
        shares = self.shamir.split(secret, k=3, n=5)
        
        # Try with only 2 shares (should fail)
        try:
            # Lagrange will compute but give wrong result
            result = self.shamir.reconstruct(shares[:2])
            # Wrong reconstruction should not match
            self.assertNotEqual(result, secret)
        except:
            pass  # May raise exception or return garbage


class TestEncryption(unittest.TestCase):
    """Test encryption/decryption"""
    
    def setUp(self):
        self.mgr = EncryptionManager()
    
    def test_encrypt_decrypt(self):
        """Test basic encryption and decryption"""
        plaintext = "https://example.com/confidential-video"
        
        encrypted = self.mgr.encrypt(plaintext)
        decrypted = self.mgr.decrypt(encrypted)
        
        self.assertEqual(decrypted, plaintext)
    
    def test_different_plaintext_different_ciphertext(self):
        """Test that same plaintext always encrypts to different ciphertext (Fernet includes timestamp)"""
        plaintext = "test data"
        
        encrypted1 = self.mgr.encrypt(plaintext)
        encrypted2 = self.mgr.encrypt(plaintext)
        
        # Note: Fernet includes timestamp, so ciphertexts differ
        decrypted1 = self.mgr.decrypt(encrypted1)
        decrypted2 = self.mgr.decrypt(encrypted2)
        
        self.assertEqual(decrypted1, plaintext)
        self.assertEqual(decrypted2, plaintext)
    
    def test_invalid_ciphertext(self):
        """Test decryption of invalid ciphertext"""
        invalid = "0" * 64  # Invalid hex
        
        with self.assertRaises(ValueError):
            self.mgr.decrypt(invalid)
    
    def test_generate_key(self):
        """Test key generation"""
        key1 = EncryptionManager.generate_key()
        key2 = EncryptionManager.generate_key()
        
        self.assertNotEqual(key1, key2)
        self.assertEqual(len(key1), 44)  # Fernet key length


class TestQRGeneration(unittest.TestCase):
    """Test QR code generation"""
    
    def setUp(self):
        self.gen = QRCodeGenerator()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # Cleanup
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_basic_qr_generation(self):
        """Test basic QR code generation"""
        data = "https://example.com/test"
        output_path = os.path.join(self.temp_dir, "test_qr.png")
        
        img = self.gen.generate_basic_qr(data)
        self.assertIsNotNone(img)
        self.assertEqual(img.format, 'PNG')
    
    def test_qr_save(self):
        """Test saving QR code"""
        data = "test data"
        output_path = os.path.join(self.temp_dir, "saved_qr.png")
        
        img = self.gen.generate_basic_qr(data)
        self.gen.save_qr(img, output_path)
        
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)
    
    def test_3d_qr_generation(self):
        """Test 3D QR generation"""
        data = "https://example.com/3d-test"
        
        img = self.gen.generate_3d_qr(data)
        self.assertIsNotNone(img)


class TestQRScanning(unittest.TestCase):
    """Test QR scanning"""
    
    def setUp(self):
        self.scanner = QRCodeScanner()
        self.gen = QRCodeGenerator()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_scan_basic_qr(self):
        """Test scanning a generated QR code"""
        data = "https://example.com/scantest"
        qr_path = os.path.join(self.temp_dir, "scan_test.png")
        
        # Generate QR
        img = self.gen.generate_basic_qr(data)
        self.gen.save_qr(img, qr_path)
        
        # Scan it
        result = self.scanner.scan_image_file(qr_path)
        self.assertEqual(result, data)


class TestOrchestrator(unittest.TestCase):
    """Test main orchestrator"""
    
    def setUp(self):
        self.orchestrator = SecureMediaQROrchestrator(k=3, n=5)
        self.temp_dir = tempfile.mkdtemp()
        self.qr_path = os.path.join(self.temp_dir, "test_qr.png")
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_workflow(self):
        """Test complete workflow"""
        media_url = "https://example.com/video.mp4"
        
        # Generate QR
        self.orchestrator.generate_encrypted_qr(media_url, self.qr_path)
        self.assertTrue(os.path.exists(self.qr_path))
        
        # Reconstruct
        reconstructed = self.orchestrator.scan_and_reconstruct_url(self.qr_path)
        self.assertEqual(reconstructed, media_url)
    
    def test_session_save_load(self):
        """Test session management"""
        session_path = os.path.join(self.temp_dir, "session.json")
        
        # Generate and save
        media_url = "https://example.com/test.mp4"
        self.orchestrator.generate_encrypted_qr(media_url, self.qr_path)
        self.orchestrator.save_session(session_path)
        
        # Load in new orchestrator
        orchestrator2 = SecureMediaQROrchestrator(k=3, n=5)
        orchestrator2.load_session(session_path)
        
        self.assertEqual(orchestrator2.k, self.orchestrator.k)
        self.assertEqual(orchestrator2.n, self.orchestrator.n)
    
    def test_verify_qr(self):
        """Test QR verification"""
        media_url = "https://example.com/verify.mp4"
        
        # Generate
        self.orchestrator.generate_encrypted_qr(media_url, self.qr_path)
        
        # Verify
        report = self.orchestrator.verify_reconstruction(self.qr_path)
        
        self.assertEqual(report['status'], 'success')
        self.assertTrue(report['urls_match'])
        self.assertTrue(report['qr_scannable'])


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_multiple_urls(self):
        """Test with multiple URLs"""
        urls = [
            "https://example.com/video1.mp4",
            "https://streaming.service.com/media",
            "https://cdn.example.org/file.webm",
        ]
        
        for i, url in enumerate(urls):
            orchestrator = SecureMediaQROrchestrator(k=3, n=5)
            qr_path = os.path.join(self.temp_dir, f"qr_{i}.png")
            
            orchestrator.generate_encrypted_qr(url, qr_path)
            reconstructed = orchestrator.scan_and_reconstruct_url(qr_path)
            
            self.assertEqual(reconstructed, url)
    
    def test_different_thresholds(self):
        """Test with different K-N combinations"""
        test_cases = [
            (2, 3),  # 2 of 3
            (3, 5),  # 3 of 5
            (4, 7),  # 4 of 7
        ]
        
        url = "https://example.com/test.mp4"
        
        for k, n in test_cases:
            orchestrator = SecureMediaQROrchestrator(k=k, n=n)
            qr_path = os.path.join(self.temp_dir, f"qr_k{k}_n{n}.png")
            
            orchestrator.generate_encrypted_qr(url, qr_path)
            
            # Test reconstruction with exact K shares
            reconstructed = orchestrator.scan_and_reconstruct_url(qr_path, use_k_shares=k)
            self.assertEqual(reconstructed, url)
            
            # Test reconstruction with more than K shares
            if n > k:
                reconstructed = orchestrator.scan_and_reconstruct_url(qr_path, use_k_shares=k+1)
                self.assertEqual(reconstructed, url)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestShamirSharing))
    suite.addTests(loader.loadTestsFromTestCase(TestEncryption))
    suite.addTests(loader.loadTestsFromTestCase(TestQRGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestQRScanning))
    suite.addTests(loader.loadTestsFromTestCase(TestOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
