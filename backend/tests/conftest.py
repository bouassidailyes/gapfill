import pytest


@pytest.fixture(autouse=True)
def _offline_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    # Keep unit tests off the live Gemini API even if a key is in .env.
    monkeypatch.setenv("DEMO_MODE", "1")
