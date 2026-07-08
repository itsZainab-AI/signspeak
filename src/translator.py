import requests
from dotenv import load_dotenv
import os

load_dotenv()

TRANSLATION_API_URL = os.getenv("TRANSLATION_API_URL")
TRANSLATION_API_KEY = os.getenv("TRANSLATION_API_KEY")


def translate_text(text: str, target_language: str = "en") -> str:
    if not TRANSLATION_API_URL or not TRANSLATION_API_KEY:
        return f"[Translation API not configured] {text}"
    try:
        response = requests.post(
            TRANSLATION_API_URL,
            json={"text": text, "target": target_language},
            headers={"Authorization": f"Bearer {TRANSLATION_API_KEY}"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("translated_text", text)
    except Exception as e:
        return f"Error: {str(e)}"
