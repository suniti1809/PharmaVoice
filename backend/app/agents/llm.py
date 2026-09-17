"""Thin Groq/LangChain wrapper with JSON-safe helpers and a model fallback chain.

Why a wrapper instead of calling `ChatGroq` inside every node:
  * every node needs the same "give me valid JSON" behaviour,
  * the app must stay demo-able when no GROQ_API_KEY is present,
  * model choice is a per-node decision (small model for field spotting, larger
    model for reasoning),
  * Groq retires models. The assignment specifies `gemma2-9b-it`, which Groq has
    since decommissioned, so each logical model is a *chain*: the mandated model
    is tried first and, if the platform reports it as decommissioned/unknown, the
    next candidate in the chain is used and reported honestly in the response.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

# Substrings that mean "this model id is not usable" (as opposed to a transient error).
_MODEL_GONE_MARKERS = (
    "decommissioned",
    "does not exist",
    "not found",
    "model_not_found",
    "invalid model",
    "unknown model",
    "no longer supported",
)


class LLMUnavailable(RuntimeError):
    """Raised when no API key is configured or every candidate model failed."""


@dataclass(slots=True)
class LLMResult:
    text: str
    model: str


@lru_cache(maxsize=8)
def _client(model: str):
    if not settings.llm_enabled:
        raise LLMUnavailable("GROQ_API_KEY is not configured")
    from langchain_groq import ChatGroq  # lazy import keeps cold start fast

    return ChatGroq(
        model=model,
        api_key=settings.groq_api_key,
        temperature=settings.llm_temperature,
        max_retries=settings.llm_max_retries,
        timeout=60,
    )


def _is_model_gone(error: Exception) -> bool:
    message = str(error).lower()
    return any(marker in message for marker in _MODEL_GONE_MARKERS)


def complete(system: str, user: str, *, chain: list[str] | None = None) -> LLMResult:
    """Single-turn completion. Walks the model chain until one answers."""
    candidates = [m for m in (chain or settings.extraction_chain) if m]
    if not candidates:
        raise LLMUnavailable("no model configured")

    messages = [("system", system), ("human", user)]
    last_error: Exception | None = None

    for model in candidates:
        try:
            response = _client(model).invoke(messages)
            return LLMResult(text=str(response.content).strip(), model=model)
        except LLMUnavailable:
            raise
        except Exception as exc:
            last_error = exc
            if _is_model_gone(exc):
                logger.warning("model %s unavailable on Groq, falling back", model)
                continue
            logger.warning("Groq call failed on %s: %s", model, exc)
            continue

    raise LLMUnavailable(str(last_error) if last_error else "all candidate models failed")


_FENCE = re.compile(r"```(?:json)?(.*?)```", re.S)


def _first_json_object(text: str) -> str:
    """Pull the first balanced {...} block out of a model response."""
    fenced = _FENCE.search(text)
    if fenced:
        text = fenced.group(1)
    start = text.find("{")
    if start == -1:
        raise ValueError("no JSON object in model output")
    depth = 0
    in_string = False
    escape = False
    for idx in range(start, len(text)):
        ch = text[idx]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]
    raise ValueError("unterminated JSON object in model output")


def complete_json(system: str, user: str, *, chain: list[str] | None = None) -> tuple[dict[str, Any], str]:
    """Completion that must yield a JSON object.

    Small instruct models have no reliable JSON mode, so we instruct hard and then
    repair: strip prose and code fences, then parse the first balanced object.
    """
    guarded = system + (
        "\n\nRespond with ONE valid JSON object and nothing else. "
        "No prose, no explanation, no markdown fences."
    )
    result = complete(guarded, user, chain=chain)
    try:
        return json.loads(_first_json_object(result.text)), result.model
    except (ValueError, json.JSONDecodeError) as exc:
        logger.warning("JSON repair failed (%s). Raw head: %s", exc, result.text[:300])
        raise LLMUnavailable(f"model {result.model} did not return JSON: {exc}") from exc
