"""Part of Image Generation API by Viprasol Tech Private Limited (https://viprasol.com).

A tiny, dependency-free in-memory fixed-window rate limiter.
"""

from __future__ import annotations

import time
from collections import defaultdict


class RateLimiter:
    """Fixed-window rate limiter keyed by an arbitrary client identifier."""

    def __init__(self, max_requests: int = 60, window_seconds: float = 60.0) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def allow(self, key: str, *, now: float | None = None) -> bool:
        """Return ``True`` if ``key`` may make a request within the window."""
        current = time.monotonic() if now is None else now
        cutoff = current - self.window_seconds
        hits = [t for t in self._hits[key] if t > cutoff]
        if len(hits) >= self.max_requests:
            self._hits[key] = hits
            return False
        hits.append(current)
        self._hits[key] = hits
        return True

    def reset(self) -> None:
        """Clear all recorded request history (useful in tests)."""
        self._hits.clear()
