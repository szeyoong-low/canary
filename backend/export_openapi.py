"""
Exports the backend API's OpenAPI schema, from which the frontend generates its
TypeScript types. Run from `backend/` with uv run python export_openapi.py
"""

from json import dumps
from os import environ
from pathlib import Path
from sys import path

BACKEND_DIRECTORY: Path = Path(__file__).parent

OUTPUT_PATH: Path = BACKEND_DIRECTORY / "openapi.json"

# `main` imports its siblings relatively (`.src.api.errors`), so it is only
# importable as `backend.main`, which needs the repository root on the path.
path.insert(0, str(BACKEND_DIRECTORY.parent))

# Do not dump dev-only endpoints.
environ["DEVELOPMENT"] = "false"

# Deliberately not at the top of the file: it must follow the two statements
# above, which it reads at import time.
from backend.main import app


def main() -> None:
    OUTPUT_PATH.write_text(
        # `sort_keys` makes the file stable. FastAPI emits paths in route
        # declaration order.
        dumps(app.openapi(), indent=2, sort_keys=True) + "\n"
    )

    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
