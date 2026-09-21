from pathlib import Path

from app.models import AllocationOutput, ScheduleResponse, Settings

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "fixtures"


def test_schedule_mock_matches_contract() -> None:
    ScheduleResponse.model_validate_json(
        (FIXTURES / "schedule.mock.json").read_text(encoding="utf-8")
    )


def test_allocation_mock_matches_contract() -> None:
    AllocationOutput.model_validate_json(
        (FIXTURES / "allocation.mock.json").read_text(encoding="utf-8")
    )


def test_settings_fixture_matches_contract() -> None:
    Settings.model_validate_json((FIXTURES / "settings.json").read_text(encoding="utf-8"))
