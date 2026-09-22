"""Offline readiness checks for the mandatory learner path."""

from __future__ import annotations

import json
import re
import unittest

from _support import DATA_DIR, REPOSITORY_ROOT, SCHEMA_DIR, load_jsonl, load_schema

from rafeeq.config import Settings
from rafeeq.graph import RafeeqRuntime


class ReadinessTests(unittest.TestCase):
    def test_required_public_assets_exist_and_are_nonempty(self) -> None:
        paths = [
            DATA_DIR / "orders.csv",
            DATA_DIR / "policy_chunks.jsonl",
            DATA_DIR / "memory_seed.jsonl",
            DATA_DIR / "tickets_dev.jsonl",
            DATA_DIR / "eval_public.jsonl",
            DATA_DIR / "security_cases.jsonl",
            SCHEMA_DIR / "state.schema.json",
            SCHEMA_DIR / "trace.schema.json",
            SCHEMA_DIR / "assessment.schema.json",
            SCHEMA_DIR / "manifest.schema.json",
            REPOSITORY_ROOT / "mcp_server" / "tawseel_server.py",
            REPOSITORY_ROOT / "src" / "rafeeq" / "graph.py",
        ]
        for path in paths:
            with self.subTest(path=path.relative_to(REPOSITORY_ROOT)):
                self.assertTrue(path.is_file())
                self.assertGreater(path.stat().st_size, 0)

        for name in ("policy_chunks.jsonl", "memory_seed.jsonl", "tickets_dev.jsonl", "eval_public.jsonl", "security_cases.jsonl"):
            self.assertGreater(len(load_jsonl(name)), 0)

    def test_environment_is_ready_offline_with_published_limits(self) -> None:
        self.assertEqual(Settings.from_env().llm_mode, "stub")
        health = RafeeqRuntime(DATA_DIR).health_snapshot()

        self.assertEqual(health["status"], "ready")
        self.assertEqual(health["llm_mode"], "stub")
        self.assertFalse(health["network_required"])
        self.assertGreater(health["orders_loaded"], 0)
        self.assertGreater(health["policies_loaded"], 0)
        self.assertGreater(health["memories_loaded"], 0)
        self.assertEqual(health["limits"], {"steps": 6, "transitions": 12, "handoffs": 2, "reflections": 1})

    def test_schemas_are_valid_json_with_strict_required_top_levels(self) -> None:
        expected = {
            "assessment.schema.json": {
                "schema_version", "run_id", "generated_at_utc", "llm_mode", "mcp_transport",
                "versions", "cases", "metrics", "critical_gates", "optimization", "readiness",
                "all_critical_gates_passed",
            },
            "manifest.schema.json": {
                "schema_version", "generated_at_utc", "export_id", "assessment_run_id",
                "assessment_sha256", "expected_final_commit_message",
                "completed_notebook_upload_required", "learner_todo_status",
                "files", "safety_checks", "all_passed",
            },
        }
        for name in ("state.schema.json", "trace.schema.json", *expected):
            with self.subTest(schema=name):
                schema = load_schema(name)
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(schema["type"], "object")
                self.assertIsInstance(schema["required"], list)
                if name in expected:
                    self.assertEqual(set(schema["required"]), expected[name])

    def test_public_test_and_data_tree_contains_no_private_material_or_secrets(self) -> None:
        forbidden_names = re.compile(r"(?:hidden|solution|answer[_-]?key|instructor[_-]?package)", re.I)
        secret_pattern = re.compile(
            r"\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{12,}|ghp_[A-Za-z0-9]{12,}|github_pat_[A-Za-z0-9_]{12,})\b"
        )
        roots = (REPOSITORY_ROOT / "tests" / "public", DATA_DIR)

        for root in roots:
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                relative = path.relative_to(REPOSITORY_ROOT).as_posix()
                self.assertIsNone(forbidden_names.search(relative), relative)
                if path.suffix in {".py", ".md", ".json", ".jsonl", ".csv"}:
                    text = path.read_text(encoding="utf-8")
                    self.assertIsNone(secret_pattern.search(text), relative)
                    if path.suffix == ".json":
                        json.loads(text)


if __name__ == "__main__":
    unittest.main()
