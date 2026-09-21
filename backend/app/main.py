from __future__ import annotations

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.csv_parse import CsvParseError, parse_csv
from app.ics_export import IcsExportError, blocks_to_ics
from app.ics_parse import IcsParseError, parse_ics
from app.models import (
    ExportIcsRequest,
    HealthResponse,
    ParseIcsResponse,
    ScheduleRequest,
    ScheduleResponse,
)
from app.planner import build_plan

load_dotenv()

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


@app.post("/api/parse-csv", response_model=ParseIcsResponse)
async def parse_csv_route(file: UploadFile = File(...)) -> ParseIcsResponse:
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=422, detail="The uploaded file is empty.")
    try:
        events = parse_csv(raw)
    except CsvParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ParseIcsResponse(events=events)


@app.post("/api/schedule", response_model=ScheduleResponse)
def schedule(req: ScheduleRequest) -> ScheduleResponse:
    try:
        return build_plan(req)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not build a plan: {exc}") from exc


@app.post("/api/export-ics")
def export_ics(req: ExportIcsRequest) -> Response:
    if not req.blocks:
        raise HTTPException(status_code=422, detail="There is nothing to export yet.")
    try:
        payload = blocks_to_ics(req.blocks, include_fixed=req.include_fixed)
    except IcsExportError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return Response(
        content=payload,
        media_type="text/calendar",
        headers={"Content-Disposition": 'attachment; filename="gapfill-plan.ics"'},
    )
