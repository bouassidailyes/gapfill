"""API + pipeline schemas. Mirror of architecture.md section 6 and frontend/src/types.ts."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class Event(BaseModel):
    id: str
    title: str
    start: str
    end: str
    location: Optional[str] = None


class MealSpec(BaseModel):
    window: tuple[str, str]
    minutes: int


class Meals(BaseModel):
    breakfast: Optional[MealSpec] = None
    lunch: MealSpec
    dinner: MealSpec


class Cooking(BaseModel):
    mode: Literal["daily", "batch", "none"]
    batch_per_week: int
    cook_minutes: int


class TravelOverride(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: str = Field(alias="from")
    to: str
    minutes: int


class Settings(BaseModel):
    timezone: str
    horizon_start: str
    horizon_days: int
    day_start: str
    day_end: str
    meals: Meals
    cooking: Cooking
    transition_minutes: int
    travel_overrides: list[TravelOverride]
    lost_time_pct: float
    free_time_min_per_day: int


class TaskInput(BaseModel):
    id: str
    text: str
    estimated_minutes: Optional[int] = None


BlockType = Literal["event", "task", "meal", "cook", "travel", "free", "slack"]


class Block(BaseModel):
    id: str
    type: BlockType
    title: str
    start: str
    end: str
    task_id: Optional[str] = None
    location: Optional[str] = None
    locked: Optional[bool] = None


class Session(BaseModel):
    id: str
    minutes: int
    kind: Literal["deep", "light"]


class TaskPlan(BaseModel):
    task_id: str
    title: str
    deadline: Optional[str] = None
    priority: Literal[1, 2, 3]
    estimated_minutes: int
    sessions: list[Session]
    preferred_time: Literal["morning", "afternoon", "evening", "any"]
    notes: Optional[str] = None


class ScheduleRequest(BaseModel):
    events: list[Event]
    tasks: list[TaskInput]
    settings: Settings
    pinned: Optional[list[Block]] = None


class ScheduleResponse(BaseModel):
    blocks: list[Block]
    task_plans: list[TaskPlan]
    warnings: list[str]


class ParseIcsResponse(BaseModel):
    events: list[Event]


class ExportIcsRequest(BaseModel):
    blocks: list[Block]
    include_fixed: bool = False


class HealthResponse(BaseModel):
    ok: bool


# Internal pipeline types (not in the public TS contract)

class FreeWindow(BaseModel):
    id: str
    start: str
    end: str


class Placement(BaseModel):
    session_id: str
    start: str
    end: str


class AllocationOutput(BaseModel):
    task_plans: list[TaskPlan]


class PlaceOutput(BaseModel):
    placements: list[Placement]
