"""Part of Image Generation API by Viprasol Tech Private Limited (https://viprasol.com).

Image provider abstraction plus a deterministic offline fake and optional
lazy-import adapters for OpenAI Images and Stable Diffusion.

The :class:`FakeImageProvider` synthesises a valid PNG entirely from the Python
standard library (``zlib`` + ``struct``), so the whole service runs and tests
fully offline with no network access and no API keys.
"""

from __future__ import annotations

import hashlib
import struct
import zlib
from abc import ABC, abstractmethod


class ImageProvider(ABC):
    """Abstract base class every image backend must implement."""

    name: str = "base"

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        width: int,
        height: int,
        seed: int | None = None,
    ) -> bytes:
        """Return PNG-encoded image bytes for ``prompt``."""
        raise NotImplementedError


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    """Build a single length-prefixed, CRC-suffixed PNG chunk."""
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def encode_png(pixels: bytes, width: int, height: int) -> bytes:
    """Encode raw RGB ``pixels`` (3 bytes/pixel) into a PNG byte string."""
    expected = width * height * 3
    if len(pixels) != expected:
        msg = f"expected {expected} pixel bytes, got {len(pixels)}"
        raise ValueError(msg)

    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter type 0 (None) for each scanline
        raw.extend(pixels[y * stride : (y + 1) * stride])

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _png_chunk(b"IEND", b"")
    )


class FakeImageProvider(ImageProvider):
    """Deterministic offline provider that renders a prompt-derived image.

    The output is a smooth gradient whose colours are seeded from the SHA-256
    hash of ``prompt`` (and optional ``seed``), so identical inputs always yield
    byte-identical PNGs — ideal for reproducible offline tests.
    """

    name = "fake"

    def generate(
        self,
        prompt: str,
        *,
        width: int,
        height: int,
        seed: int | None = None,
    ) -> bytes:
        key = prompt if seed is None else f"{prompt}:{seed}"
        digest = hashlib.sha256(key.encode("utf-8")).digest()
        r0, g0, b0, r1, g1, b1 = digest[:6]

        pixels = bytearray(width * height * 3)
        wd = max(width - 1, 1)
        hd = max(height - 1, 1)
        for y in range(height):
            fy = y / hd
            for x in range(width):
                fx = x / wd
                t = (fx + fy) / 2.0
                i = (y * width + x) * 3
                pixels[i] = int(r0 + (r1 - r0) * t) & 0xFF
                pixels[i + 1] = int(g0 + (g1 - g0) * fx) & 0xFF
                pixels[i + 2] = int(b0 + (b1 - b0) * fy) & 0xFF
        return encode_png(bytes(pixels), width, height)


class OpenAIImageProvider(ImageProvider):
    """Adapter for the OpenAI Images API. Imports the SDK lazily on first use."""

    name = "openai"

    def __init__(self, api_key: str | None = None, model: str = "dall-e-3") -> None:
        self._api_key = api_key
        self._model = model

    def generate(
        self,
        prompt: str,
        *,
        width: int,
        height: int,
        seed: int | None = None,
    ) -> bytes:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - optional dependency
            msg = "openai package is required for OpenAIImageProvider"
            raise RuntimeError(msg) from exc

        import base64

        client = OpenAI(api_key=self._api_key)
        size = f"{width}x{height}"
        result = client.images.generate(
            model=self._model, prompt=prompt, size=size, response_format="b64_json", n=1
        )
        b64 = result.data[0].b64_json
        if b64 is None:  # pragma: no cover - defensive
            msg = "OpenAI returned no image data"
            raise RuntimeError(msg)
        return base64.b64decode(b64)


class StableDiffusionProvider(ImageProvider):
    """Adapter for a local Stable Diffusion ``diffusers`` pipeline (lazy import)."""

    name = "stable-diffusion"

    def __init__(self, model_id: str = "stabilityai/stable-diffusion-2-1") -> None:
        self._model_id = model_id
        self._pipe: object | None = None

    def generate(
        self,
        prompt: str,
        *,
        width: int,
        height: int,
        seed: int | None = None,
    ) -> bytes:
        try:
            import io

            import torch
            from diffusers import StableDiffusionPipeline
        except ImportError as exc:  # pragma: no cover - optional dependency
            msg = "diffusers and torch are required for StableDiffusionProvider"
            raise RuntimeError(msg) from exc

        if self._pipe is None:
            self._pipe = StableDiffusionPipeline.from_pretrained(self._model_id)

        generator = None
        if seed is not None:
            generator = torch.Generator().manual_seed(seed)

        pipe = self._pipe
        image = pipe(  # type: ignore[operator]
            prompt, width=width, height=height, generator=generator
        ).images[0]
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
