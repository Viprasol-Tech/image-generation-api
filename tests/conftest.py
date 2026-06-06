"""Part of Image Generation API by Viprasol Tech Private Limited (https://viprasol.com).

Shared pytest fixtures. Everything runs fully offline via the FakeImageProvider.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from image_generation_api.app import create_app
from image_generation_api.providers import FakeImageProvider
from image_generation_api.rate_limit import RateLimiter


@pytest.fixture
def client() -> TestClient:
    """A TestClient backed by the offline fake provider with a roomy limit."""
    app = create_app(FakeImageProvider(), rate_limiter=RateLimiter(max_requests=1000))
    return TestClient(app)
