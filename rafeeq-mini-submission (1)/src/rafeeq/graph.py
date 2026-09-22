"""Bounded deterministic runtime for the three-day Rafeeq Mini lab."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping
import uuid

from .agents import (
    AgentReply,
    LocalToolClient,
    OrderAgent,
    RefundAgent,
    RefundEvaluation,
    ToolClient,
    build_handoff,
    detect_locale,
    evaluate_refund,
    extract_order_id,
    supervisor_route,
)
from .approval import ApprovalStore
from .config import Limits, Settings
from .data import DataStore, OrderRecord
from .guards import GuardDecision, default_input_guard, guard_output
from .memory import SeedMemoryStore, SessionMemory
from .retrieval import PolicyRetriever
from .state import AgentState, Locale, Route, RunStatus
from .tracing import JsonlTracer


RouteFunction = Callable[[str, str | None], Route]
RefundGateFunction = Callable[
    [OrderRecord | Mapping[str, Any] | None, str, bool | None],
    RefundEvaluation,
]
InputGuardFunction = Callable[..., GuardDecision]


@dataclass(frozen=True, slots=True)
class ReflectionResult:
    """One bounded quality check, expressed without private reasoning."""

    checked: bool
    passed: bool
    code: str
    response: str


def bounded_reflection(state: AgentState, response: str, limits: Limits | None = None) -> ReflectionResult:
    """Perform at most one deterministic output-completeness check.

    This is a validator, not a hidden reasoning loop.  It can insert a safe
    fallback but cannot call tools or mutate business data.
    """

    active_limits = limits or Limits()
    if not state.reflect(active_limits):
        return ReflectionResult(False, bool(response.strip()), "REFLECTION_LIMIT", response)
    if response.strip():
        return ReflectionResult(True, True, "RESPONSE_PRESENT", response.strip())
    fallback = (
        "تعذر إعداد استجابة آمنة؛ حُوّل الطلب للمراجعة البشرية."
        if state.locale is Locale.AR
        else "A safe response could not be prepared; the request was escalated for human review."
    )
    return ReflectionResult(True, False, "EMPTY_RESPONSE_REPAIRED", fallback)


def should_stop(state: AgentState, limits: Limits | None = None) -> bool:
    """Return whether the graph is terminal or has reached a hard bound."""

    active_limits = limits or Limits()
    terminal = {
        RunStatus.COMPLETED,
        RunStatus.BLOCKED,
        RunStatus.NEEDS_APPROVAL,
        RunStatus.ESCALATED,
        RunStatus.FAILED,
    }
    return (
        state.status in terminal
        or state.step_count >= active_limits.max_steps
        or state.transition_count >= active_limits.max_transitions
        or state.handoff_count >= active_limits.max_handoffs
        or state.reflection_count >= active_limits.max_reflections
    )


@dataclass(frozen=True, slots=True)
class RunResult:
    """A typed runtime result with a JSON-friendly learner view."""

    state: AgentState
    trace_events: int

    def to_dict(self) -> dict[str, Any]:
        state = self.state
        return {
            "trace_id": state.trace_id,
            "session_id": state.session_id,
            "customer_id": state.customer_id,
            "locale": state.locale.value,
            "order_id": state.order_id,
            "route": state.route.value if state.route else None,
            "status": state.status.value,
            "outcome": state.outcome,
            "response": state.response,
            "approval_id": state.approval_id,
            "approval_status": state.approval_status,
            "risk_flags": list(state.risk_flags),
            "plan": list(state.plan),
            "current_step": state.current_step,
            "last_result": state.last_result,
            "subgoal": state.subgoal,
            "resolution": state.resolution,
            "last_action": state.last_action,
            "counters": {
                "steps": state.step_count,
                "transitions": state.transition_count,
                "handoffs": state.handoff_count,
                "reflections": state.reflection_count,
                "model_calls": state.model_calls,
                "tool_calls": state.tool_calls,
                "retrieval_calls": state.retrieval_calls,
            },
            "tool_observations": [dict(item) for item in state.tool_observations],
            "errors": list(state.errors),
            "trace_events": self.trace_events,
        }


class RafeeqRuntime:
    """Run the offline Rafeeq graph with optional injected tool adapters.

    Parameters are injection points rather than service credentials.  The
    default path loads local synthetic data and remains network-free.
    """

    def __init__(
        self,
        data_dir: str | Path | None = None,
        tool_client: ToolClient | None = None,
        trace_path: str | Path | None = None,
        route_fn: RouteFunction | None = None,
        refund_gate_fn: RefundGateFunction | None = None,
        input_guard_fn: InputGuardFunction | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or Settings.from_env()
        default_data_dir = Path(__file__).resolve().parents[2] / "data" / "public"
        self.data_dir = Path(data_dir) if data_dir is not None else default_data_dir
        self.data = DataStore.from_public_dir(self.data_dir)
        self.tools = tool_client or LocalToolClient(self.data)
        if not isinstance(self.tools, ToolClient):
            raise TypeError("tool_client must implement get_order and create_refund")
        self.tracer = JsonlTracer(trace_path)
        self.route_fn = route_fn or supervisor_route
        self.refund_gate_fn = refund_gate_fn or evaluate_refund
        self.input_guard_fn = input_guard_fn or default_input_guard
        self.approvals = ApprovalStore()
        self.order_agent = OrderAgent()
        self.refund_agent = RefundAgent(self.approvals, self.refund_gate_fn)
        self.policy_retriever = PolicyRetriever(self.data.policies)
        self.long_term_memory = SeedMemoryStore(self.data.memories)
        self._sessions: dict[tuple[str, str], SessionMemory] = {}

    def _counters(self, state: AgentState) -> dict[str, int]:
        return {
            "steps": state.step_count,
            "transitions": state.transition_count,
            "handoffs": state.handoff_count,
            "reflections": state.reflection_count,
            "model_calls": state.model_calls,
            "tool_calls": state.tool_calls,
            "retrieval_calls": state.retrieval_calls,
        }

    def _trace(
        self,
        state: AgentState,
        event: str,
        node: str,
        *,
        tool: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        model_calls_delta: int = 0,
        tool_calls_delta: int = 0,
        retrieval_calls_delta: int = 0,
    ) -> None:
        self.tracer.emit(
            trace_id=state.trace_id,
            session_id=state.session_id,
            event=event,
            node=node,
            status=state.status.value,
            route=state.route.value if state.route else None,
            outcome=state.outcome or None,
            tool=tool,
            risk_flags=tuple(state.risk_flags),
            model_calls_delta=model_calls_delta,
            tool_calls_delta=tool_calls_delta,
            retrieval_calls_delta=retrieval_calls_delta,
            counters=self._counters(state),
            metadata=metadata,
        )

    def _guard_input(self, message: str) -> GuardDecision:
        try:
            return self.input_guard_fn(message, max_chars=self.settings.limits.max_input_chars)
        except TypeError:
            return self.input_guard_fn(message)

    def _specialist_reply(
        self,
        state: AgentState,
        approval: bool | None,
    ) -> AgentReply:
        assert state.route is not None
        if "step_limit" in state.risk_flags:
            response = (
                "تم إيقاف الحلقة عند حد التنفيذ وتحويل الطلب للمراجعة."
                if state.locale is Locale.AR
                else "The loop was stopped at the execution limit and escalated for review."
            )
            return AgentReply("escalated_budget_exhausted", response)
        handoff = build_handoff(state.route, state)
        if state.route is Route.ORDERS:
            return self.order_agent.handle(handoff, self.tools)
        if state.route is Route.REFUND:
            return self.refund_agent.handle(handoff, self.tools, approval)
        if state.route is Route.ESCALATE:
            if handoff.task == "clarify_request":
                response = (
                    "اذكر رقم الطلب وما إذا كنت تريد التتبع أو الاسترداد."
                    if state.locale is Locale.AR
                    else "Provide the order ID and say whether you need tracking or a refund."
                )
                return AgentReply("needs_clarification", response)
            response = (
                "تم تحويل الطلب إلى موظف مختص."
                if state.locale is Locale.AR
                else "The request was handed to a human specialist."
            )
            return AgentReply("escalated", response)
        response = (
            "يمكنني مساعدتك في حالة الطلب أو تقييم الاسترداد. أرسل رقمًا بصيغة TW-26017."
            if state.locale is Locale.AR
            else "I can check an order or evaluate a refund. Send an ID such as TW-26017."
        )
        return AgentReply("needs_clarification", response)

    @staticmethod
    def _require_refund_terminal_budget(state: AgentState, limits: Limits) -> None:
        """Reserve the reflection and terminal edge before any refund write.

        A write must not succeed and then be reported as a failed run merely
        because the graph discovers too late that its remaining budget cannot
        reach a terminal state.
        """

        if state.step_count + 1 > limits.max_steps:
            raise RuntimeError("STEP_LIMIT_REACHED")
        if state.transition_count + 2 > limits.max_transitions:
            raise RuntimeError("TRANSITION_LIMIT_REACHED")

    def run_state(
        self,
        message: str,
        customer_id: str,
        locale: str | Locale | None = None,
        thread_id: str | None = None,
        approval: bool | None = None,
    ) -> RunResult:
        """Execute one bounded turn and return the typed result."""

        if approval is not None and not isinstance(approval, bool):
            raise TypeError("approval must be True, False, or None")
        chosen_locale = Locale(locale) if locale is not None else detect_locale(message)
        state = AgentState(
            customer_id=customer_id.strip().upper(),
            message=message,
            session_id=thread_id or uuid.uuid4().hex[:16],
            locale=chosen_locale,
        )
        starting_events = len(self.tracer.events)
        limits = self.settings.limits
        state.status = RunStatus.RUNNING
        try:
            state.advance("input_guard", limits)
            decision = self._guard_input(message)
            state.risk_flags = list(decision.flags)
            self._trace(state, "guard_checked", "input_guard", metadata={"code": decision.code, "flags": decision.flags})
            if not decision.allowed:
                state.route = Route.ESCALATE
                state.status = RunStatus.BLOCKED
                state.outcome = decision.code.casefold()
                state.response = decision.safe_text
                state.plan = ["validate_input", "stop"]
                state.subgoal = "block_unsafe_input"
                state.last_result = state.outcome
                state.resolution = state.response
                state.last_action = "blocked"
                self._trace(state, "run_finished", "input_guard")
                return RunResult(state, len(self.tracer.events) - starting_events)

            session_key = (state.customer_id, state.session_id)
            session = self._sessions.setdefault(
                session_key,
                SessionMemory(self.settings.limits.session_memory_items),
            )
            state.order_id = extract_order_id(message)
            recalled_order = False
            if state.order_id is None:
                for item in reversed(session.recent(self.settings.limits.session_memory_items)):
                    remembered = extract_order_id(item.summary)
                    if remembered:
                        state.order_id = remembered
                        recalled_order = True
                        break
            state.transition("to_supervisor", limits)
            state.advance("supervisor", limits)
            route = Route.ESCALATE if "step_limit" in state.risk_flags else self.route_fn(message, state.order_id)
            state.route = route if isinstance(route, Route) else Route(str(route))
            handoff = build_handoff(state.route, state)
            state.subgoal = handoff.task
            state.plan = ["validate_input", "route", handoff.task, "validate_output"]
            self._trace(
                state,
                "route_selected",
                "supervisor",
                metadata={"has_order_id": bool(state.order_id), "order_recalled": recalled_order},
            )

            state.transition("to_specialist", limits)
            state.advance(state.route.value, limits)
            if state.route is not Route.FINISH:
                state.handoff(limits)
            if state.route is Route.REFUND:
                self._require_refund_terminal_budget(state, limits)
            reply = self._specialist_reply(state, approval)
            state.outcome = reply.outcome
            state.response = reply.response
            state.approval_id = reply.approval_id
            state.last_result = reply.outcome
            state.resolution = reply.response
            state.tool_calls += reply.tool_calls
            structural_flags = {
                "ownership_mismatch": "cross_customer",
                "already_refunded": "duplicate",
                "requires_human_approval": "high_value",
            }
            added_flag = structural_flags.get(reply.outcome)
            if added_flag and added_flag not in state.risk_flags:
                state.risk_flags.append(added_flag)
            if reply.approval_id and "high_value" not in state.risk_flags:
                state.risk_flags.append("high_value")
            if reply.outcome == "requires_human_approval":
                state.approval_status = "pending"
            elif reply.approval_id and approval is True:
                state.approval_status = "approved"
            elif reply.approval_id and approval is False:
                state.approval_status = "rejected"
            if reply.tool_result:
                state.tool_observations.append(
                    {
                        "code": reply.tool_result.code,
                        "ok": reply.tool_result.ok,
                        "write_performed": reply.tool_result.write_performed,
                    }
                )
            self._trace(
                state,
                "specialist_finished",
                state.route.value,
                tool=("create_refund" if reply.tool_result and reply.tool_result.write_performed else "get_order" if reply.tool_result else None),
                metadata={"tool_code": reply.tool_result.code if reply.tool_result else None},
                tool_calls_delta=reply.tool_calls,
            )

            high_impact = state.route in {Route.REFUND, Route.ESCALATE} or bool(state.risk_flags)
            if high_impact:
                state.transition("to_reflection", limits)
                state.advance("reflection", limits)
                reflection = bounded_reflection(state, state.response, limits)
                state.response = reflection.response
                self._trace(
                    state,
                    "output_checked",
                    "reflection",
                    metadata={"code": reflection.code, "passed": reflection.passed},
                )
            else:
                self._trace(
                    state,
                    "reflection_skipped",
                    "reflection",
                    metadata={"reason": "low_impact_read"},
                )

            output = guard_output(state.response, forbidden_terms=("system prompt", "chain-of-thought"))
            state.response = output.safe_text
            state.resolution = state.response
            for flag in output.flags:
                if flag not in state.risk_flags:
                    state.risk_flags.append(flag)
            if not output.allowed:
                state.status = RunStatus.BLOCKED
                state.outcome = "output_blocked"
            elif reply.outcome == "requires_human_approval":
                state.status = RunStatus.NEEDS_APPROVAL
            elif reply.outcome in {"escalated", "escalated_budget_exhausted", "tool_error"}:
                state.status = RunStatus.ESCALATED
            else:
                state.status = RunStatus.COMPLETED
            state.transition("to_end", limits)
            state.last_action = "end"
            summary = f"route={state.route.value}; outcome={state.outcome}"
            if state.order_id:
                summary += f"; order_id={state.order_id}"
            session.add("assistant", summary)
            self._trace(state, "run_finished", "end", metadata={"output_flags": output.flags})
        except Exception as exc:
            state.status = RunStatus.FAILED
            candidate = str(exc).strip()
            allowed_codes = {
                "STEP_LIMIT_REACHED",
                "TRANSITION_LIMIT_REACHED",
                "HANDOFF_LIMIT_REACHED",
            }
            code = candidate if candidate in allowed_codes else type(exc).__name__.upper()
            state.errors.append(code)
            state.outcome = "runtime_error"
            state.response = (
                "توقف التشغيل بأمان وحُوّل الطلب للمراجعة."
                if state.locale is Locale.AR
                else "The run stopped safely and was sent for review."
            )
            state.last_action = "failed_safe"
            self._trace(state, "run_failed", "error", metadata={"error_type": type(exc).__name__, "code": code})
        return RunResult(state, len(self.tracer.events) - starting_events)

    def run(
        self,
        message: str,
        customer_id: str,
        locale: str | Locale | None = None,
        thread_id: str | None = None,
        approval: bool | None = None,
    ) -> dict[str, Any]:
        """Execute one turn and return a notebook-friendly dictionary."""

        return self.run_state(message, customer_id, locale, thread_id, approval).to_dict()

    def session_memory(self, thread_id: str, customer_id: str | None = None) -> SessionMemory:
        """Return one customer's bounded thread memory without cross-owner reuse.

        ``customer_id`` may be omitted only when exactly one owner has used the
        thread. New or ambiguous thread IDs require an explicit owner.
        """

        clean_thread = thread_id.strip()
        if not clean_thread:
            raise ValueError("thread_id is required")
        if customer_id is not None:
            key = (customer_id.strip().upper(), clean_thread)
            return self._sessions.setdefault(
                key,
                SessionMemory(self.settings.limits.session_memory_items),
            )
        matches = [memory for (_owner, thread), memory in self._sessions.items() if thread == clean_thread]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise ValueError("customer_id is required for a new thread")
        raise ValueError("customer_id is required for a thread used by multiple customers")

    def health_snapshot(self) -> dict[str, Any]:
        """Return a credential-free readiness snapshot."""

        return {
            "status": "ready",
            "llm_mode": self.settings.llm_mode,
            "network_required": False,
            "orders_loaded": len(self.data.orders),
            "policies_loaded": len(self.data.policies),
            "memories_loaded": len(self.data.memories),
            "limits": {
                "steps": self.settings.limits.max_steps,
                "transitions": self.settings.limits.max_transitions,
                "handoffs": self.settings.limits.max_handoffs,
                "reflections": self.settings.limits.max_reflections,
            },
        }


def health_snapshot(runtime: RafeeqRuntime | None = None) -> dict[str, Any]:
    """Convenience health check used by the Colab environment doctor."""

    return (runtime or RafeeqRuntime()).health_snapshot()
