"""Deterministic input and output guardrails for the public simulation."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


@dataclass(frozen=True, slots=True)
class GuardDecision:
    """A machine-readable guard result with a safe learner-facing reason."""

    allowed: bool
    code: str
    safe_text: str
    flags: tuple[str, ...] = ()


_INJECTION_PATTERNS = (
    re.compile(r"\bignore\s+(?:all\s+)?(?:(?:previous|prior)\s+)?(?:system\s+)?instructions?\b", re.I),
    re.compile(r"\breveal\s+(the\s+)?(system|developer)\s+prompt\b", re.I),
    re.compile(r"\b(disable|bypass|override)\s+(the\s+)?(guard|policy|safety)", re.I),
    re.compile(r"(?:تجاهل|الغ|ألغي)\s+(?:(?:كل|جميع)\s+)?(?:التعليمات|الضوابط|السياسات|القيود)", re.I),
    re.compile(r"\bignore\s+(?:all\s+)?(?:constraints|restrictions|rules)\b", re.I),
    re.compile(r"(?:اكشف|اعرض)\s+(?:رسالة|تعليمات)\s+(?:النظام|المطور)", re.I),
)

_SECRET_PATTERNS = (
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\b(?:ghp_[A-Za-z0-9]{12,}|github_pat_[A-Za-z0-9_]{12,})\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{12,}=*\b", re.I),
    re.compile(r"\b(?:api[_ -]?key|password|secret)\s*[:=]\s*\S+", re.I),
)

_SENSITIVE_PATTERNS = (
    re.compile(r"(?<!\d)(?:\d[ -]?){15,19}(?!\d)"),  # payment card-like
    re.compile(r"(?<!\d)[12]\d{9}(?!\d)"),  # Saudi national/Iqama-like
)


def guard_input(message: str, *, max_chars: int = 2_000) -> GuardDecision:
    """Reject oversized, secret-bearing, or instruction-injection inputs."""

    if not isinstance(message, str) or not message.strip():
        return GuardDecision(False, "EMPTY_INPUT", "Please enter a support request. | فضلاً أدخل طلب الدعم.")
    if len(message) > max_chars:
        return GuardDecision(False, "INPUT_TOO_LONG", "Please shorten the request. | يرجى اختصار الطلب.")
    flags: list[str] = []
    blocking: list[str] = []
    if any(pattern.search(message) for pattern in _INJECTION_PATTERNS):
        blocking.append("prompt_injection")
    if any(pattern.search(message) for pattern in _SECRET_PATTERNS):
        blocking.append("secret")
    if any(pattern.search(message) for pattern in _SENSITIVE_PATTERNS):
        blocking.append("sensitive_identifier")
    normalized = message.casefold()
    if re.search(r"\b(?:skip|bypass|ignore)\s+(?:the\s+)?approval\b", normalized) or re.search(
        r"(?:تجاوز|تخط|تجاهل)\s+(?:خطوة\s+)?الموافقة", normalized
    ):
        flags.append("approval_bypass")
    if re.search(r"approval[_ ]status\s*(?:to|=|:)\s*approved", normalized) or re.search(
        r"(?:عيّن|اجعل)\s+حالة\s+الموافقة\s+(?:إلى\s+)?موافق", normalized
    ):
        flags.append("privilege_escalation")
    if re.search(r"\b(?:keep\s+)?retry(?:ing)?\b.*\b(?:write|refund)\b", normalized) or re.search(
        r"(?:أعد|كرر)\s+(?:محاولة\s+)?(?:الكتابة|الاسترداد)", normalized
    ):
        flags.append("write_retry")
    if re.search(r"\b(?:never\s+stop|loop\s+forever|without\s+stopping)\b", normalized) or re.search(
        r"(?:بلا\s+توقف|دون\s+توقف|لا\s+تُ?نهِ|كرر.*(?:دائمًا|للأبد))", normalized
    ):
        flags.append("step_limit")
    amounts = [float(value) for value in re.findall(r"(?<!\d)(\d+(?:\.\d{1,2})?)\s*(?:sar|ريال)", normalized)]
    if any(amount > 500 for amount in amounts):
        flags.append("high_value")
    all_flags = tuple(dict.fromkeys(blocking + flags))
    if blocking:
        return GuardDecision(
            False,
            "UNSAFE_INPUT",
            "The request was blocked; remove secrets or unsafe instructions. | حُجب الطلب؛ احذف الأسرار أو التعليمات غير الآمنة.",
            all_flags,
        )
    return GuardDecision(True, "INPUT_OK", message.strip(), all_flags)


_OUTPUT_REDACTIONS = (
    (re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{8,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\b(?:ghp_[A-Za-z0-9]{8,}|github_pat_[A-Za-z0-9_]{8,})\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{12,}=*\b", re.I), "[REDACTED_TOKEN]"),
    (re.compile(r"\b(?:api[_ -]?key|password|secret)\s*[:=]\s*\S+", re.I), "[REDACTED_SECRET]"),
    (re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
    (re.compile(r"(?<!\d)(?:\+?966|0)?5\d{8}(?!\d)"), "[REDACTED_PHONE]"),
    (re.compile(r"(?<!\d)[12]\d{9}(?!\d)"), "[REDACTED_IDENTIFIER]"),
    (re.compile(r"(?<!\d)(?:\d[ -]?){15,19}(?!\d)"), "[REDACTED_NUMBER]"),
    (re.compile(r"\bCUST-\d+\b", re.I), "[REDACTED_CUSTOMER]"),
)


def redact_text(text: str) -> tuple[str, tuple[str, ...]]:
    """Redact common secrets and identifiers and report applied redactions."""

    clean = str(text)
    flags: list[str] = []
    for pattern, replacement in _OUTPUT_REDACTIONS:
        clean, count = pattern.subn(replacement, clean)
        if count:
            flags.append(replacement.strip("[]").lower())
    return clean, tuple(flags)


def guard_output(text: str, *, forbidden_terms: Iterable[str] = ()) -> GuardDecision:
    """Sanitize output and block accidental internal-instruction disclosure."""

    clean, flags = redact_text(text)
    lower = clean.casefold()
    if any(pattern.search(clean) for pattern in _INJECTION_PATTERNS):
        return GuardDecision(
            False,
            "UNTRUSTED_TOOL_OUTPUT",
            "Untrusted instructions in tool output were ignored. | تم تجاهل تعليمات غير موثوقة في مخرجات الأداة.",
            flags + ("indirect_prompt_injection",),
        )
    if any(term.casefold() in lower for term in forbidden_terms if term):
        return GuardDecision(
            False,
            "OUTPUT_BLOCKED",
            "The response was withheld for safety. | تم حجب الاستجابة لأسباب أمنية.",
            flags + ("forbidden_term",),
        )
    return GuardDecision(True, "OUTPUT_OK", clean, flags)


def default_input_guard(message: str, max_chars: int = 2_000) -> GuardDecision:
    """Named adapter used by :class:`rafeeq.graph.RafeeqRuntime`."""

    return guard_input(message, max_chars=max_chars)
