"""Reflection is a bounded quality check, never an open-ended loop."""

from __future__ import annotations

import unittest

import _support  # noqa: F401 -- installs the local src path for plain unittest

from rafeeq.config import Limits
from rafeeq.state import AgentState


class ReflectionBoundTests(unittest.TestCase):
    def test_default_budget_allows_exactly_one_reflection(self) -> None:
        state = AgentState(customer_id="CUST-001", message="Track TW-26001")
        limits = Limits()

        self.assertTrue(state.reflect(limits))
        self.assertFalse(state.reflect(limits))
        self.assertEqual(state.reflection_count, 1)

    def test_reflection_ceiling_cannot_be_configured_above_one(self) -> None:
        with self.assertRaisesRegex(ValueError, "max_reflections"):
            Limits(max_reflections=2)

    def test_zero_reflection_budget_is_supported(self) -> None:
        state = AgentState(customer_id="CUST-001", message="Track TW-26001")
        self.assertFalse(state.reflect(Limits(max_reflections=0)))
        self.assertEqual(state.reflection_count, 0)


if __name__ == "__main__":
    unittest.main()
