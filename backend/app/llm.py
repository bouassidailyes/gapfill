"""call_json(): call the model, parse JSON, pydantic-validate, retry once. (Phase 3)"""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def call_json(system: str, user: str, schema: type[T]) -> T:
    raise NotImplementedError("llm.py is implemented in phase 3")
