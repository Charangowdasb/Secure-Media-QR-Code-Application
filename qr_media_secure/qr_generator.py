"""
QR Code Generation with 3D Visual Effects

This module generates QR codes with visual enhancements including gradients,
shadows, and depth effects to create a 3D appearance.
"""

import qrcode
from qrcode.image.pure import PyPNGImage
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from typing import Tuple, Optional
from config import (
    QR_VERSION, QR_ERROR_CORRECTION, QR_BOX_SIZE, QR_BORDER,
    QR_FILL_COLOR, QR_BACK_COLOR, GRADIENT_ENABLED, SHADOW_ENABLED,
    DEPTH_EFFECT_ENABLED, SHADOW_OFFSET, SHADOW_COLOR, ENABLE_3D_EFFECTS
)
from utils import get_logger

logger = get_logger(__name__)


class QRCodeGenerator:
    """Generate QR codes with optional 3D visual effects"""
    
    def __init__(self, version: int = QR_VERSION, 
                 error_correction: str = QR_ERROR_CORRECTION,
                 box_size: int = QR_BOX_SIZE,
                 border: int = QR_BORDER):
        """
        Initialize QR code generator
        
        Args:
            version: QR code version (1-40, or None for auto)
            error_correction: Error correction level (L, M, Q, H)
            box_size: Size of each box in pixels
            border: Border size in boxes
        """
        # If version is None, set to 1 and let fit=True handle it
        self.version = version if version is not None else 1
        self.error_correction = self._get_error_correction_level(error_correction)
        self.box_size = box_size
        self.border = border
        logger.info(f"QRCodeGenerator initialized: version={self.version}, error_correction={error_correction}")

    @staticmethod
    def _get_error_correction_level(level: str):
        """Convert string to qrcode error correction level"""
        levels = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H,
        }
        return levels.get(level, qrcode.constants.ERROR_CORRECT_H)

    def generate_basic_qr(self, data: str) -> Image.Image:
        """
        Generate a basic QR code
        
        Args:
            data: Data to encode in QR code
            
        Returns:
            PIL Image of the QR code
        """
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(data)
        qr.make(fit=True)  # Auto-fit to version if needed
        
        img = qr.make_image(fill_color=QR_FILL_COLOR, back_color=QR_BACK_COLOR)
        logger.info(f"Basic QR code generated for data: {data[:50]}... (size={qr.version})")
        return img

    def apply_shadow_effect(self, img: Image.Image, offset: int = SHADOW_OFFSET) -> Image.Image:
        """
        Apply shadow effect to create depth
        
        Args:
            img: PIL Image
            offset: Shadow offset in pixels
            
        Returns:
            Image with shadow effect
        """
        # Create shadow layer
        shadow = Image.new('RGB', img.size, QR_BACK_COLOR)
        shadow_draw = ImageDraw.Draw(shadow)
        
        # Convert image to numpy for easier manipulation
        img_array = np.array(img.convert('RGB'))
        
        # Create shadow by drawing at offset
        for i in range(offset):
            shadow_alpha = int(200 * (1 - i / offset))
            shadow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            shadow_draw_layer = ImageDraw.Draw(shadow_layer)
            
            # Fill shadow with offset
            for y in range(img.height):
                for x in range(img.width):
                    if img_array[y, x, 0] < 128:  # If pixel is dark
                        shadow_draw_layer.point((x + i, y + i), fill=SHADOW_COLOR + (50,))
        
        # Apply blur to shadow
        result = shadow.copy()
        result.paste(img, (0, 0))
        
        logger.debug("Shadow effect applied")
        return result

    def apply_gradient_effect(self, img: Image.Image) -> Image.Image:
        """
        Apply subtle gradient effect
        
        Args:
            img: PIL Image
            
        Returns:
            Image with gradient effect
        """
        width, height = img.size
        gradient = Image.new('RGBA', (width, height))
        gradient_draw = ImageDraw.Draw(gradient)
        
        # Create radial gradient from center
        center_x, center_y = width / 2, height / 2
        max_dist = ((width / 2) ** 2 + (height / 2) ** 2) ** 0.5
        
        for y in range(height):
            for x in range(width):
                dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                alpha = int(30 * (1 - dist / max_dist))
                alpha = max(0, min(255, alpha))
        
        # Create result
        result = img.convert('RGBA')
        result = Image.alpha_composite(result, gradient)
        
        logger.debug("Gradient effect applied")
        return result.convert('RGB')

    def apply_depth_effect(self, img: Image.Image) -> Image.Image:
        """
        Apply depth effect with color grading
        
        Args:
            img: PIL Image
            
        Returns:
            Image with depth effect
        """
        # Convert to PIL Image if needed
        if not isinstance(img, Image.Image):
            img = Image.fromarray(img)
        
        # Apply slight color shift for depth perception
        img_array = np.array(img.convert('RGB')).astype(float)
        
        # Enhance contrast
        img_array = np.clip(img_array * 1.1, 0, 255)
        
        # Create result
        result = Image.fromarray(img_array.astype(np.uint8))
        
        # Apply slight blur to edges for softness
        result = result.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        logger.debug("Depth effect applied")
        return result

    def generate_3d_qr(self, data: str, use_shadow: bool = SHADOW_ENABLED,
                       use_gradient: bool = GRADIENT_ENABLED,
                       use_depth: bool = DEPTH_EFFECT_ENABLED) -> Image.Image:
        """
        Generate QR code with 3D visual effects
        
        Args:
            data: Data to encode
            use_shadow: Apply shadow effect
            use_gradient: Apply gradient effect
            use_depth: Apply depth effect
            
        Returns:
            PIL Image of enhanced QR code
        """
        # Generate basic QR code
        img = self.generate_basic_qr(data)
        img = img.convert('RGB')
        
        if not ENABLE_3D_EFFECTS:
            logger.info("3D effects disabled in config")
            return img
        
        # Apply effects in sequence
        if use_shadow:
            logger.debug("Applying shadow effect...")
            img = self.apply_shadow_effect(img)
        
        if use_gradient:
            logger.debug("Applying gradient effect...")
            img = self.apply_gradient_effect(img)
        
        if use_depth:
            logger.debug("Applying depth effect...")
            img = self.apply_depth_effect(img)
        
        logger.info(f"3D QR code generated with effects: shadow={use_shadow}, gradient={use_gradient}, depth={use_depth}")
        return img

    def save_qr(self, img: Image.Image, filepath: str) -> None:
        """
        Save QR code to file
        
        Args:
            img: PIL Image
            filepath: Output file path
        """
        try:
            img.save(filepath)
            logger.info(f"QR code saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving QR code to {filepath}: {e}")
            raise

    def generate_and_save(self, data: str, filepath: str, 
                         use_3d: bool = ENABLE_3D_EFFECTS) -> None:
        """
        Generate QR code and save to file
        
        Args:
            data: Data to encode
            filepath: Output file path
            use_3d: Enable 3D effects
        """
        if use_3d:
            img = self.generate_3d_qr(data)
        else:
            img = self.generate_basic_qr(data)
        
        self.save_qr(img, filepath)


class QRCodeWithCustomColors:
    """Generate QR code with custom color schemes"""
    
    def __init__(self, fill_color: Tuple[int, int, int] = (0, 0, 0),
                 back_color: Tuple[int, int, int] = (255, 255, 255)):
        """
        Initialize with custom colors
        
        Args:
            fill_color: RGB tuple for QR code color
            back_color: RGB tuple for background color
        """
        self.generator = QRCodeGenerator()
        self.fill_color = fill_color
        self.back_color = back_color
        logger.info(f"QRCodeWithCustomColors initialized with colors: {fill_color}, {back_color}")

    def generate(self, data: str) -> Image.Image:
        """Generate QR with custom colors"""
        qr = qrcode.QRCode(
            version=QR_VERSION,
            error_correction=QRCodeGenerator._get_error_correction_level(QR_ERROR_CORRECTION),
            box_size=QR_BOX_SIZE,
            border=QR_BORDER,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color=self.fill_color, back_color=self.back_color)
        return img.convert('RGB')
