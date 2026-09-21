"""Block[] → .ics bytes. (Phase 4)"""

from __future__ import annotations

from app.models import Block


def blocks_to_ics(blocks: list[Block], include_fixed: bool = False) -> bytes:
    raise NotImplementedError("ics_export.py is implemented in phase 4")
