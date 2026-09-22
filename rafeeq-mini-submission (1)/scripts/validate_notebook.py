#!/usr/bin/env python3
"""Validate the public Rafeeq notebook structure without executing learner TODOs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NOTEBOOK = ROOT / "notebooks" / "Rafeeq_Mini_Capstone.ipynb"

EXPECTED_SECTIONS = (
    "C0_ENV_DOCTOR",
    "C1_ARCHITECTURE",
    "C2_TYPED_STATE",
    "C3_BOUNDED_GRAPH",
    "C4_REASONING_TRACES",
    "C5_REACT_ORDERS",
    "C6_TOOL_SCHEMA",
    "C7_MCP_SERVER",
    "C8_MCP_CLIENT",
    "C9_DAY1_GATE",
    "C10_RESTORE",
    "C11_SESSION_MEMORY",
    "C12_SCOPED_RECALL",
    "C13_POLICY_RETRIEVAL",
    "C14_SPECIALISTS",
    "C15_SUPERVISOR",
    "C16_TYPED_HANDOFF",
    "C17_PLAN_EXECUTE",
    "C18_REFUND_GATE",
    "C19_INTERRUPT_RESUME",
    "C20_DAY2_GATE",
    "C21_THREAT_MODEL",
    "C22_ATTACK_SUITE",
    "C23_GUARD_FIX_RETEST",
    "C24_REFLECTION_GATE",
    "C25_TRACE_EVAL",
    "C26_ONE_OPTIMIZATION",
    "C27_SCORECARD",
    "C28_READINESS",
    "C29_EXPORT_SAFETY_CHECK",
)


def source_text(cell: dict[str, Any]) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"cannot read notebook: {exc}"]

    if notebook.get("nbformat") != 4:
        errors.append("notebook must use nbformat 4")
    cells = notebook.get("cells")
    if not isinstance(cells, list) or not cells:
        return errors + ["notebook has no cells"]

    combined = "\n".join(source_text(cell) for cell in cells if isinstance(cell, dict))
    section_cell_indexes: list[int] = []
    for section in EXPECTED_SECTIONS:
        occurrences: list[tuple[int, dict[str, Any]]] = []
        for index, cell in enumerate(cells):
            if isinstance(cell, dict):
                occurrences.extend((index, cell) for _ in range(source_text(cell).count(section)))
        if len(occurrences) != 1:
            errors.append(f"section marker must appear exactly once: {section} (found {len(occurrences)})")
        if not occurrences:
            errors.append(f"missing section marker: {section}")
            continue
        cell_index, marker_cell = occurrences[0]
        section_cell_indexes.append(cell_index)
        tags = marker_cell.get("metadata", {}).get("tags", [])
        if marker_cell.get("cell_type") != "markdown":
            errors.append(f"section marker must be in a markdown cell: {section}")
        if not isinstance(tags, list) or section not in tags:
            errors.append(f"section markdown cell must carry matching tag: {section}")
    if section_cell_indexes != sorted(section_cell_indexes):
        errors.append("C0-C29 section markers are not in the approved order")

    todo_cell_indexes: set[int] = set()
    for number in range(1, 15):
        marker = f"TODO-{number}"
        pattern = re.compile(rf"{re.escape(marker)}(?!\d)")
        occurrences: list[tuple[int, dict[str, Any]]] = []
        for index, cell in enumerate(cells):
            if isinstance(cell, dict):
                occurrences.extend((index, cell) for _ in pattern.finditer(source_text(cell)))
        if len(occurrences) != 1:
            errors.append(f"learner marker must appear exactly once: {marker} (found {len(occurrences)})")
        if not occurrences:
            continue
        cell_index, marker_cell = occurrences[0]
        todo_cell_indexes.add(cell_index)
        tags = marker_cell.get("metadata", {}).get("tags", [])
        if marker_cell.get("cell_type") != "code":
            errors.append(f"learner marker must be in a code cell: {marker}")
        if not isinstance(tags, list) or "learner-exercise" not in tags:
            errors.append(f"learner marker code cell must be tagged learner-exercise: {marker}")
    if len(todo_cell_indexes) != 14:
        errors.append(f"learner TODOs must occupy exactly 14 distinct code cells (found {len(todo_cell_indexes)})")
    unexpected_numbers = sorted({int(value) for value in re.findall(r"TODO-(\d+)", combined) if int(value) not in range(1, 15)})
    unexpected = [f"TODO-{index}" for index in unexpected_numbers]
    if unexpected:
        errors.append(f"unexpected learner TODO markers: {', '.join(unexpected)}")

    if "FINAL_EXPORT" not in combined or "FINAL_EXPORT_SKIPPED" not in combined:
        errors.append("C29 must expose the guarded FINAL_EXPORT flow")
    if "LLM_MODE" not in combined or "stub" not in combined:
        errors.append("mandatory offline stub mode is not explicit")
    if "API_KEY" in combined and "No API key" not in combined and "لا يحتاج" not in combined:
        errors.append("API-key language is ambiguous")

    for index, cell in enumerate(cells):
        if not isinstance(cell, dict):
            errors.append(f"cell {index} is not an object")
            continue
        if cell.get("cell_type") == "code":
            if cell.get("outputs") not in ([], None):
                errors.append(f"code cell {index} contains saved output")
            if cell.get("execution_count") is not None:
                errors.append(f"code cell {index} has an execution count")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_NOTEBOOK)
    args = parser.parse_args(argv)
    errors = validate(args.path)
    if errors:
        print("NOTEBOOK CHECK: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("NOTEBOOK CHECK: PASSED")
    print(f"- sections: {len(EXPECTED_SECTIONS)}")
    print("- learner TODOs: 14")
    print("- outputs: cleared")
    return 0


if __name__ == "__main__":
    sys.exit(main())
