import pytest
from src.ocr_reader import extract_text_from_image


def test_extract_text_missing_file():
    result = extract_text_from_image("nonexistent_image.png")
    assert result.startswith("Error:")
