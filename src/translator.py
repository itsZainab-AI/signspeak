import json
import re

import requests
from dotenv import load_dotenv

load_dotenv()


class TranslationError(Exception):
    pass


LANGUAGE_TO_ISO = {
    "arabic": "ar",
    "korean": "ko",
    "chinese": "zh",
    "japanese": "ja",
    "spanish": "es",
    "french": "fr",
    "hindi": "hi",
    "german": "de",
    "portuguese": "pt",
    "english": "en",
}


def _translate_with_libretranslate(text: str, target_language: str) -> str:
    if target_language.lower() == "english":
        return text

    iso_code = LANGUAGE_TO_ISO.get(target_language.lower())
    if not iso_code:
        raise TranslationError(f"Unsupported target language: {target_language}")

    try:
        response = requests.post(
            "http://localhost:5000/translate",
            json={"q": text, "source": "en", "target": iso_code, "format": "text"},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()["translatedText"]
    except requests.exceptions.ConnectionError as e:
        raise TranslationError(f"LibreTranslate connection failed: {str(e)}") from e
    except requests.exceptions.Timeout as e:
        raise TranslationError(f"LibreTranslate request timed out: {str(e)}") from e
    except Exception as e:
        raise TranslationError(f"LibreTranslate translation failed: {str(e)}") from e


def _call_ollama(prompt: str) -> str:
    """Call the local Ollama API and return the clean extracted response text.

    Parses the JSON reply from Ollama, extracts the ``response`` field,
    and returns it stripped of surrounding whitespace. Never returns
    the raw JSON blob.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma2:2b", "prompt": prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data["response"].strip()
    except Exception as e:
        raise TranslationError(f"Ollama request failed: {str(e)}") from e


def _extract_json_object(text: str) -> dict | None:
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except (ValueError, TypeError):
            return None
    return None


def translate_and_explain(text: str, target_language: str) -> dict:
    # Optimization: skip translation if target is English
    if target_language.lower() == "english":
        translation = text
    else:
        translation = _translate_with_libretranslate(text, target_language)

    explanation_prompt = (
        "Provide a one-sentence explanation of the following English text: "
        f"{text!r}"
    )

    explanation = _call_ollama(explanation_prompt)

    return {
        "translation": translation,
        "explanation": explanation,
    }
