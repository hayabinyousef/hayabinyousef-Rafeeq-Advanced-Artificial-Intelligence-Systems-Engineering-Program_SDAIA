"""Hard-budget and fail-safe termination checks."""

from __future__ import annotations

import unittest

from _support import DATA_DIR, load_jsonl

from rafeeq.agents import LocalToolClient, ToolResult
from rafeeq.config import Limits, Settings
from rafeeq.data import DataStore
from rafeeq.graph import RafeeqRuntime
from rafeeq.state import AgentState


class TerminationTests(unittest.TestCase):
    def test_default_limits_are_the_published_6_12_2_1_contract(self) -> None:
        limits = Limits()
        self.assertEqual(
            (limits.max_steps, limits.max_transitions, limits.max_handoffs, limits.max_reflections),
            (6, 12, 2, 1),
        )

    def test_each_counter_rejects_the_first_operation_beyond_its_limit(self) -> None:
        limits = Limits()
        state = AgentState(customer_id="CUST-001", message="bounded run")

        for index in range(6):
            state.advance(f"step-{index}", limits)
        with self.assertRaisesRegex(RuntimeError, "STEP_LIMIT_REACHED"):
            state.advance("step-7", limits)

        for index in range(12):
            state.transition(f"edge-{index}", limits)
        with self.assertRaisesRegex(RuntimeError, "TRANSITION_LIMIT_REACHED"):
            state.transition("edge-13", limits)

        state.handoff(limits)
        state.handoff(limits)
        with self.assertRaisesRegex(RuntimeError, "HANDOFF_LIMIT_REACHED"):
            state.handoff(limits)

    def test_reduced_budget_fails_closed_instead_of_looping(self) -> None:
        runtime = RafeeqRuntime(
            DATA_DIR,
            settings=Settings(limits=Limits(max_steps=2, max_transitions=12, max_handoffs=2)),
        )
        result = runtime.run("Track order TW-26018", "CUST-012", locale="en")

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["outcome"], "runtime_error")
        self.assertIn("STEP_LIMIT_REACHED", result["errors"])
        self.assertLessEqual(result["counters"]["steps"], 2)

    def test_refund_write_is_blocked_when_terminal_budget_is_unavailable(self) -> None:
        class CountingLocalTool(LocalToolClient):
            def __init__(self, store: DataStore) -> None:
                super().__init__(store)
                self.write_calls = 0

            def create_refund(
                self,
                order_id: str,
                customer_id: str,
                idempotency_key: str,
                approval: bool | None = None,
                approval_id: str | None = None,
            ) -> ToolResult:
                self.write_calls += 1
                return super().create_refund(
                    order_id,
                    customer_id,
                    idempotency_key,
                    approval,
                    approval_id,
                )

        store = DataStore.from_public_dir(DATA_DIR)
        for limits in (
            Limits(max_steps=3),
            Limits(max_transitions=2),
        ):
            with self.subTest(limits=limits):
                tools = CountingLocalTool(store)
                runtime = RafeeqRuntime(
                    DATA_DIR,
                    tool_client=tools,
                    settings=Settings(limits=limits),
                )
                result = runtime.run("refund delayed order TW-26008", "CUST-008")

                self.assertEqual(result["status"], "failed")
                self.assertEqual(result["outcome"], "runtime_error")
                self.assertEqual(tools.write_calls, 0)
                self.assertFalse(result["tool_observations"])

    def test_all_public_cases_finish_inside_every_budget(self) -> None:
        runtime = RafeeqRuntime(DATA_DIR)
        terminal = {"completed", "blocked", "needs_approval", "escalated", "failed"}
        cases = load_jsonl("tickets_dev.jsonl") + load_jsonl("eval_public.jsonl")

        for case in cases:
            with self.subTest(case_id=case.get("ticket_id", case.get("case_id"))):
                result = runtime.run(case["message"], case["customer_id"], locale=case["locale"])
                counters = result["counters"]
                self.assertIn(result["status"], terminal)
                self.assertLessEqual(counters["steps"], 6)
                self.assertLessEqual(counters["transitions"], 12)
                self.assertLessEqual(counters["handoffs"], 2)
                self.assertLessEqual(counters["reflections"], 1)


if __name__ == "__main__":
    unittest.main()
