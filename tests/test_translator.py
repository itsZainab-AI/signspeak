import pytest
from src.translator import translate_text


def test_translate_text_placeholder():
    result = translate_text("hello", "es")
    assert isinstance(result, str)


def test_translate_text_no_api_key(monkeypatch):
    monkeypatch.delenv("TRANSLATION_API_URL", raising=False)
    monkeypatch.delenv("TRANSLATION_API_KEY", raising=False)
    result = translate_text("hello", "es")
    assert "[Translation API not configured]" in result
