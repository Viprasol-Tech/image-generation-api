"""Part of Image Generation API by Viprasol Tech Private Limited (https://viprasol.com).

Module entry point: ``python -m image_generation_api`` launches uvicorn.
"""

from __future__ import annotations

import os


def main() -> None:
    """Run the API with uvicorn using host/port from the environment."""
    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")  # noqa: S104 - container default
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("image_generation_api.app:app", host=host, port=port)


if __name__ == "__main__":
    main()
