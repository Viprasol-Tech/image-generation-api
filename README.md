<p align="center"><img src="docs/assets/logo.png" width="120"></p>

# Image Generation API

> Text-to-image generation behind one clean, provider-agnostic HTTP API — runs fully offline out of the box.

*Built and maintained by [Viprasol Tech](https://viprasol.com) — Fintech Experts. Full-Stack Builders.*

[![CI](https://img.shields.io/github/actions/workflow/status/Viprasol-Tech/image-generation-api/ci.yml?branch=main&style=flat-square)](https://github.com/Viprasol-Tech/image-generation-api/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue?style=flat-square)](https://www.python.org/)
[![Ruff](https://img.shields.io/badge/lint-ruff-261230?style=flat-square)](https://github.com/astral-sh/ruff)
[![Telegram](https://img.shields.io/badge/Telegram-help-26A5E4?style=flat-square&logo=telegram)](https://t.me/viprasol_help)
[![Stars](https://img.shields.io/github/stars/Viprasol-Tech/image-generation-api?style=flat-square)](https://github.com/Viprasol-Tech/image-generation-api/stargazers)

---

A small, production-shaped FastAPI service that wraps text-to-image generation behind a single clean API. It ships with a deterministic, **offline** fake provider so you can develop, demo, and test with **zero network access and zero API keys** — then drop in OpenAI Images or Stable Diffusion when you are ready for real pixels.

## ✨ Features

- 🎨 **One clean API** — `POST /generate` turns a prompt into a PNG, every time.
- 🔌 **Pluggable providers** — a small `ImageProvider` ABC; swap backends freely.
- 🧪 **Fully offline** — the `FakeImageProvider` renders valid PNGs from the stdlib (`zlib` + `struct`); no Pillow, no network, no keys.
- 🎯 **Deterministic** — identical prompt + seed always yields byte-identical output, perfect for reproducible tests.
- 🤖 **Real adapters** — optional lazy-import adapters for **OpenAI Images** and **Stable Diffusion** (`diffusers`).
- 📦 **Base64 or raw bytes** — return JSON with base64, or stream raw `image/png`.
- 🧾 **Validated requests** — Pydantic v2 models guard prompt length and image dimensions.
- 🗂️ **Job model** — every request gets a tracked job you can look up at `GET /jobs/{id}`.
- 🚦 **Built-in rate limiting** — simple in-memory fixed-window limiter, returns `429`.
- ❤️ **Health endpoint** — `GET /health` for load balancers and probes.
- 📜 **OpenAPI docs** — interactive Swagger UI at `/docs` for free.
- 🐳 **Docker-first** — `Dockerfile` + `docker-compose.yml`, up in one command.
- ✅ **Strict quality bar** — ruff, mypy `strict`, and 10+ offline tests in CI across 3 OSes × 3 Python versions.

## 🚀 Quickstart

### Docker (recommended)

```bash
docker compose up --build
# API now on http://localhost:8000  (Swagger UI at /docs)
```

### Local Python

```bash
pip install -e ".[dev]"
python -m image_generation_api          # serves on http://localhost:8000
```

## 🧑‍💻 Usage

Generate an image (base64 JSON, the default):

```bash
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a serene mountain lake at dawn", "width": 256, "height": 256, "seed": 42}'
```

Get raw PNG bytes straight to a file:

```bash
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "neon city skyline", "response_format": "png"}' \
  --output generated_skyline.png
```

In Python, fully offline via the FastAPI `TestClient`:

```python
from fastapi.testclient import TestClient
from image_generation_api.app import create_app

client = TestClient(create_app())
resp = client.post("/generate", json={"prompt": "a fox", "seed": 7})
print(resp.json()["status"])  # -> "succeeded"
```

Switch to a real provider:

```python
from image_generation_api.app import create_app
from image_generation_api.providers import OpenAIImageProvider

app = create_app(OpenAIImageProvider())  # needs `pip install ".[openai]"` + OPENAI_API_KEY
```

## 🗺️ Roadmap

- [ ] Async background jobs with a pollable queue
- [ ] Pluggable persistent storage for generated images
- [ ] Additional adapters (Replicate, Together, local ComfyUI)
- [ ] Per-API-key rate limits and usage metering
- [ ] Image-to-image and inpainting endpoints

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md) before opening a PR.

## 📬 Contact — Viprasol Tech Private Limited

- 🌐 Website: [viprasol.com](https://viprasol.com)
- ✉️ Email: [support@viprasol.com](mailto:support@viprasol.com)
- 💬 Telegram: [t.me/viprasol_help](https://t.me/viprasol_help) · 📱 WhatsApp: +91 96336 52112
- 🐙 GitHub: [@Viprasol-Tech](https://github.com/Viprasol-Tech) · 💼 [LinkedIn](https://www.linkedin.com/in/viprasol/) · 𝕏 [@viprasol](https://twitter.com/viprasol)

> *Viprasol Tech — fintech software, algorithmic trading systems, MT4/MT5 bots, AI voice agents, and B2B SaaS. Need a custom build? [Get in touch](mailto:support@viprasol.com).*

## 📄 License

Released under the [MIT License](LICENSE) © 2025 Viprasol Tech Private Limited.
