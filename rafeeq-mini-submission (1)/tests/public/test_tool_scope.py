"""Public tests for ownership and minimum-necessary tool contracts."""

from __future__ import annotations

from dataclasses import asdict
import unittest

from _support import DATA_DIR

from mcp_server.tawseel_server import TOOL_DEFINITIONS
from rafeeq.agents import build_handoff
from rafeeq.data import DataStore
from rafeeq.state import AgentState, Locale, Route


class ToolScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.store = DataStore.from_public_dir(DATA_DIR)

    def test_order_lookup_enforces_owner_and_hides_existence(self) -> None:
        owned = self.store.order_for_customer("TW-26017", "CUST-011")
        wrong_owner = self.store.order_for_customer("TW-26017", "CUST-012")
        missing = self.store.order_for_customer("TW-99999", "CUST-012")

        self.assertIsNotNone(owned)
        self.assertIsNone(wrong_owner)
        self.assertIsNone(missing)

    def test_model_visible_tool_schemas_exclude_trusted_context(self) -> None:
        forbidden = {"customer_id", "amount", "amount_sar", "approval", "approval_status"}
        for tool in TOOL_DEFINITIONS:
            with self.subTest(tool=tool["name"]):
                schema = tool["inputSchema"]
                self.assertTrue(schema["additionalProperties"] is False)
                self.assertTrue(forbidden.isdisjoint(schema["properties"]))

    def test_handoff_contains_no_raw_message(self) -> None:
        state = AgentState(
            customer_id="CUST-011",
            message="raw customer content",
            locale=Locale.AR,
            order_id="TW-26017",
        )
        handoff = asdict(build_handoff(Route.REFUND, state))

        self.assertNotIn("message", handoff)
        self.assertEqual(handoff["customer_id"], "CUST-011")
        self.assertEqual(handoff["order_id"], "TW-26017")
        self.assertEqual(handoff["task"], "evaluate_refund")


if __name__ == "__main__":
    unittest.main()
