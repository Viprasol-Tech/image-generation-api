"""Part of Image Generation API by Viprasol Tech Private Limited (https://viprasol.com).

Offline integration tests for the FastAPI endpoints via TestClient.
"""

from __future__ import annotations

import base64

from fastapi.testclient import TestClient

from image_generation_api import __version__
from image_generation_api.app import create_app
from image_generation_api.providers import FakeImageProvider
from image_generation_api.rate_limit import RateLimiter

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def test_health_ok(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"status": "ok", "version": __version__, "provider": "fake"}


def test_generate_base64_default(client: TestClient) -> None:
    resp = client.post("/generate", json={"prompt": "a serene lake", "width": 32, "height": 32})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "succeeded"
    assert body["provider"] == "fake"
    assert body["media_type"] == "image/png"
    png = base64.b64decode(body["image_base64"])
    assert png.startswith(PNG_MAGIC)


def test_generate_png_bytes(client: TestClient) -> None:
    resp = client.post(
        "/generate",
        json={"prompt": "neon city", "width": 32, "height": 32, "response_format": "png"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    assert "X-Job-Id" in resp.headers
    assert resp.content.startswith(PNG_MAGIC)


def test_generate_is_deterministic_over_api(client: TestClient) -> None:
    payload = {"prompt": "fixed", "width": 32, "height": 32, "seed": 99}
    a = client.post("/generate", json=payload).json()["image_base64"]
    b = client.post("/generate", json=payload).json()["image_base64"]
    assert a == b


def test_generate_rejects_empty_prompt(client: TestClient) -> None:
    resp = client.post("/generate", json={"prompt": ""})
    assert resp.status_code == 422


def test_generate_rejects_oversized_dimensions(client: TestClient) -> None:
    resp = client.post("/generate", json={"prompt": "x", "width": 5000})
    assert resp.status_code == 422


def test_generate_unknown_provider_rejected(client: TestClient) -> None:
    resp = client.post("/generate", json={"prompt": "x", "provider": "midjourney"})
    assert resp.status_code == 400


def test_job_lookup_after_generate(client: TestClient) -> None:
    body = client.post("/generate", json={"prompt": "track me", "width": 32, "height": 32}).json()
    job_id = body["job_id"]
    resp = client.get(f"/jobs/{job_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "succeeded"


def test_job_lookup_missing(client: TestClient) -> None:
    assert client.get("/jobs/does-not-exist").status_code == 404


def test_rate_limit_returns_429() -> None:
    app = create_app(FakeImageProvider(), rate_limiter=RateLimiter(max_requests=2))
    limited = TestClient(app)
    payload = {"prompt": "spam", "width": 16, "height": 16}
    assert limited.post("/generate", json=payload).status_code == 200
    assert limited.post("/generate", json=payload).status_code == 200
    assert limited.post("/generate", json=payload).status_code == 429


def test_openapi_schema_available(client: TestClient) -> None:
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert "/generate" in resp.json()["paths"]
