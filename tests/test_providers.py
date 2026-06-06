"""Part of Image Generation API by Viprasol Tech Private Limited (https://viprasol.com).

Offline unit tests for the provider layer and PNG encoder.
"""

from __future__ import annotations

import struct

import pytest

from image_generation_api.providers import (
    FakeImageProvider,
    ImageProvider,
    encode_png,
)

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _png_dimensions(png: bytes) -> tuple[int, int]:
    # IHDR width/height are the two big-endian uint32s right after the IHDR tag.
    idx = png.index(b"IHDR") + 4
    width, height = struct.unpack(">II", png[idx : idx + 8])
    return width, height


def test_fake_provider_is_image_provider() -> None:
    assert isinstance(FakeImageProvider(), ImageProvider)


def test_fake_provider_returns_valid_png_magic() -> None:
    png = FakeImageProvider().generate("a cat", width=32, height=32)
    assert png.startswith(PNG_MAGIC)
    assert png.rstrip().endswith(b"IEND" + struct.pack(">I", 2923585666))


def test_fake_provider_respects_dimensions() -> None:
    png = FakeImageProvider().generate("skyline", width=48, height=24)
    assert _png_dimensions(png) == (48, 24)


def test_fake_provider_is_deterministic() -> None:
    a = FakeImageProvider().generate("same prompt", width=32, height=32, seed=7)
    b = FakeImageProvider().generate("same prompt", width=32, height=32, seed=7)
    assert a == b


def test_fake_provider_prompt_changes_output() -> None:
    a = FakeImageProvider().generate("prompt one", width=32, height=32)
    b = FakeImageProvider().generate("prompt two", width=32, height=32)
    assert a != b


def test_fake_provider_seed_changes_output() -> None:
    a = FakeImageProvider().generate("p", width=32, height=32, seed=1)
    b = FakeImageProvider().generate("p", width=32, height=32, seed=2)
    assert a != b


def test_encode_png_rejects_wrong_pixel_count() -> None:
    with pytest.raises(ValueError, match="pixel bytes"):
        encode_png(b"\x00\x00\x00", width=10, height=10)
