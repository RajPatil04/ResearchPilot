"""Gemma 4 Client integration using the official Google Gen AI Python SDK.

Strictly accesses Gemma 4 models (e.g. gemma-4-26b-a4b-it) without substituting
other model families (e.g., Gemini 2.5, GPT, Claude).
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional, Tuple

from google import genai
from google.genai import types
from google.genai import errors


DEFAULT_GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it")
AVAILABLE_GEMMA_MODELS = [
    "gemma-4-26b-a4b-it",
    "gemma-4-31b-it"
]


class GemmaClientError(Exception):
    """Custom exception for Gemma API interaction failures."""
    pass


class GemmaClient:
    """Wrapper around Google Gen AI SDK dedicated specifically to Gemma 4."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        enable_thinking: bool = False
    ):
        # Resolve API key from argument, then environment variable
        resolved_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
        if not resolved_key:
            raise GemmaClientError(
                "No API key provided. Please supply your Google AI Studio API key in the sidebar "
                "or set the GEMINI_API_KEY environment variable."
            )

        self._api_key = resolved_key
        self.model = (model or DEFAULT_GEMMA_MODEL).strip()
        self.enable_thinking = enable_thinking

        try:
            self._client = genai.Client(api_key=self._api_key)
        except Exception as exc:
            raise GemmaClientError(f"Failed to initialize Google Gen AI Client: {self._sanitize_error(str(exc))}")

    @property
    def masked_key(self) -> str:
        """Returns a securely masked preview of the active API key."""
        if not self._api_key:
            return "Not set"
        if len(self._api_key) <= 8:
            return "••••••••"
        return f"{self._api_key[:4]}••••••••{self._api_key[-4:]}"

    def _sanitize_error(self, error_message: str) -> str:
        """Strips any accidental occurrences of API keys from error outputs."""
        if self._api_key and self._api_key in error_message:
            return error_message.replace(self._api_key, "[REDACTED_API_KEY]")
        # Regex catch for generic AI Studio keys (AIza...)
        return re.sub(r"AIza[0-9A-Za-z-_]{35}", "[REDACTED_API_KEY]", error_message)

    def _build_config(
        self,
        system_instruction: Optional[str] = None,
        thinking: Optional[bool] = None,
        tools: Optional[List[Any]] = None
    ) -> types.GenerateContentConfig:
        """Constructs GenerateContentConfig honoring thinking parameters and system instruction."""
        use_thinking = self.enable_thinking if thinking is None else thinking
        config_kwargs: Dict[str, Any] = {}

        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction

        if use_thinking:
            # Gemma 4 thinking configuration
            config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_level="high")
        else:
            config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_level="minimal")

        if tools:
            config_kwargs["tools"] = tools

        return types.GenerateContentConfig(**config_kwargs)

    def test_connection(self) -> Tuple[bool, str]:
        """Pings the Gemma 4 model to verify API credentials and model accessibility."""
        test_prompt = "Hello. Confirm readiness in one short sentence."
        try:
            # Fast ping without thinking overhead
            config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="minimal")
            )
            response = self._client.models.generate_content(
                model=self.model,
                contents=[test_prompt],
                config=config
            )
            text = (response.text or "").strip()
            if text:
                return True, f"Successfully connected to {self.model} via Google Gen AI API."
            return True, f"Connected to {self.model} (empty test response received)."
        except errors.APIError as exc:
            msg = self._sanitize_error(str(exc))
            return False, f"Gemma API Error: {msg}"
        except Exception as exc:
            msg = self._sanitize_error(str(exc))
            return False, f"Connection Failed: {msg}"

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        thinking: Optional[bool] = None
    ) -> str:
        """Generates text from Gemma 4. Never substitutes another model family."""
        try:
            config = self._build_config(system_instruction=system_instruction, thinking=thinking)
            response = self._client.models.generate_content(
                model=self.model,
                contents=[prompt],
                config=config
            )
            if not response or not response.text:
                raise GemmaClientError(
                    f"Model {self.model} completed without returning text. Check prompt length or content filters."
                )
            return response.text
        except errors.APIError as exc:
            sanitized = self._sanitize_error(str(exc))
            # Check for unsupported thinking
            if "thinking" in sanitized.lower() and (self.enable_thinking or thinking):
                # Retry once without thinking
                try:
                    retry_config = types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        thinking_config=types.ThinkingConfig(thinking_level="minimal")
                    )
                    retry_resp = self._client.models.generate_content(
                        model=self.model,
                        contents=[prompt],
                        config=retry_config
                    )
                    if retry_resp and retry_resp.text:
                        return f"> [Notice: Thinking mode not supported on {self.model}; executed in standard mode.]\n\n{retry_resp.text}"
                except Exception:
                    pass
            raise GemmaClientError(f"Gemma 4 API Error: {sanitized}")
        except Exception as exc:
            sanitized = self._sanitize_error(str(exc))
            raise GemmaClientError(f"Unexpected failure invoking {self.model}: {sanitized}")

    def generate_with_image(
        self,
        prompt: str,
        image_bytes: bytes,
        mime_type: str = "image/png",
        system_instruction: Optional[str] = None,
        thinking: Optional[bool] = None
    ) -> str:
        """Sends visual content (e.g. rendered PDF page or figure) to Gemma 4."""
        if not image_bytes:
            raise GemmaClientError("No image bytes provided for visual analysis.")

        try:
            part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            contents = [prompt, part]
            config = self._build_config(system_instruction=system_instruction, thinking=thinking)

            response = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config
            )
            if not response or not response.text:
                raise GemmaClientError(
                    f"Model {self.model} returned no text for this image. Verify that the image is readable."
                )
            return response.text
        except errors.APIError as exc:
            sanitized = self._sanitize_error(str(exc))
            if "image" in sanitized.lower() or "multimodal" in sanitized.lower():
                raise GemmaClientError(
                    f"Multimodal input error on {self.model}: {sanitized}. "
                    "Ensure your configured Gemma model and API key tier support image inputs."
                )
            raise GemmaClientError(f"Gemma 4 API Error: {sanitized}")
        except Exception as exc:
            sanitized = self._sanitize_error(str(exc))
            raise GemmaClientError(f"Visual analysis failed on {self.model}: {sanitized}")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_instruction: Optional[str] = None,
        thinking: Optional[bool] = None,
        paper_context: Optional[str] = None
    ) -> str:
        """Multi-turn chat completion grounded in paper context."""
        if not messages:
            raise GemmaClientError("Cannot generate chat completion with empty message history.")

        # Build conversation prompt with strict grounding
        formatted_turns = []
        for turn in messages:
            role = turn.get("role", "user").capitalize()
            content = turn.get("content", "").strip()
            formatted_turns.append(f"{role}: {content}")

        history_block = "\n\n".join(formatted_turns)
        context_block = f"\nPAPER CONTEXT:\n{paper_context}\n" if paper_context else ""

        full_prompt = (
            f"{context_block}\n"
            f"CONVERSATION HISTORY:\n{history_block}\n\n"
            f"Assistant (respond based strictly on the paper context and conversation above):"
        )

        return self.generate_text(
            prompt=full_prompt,
            system_instruction=system_instruction,
            thinking=thinking
        )
