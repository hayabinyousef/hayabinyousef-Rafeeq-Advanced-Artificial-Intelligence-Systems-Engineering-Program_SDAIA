"""Public checks for scope-first memory and current-policy retrieval."""

from __future__ import annotations

from datetime import datetime, timezone
import unittest

from _support import DATA_DIR

from rafeeq.data import DataStore
from rafeeq.graph import RafeeqRuntime
from rafeeq.memory import SeedMemoryStore
from rafeeq.retrieval import PolicyRetriever


NOW = datetime(2026, 9, 17, 12, 0, tzinfo=timezone.utc)


class MemoryScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = DataStore.from_public_dir(DATA_DIR)

    def test_owner_filter_runs_before_similarity_ranking(self) -> None:
        store = SeedMemoryStore(self.data.memories)
        hits = store.recall(
            "تعذر تسليم الطلب وفتح طلب متابعة",
            "CUST-011",
            now=NOW,
            locale="ar",
            top_k=10,
        )
        ids = [hit.record.memory_id for hit in hits]

        self.assertEqual(ids, ["MEM-004"])
        self.assertNotIn("MEM-008", ids)  # near-duplicate text owned by CUST-009
        self.assertTrue(all(hit.record.customer_id == "CUST-011" for hit in hits))

    def test_expired_and_inactive_memory_are_removed_before_rank(self) -> None:
        store = SeedMemoryStore(self.data.memories)
        expired = store.recall("refund timing", "CUST-015", now=NOW, locale="en")
        inactive = store.recall("delayed order follow-up", "CUST-016", now=NOW, locale="en")

        self.assertEqual(expired, [])
        self.assertEqual(inactive, [])

    def test_only_active_current_policy_is_searchable(self) -> None:
        retriever = PolicyRetriever(self.data.policies)
        current = retriever.current(now=NOW, locale="en", category="refund_limit")
        hits = retriever.search(
            "human approval above SAR 500",
            now=NOW,
            locale="en",
            category="refund_limit",
        )

        self.assertEqual([item.policy_id for item in current], ["REF-03-EN"])
        self.assertEqual(hits[0].record.policy_id, "REF-03-EN")
        self.assertNotIn("300", hits[0].record.text)

    def test_session_memory_is_scoped_by_customer_even_when_thread_id_is_reused(self) -> None:
        runtime = RafeeqRuntime(DATA_DIR)
        runtime.run("status order TW-26017", "CUST-011", thread_id="shared-thread")
        second = runtime.run("refund it", "CUST-012", thread_id="shared-thread")

        self.assertIsNone(second["order_id"])
        self.assertEqual(second["route"], "refund")
        self.assertEqual(second["outcome"], "needs_clarification")
        self.assertEqual(runtime.session_memory("shared-thread", "CUST-011").recent()[-1].role, "assistant")
        with self.assertRaisesRegex(ValueError, "multiple customers"):
            runtime.session_memory("shared-thread")


if __name__ == "__main__":
    unittest.main()
