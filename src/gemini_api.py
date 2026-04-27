from typing import Optional

import streamlit as st

from src.config import DEFAULT_GEMINI_MODEL

try:
    from google import genai
except ImportError:
    genai = None


def is_genai_sdk_available() -> bool:
    return genai is not None


def _get_secret_value(key: str, default=None):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def get_gemini_api_key() -> Optional[str]:
    return _get_secret_value("gemini_api_key")


def get_gemini_model() -> str:
    return _get_secret_value("gemini_model", DEFAULT_GEMINI_MODEL)


def mask_api_key(api_key: Optional[str]) -> str:
    if not api_key:
        return "No disponible"

    if len(api_key) <= 8:
        return "*" * len(api_key)

    return f"{api_key[:4]}...{api_key[-4:]}"


def get_gemini_setup_status() -> dict:
    api_key = get_gemini_api_key()

    return {
        "sdk_available": is_genai_sdk_available(),
        "api_key_present": bool(api_key),
        "masked_api_key": mask_api_key(api_key),
        "model_name": get_gemini_model(),
        "secret_source": ".streamlit/secrets.toml",
        "secret_key_name": "gemini_api_key",
    }


def build_gemini_client():
    if not is_genai_sdk_available():
        raise ImportError(
            "No se encontró el SDK 'google-genai'. Instálalo con 'pip install google-genai'."
        )

    api_key = get_gemini_api_key()

    if not api_key:
        raise ValueError(
            "No se encontró 'gemini_api_key' en '.streamlit/secrets.toml'."
        )

    return genai.Client(api_key=api_key)


def test_gemini_connection(prompt: str = "Responde únicamente con: OK") -> str:
    client = build_gemini_client()
    model_name = get_gemini_model()

    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )

    text_response = getattr(response, "text", None)

    if text_response and text_response.strip():
        return text_response.strip()

    return "La API respondió, pero no se pudo extraer texto simple de la respuesta."


def generate_gemini_response(prompt_text: str) -> str:
    client = build_gemini_client()
    model_name = get_gemini_model()

    response = client.models.generate_content(
        model=model_name,
        contents=prompt_text
    )

    text_response = getattr(response, "text", None)

    if text_response and text_response.strip():
        return text_response.strip()

    return "La API respondió, pero no se pudo extraer texto de la respuesta."