"""Public refund-gate, approval, idempotency and no-retry checks."""

from __future__ import annotations

from dataclasses import asdict
import unittest

from _support import DATA_DIR

from rafeeq.agents import (
    Handoff,
    LocalToolClient,
    RefundAgent,
    ToolResult,
    evaluate_refund,
    refund_idempotency_key,
)
from rafeeq.approval import ApprovalStore, approval_id_for
from rafeeq.data import DataStore, OrderRecord
from rafeeq.state import Locale, Route


class FailingWriteTool:
    """A deterministic fake used only to prove that writes are not retried."""

    def __init__(self, order: OrderRecord) -> None:
        self.order = order
        self.read_calls = 0
        self.write_calls = 0

    def get_order(self, order_id: str, customer_id: str) -> ToolResult:
        self.read_calls += 1
        return ToolResult(True, "ORDER_FOUND", asdict(self.order))

    def create_refund(self, order_id: str, customer_id: str, idempotency_key: str) -> ToolResult:
        self.write_calls += 1
        return ToolResult(False, "SIMULATED_TRANSIENT_FAILURE", {}, False)


class CountingTool(LocalToolClient):
    def __init__(self, store: DataStore) -> None:
        super().__init__(store)
        self.write_calls = 0

    def create_refund(self, order_id: str, customer_id: str, idempotency_key: str) -> ToolResult:
        self.write_calls += 1
        return super().create_refund(order_id, customer_id, idempotency_key)


class RefundGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.store = DataStore.from_public_dir(DATA_DIR)

    @staticmethod
    def _handoff(customer_id: str, order_id: str) -> Handoff:
        return Handoff(Route.REFUND, customer_id, order_id, Locale.EN, "evaluate_refund")

    def test_sar_500_boundary_is_eligible_without_human_approval(self) -> None:
        order = self.store.order_for_customer("TW-26003", "CUST-003")
        decision = evaluate_refund(order, "CUST-003")

        self.assertIsNotNone(order)
        self.assertEqual(order.amount_sar, 500.0)
        self.assertTrue(decision.eligible)
        self.assertFalse(decision.requires_approval)
        self.assertEqual(decision.outcome, "eligible")

    def test_above_sar_500_requires_explicit_human_approval(self) -> None:
        order = self.store.order_for_customer("TW-26004", "CUST-004")
        pending = evaluate_refund(order, "CUST-004")
        approved = evaluate_refund(order, "CUST-004", approval=True)

        self.assertIsNotNone(order)
        self.assertEqual(order.amount_sar, 500.01)
        self.assertTrue(pending.requires_approval)
        self.assertFalse(pending.eligible)
        self.assertEqual(pending.outcome, "requires_human_approval")
        self.assertTrue(approved.eligible)
        self.assertEqual(approved.outcome, "approved")

    def test_prior_refund_is_rejected_before_idempotency_logic(self) -> None:
        tools = CountingTool(self.store)
        reply = RefundAgent(ApprovalStore()).handle(
            self._handoff("CUST-005", "TW-26005"),
            tools,
        )

        self.assertEqual(reply.outcome, "already_refunded")
        self.assertEqual(tools.write_calls, 0)

    def test_rerun_is_idempotent_not_a_prior_refund(self) -> None:
        tools = CountingTool(self.store)
        agent = RefundAgent(ApprovalStore())
        handoff = self._handoff("CUST-003", "TW-26003")
        first = agent.handle(handoff, tools)
        second = agent.handle(handoff, tools)

        self.assertEqual(first.outcome, "created")
        self.assertTrue(first.tool_result.write_performed)
        self.assertEqual(second.outcome, "created")
        self.assertEqual(second.tool_result.code, "IDEMPOTENT_REPLAY")
        self.assertFalse(second.tool_result.write_performed)
        self.assertEqual(first.tool_result.data["refund_id"], second.tool_result.data["refund_id"])

    def test_failed_write_is_attempted_once_without_retry(self) -> None:
        order = self.store.order_for_customer("TW-26003", "CUST-003")
        self.assertIsNotNone(order)
        tools = FailingWriteTool(order)
        reply = RefundAgent(ApprovalStore()).handle(
            self._handoff("CUST-003", "TW-26003"),
            tools,
        )

        self.assertEqual(reply.outcome, "tool_error")
        self.assertEqual(tools.read_calls, 1)
        self.assertEqual(tools.write_calls, 1)

    def test_local_tool_repeats_policy_and_approval_at_its_boundary(self) -> None:
        tools = LocalToolClient(self.store)
        blocked = (
            ("TW-26004", "CUST-004", "APPROVAL_REQUIRED"),
            ("TW-26005", "CUST-005", "ALREADY_REFUNDED"),
            ("TW-26007", "CUST-007", "REFUND_NOT_ELIGIBLE"),
        )
        for order_id, customer_id, expected_code in blocked:
            with self.subTest(order_id=order_id):
                result = tools.create_refund(
                    order_id,
                    customer_id,
                    refund_idempotency_key(customer_id, order_id),
                )
                self.assertFalse(result.ok)
                self.assertEqual(result.code, expected_code)
                self.assertFalse(result.write_performed)

        approved = tools.create_refund(
            "TW-26004",
            "CUST-004",
            "caller-key-is-not-authoritative",
            approval=True,
            approval_id=approval_id_for("CUST-004", "TW-26004"),
        )
        self.assertTrue(approved.ok)
        self.assertTrue(approved.write_performed)

    def test_local_tool_derives_idempotency_key_instead_of_trusting_caller(self) -> None:
        tools = LocalToolClient(self.store)
        first = tools.create_refund("TW-26003", "CUST-003", "first-caller-key")
        replay = tools.create_refund("TW-26003", "CUST-003", "different-caller-key")

        self.assertTrue(first.write_performed)
        self.assertFalse(replay.write_performed)
        self.assertEqual(replay.code, "IDEMPOTENT_REPLAY")
        self.assertEqual(first.data["refund_id"], replay.data["refund_id"])


if __name__ == "__main__":
    unittest.main()
