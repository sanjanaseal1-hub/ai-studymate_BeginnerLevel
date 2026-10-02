"""LLM provider layer.

Routes and services only know the `LLMClient` interface. To switch provider
(OpenAI, Claude, ...) write another subclass and change `get_llm_client`.
"""
import logging
from abc import ABC, abstractmethod

import httpx

from utils import config
from utils.errors import LLMError

logger = logging.getLogger("studymate.llm")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GENERIC_FAIL = "Unable to generate the response right now. Please try again."


class LLMClient(ABC):
    @abstractmethod
    async def generate(self, system_instruction: str, prompt: str) -> str:
        """Return the model's text answer or raise LLMError."""


def map_http_error(status: int, body: str) -> LLMError:
    """Turn a provider HTTP error into a safe, user-friendly LLMError."""
    detail = f"Gemini returned HTTP {status}: {body[:300]}"
    if status in (401, 403) or (status == 400 and "API key" in body):
        return LLMError(500, "The AI service is not configured correctly. Please contact the administrator.", detail)
    if status == 429:
        return LLMError(429, "Too many requests right now. Please wait a moment and try again.", detail)
    if status >= 500:
        return LLMError(503, "The AI service is temporarily unavailable. Please try again later.", detail)
    return LLMError(502, GENERIC_FAIL, detail)


def extract_text(data: dict) -> str:
    """Pull the answer text out of Gemini's JSON, validating its shape."""
    if not isinstance(data, dict):
        raise LLMError(502, GENERIC_FAIL, "Response is not a JSON object")
    block = data.get("promptFeedback", {}).get("blockReason")
    if block:
        raise LLMError(422, "The AI could not process this content. Please try different study material.", f"Blocked: {block}")
    try:
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(part.get("text", "") for part in parts).strip()
    except (KeyError, IndexError, TypeError, AttributeError):
        raise LLMError(502, GENERIC_FAIL, f"Malformed response: {str(data)[:300]}")
    if not text:
        raise LLMError(502, "The AI returned an empty response. Please try again.", "Empty text in response")
    return text


class GeminiClient(LLMClient):
    def __init__(self, api_key: str, model: str, timeout: float = 45.0):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    async def generate(self, system_instruction: str, prompt: str) -> str:
        if not self.api_key:
            raise LLMError(500, "The AI service is not configured correctly. Please contact the administrator.",
                           "GEMINI_API_KEY is missing")
        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 2048},
        }
        # The key goes in a header (not the URL) so it never shows up in logs.
        headers = {"x-goog-api-key": self.api_key}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(GEMINI_URL.format(model=self.model), json=payload, headers=headers)
        except httpx.TimeoutException:
            raise LLMError(504, "The AI took too long to respond. Please try again.", "Gemini request timed out")
        except httpx.RequestError as exc:
            raise LLMError(502, "Could not reach the AI service. Please check the connection and try again.",
                           f"Network error: {type(exc).__name__}")
        if response.status_code != 200:
            raise map_http_error(response.status_code, response.text)
        try:
            data = response.json()
        except ValueError:
            raise LLMError(502, GENERIC_FAIL, "Invalid JSON from Gemini")
        return extract_text(data)


def get_llm_client() -> LLMClient:
    """FastAPI dependency (tests replace it with a fake client)."""
    return GeminiClient(config.get_api_key(), config.get_model())
