"""Transparent bilingual routing checks backed by public cases."""

from __future__ import annotations

import unittest

from _support import load_jsonl

from rafeeq.agents import detect_locale, extract_order_id, supervisor_route


class RoutingTests(unittest.TestCase):
    def test_public_development_and_evaluation_routes(self) -> None:
        cases = load_jsonl("tickets_dev.jsonl") + load_jsonl("eval_public.jsonl")
        for case in cases:
            # Unsafe inputs are stopped by the input guard before the router;
            # they are exercised in test_security.py instead.
            if case.get("risk_label") == "injection" or "prompt_injection" in case.get(
                "expected_risk_flags", []
            ):
                continue
            with self.subTest(case_id=case.get("ticket_id", case.get("case_id"))):
                order_id = extract_order_id(case["message"])
                route = supervisor_route(case["message"], order_id)
                self.assertEqual(route.value, case["expected_route"])

    def test_refund_has_priority_when_status_and_refund_coexist(self) -> None:
        message = "Check order TW-26012 and start a refund if eligible."
        self.assertEqual(supervisor_route(message, extract_order_id(message)).value, "refund")

    def test_order_id_and_locale_are_normalized(self) -> None:
        self.assertEqual(extract_order_id("status tw_26017 please"), "TW-26017")
        self.assertEqual(detect_locale("حالة الطلب").value, "ar")
        self.assertEqual(detect_locale("Track the order").value, "en")


if __name__ == "__main__":
    unittest.main()
