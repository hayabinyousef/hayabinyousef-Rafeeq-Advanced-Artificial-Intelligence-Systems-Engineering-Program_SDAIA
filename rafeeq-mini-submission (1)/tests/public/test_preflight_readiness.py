from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "preflight_readiness.py"
SPEC = importlib.util.spec_from_file_location("preflight_readiness", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PreflightReadinessTests(unittest.TestCase):
    def test_public_repository_passes_automated_preflight(self) -> None:
        report = MODULE.collect_preflight(ROOT)
        self.assertTrue(report["automated_ready"], report)
        self.assertFalse(report["release_ready"])
        self.assertEqual(
            report["release_status"],
            "manual_hosted_colab_acceptance_required",
        )

    def test_manual_acceptance_is_explicit_and_not_auto_claimed(self) -> None:
        report = MODULE.collect_preflight(ROOT)
        identifiers = {item["id"] for item in report["manual_acceptance"]}
        self.assertEqual(
            identifiers,
            {
                "clean_google_account",
                "hosted_colab_c0_c29",
                "runtime_recovery",
                "github_export",
                "github_actions_green",
            },
        )
        self.assertTrue(all(item["status"] == "pending" for item in report["manual_acceptance"]))


if __name__ == "__main__":
    unittest.main()
