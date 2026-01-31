"""
QR Code Scanner and Decoder

This module handles scanning QR codes from images and extracting the encoded data.
Supports both static image files and camera input.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Optional, List
from pyzbar import pyzbar
from utils import get_logger

logger = get_logger(__name__)


class QRCodeScanner:
    """Scan and decode QR codes from various sources"""
    
    def __init__(self):
        """Initialize QR code scanner"""
        logger.info("QRCodeScanner initialized")

    def scan_image_file(self, image_path: str) -> Optional[str]:
        """
        Scan QR code from image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            Decoded data from QR code or None if not found
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to read image: {image_path}")
                return None
            
            # Decode QR code
            decoded_objects = pyzbar.decode(image)
            
            if decoded_objects:
                for obj in decoded_objects:
                    data = obj.data.decode('utf-8')
                    logger.info(f"QR code decoded from {image_path}: {data[:50]}...")
                    return data
            else:
                logger.warning(f"No QR code found in {image_path}")
                return None
        
        except Exception as e:
            logger.error(f"Error scanning image {image_path}: {e}")
            raise

    def scan_pil_image(self, pil_image: Image.Image) -> Optional[str]:
        """
        Scan QR code from PIL Image
        
        Args:
            pil_image: PIL Image object
            
        Returns:
            Decoded data or None
        """
        try:
            # Convert PIL image to numpy array
            image_array = np.array(pil_image.convert('RGB'))
            
            # Convert RGB to BGR for OpenCV
            image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            # Decode
            decoded_objects = pyzbar.decode(image_bgr)
            
            if decoded_objects:
                for obj in decoded_objects:
                    data = obj.data.decode('utf-8')
                    logger.info(f"QR code decoded from PIL image: {data[:50]}...")
                    return data
            else:
                logger.warning("No QR code found in PIL image")
                return None
        
        except Exception as e:
            logger.error(f"Error scanning PIL image: {e}")
            raise

    def scan_all_qr_codes(self, image_path: str) -> List[str]:
        """
        Scan all QR codes in an image
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of decoded data from all QR codes
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to read image: {image_path}")
                return []
            
            decoded_objects = pyzbar.decode(image)
            results = []
            
            for obj in decoded_objects:
                data = obj.data.decode('utf-8')
                results.append(data)
                logger.debug(f"Found QR code: {data[:50]}...")
            
            logger.info(f"Scanned {len(results)} QR codes from {image_path}")
            return results
        
        except Exception as e:
            logger.error(f"Error scanning multiple QR codes: {e}")
            raise

    def scan_camera(self, timeout_ms: int = 30000) -> Optional[str]:
        """
        Scan QR code from camera (webcam)
        Requires manual pressing 'q' to quit or timeout
        
        Args:
            timeout_ms: Timeout in milliseconds
            
        Returns:
            Decoded data or None if not found
        """
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                logger.error("Failed to open camera")
                return None
            
            logger.info("Camera started. Press 'q' to quit scanning...")
            start_time = cv2.getTickCount()
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.error("Failed to read from camera")
                    break
                
                # Display frame
                cv2.imshow('QR Code Scanner', frame)
                
                # Try to decode
                decoded_objects = pyzbar.decode(frame)
                if decoded_objects:
                    cap.release()
                    cv2.destroyAllWindows()
                    data = decoded_objects[0].data.decode('utf-8')
                    logger.info(f"QR code scanned from camera: {data[:50]}...")
                    return data
                
                # Check timeout
                elapsed_ms = (cv2.getTickCount() - start_time) / cv2.getTickFrequency() * 1000
                if elapsed_ms > timeout_ms:
                    logger.info("Camera scan timeout")
                    break
                
                # Check for 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("Camera scanning cancelled by user")
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            return None
        
        except Exception as e:
            logger.error(f"Error scanning camera: {e}")
            return None

    def enhance_image_for_scanning(self, image_path: str, output_path: str = None) -> Image.Image:
        """
        Enhance image for better QR code scanning
        Increases contrast and adjusts brightness
        
        Args:
            image_path: Input image path
            output_path: Optional output path to save enhanced image
            
        Returns:
            Enhanced PIL Image
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to read image: {image_path}")
                return None
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Increase contrast using CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Apply thresholding
            _, binary = cv2.threshold(enhanced, 127, 255, cv2.THRESH_BINARY)
            
            # Convert back to BGR
            result = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
            
            # Save if output path provided
            if output_path:
                cv2.imwrite(output_path, result)
                logger.info(f"Enhanced image saved to {output_path}")
            
            # Convert to PIL Image
            result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(result_rgb)
            
            logger.info("Image enhancement completed")
            return pil_image
        
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            raise

    def validate_qr_content(self, data: str) -> bool:
        """
        Validate if scanned data looks like valid QR content
        
        Args:
            data: Scanned data
            
        Returns:
            True if data looks valid
        """
        if not data:
            return False
        
        # Check if data contains expected format (e.g., share:value or encrypted:data)
        if ':' in data or len(data) > 10:
            return True
        
        return False


def create_scanner() -> QRCodeScanner:
    """Factory function to create a QRCodeScanner instance"""
    return QRCodeScanner()
