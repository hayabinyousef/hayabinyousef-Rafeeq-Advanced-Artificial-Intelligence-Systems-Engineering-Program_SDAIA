"""Typed state shared by every node in the bounded Rafeeq graph."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any
import uuid

from .config import Limits


class Locale(str, Enum):
    """Supported response languages."""

    AR = "ar"
    EN = "en"


class Route(str, Enum):
    """Supervisor destinations."""

    ORDERS = "orders"
    REFUND = "refund"
    FINISH = "finish"
    ESCALATE = "escalate"


class RunStatus(str, Enum):
    """Observable lifecycle states; none contains private reasoning."""

    NEW = "new"
    RUNNING = "running"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    NEEDS_APPROVAL = "needs_approval"
    ESCALATED = "escalated"
    FAILED = "failed"


@dataclass(slots=True)
class AgentState:
    """Serializable state for one learner-visible run.

    ``message`` is intentionally excluded from :meth:`safe_snapshot`; traces
    must never contain raw user messages or hidden chain-of-thought.
    """

    customer_id: str
    message: str
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    locale: Locale = Locale.EN
    order_id: str | None = None
    route: Route | None = None
    status: RunStatus = RunStatus.NEW
    response: str = ""
    outcome: str = ""
    last_action: str = "created"
    step_count: int = 0
    transition_count: int = 0
    handoff_count: int = 0
    reflection_count: int = 0
    approval_id: str | None = None
    approval_status: str = "not_required"
    risk_flags: list[str] = field(default_factory=list)
    plan: list[str] = field(default_factory=list)
    current_step: int = 0
    last_result: str | None = None
    subgoal: str | None = None
    resolution: str | None = None
    model_calls: int = 0
    tool_calls: int = 0
    retrieval_calls: int = 0
    tool_observations: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def advance(self, action: str, limits: Limits) -> None:
        """Record one graph node and enforce the six-step ceiling."""

        if self.step_count >= limits.max_steps:
            raise RuntimeError("STEP_LIMIT_REACHED")
        self.step_count += 1
        self.current_step = self.step_count
        self.last_action = action

    def transition(self, action: str, limits: Limits) -> None:
        """Record one edge and enforce the transition ceiling."""

        if self.transition_count >= limits.max_transitions:
            raise RuntimeError("TRANSITION_LIMIT_REACHED")
        self.transition_count += 1
        self.last_action = action

    def handoff(self, limits: Limits) -> None:
        """Record a typed delegation without allowing handoff loops."""

        if self.handoff_count >= limits.max_handoffs:
            raise RuntimeError("HANDOFF_LIMIT_REACHED")
        self.handoff_count += 1

    def reflect(self, limits: Limits) -> bool:
        """Reserve one bounded output check; return ``False`` if unavailable."""

        if self.reflection_count >= limits.max_reflections:
            return False
        self.reflection_count += 1
        return True

    def safe_snapshot(self) -> dict[str, Any]:
        """Return trace-safe fields, excluding the raw message and tool data."""

        values = asdict(self)
        values.pop("message", None)
        values.pop("tool_observations", None)
        values["locale"] = self.locale.value
        values["route"] = self.route.value if self.route else None
        values["status"] = self.status.value
        return values
