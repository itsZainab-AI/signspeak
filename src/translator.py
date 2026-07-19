import json
import os
import re
import time

import requests
from dotenv import load_dotenv

load_dotenv()

DEPLOY_MODE = os.getenv("DEPLOY_MODE", "local")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


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


def _call_groq(prompt: str) -> str:
    """Call Groq's OpenAI-compatible chat completions API for hosted mode.

    Sends a prompt to Groq's llama-3.1-8b-instant model and returns the clean extracted response text.
    """
    if not GROQ_API_KEY:
        raise TranslationError("GROQ_API_KEY environment variable not set")

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
            },
            headers=headers,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException:
        raise TranslationError("Groq inference request failed")
    except Exception:
        raise TranslationError("Groq inference processing failed")


def _translate_with_mymemory(text: str, target_language: str) -> str:
    """Translate using MyMemory API for hosted mode."""
    if target_language.lower() == "english":
        return text

    iso_code = LANGUAGE_TO_ISO.get(target_language.lower())
    if not iso_code:
        raise TranslationError(f"Unsupported target language: {target_language}")

    email = os.getenv("MYMEMORY_EMAIL", "").strip()
    base_url = "https://api.mymemory.translated.net/get"
    if email:
        request_url = f"{base_url}?q={text}&langpair=en|{iso_code}&de={email}"
    else:
        request_url = f"{base_url}?q={text}&langpair=en|{iso_code}"

    for attempt in range(2):
        try:
            response = requests.get(request_url, timeout=8)
            response.raise_for_status()
            data = response.json()
            if data.get("responseStatus") == 200:
                return data.get("responseData", {}).get("translatedText", "")

            if attempt == 0:
                time.sleep(0.3)
                continue

            raise TranslationError(f"MyMemory API error: {data.get('responseStatus')}")
        except requests.exceptions.ConnectionError:
            if attempt == 0:
                time.sleep(0.3)
                continue
            raise TranslationError("MyMemory API connection failed")
        except requests.exceptions.Timeout:
            if attempt == 0:
                time.sleep(0.3)
                continue
            raise TranslationError("MyMemory API request timed out")
        except requests.exceptions.HTTPError:
            if attempt == 0:
                time.sleep(0.3)
                continue
            raise TranslationError("MyMemory API service returned an error")
        except Exception as e:
            if isinstance(e, TranslationError):
                raise
            if attempt == 0:
                time.sleep(0.3)
                continue
            raise TranslationError("MyMemory API translation failed")

    raise TranslationError("MyMemory API translation failed")




def _translate_with_libretranslate(text: str, target_language: str) -> str:
    if DEPLOY_MODE == "hosted":
        return _translate_with_mymemory(text, target_language)

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
    except requests.exceptions.ConnectionError:
        raise TranslationError("LibreTranslate connection failed")
    except requests.exceptions.Timeout:
        raise TranslationError("LibreTranslate request timed out")
    except requests.exceptions.HTTPError:
        raise TranslationError("LibreTranslate service returned an error")
    except Exception:
        raise TranslationError("LibreTranslate translation failed")


def _call_ollama(prompt: str) -> str:
    """Call the local Ollama API and return the clean extracted response text.

    Parses the JSON reply from Ollama, extracts the ``response`` field,
    and returns it stripped of surrounding whitespace. Never returns
    the raw JSON blob.

    In hosted mode, delegates to Groq inference API instead.
    """
    if DEPLOY_MODE == "hosted":
        return _call_groq(prompt)

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma2:2b", "prompt": prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data["response"].strip()
    except requests.exceptions.RequestException:
        raise TranslationError("Ollama request failed")
    except Exception:
        raise TranslationError("Ollama processing failed")


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
