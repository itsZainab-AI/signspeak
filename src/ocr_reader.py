import pytesseract
from PIL import Image
from dotenv import load_dotenv
import os

load_dotenv()

TESSERACT_CMD = os.getenv("TESSERACT_CMD")
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


class OCRError(Exception):
    """Custom exception for OCR processing errors."""
    pass


def extract_text(image_path: str) -> str:
    """Extract text from an image file using Tesseract OCR.

    Args:
        image_path: Path to the image file.

    Returns:
        Extracted text string.

    Raises:
        OCRError: If the file does not exist, is not a valid image, or OCR returns nothing.
    """
    if not os.path.exists(image_path):
        raise OCRError(f"File not found: {image_path}")

    try:
        with Image.open(image_path) as img:
            img.verify()
    except Exception:
        raise OCRError(f"Invalid image file: {image_path}")

    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img).strip()
    except Exception as e:
        raise OCRError(f"OCR failed: {e}")

    if not text:
        raise OCRError(f"OCR returned no text for: {image_path}")

    return text
