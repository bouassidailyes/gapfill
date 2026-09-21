"""Settings → FixedBlock[] + FreeWindow[]. Deterministic; no LLM. (Phase 2)"""

from __future__ import annotations

from app.models import Block, Event, FreeWindow, Settings


def build_constraints(
    events: list[Event],
    settings: Settings,
    pinned: list[Block] | None = None,
) -> tuple[list[Block], list[FreeWindow]]:
    raise NotImplementedError("constraints.py is implemented in phase 2")
