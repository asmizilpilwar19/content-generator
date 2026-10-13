"""
Thin wrapper around the Google Gemini API.

Keeps all SDK configuration and error handling in one place so app.py
only ever deals with plain strings (prompt in, generated text out).
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

load_dotenv()

MODEL_NAME = "gemini-flash-lite-latest"

_client = None


class GeminiConfigError(Exception):
    """Raised when the Gemini API key is missing or invalid."""


class GeminiGenerationError(Exception):
    """Raised when content generation fails or returns nothing usable."""


def is_configured() -> bool:
    """Check whether an API key is available without raising."""
    return bool(os.getenv("GEMINI_API_KEY"))


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise GeminiConfigError(
                "GEMINI_API_KEY is not set. Add it to a .env file before generating content."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def generate_content(prompt: str) -> str:
    """Send a prompt to Gemini and return the generated text.

    Raises GeminiConfigError if the API key is missing, or
    GeminiGenerationError if the request fails or returns no text.
    """
    client = _get_client()

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
    except APIError as exc:
        raise GeminiGenerationError(f"Gemini API request failed: {exc}") from exc
    except Exception as exc:
        raise GeminiGenerationError(f"Unexpected error while contacting Gemini: {exc}") from exc

    text = (response.text or "").strip()
    if not text:
        raise GeminiGenerationError("Gemini returned an empty response.")

    return text
