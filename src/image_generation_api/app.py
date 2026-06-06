"""Part of Image Generation API by Viprasol Tech Private Limited (https://viprasol.com).

FastAPI application wiring: endpoints, dependency injection, and the in-memory
job store. Defaults to the offline :class:`FakeImageProvider`.
"""

from __future__ import annotations

import base64

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status

from . import __version__
from .models import (
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    Job,
    JobStatus,
)
from .providers import FakeImageProvider, ImageProvider
from .rate_limit import RateLimiter


def create_app(
    provider: ImageProvider | None = None,
    *,
    rate_limiter: RateLimiter | None = None,
) -> FastAPI:
    """Build and return a configured FastAPI application instance."""
    active_provider: ImageProvider = provider or FakeImageProvider()
    limiter = rate_limiter or RateLimiter(max_requests=60, window_seconds=60.0)
    jobs: dict[str, Job] = {}

    app = FastAPI(
        title="Image Generation API",
        version=__version__,
        description=(
            "Text-to-image generation behind one clean API. "
            "By Viprasol Tech Private Limited (https://viprasol.com)."
        ),
    )
    app.state.provider = active_provider
    app.state.rate_limiter = limiter
    app.state.jobs = jobs

    def get_provider() -> ImageProvider:
        provider_obj: ImageProvider = app.state.provider
        return provider_obj

    def get_limiter() -> RateLimiter:
        limiter_obj: RateLimiter = app.state.rate_limiter
        return limiter_obj

    def enforce_rate_limit(request: Request, limiter: RateLimiter = Depends(get_limiter)) -> None:
        client = request.client.host if request.client else "anonymous"
        if not limiter.allow(client):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later.",
            )

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    def health(provider: ImageProvider = Depends(get_provider)) -> HealthResponse:
        return HealthResponse(version=__version__, provider=provider.name)

    @app.post(
        "/generate",
        response_model=GenerateResponse,
        responses={200: {"content": {"image/png": {}}}},
        dependencies=[Depends(enforce_rate_limit)],
        tags=["generation"],
    )
    def generate(
        payload: GenerateRequest,
        provider: ImageProvider = Depends(get_provider),
    ) -> Response | GenerateResponse:
        if payload.provider and payload.provider != provider.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"provider '{payload.provider}' is not configured",
            )

        job = Job(
            prompt=payload.prompt,
            width=payload.width,
            height=payload.height,
            seed=payload.seed,
            provider=provider.name,
        )
        job.status = JobStatus.RUNNING
        app.state.jobs[job.job_id] = job

        try:
            png = provider.generate(
                payload.prompt,
                width=payload.width,
                height=payload.height,
                seed=payload.seed,
            )
        except Exception as exc:  # surface provider errors cleanly
            job.status = JobStatus.FAILED
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"image generation failed: {exc}",
            ) from exc

        job.status = JobStatus.SUCCEEDED

        if payload.response_format == "png":
            return Response(
                content=png,
                media_type="image/png",
                headers={"X-Job-Id": job.job_id},
            )

        return GenerateResponse(
            job_id=job.job_id,
            status=job.status,
            provider=provider.name,
            prompt=payload.prompt,
            width=payload.width,
            height=payload.height,
            seed=payload.seed,
            image_base64=base64.b64encode(png).decode("ascii"),
        )

    @app.get("/jobs/{job_id}", response_model=Job, tags=["generation"])
    def get_job(job_id: str) -> Job:
        job: Job | None = app.state.jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")
        return job

    return app


app = create_app()
