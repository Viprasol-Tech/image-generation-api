"""Part of Image Generation API by Viprasol Tech Private Limited (https://viprasol.com).

Pydantic request/response models and the in-memory job model.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    """Lifecycle states for a generation job."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class GenerateRequest(BaseModel):
    """Validated payload for ``POST /generate``."""

    prompt: str = Field(..., min_length=1, max_length=1000, description="Text prompt.")
    width: int = Field(256, ge=16, le=1024, description="Image width in pixels.")
    height: int = Field(256, ge=16, le=1024, description="Image height in pixels.")
    seed: int | None = Field(None, ge=0, description="Optional deterministic seed.")
    provider: str | None = Field(None, description="Provider name override.")
    response_format: Literal["base64", "png"] = Field(
        "base64", description="Return base64 JSON or raw PNG bytes."
    )


class GenerateResponse(BaseModel):
    """JSON body returned when ``response_format='base64'``."""

    job_id: str
    status: JobStatus
    provider: str
    prompt: str
    width: int
    height: int
    seed: int | None
    image_base64: str
    media_type: str = "image/png"


class HealthResponse(BaseModel):
    """Body returned by ``GET /health``."""

    status: Literal["ok"] = "ok"
    version: str
    provider: str


class Job(BaseModel):
    """In-memory record of a single generation request."""

    job_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    prompt: str
    width: int
    height: int
    seed: int | None
    provider: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
