"""Deterministic supervisor, typed delegation and specialist agents."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import inspect
import re
from typing import Any, Callable, Mapping, Protocol, runtime_checkable

from .approval import ApprovalStore, approval_id_for
from .data import DataStore, OrderRecord
from .state import AgentState, Locale, Route


_ORDER_RE = re.compile(r"\bTW[\s_-]?(\d{5,10})\b", re.I)
_ARABIC_RE = re.compile(r"[\u0600-\u06ff]")


def extract_order_id(text: str) -> str | None:
    """Extract and normalize a synthetic Tawseel order identifier."""

    match = _ORDER_RE.search(text or "")
    return f"TW-{match.group(1)}" if match else None


def detect_locale(text: str) -> Locale:
    """Choose Arabic when Arabic letters are present; otherwise English."""

    return Locale.AR if _ARABIC_RE.search(text or "") else Locale.EN


_REFUND_WORDS = (
    "refund", "return my money", "money back", "reimburse",
    "استرداد", "استرجاع", "استعادة المبلغ", "رجعوا المبلغ", "فلوسي",
)
_ORDER_WORDS = (
    "order", "status", "where is", "track", "delivery", "shipment", "delayed",
    "طلب", "طلبي", "حالة", "وين", "تتبع", "شحنة", "توصيل", "متأخر",
)
_ESCALATE_WORDS = (
    "human", "manager", "complaint", "agent", "escalate",
    "موظف", "مدير", "شكوى", "تصعيد", "انسان", "إنسان",
)
_HELP_WORDS = ("help", "assist", "support", "مساعدة", "ساعدني")


def supervisor_route(message: str, order_id: str | None = None) -> Route:
    """Route with transparent keywords; refund takes precedence over status."""

    normalized = message.casefold()
    if any(word in normalized for word in _REFUND_WORDS):
        return Route.REFUND
    if any(word in normalized for word in _ESCALATE_WORDS):
        return Route.ESCALATE
    if order_id:
        return Route.ORDERS
    if any(word in normalized for word in _HELP_WORDS):
        return Route.ESCALATE
    if any(word in normalized for word in _ORDER_WORDS):
        return Route.ORDERS
    return Route.FINISH


@dataclass(frozen=True, slots=True)
class Handoff:
    """A typed, minimum-necessary message from supervisor to specialist."""

    target: Route
    customer_id: str
    order_id: str | None
    locale: Locale
    task: str


def build_handoff(route: Route, state: AgentState) -> Handoff:
    """Build a delegation without including the raw user message."""

    task = {
        Route.ORDERS: "read_order_status",
        Route.REFUND: "evaluate_refund",
        Route.ESCALATE: (
            "create_human_handoff"
            if any(word in state.message.casefold() for word in _ESCALATE_WORDS)
            else "clarify_request"
        ),
        Route.FINISH: "answer_without_tool",
    }[route]
    return Handoff(route, state.customer_id, state.order_id, state.locale, task)


@dataclass(frozen=True, slots=True)
class ToolResult:
    """Structured tool response; failures are values rather than exceptions."""

    ok: bool
    code: str
    data: Mapping[str, Any]
    write_performed: bool = False


@runtime_checkable
class ToolClient(Protocol):
    """Narrow injectable tool contract used by the runtime."""

    def get_order(self, order_id: str, customer_id: str) -> ToolResult: ...

    def create_refund(
        self,
        order_id: str,
        customer_id: str,
        idempotency_key: str,
        approval: bool | None = None,
        approval_id: str | None = None,
    ) -> ToolResult: ...


class LocalToolClient:
    """Offline adapter over :class:`DataStore` with idempotent writes."""

    def __init__(self, store: DataStore) -> None:
        self.store = store
        self._refunds: dict[str, ToolResult] = {}

    def get_order(self, order_id: str, customer_id: str) -> ToolResult:
        order = self.store.order_for_customer(order_id, customer_id)
        if order is None:
            return ToolResult(False, "ORDER_NOT_ACCESSIBLE", {})
        return ToolResult(True, "ORDER_FOUND", asdict(order))

    def create_refund(
        self,
        order_id: str,
        customer_id: str,
        idempotency_key: str,
        approval: bool | None = None,
        approval_id: str | None = None,
    ) -> ToolResult:
        # Treat every caller-provided value as untrusted. The tool boundary
        # repeats the policy decision and derives its own idempotency key so a
        # caller cannot bypass the agent or create duplicates by changing keys.
        del idempotency_key
        order = self.store.order_for_customer(order_id, customer_id)
        if order is None:
            return ToolResult(False, "ORDER_NOT_ACCESSIBLE", {})
        evaluation = evaluate_refund(order, customer_id, approval)
        if evaluation.requires_approval:
            return ToolResult(False, "APPROVAL_REQUIRED", {})
        if not evaluation.eligible:
            failure_codes = {
                "already_refunded": "ALREADY_REFUNDED",
                "not_eligible": "REFUND_NOT_ELIGIBLE",
                "approval_rejected": "APPROVAL_REJECTED",
                "ownership_mismatch": "ORDER_NOT_ACCESSIBLE",
            }
            return ToolResult(False, failure_codes.get(evaluation.outcome, "REFUND_NOT_ALLOWED"), {})
        if order.amount_sar > 500:
            expected_approval_id = approval_id_for(customer_id, order_id)
            if approval is not True or approval_id != expected_approval_id:
                return ToolResult(False, "APPROVAL_SCOPE_MISMATCH", {})

        effective_key = refund_idempotency_key(customer_id, order_id)
        if effective_key in self._refunds:
            previous = self._refunds[effective_key]
            return ToolResult(previous.ok, "IDEMPOTENT_REPLAY", previous.data, False)
        reference = "RFD-" + hashlib.sha256(effective_key.encode("utf-8")).hexdigest()[:10].upper()
        result = ToolResult(
            True,
            "REFUND_CREATED",
            {"refund_id": reference, "order_id": order.order_id, "status": "created"},
            True,
        )
        self._refunds[effective_key] = result
        return result


@dataclass(frozen=True, slots=True)
class RefundEvaluation:
    """Deterministic refund decision before any write tool can run."""

    eligible: bool
    outcome: str
    requires_approval: bool = False


def evaluate_refund(
    order: OrderRecord | Mapping[str, Any] | None,
    customer_id: str,
    approval: bool | None = None,
) -> RefundEvaluation:
    """Apply ownership, delay, duplicate and amount gates in that order."""

    if order is None:
        return RefundEvaluation(False, "ownership_mismatch")
    owner = order.customer_id if isinstance(order, OrderRecord) else str(order.get("customer_id", ""))
    if owner.upper() != customer_id.strip().upper():
        return RefundEvaluation(False, "ownership_mismatch")
    raw_refunded = order.already_refunded if isinstance(order, OrderRecord) else order.get("already_refunded", False)
    already_refunded = raw_refunded if isinstance(raw_refunded, bool) else str(raw_refunded).lower() == "true"
    if already_refunded:
        return RefundEvaluation(False, "already_refunded")
    delay_days = order.delay_days if isinstance(order, OrderRecord) else int(order.get("delay_days", 0))
    if delay_days <= 2:
        return RefundEvaluation(False, "not_eligible")
    amount = order.amount_sar if isinstance(order, OrderRecord) else float(order.get("amount_sar", 0.0))
    if amount > 500:
        if approval is True:
            return RefundEvaluation(True, "approved")
        if approval is False:
            return RefundEvaluation(False, "approval_rejected")
        return RefundEvaluation(False, "requires_human_approval", True)
    return RefundEvaluation(True, "eligible")


def refund_idempotency_key(customer_id: str, order_id: str) -> str:
    source = f"refund|{customer_id.upper()}|{order_id.upper()}".encode("utf-8")
    return hashlib.sha256(source).hexdigest()


@dataclass(frozen=True, slots=True)
class AgentReply:
    """Specialist output consumed by the graph."""

    outcome: str
    response: str
    tool_result: ToolResult | None = None
    approval_id: str | None = None
    tool_calls: int = 0


class OrderAgent:
    """Read-only order specialist."""

    def handle(self, handoff: Handoff, tools: ToolClient) -> AgentReply:
        if not handoff.order_id:
            response = "يرجى تزويدي برقم الطلب بصيغة TW-26017." if handoff.locale is Locale.AR else "Please provide an order ID such as TW-26017."
            return AgentReply("needs_clarification", response)
        result = tools.get_order(handoff.order_id, handoff.customer_id)
        if not result.ok:
            response = "تعذر الوصول إلى هذا الطلب. تحقق من الرقم والحساب." if handoff.locale is Locale.AR else "This order is not accessible. Check the number and account."
            return AgentReply("ownership_mismatch", response, result, tool_calls=1)
        status = str(result.data.get("status", "unknown"))
        response = (
            f"حالة الطلب {handoff.order_id}: {status}."
            if handoff.locale is Locale.AR
            else f"Order {handoff.order_id} status: {status}."
        )
        return AgentReply(status, response, result, tool_calls=1)


class RefundAgent:
    """Refund specialist with a deterministic gate and one-shot write."""

    def __init__(
        self,
        approvals: ApprovalStore,
        gate_fn: Callable[[OrderRecord | Mapping[str, Any] | None, str, bool | None], RefundEvaluation] = evaluate_refund,
    ) -> None:
        self.approvals = approvals
        self.gate_fn = gate_fn

    def handle(self, handoff: Handoff, tools: ToolClient, approval: bool | None = None) -> AgentReply:
        if not handoff.order_id:
            response = "يرجى تزويدي برقم الطلب لتقييم الاسترداد." if handoff.locale is Locale.AR else "Please provide the order ID to evaluate the refund."
            return AgentReply("needs_clarification", response)
        lookup = tools.get_order(handoff.order_id, handoff.customer_id)
        if not lookup.ok:
            response = "تعذر التحقق من ملكية الطلب." if handoff.locale is Locale.AR else "The order ownership could not be verified."
            return AgentReply("ownership_mismatch", response, lookup, tool_calls=1)
        evaluation = self.gate_fn(lookup.data, handoff.customer_id, approval)
        amount = float(lookup.data.get("amount_sar", 0.0))
        decided_request = None
        if amount > 500 and approval is not None:
            decided_request = self.approvals.request(handoff.customer_id, handoff.order_id, amount)
            decided_request = self.approvals.decide(decided_request.approval_id, approval)
        if evaluation.requires_approval:
            request = self.approvals.request(
                handoff.customer_id,
                handoff.order_id,
                amount,
            )
            response = "يتطلب هذا الاسترداد موافقة بشرية بسبب قيمة الطلب." if handoff.locale is Locale.AR else "This refund requires human approval because of the order value."
            return AgentReply(evaluation.outcome, response, lookup, request.approval_id, tool_calls=1)
        if not evaluation.eligible:
            messages = {
                "already_refunded": ("تم استرداد هذا الطلب مسبقًا.", "This order was already refunded."),
                "not_eligible": ("الطلب غير مؤهل للاسترداد وفق شرط التأخير.", "The order is not eligible under the delay rule."),
                "approval_rejected": ("لم تتم الموافقة على طلب الاسترداد.", "The refund request was not approved."),
                "ownership_mismatch": ("تعذر التحقق من ملكية الطلب.", "The order ownership could not be verified."),
            }
            ar, en = messages[evaluation.outcome]
            return AgentReply(
                evaluation.outcome,
                ar if handoff.locale is Locale.AR else en,
                lookup,
                decided_request.approval_id if decided_request else None,
                tool_calls=1,
            )
        # Write tools are never retried.  The deterministic key makes a notebook
        # cell rerun safe while preserving evidence of whether a write occurred.
        write = tools.create_refund
        parameters = inspect.signature(write).parameters.values()
        supports_approval = any(parameter.name == "approval" for parameter in parameters) or any(
            parameter.kind is inspect.Parameter.VAR_KEYWORD for parameter in parameters
        )
        write_args = (
            handoff.order_id,
            handoff.customer_id,
            refund_idempotency_key(handoff.customer_id, handoff.order_id),
        )
        # Signature inspection preserves compatibility with a day-one teaching
        # double while still invoking the write exactly once.
        if supports_approval:
            result = write(
                *write_args,
                approval=approval,
                approval_id=decided_request.approval_id if decided_request else None,
            )
        else:
            result = write(*write_args)
        if not result.ok:
            response = "تعذر إنشاء الاسترداد؛ حُوّل الطلب للمراجعة." if handoff.locale is Locale.AR else "The refund could not be created; the request was escalated."
            return AgentReply(
                "tool_error",
                response,
                result,
                decided_request.approval_id if decided_request else None,
                tool_calls=2,
            )
        response = "تم إنشاء طلب الاسترداد بنجاح." if handoff.locale is Locale.AR else "The refund request was created successfully."
        return AgentReply(
            "created",
            response,
            result,
            decided_request.approval_id if decided_request else None,
            tool_calls=2,
        )
