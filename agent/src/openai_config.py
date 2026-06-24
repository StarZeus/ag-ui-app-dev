"""OpenAI model configuration helpers."""

from __future__ import annotations

import os
from typing import Any


def _read_env(name: str) -> str | None:
    value = os.getenv(name, "").strip()
    return value or None


def build_chat_openai_kwargs(default_model: str = "gpt-5.4-mini", **overrides: Any) -> dict[str, Any]:
    """Build ChatOpenAI kwargs from environment variables.

    Supported environment variables:
    - OPENAI_API_KEY
    - OPENAI_BASE_URL
    - OPENAI_API_BASE, as a compatibility fallback
    - OPENAI_MODEL
    """
    kwargs: dict[str, Any] = {
        "model": _read_env("OPENAI_MODEL") or default_model,
    }

    api_key = _read_env("OPENAI_API_KEY")
    if api_key:
        kwargs["api_key"] = api_key

    base_url = _read_env("OPENAI_BASE_URL") or _read_env("OPENAI_API_BASE")
    if base_url:
        kwargs["base_url"] = base_url

    kwargs.update(overrides)
    return kwargs
