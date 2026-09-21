from app.llm import _loads, fill_prompt
from app.models import AllocationOutput


def test_fill_prompt_replaces_placeholders() -> None:
    text = fill_prompt("allocate", today="2026-09-21", horizon_days="7", free_minutes_per_day="{}", tasks="[]")
    assert "{{today}}" not in text
    assert "2026-09-21" in text


def test_strips_markdown_fences() -> None:
    data = _loads('```json\n{"task_plans": []}\n```')
    assert data == {"task_plans": []}


def test_allocation_output_validates() -> None:
    raw = {
        "task_plans": [
            {
                "task_id": "t1",
                "title": "Essay",
                "deadline": None,
                "priority": 2,
                "estimated_minutes": 60,
                "sessions": [{"id": "t1-s1", "minutes": 60, "kind": "deep"}],
                "preferred_time": "morning",
            }
        ]
    }
    parsed = AllocationOutput.model_validate(raw)
    assert parsed.task_plans[0].sessions[0].minutes == 60
