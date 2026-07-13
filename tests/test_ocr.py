import os
import tempfile
import pytest
from PIL import Image, ImageDraw, ImageFont

from src.ocr_reader import extract_text, OCRError


def get_test_font(size=40):
    """
    Try to load Arial font, fall back to default if not available.
    """
    font_paths = [
        "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        "/System/Library/Fonts/Arial.ttf",  # macOS
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                pass
    
    # Fall back to default font
    return ImageFont.load_default()


class TestExtractText:
    """Test suite for OCR extract_text function."""

    def test_extract_text_missing_file(self):
        """Test that extract_text raises OCRError for non-existent file.
        
        Asserts that the error message is generic and doesn't contain
        the actual file path.
        """
        fake_path = "nonexistent_image_xyz123.png"
        with pytest.raises(OCRError) as exc_info:
            extract_text(fake_path)
        
        error_msg = str(exc_info.value)
        # Error message should be generic, not containing the file path
        assert "Could not read the uploaded image" in error_msg
        assert fake_path not in error_msg

    def test_extract_text_invalid_image(self):
        """Test that extract_text raises OCRError for invalid image file.
        
        Creates a fake image file by renaming a .txt file to .png,
        then verifies OCRError is raised.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a fake image file (text file with .png extension)
            fake_image_path = os.path.join(tmpdir, "fake_image.png")
            with open(fake_image_path, "w") as f:
                f.write("This is just text, not an image")
            
            with pytest.raises(OCRError) as exc_info:
                extract_text(fake_image_path)
            
            error_msg = str(exc_info.value)
            # Should get generic error, not revealing the file path
            assert "Could not read the uploaded image" in error_msg

    def test_extract_text_plain_high_contrast_text(self):
        """Test extract_text with plain, high-contrast text.
        
        Generates a test image with white background and black text
        (EXIT THIS WAY) at size 40, then verifies the extracted text
        contains both "EXIT" and "WAY".
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = os.path.join(tmpdir, "plain_text.png")
            
            # Create image: white background, black text
            img = Image.new("RGB", (400, 200), color="white")
            draw = ImageDraw.Draw(img)
            font = get_test_font(size=40)
            
            text = "EXIT THIS WAY"
            draw.text((20, 50), text, fill="black", font=font)
            img.save(image_path)
            
            # Extract text
            result = extract_text(image_path)
            
            # Verify key words are present
            assert "EXIT" in result
            assert "WAY" in result

    def test_extract_text_stylized_graphic_signage(self):
        """Test extract_text with styled/graphic signage.
        
        Generates a test image with colored background (yellow)
        and bold black text (TICKETS HERE), specifically testing
        the binarization preprocessing.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = os.path.join(tmpdir, "stylized_text.png")
            
            # Create image: yellow background, black bold text
            img = Image.new("RGB", (400, 200), color="yellow")
            draw = ImageDraw.Draw(img)
            font = get_test_font(size=40)
            
            text = "TICKETS HERE"
            # Draw text multiple times to create bold effect
            draw.text((20, 50), text, fill="black", font=font)
            draw.text((21, 50), text, fill="black", font=font)
            img.save(image_path)
            
            # Extract text
            result = extract_text(image_path)
            
            # Verify key words are present
            assert "TICKETS" in result
            assert "HERE" in result

    def test_extract_text_blank_image_no_text(self):
        """Test extract_text with blank white image (no text).
        
        Creates a blank white image and verifies that OCRError is
        raised with the specific message "No readable text was found
        in this image."
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = os.path.join(tmpdir, "blank_image.png")
            
            # Create blank white image
            img = Image.new("RGB", (400, 200), color="white")
            img.save(image_path)
            
            # Should raise OCRError with specific message
            with pytest.raises(OCRError) as exc_info:
                extract_text(image_path)
            
            error_msg = str(exc_info.value)
            assert error_msg == "No readable text was found in this image."
