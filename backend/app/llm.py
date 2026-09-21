"""call_json(): call the model, parse JSON, pydantic-validate, retry once."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

PROMPTS = Path(__file__).resolve().parent / "prompts"
ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "cache" / "llm"
TIMEOUT = 60.0
TEMPERATURE = 0.2
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"
log = logging.getLogger(__name__)

# override=True so DEMO_MODE=0 in .env wins over a leftover DEMO_MODE=1 in the shell.
load_dotenv(ROOT / ".env", override=True)


class LlmError(RuntimeError):
    """The model returned nothing we can use."""


def llm_enabled() -> bool:
    if os.getenv("DEMO_MODE") == "1":
        return False
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))


def fill_prompt(name: str, **values: str) -> str:
    text = (PROMPTS / f"{name}.md").read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def call_json(system: str, user: str, schema: type[T]) -> T:
    last_error = ""
    prompt = user
    for _attempt in range(2):
        if last_error:
            prompt = user + "\n\nYour previous reply was invalid:\n" + last_error + "\nReturn corrected JSON only."
        raw = _cached_complete(system, prompt)
        try:
            return schema.model_validate(_loads(raw))
        except (json.JSONDecodeError, ValidationError, LlmError) as exc:
            last_error = str(exc)
    raise LlmError(last_error or "The model did not return valid JSON.")


def _cached_complete(system: str, user: str) -> str:
    key = hashlib.sha256(f"{system}\n---\n{user}\n---\n{os.getenv('LLM_MODEL', '')}".encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if path.exists():
        return path.read_text(encoding="utf-8")
    text = _complete(system, user)
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text


def _complete(system: str, user: str) -> str:
    gemini = os.getenv("GEMINI_API_KEY")
    if gemini:
        return _gemini(system, user, gemini)
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        return _anthropic(system, user, anthropic_key)
    raise LlmError("No LLM API key set (GEMINI_API_KEY or ANTHROPIC_API_KEY).")


def _gemini(system: str, user: str, api_key: str) -> str:
    model = os.getenv("LLM_MODEL") or DEFAULT_GEMINI_MODEL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": TEMPERATURE, "responseMimeType": "application/json"},
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    body: dict[str, object] | None = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                body = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            message = _gemini_http_error(exc, api_key)
            if exc.code == 503 and attempt == 0:
                log.warning("%s; retrying once", message)
                time.sleep(1.5)
                continue
            raise LlmError(message) from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise LlmError(f"Gemini request failed: {_redact(exc, api_key)}") from exc
    if body is None:
        raise LlmError("Gemini request failed after retry.")
    try:
        return body["candidates"][0]["content"]["parts"][0]["text"]  # type: ignore[index]
    except (KeyError, IndexError, TypeError) as exc:
        raise LlmError("Gemini returned an empty reply.") from exc


def _gemini_http_error(exc: urllib.error.HTTPError, api_key: str) -> str:
    raw = _redact(exc.read().decode("utf-8", "replace"), api_key)
    try:
        payload = json.loads(raw)
        detail = payload.get("error", {}).get("message") or raw
    except (json.JSONDecodeError, AttributeError, TypeError):
        detail = raw
    return f"Gemini HTTP {exc.code}: {str(detail).strip()[:240]}"


def _redact(value: object, api_key: str) -> str:
    text = str(value)
    return text.replace(api_key, "***") if api_key else text


def _anthropic(system: str, user: str, api_key: str) -> str:
    from anthropic import Anthropic

    model = os.getenv("LLM_MODEL") or "claude-sonnet-4-5"
    try:
        message = Anthropic(api_key=api_key).messages.create(
            model=model,
            max_tokens=4096,
            temperature=TEMPERATURE,
            system=system,
            messages=[{"role": "user", "content": user}],
            timeout=TIMEOUT,
        )
    except Exception as exc:
        raise LlmError(f"Anthropic request failed: {exc}") from exc
    parts = [getattr(block, "text", "") for block in message.content]
    text = "".join(parts).strip()
    if not text:
        raise LlmError("Anthropic returned an empty reply.")
    return text


def _loads(text: str) -> object:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end < start:
        raise LlmError("Reply did not contain a JSON object.")
    return json.loads(cleaned[start : end + 1])
