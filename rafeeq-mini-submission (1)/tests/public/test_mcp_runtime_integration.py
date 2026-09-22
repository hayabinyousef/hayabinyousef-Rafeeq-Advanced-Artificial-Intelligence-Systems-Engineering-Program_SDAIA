"""Prove that the bounded agent graph can use the real MCP stdio adapter."""

from __future__ import annotations

import unittest

from _support import DATA_DIR

from rafeeq.agents import ToolClient
from rafeeq.graph import RafeeqRuntime
from rafeeq.mcp_client import MCPToolClient


class MCPRuntimeIntegrationTests(unittest.TestCase):
    def test_runtime_reads_and_idempotent_write_cross_mcp_boundary(self) -> None:
        with MCPToolClient(DATA_DIR) as tools:
            self.assertIsInstance(tools, ToolClient)
            runtime = RafeeqRuntime(data_dir=DATA_DIR, tool_client=tools)
            status = runtime.run(
                "Track order TW-26018",
                "CUST-012",
                thread_id="mcp-runtime-read",
            )
            first = runtime.run(
                "Refund delayed order TW-26003",
                "CUST-003",
                thread_id="mcp-runtime-write-1",
            )
            replay = runtime.run(
                "Refund delayed order TW-26003",
                "CUST-003",
                thread_id="mcp-runtime-write-2",
            )

        self.assertEqual(status["outcome"], "out_for_delivery")
        self.assertEqual(first["outcome"], "created")
        self.assertTrue(first["tool_observations"][0]["write_performed"])
        self.assertEqual(replay["outcome"], "created")
        self.assertFalse(replay["tool_observations"][0]["write_performed"])


if __name__ == "__main__":
    unittest.main()
