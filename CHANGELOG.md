# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-01

### Added

- `POST /generate` endpoint (base64 JSON or raw PNG bytes) and `GET /health`.
- `GET /jobs/{job_id}` lookup backed by an in-memory job model.
- `ImageProvider` abstract base class.
- Deterministic offline `FakeImageProvider` that renders valid PNGs from the
  standard library (`zlib` + `struct`) — no network, no keys.
- Lazy-import adapters for OpenAI Images and Stable Diffusion.
- Pydantic v2 request validation and a simple in-memory rate limiter (`429`).
- 10+ fully offline tests via FastAPI `TestClient`.
- Tooling: ruff, mypy strict, pytest, GitHub Actions CI, Docker, and docs.

[0.1.0]: https://github.com/Viprasol-Tech/image-generation-api/releases/tag/v0.1.0
