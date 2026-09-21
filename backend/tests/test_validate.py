from app.models import FreeWindow, Placement, Session, TaskPlan
from app.validate import check_placements, greedy_place, validate_and_repair

WINDOW = FreeWindow(id="w1", start="2026-09-21T08:00:00+02:00", end="2026-09-21T12:00:00+02:00")
PLAN = TaskPlan(
    task_id="t1",
    title="Essay",
    deadline=None,
    priority=2,
    estimated_minutes=60,
    sessions=[Session(id="t1-s1", minutes=60, kind="deep")],
    preferred_time="any",
)


def test_overlap_is_a_violation() -> None:
    placements = [
        Placement(session_id="t1-s1", start="2026-09-21T08:00:00+02:00", end="2026-09-21T09:00:00+02:00"),
        Placement(session_id="t1-s1", start="2026-09-21T08:30:00+02:00", end="2026-09-21T09:30:00+02:00"),
    ]
    assert check_placements(placements, [WINDOW], [PLAN])


def test_outside_window_is_a_violation() -> None:
    bad = [Placement(session_id="t1-s1", start="2026-09-21T18:00:00+02:00", end="2026-09-21T19:00:00+02:00")]
    assert any("free window" in v for v in check_placements(bad, [WINDOW], [PLAN]))


def test_wrong_duration_is_a_violation() -> None:
    bad = [Placement(session_id="t1-s1", start="2026-09-21T08:00:00+02:00", end="2026-09-21T08:10:00+02:00")]
    assert any("expected 60" in v for v in check_placements(bad, [WINDOW], [PLAN]))


def test_broken_llm_output_still_yields_a_valid_calendar() -> None:
    broken = [Placement(session_id="t1-s1", start="2026-09-21T18:00:00+02:00", end="2026-09-21T19:00:00+02:00")]
    blocks, warnings = validate_and_repair(broken, [WINDOW], [PLAN])
    assert any("backup placer" in w for w in warnings)
    assert len(blocks) == 1
    assert blocks[0].start == "2026-09-21T08:00:00+02:00"
    assert blocks[0].end == "2026-09-21T09:00:00+02:00"


def test_greedy_respects_the_window() -> None:
    blocks, warnings = greedy_place([WINDOW], [PLAN])
    assert warnings == []
    assert blocks[0].start.startswith("2026-09-21T08:00")
