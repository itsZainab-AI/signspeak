import os
import re

import pytesseract
from PIL import Image, ImageOps

TESSERACT_CMD = os.getenv("TESSERACT_CMD")
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


class OCRError(Exception):
    """Custom exception for OCR processing errors."""


def extract_text(image_path: str) -> str:
    """Extract text from an image file using Tesseract OCR."""
    if not os.path.exists(image_path):
        raise OCRError("Could not read the uploaded image.")
    try:
        with Image.open(image_path) as img:
            img.verify()
    except Exception:
        raise OCRError("Could not read the uploaded image.")
    try:
        with Image.open(image_path) as img:
            processed_img = img.convert("L")
            processed_img = ImageOps.autocontrast(processed_img)
            processed_img = processed_img.resize((processed_img.width * 2, processed_img.height * 2))
            processed_img = processed_img.point(lambda pixel: 0 if pixel < 140 else 255, '1')
            text = pytesseract.image_to_string(processed_img, config="--psm 11").strip()
    except Exception:
        raise OCRError("OCR processing failed for this image.")
    if not text:
        raise OCRError("No readable text was found in this image.")
    cleaned_text = re.sub(r"[^A-Za-z0-9\s.,!?;:'\"()\-_/\\n]", "", text)
    return cleaned_text.strip()

