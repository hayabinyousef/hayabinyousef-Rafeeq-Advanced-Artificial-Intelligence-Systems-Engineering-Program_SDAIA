"""Redacted JSONL tracing without raw messages or chain-of-thought."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

from .guards import redact_text


_DENIED_KEYS = {
    "message",
    "raw_message",
    "prompt",
    "system_prompt",
    "chain_of_thought",
    "cot",
    "reasoning",
    "customer_id",
    "email",
    "phone",
}
_ORDER_RE = re.compile(r"\bTW-\d+\b", re.I)


def fingerprint(value: str) -> str:
    """Return a short, one-way correlation label."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _safe_value(key: str, value: Any) -> Any:
    lowered = key.casefold()
    if lowered in _DENIED_KEYS or any(token in lowered for token in ("secret", "token", "password", "api_key")):
        return "[REDACTED]"
    if isinstance(value, Mapping):
        return {str(child_key): _safe_value(str(child_key), child) for child_key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe_value(key, item) for item in value]
    if isinstance(value, str):
        clean, _ = redact_text(value)
        clean = _ORDER_RE.sub(lambda match: f"ORDER#{fingerprint(match.group(0).upper())}", clean)
        return clean[:500]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)[:200]


@dataclass(frozen=True, slots=True)
class TraceEvent:
    """An operational event containing decisions and counters only."""

    timestamp_utc: str
    trace_id: str
    span_id: str
    parent_span_id: str | None
    session_id: str
    component: str
    event_type: str
    status: str
    latency_ms: float = 0.0
    route: str | None = None
    outcome: str | None = None
    tool: str | None = None
    risk_flags: tuple[str, ...] = ()
    model_calls_delta: int = 0
    tool_calls_delta: int = 0
    retrieval_calls_delta: int = 0
    redacted: bool = True
    counters: Mapping[str, int] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def event(self) -> str:
        """Backward-compatible in-memory alias; not duplicated in JSONL."""

        return self.event_type

    @property
    def node(self) -> str:
        """Backward-compatible in-memory alias; not duplicated in JSONL."""

        return self.component


class JsonlTracer:
    """Collect safe events in memory and optionally append them to JSONL."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self.events: list[TraceEvent] = []
        self._last_span_by_trace: dict[str, str] = {}
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(
        self,
        *,
        trace_id: str,
        session_id: str,
        event: str,
        node: str,
        status: str,
        route: str | None = None,
        outcome: str | None = None,
        tool: str | None = None,
        latency_ms: float = 0.0,
        risk_flags: tuple[str, ...] = (),
        model_calls_delta: int = 0,
        tool_calls_delta: int = 0,
        retrieval_calls_delta: int = 0,
        counters: Mapping[str, int] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        """Create one redacted event.  Raw text keys are always discarded."""

        safe_metadata = _safe_value("metadata", dict(metadata or {}))
        parent_span_id = self._last_span_by_trace.get(trace_id)
        span_number = sum(1 for existing in self.events if existing.trace_id == trace_id) + 1
        span_id = hashlib.sha256(f"{trace_id}|{span_number}".encode("utf-8")).hexdigest()[:16]
        item = TraceEvent(
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            session_id=f"SESSION#{fingerprint(session_id)}",
            component=str(node),
            event_type=str(event),
            status=str(status),
            latency_ms=max(0.0, float(latency_ms)),
            route=str(route) if route else None,
            outcome=str(outcome) if outcome else None,
            tool=str(tool) if tool else None,
            risk_flags=tuple(str(flag) for flag in risk_flags),
            model_calls_delta=max(0, int(model_calls_delta)),
            tool_calls_delta=max(0, int(tool_calls_delta)),
            retrieval_calls_delta=max(0, int(retrieval_calls_delta)),
            redacted=True,
            counters={str(key): int(value) for key, value in (counters or {}).items()},
            metadata=safe_metadata,
        )
        self.events.append(item)
        self._last_span_by_trace[trace_id] = span_id
        if self.path:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(asdict(item), ensure_ascii=False, sort_keys=True) + "\n")
        return item

    def for_trace(self, trace_id: str) -> tuple[TraceEvent, ...]:
        return tuple(event for event in self.events if event.trace_id == trace_id)
