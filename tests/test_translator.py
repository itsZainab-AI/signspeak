import pytest
import json
from unittest.mock import patch, MagicMock

from src.translator import (
    translate_and_explain,
    _call_ollama,
    _translate_with_libretranslate,
    TranslationError,
)


class TestTranslateAndExplain:
    """Test suite for translate_and_explain function."""

    def test_translate_and_explain_successful_response(self):
        """Test translate_and_explain returns dict with translation and explanation keys.
        
        Mocks both _translate_with_libretranslate and _call_ollama with successful
        responses and verifies the returned dict contains the expected keys.
        """
        with patch("src.translator._translate_with_libretranslate") as mock_translate, \
             patch("src.translator._call_ollama") as mock_ollama:
            
            mock_translate.return_value = "Hola, salida"
            mock_ollama.return_value = "This is an emergency exit sign."
            
            result = translate_and_explain("EXIT", "spanish")
            
            assert isinstance(result, dict)
            assert "translation" in result
            assert "explanation" in result
            assert result["translation"] == "Hola, salida"
            assert result["explanation"] == "This is an emergency exit sign."

    def test_translate_and_explain_libretranslate_connection_error(self):
        """Test translate_and_explain raises TranslationError on LibreTranslate failure.
        
        Mocks _translate_with_libretranslate to raise TranslationError simulating
        a connection error, and verifies the error propagates.
        """
        with patch("src.translator._translate_with_libretranslate") as mock_translate:
            mock_translate.side_effect = TranslationError(
                "LibreTranslate connection failed: Connection refused"
            )
            
            with pytest.raises(TranslationError) as exc_info:
                translate_and_explain("EXIT", "spanish")
            
            assert "LibreTranslate connection failed" in str(exc_info.value)

    def test_translate_and_explain_ollama_malformed_response(self):
        """Test translate_and_explain handles malformed _call_ollama response gracefully.
        
        Mocks _call_ollama to return an unexpected format (e.g., non-string or
        malformed object), and verifies the function still returns a usable dict
        without crashing.
        """
        with patch("src.translator._translate_with_libretranslate") as mock_translate, \
             patch("src.translator._call_ollama") as mock_ollama:
            
            mock_translate.return_value = "Salida"
            # Return something unexpected but not crashing
            mock_ollama.return_value = ""  # Empty string response
            
            result = translate_and_explain("EXIT", "spanish")
            
            # Should still return a dict with both keys
            assert isinstance(result, dict)
            assert "translation" in result
            assert "explanation" in result
            # Explanation may be empty or unexpected, but structure is intact
            assert result["translation"] == "Salida"

    def test_translate_and_explain_english_target_skips_translation(self):
        """Test that when target_language is 'English', returns original text unchanged.
        
        Verifies that _translate_with_libretranslate is NOT called when the
        target language is English, and the original text is returned as translation.
        """
        with patch("src.translator._translate_with_libretranslate") as mock_translate, \
             patch("src.translator._call_ollama") as mock_ollama:
            
            mock_ollama.return_value = "An exit sign."
            
            result = translate_and_explain("EXIT", "English")
            
            # _translate_with_libretranslate should NOT have been called
            mock_translate.assert_not_called()
            
            # Translation should be the original text
            assert result["translation"] == "EXIT"
            assert result["explanation"] == "An exit sign."

    def test_translate_and_explain_english_target_lowercase(self):
        """Test that 'english' (lowercase) is also recognized as no-translate target."""
        with patch("src.translator._translate_with_libretranslate") as mock_translate, \
             patch("src.translator._call_ollama") as mock_ollama:
            
            mock_ollama.return_value = "An exit sign."
            
            result = translate_and_explain("EXIT", "english")
            
            # _translate_with_libretranslate should NOT have been called
            mock_translate.assert_not_called()
            assert result["translation"] == "EXIT"


class TestCallOllama:
    """Test suite for _call_ollama function."""

    def test_call_ollama_extracts_response_field(self):
        """Test that _call_ollama extracts and returns the 'response' field from JSON.
        
        Mocks requests.post to return a full Ollama JSON reply and verifies
        that only the cleaned response text is returned, not the raw JSON.
        """
        mock_response_data = {
            "model": "gemma2:2b",
            "created_at": "2024-01-15T10:00:00Z",
            "response": "This is a sign for an exit.",
            "done": True,
            "context": [1, 2, 3],
            "total_duration": 1000000,
        }
        
        with patch("src.translator.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            result = _call_ollama("What is this image?")
            
            # Should return only the response field, not JSON blob
            assert result == "This is a sign for an exit."
            assert isinstance(result, str)
            assert "{" not in result  # No JSON in result

    def test_call_ollama_strips_whitespace(self):
        """Test that _call_ollama strips surrounding whitespace from response."""
        mock_response_data = {
            "response": "  This is a sign.  \n\t",
            "done": True,
        }
        
        with patch("src.translator.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            result = _call_ollama("What is this?")
            
            assert result == "This is a sign."

    def test_call_ollama_raises_on_connection_error(self):
        """Test that _call_ollama raises TranslationError on connection failure."""
        with patch("src.translator.requests.post") as mock_post:
            import requests
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
            
            with pytest.raises(TranslationError) as exc_info:
                _call_ollama("What is this?")
            
            assert "Ollama request failed" in str(exc_info.value)

    def test_call_ollama_raises_on_missing_response_field(self):
        """Test that _call_ollama raises TranslationError if response field is missing."""
        mock_response_data = {
            "model": "gemma2:2b",
            "done": True,
            # Missing "response" field
        }
        
        with patch("src.translator.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            with pytest.raises(TranslationError):
                _call_ollama("What is this?")


class TestTranslateWithLibreTranslate:
    """Test suite for _translate_with_libretranslate function."""

    def test_translate_with_libretranslate_english_returns_unchanged(self):
        """Test that English target language returns text unchanged."""
        result = _translate_with_libretranslate("EXIT", "english")
        assert result == "EXIT"
        
        result = _translate_with_libretranslate("EXIT", "English")
        assert result == "EXIT"

    def test_translate_with_libretranslate_spanish(self):
        """Test successful translation to Spanish."""
        mock_response_data = {"translatedText": "Salida"}
        
        with patch("src.translator.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            result = _translate_with_libretranslate("EXIT", "spanish")
            
            assert result == "Salida"
            # Verify correct API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "localhost:5000/translate" in call_args[0][0]
            assert call_args[1]["json"]["target"] == "es"

    def test_translate_with_libretranslate_unsupported_language(self):
        """Test that unsupported language raises TranslationError."""
        with pytest.raises(TranslationError) as exc_info:
            _translate_with_libretranslate("EXIT", "klingon")
        
        assert "Unsupported target language" in str(exc_info.value)

    def test_translate_with_libretranslate_connection_error(self):
        """Test that connection errors raise TranslationError."""
        with patch("src.translator.requests.post") as mock_post:
            import requests
            mock_post.side_effect = requests.exceptions.ConnectionError("refused")
            
            with pytest.raises(TranslationError) as exc_info:
                _translate_with_libretranslate("EXIT", "spanish")
            
            assert "LibreTranslate connection failed" in str(exc_info.value)

    def test_translate_with_libretranslate_timeout_error(self):
        """Test that timeout errors raise TranslationError."""
        with patch("src.translator.requests.post") as mock_post:
            import requests
            mock_post.side_effect = requests.exceptions.Timeout("request timed out")
            
            with pytest.raises(TranslationError) as exc_info:
                _translate_with_libretranslate("EXIT", "spanish")
            
            assert "LibreTranslate request timed out" in str(exc_info.value)
