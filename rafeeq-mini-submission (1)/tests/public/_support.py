"""Shared paths and small loaders for the public learner tests."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPOSITORY_ROOT / "data" / "public"
SCHEMA_DIR = REPOSITORY_ROOT / "tests" / "schemas"
SOURCE_DIR = REPOSITORY_ROOT / "src"

# Keep the repository runnable without packaging or a shell-specific
# PYTHONPATH.  This is the same layout used by the Colab bootstrap cell.
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))


def load_jsonl(name: str) -> list[dict[str, Any]]:
    """Load a public JSONL fixture and reject non-object records."""

    records: list[dict[str, Any]] = []
    with (DATA_DIR / name).open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise AssertionError(f"{name}:{line_number} must contain a JSON object")
            records.append(value)
    return records


def load_schema(name: str) -> dict[str, Any]:
    """Load one published JSON Schema as a plain dictionary."""

    with (SCHEMA_DIR / name).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"{name} must contain a JSON object")
    return value
