"""Rafeeq Mini: a deterministic, offline-first agent workflow.

The public API intentionally stays small so it can be introduced gradually in
one Colab notebook.  No module in this package requires a network connection or
an API key.
"""

from .config import Limits, Settings
from .agents import (
    build_handoff,
    detect_locale,
    evaluate_refund,
    extract_order_id,
    supervisor_route,
)
from .graph import (
    RafeeqRuntime,
    RunResult,
    bounded_reflection,
    health_snapshot,
    should_stop,
)
from .state import AgentState, Locale, Route, RunStatus

__all__ = [
    "AgentState",
    "Limits",
    "Locale",
    "RafeeqRuntime",
    "Route",
    "RunResult",
    "RunStatus",
    "Settings",
    "bounded_reflection",
    "build_handoff",
    "detect_locale",
    "evaluate_refund",
    "extract_order_id",
    "health_snapshot",
    "should_stop",
    "supervisor_route",
]

__version__ = "0.9.0rc1"
