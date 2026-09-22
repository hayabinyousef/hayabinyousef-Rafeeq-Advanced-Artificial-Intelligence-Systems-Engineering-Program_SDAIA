"""Public contract checks for typed, serializable agent state."""

from __future__ import annotations

import unittest

from _support import load_schema

from rafeeq.config import Limits
from rafeeq.state import AgentState, Locale, Route, RunStatus


class StateContractTests(unittest.TestCase):
    def test_safe_snapshot_has_public_fields_without_raw_content(self) -> None:
        state = AgentState(
            customer_id="CUST-011",
            message="private request that must not enter a trace",
            locale=Locale.AR,
            order_id="TW-26017",
            route=Route.REFUND,
            status=RunStatus.RUNNING,
            tool_observations=[{"raw": "untrusted tool content"}],
        )
        state.advance("guard_input", Limits())
        snapshot = state.safe_snapshot()

        self.assertNotIn("message", snapshot)
        self.assertNotIn("tool_observations", snapshot)
        self.assertEqual(snapshot["locale"], "ar")
        self.assertEqual(snapshot["route"], "refund")
        self.assertEqual(snapshot["status"], "running")
        self.assertEqual(snapshot["step_count"], 1)

    def test_published_state_schema_matches_enums_and_required_core(self) -> None:
        schema = load_schema("state.schema.json")
        required = set(schema["required"])
        self.assertTrue(
            {
                "customer_id",
                "session_id",
                "trace_id",
                "locale",
                "status",
                "step_count",
                "transition_count",
                "handoff_count",
                "reflection_count",
            }.issubset(required)
        )
        properties = schema["properties"]
        self.assertEqual(set(properties["locale"]["enum"]), {item.value for item in Locale})
        self.assertEqual(set(properties["route"]["enum"]), {item.value for item in Route} | {None})
        self.assertEqual(set(properties["status"]["enum"]), {item.value for item in RunStatus})


if __name__ == "__main__":
    unittest.main()
