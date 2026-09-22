"""End-to-end smoke checks for the local MCP stdio boundary."""

from __future__ import annotations

import unittest

from _support import DATA_DIR

from rafeeq.mcp_client import MCPToolClient, PROTOCOL_VERSION


class MCPStdioSmokeTests(unittest.TestCase):
    def test_discovery_owned_read_and_denied_read_use_stdio(self) -> None:
        report = MCPToolClient(DATA_DIR).smoke_test()

        self.assertTrue(report["ok"], report)
        self.assertEqual(report["transport"], "stdio")
        self.assertEqual(report["protocol_version"], PROTOCOL_VERSION)
        self.assertTrue(report["closed_after_context"])
        self.assertEqual(
            report["tools"],
            ["get_order_status", "get_refund_context", "create_refund_request"],
        )
        self.assertTrue(report["owned_status"]["ok"])
        self.assertEqual(report["forbidden"]["error"]["code"], "ORDER_FORBIDDEN")
        events = [event["event"] for event in report["events"]]
        self.assertEqual(events.count("transport_open"), 1)
        self.assertEqual(events.count("transport_close"), 1)

    def test_cross_customer_result_discloses_no_order_details(self) -> None:
        client = MCPToolClient(DATA_DIR)
        result = client.call_tool(
            "get_order_status",
            {"order_id": "TW-26017"},
            {"customer_id": "CUST-012", "locale": "en"},
        )

        payload = result["structuredContent"]
        self.assertTrue(result["isError"])
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "ORDER_FORBIDDEN")
        self.assertNotIn("data", payload)
        self.assertRegex(result["_meta"]["requestId"], r"^req-[a-p]{16}$")
        self.assertNotIn("740", str(result))
        self.assertNotIn("CUST-011", str(result))


if __name__ == "__main__":
    unittest.main()
