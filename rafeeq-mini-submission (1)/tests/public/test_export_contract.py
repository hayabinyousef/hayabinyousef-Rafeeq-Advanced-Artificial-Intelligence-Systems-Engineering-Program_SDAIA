"""Public checks for the clean learner-export contract."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from _support import REPOSITORY_ROOT


def _load_export_module():
    path = REPOSITORY_ROOT / "scripts" / "export_safety_check.py"
    spec = importlib.util.spec_from_file_location("rafeeq_export_contract_test", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load export contract")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExportContractTests(unittest.TestCase):
    def test_learner_bundle_replaces_course_only_automation(self) -> None:
        contract = _load_export_module()
        paths = {path.relative_to(REPOSITORY_ROOT).as_posix() for path in contract.candidate_files()}

        self.assertNotIn(".github/workflows/learner-quality.yml", paths)
        self.assertNotIn(".github/workflows/pages.yml", paths)
        self.assertNotIn(".github/workflows/learner-submission-quality.yml", paths)
        self.assertNotIn(".github/pull_request_template.md", paths)
        self.assertIn("COURSE_USE_PERMISSION.md", paths)
        self.assertEqual(set(contract.VIRTUAL_FILES), {contract.STUDENT_WORKFLOW_PATH})
        self.assertNotIn("branches: [main]", contract.STUDENT_WORKFLOW)
        self.assertIn("push:\n", contract.STUDENT_WORKFLOW)
        self.assertIn("--write-receipt", contract.STUDENT_WORKFLOW)
        self.assertIn("actions/upload-artifact@v4", contract.STUDENT_WORKFLOW)

    def test_complete_todo_status_is_embedded_once_in_manifest(self) -> None:
        contract = _load_export_module()
        status = {
            "schema_version": "1.0",
            "completed": 14,
            "total": 14,
            "all_complete": True,
            "items": [
                {"exercise": f"TODO-{number}", "passed": True}
                for number in range(1, 15)
            ],
        }
        original = contract.LEARNER_STATUS_PATH
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "learner_todo_status.json"
                path.write_text(json.dumps(status), encoding="utf-8")
                contract.LEARNER_STATUS_PATH = path
                ready, loaded = contract.load_learner_todo_status()
        finally:
            contract.LEARNER_STATUS_PATH = original

        self.assertTrue(ready)
        self.assertEqual(loaded["completed"], 14)
        self.assertEqual(len(loaded["items"]), 14)


if __name__ == "__main__":
    unittest.main()
