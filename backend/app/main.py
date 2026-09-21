from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.ics_parse import IcsParseError, parse_ics
from app.models import (
    ExportIcsRequest,
    HealthResponse,
    ParseIcsResponse,
    ScheduleRequest,
    ScheduleResponse,
)

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "fixtures"

app = FastAPI(title="AI Student Scheduler")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(ok=True)


@app.post("/api/parse-ics", response_model=ParseIcsResponse)
async def parse_ics_route(file: UploadFile = File(...)) -> ParseIcsResponse:
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=422, detail="The uploaded file is empty.")
    try:
        events = parse_ics(raw)
    except IcsParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ParseIcsResponse(events=events)


@app.post("/api/schedule", response_model=ScheduleResponse)
def schedule(req: ScheduleRequest) -> ScheduleResponse:
    if os.getenv("DEMO_MODE") == "1":
        mock = FIXTURES / "schedule.mock.json"
        return ScheduleResponse.model_validate_json(mock.read_text(encoding="utf-8"))
    raise HTTPException(
        status_code=501,
        detail="Scheduling pipeline is not wired yet. Set DEMO_MODE=1 to use fixtures.",
    )


@app.post("/api/export-ics")
def export_ics(req: ExportIcsRequest) -> None:
    raise HTTPException(status_code=501, detail="ICS export is not implemented yet.")
