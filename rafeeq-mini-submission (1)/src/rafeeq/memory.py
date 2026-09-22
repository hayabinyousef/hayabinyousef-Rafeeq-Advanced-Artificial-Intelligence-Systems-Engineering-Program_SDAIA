"""Bounded session memory and scoped semantic recall using standard Python."""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from datetime import datetime, timezone
import math
import re
from typing import Iterable, Sequence

from .data import MemoryRecord


_SPACE_RE = re.compile(r"\s+")


def _normalise(text: str) -> str:
    return _SPACE_RE.sub(" ", text.casefold().strip())


def char_ngrams(text: str, n: int = 3) -> Counter[str]:
    """Return character n-gram counts suitable for Arabic and English."""

    normalized = f" {_normalise(text)} "
    if len(normalized) <= n:
        return Counter({normalized: 1}) if normalized.strip() else Counter()
    return Counter(normalized[index : index + n] for index in range(len(normalized) - n + 1))


def rank_texts(query: str, texts: Sequence[str]) -> list[tuple[int, float]]:
    """Rank texts with deterministic character n-gram TF-IDF cosine scores.

    The function has no fitted global state, which keeps notebook reruns
    reproducible.  Callers must apply authorization and expiry filters first.
    """

    if not texts:
        return []
    documents = [char_ngrams(text) for text in texts]
    query_terms = char_ngrams(query)
    document_frequency: Counter[str] = Counter()
    for document in documents:
        document_frequency.update(document.keys())
    count = len(documents)

    def vector(terms: Counter[str]) -> dict[str, float]:
        total = sum(terms.values()) or 1
        return {
            term: (frequency / total) * (math.log((count + 1) / (document_frequency.get(term, 0) + 1)) + 1.0)
            for term, frequency in terms.items()
        }

    query_vector = vector(query_terms)
    query_norm = math.sqrt(sum(value * value for value in query_vector.values()))
    ranked: list[tuple[int, float]] = []
    for index, document in enumerate(documents):
        document_vector = vector(document)
        document_norm = math.sqrt(sum(value * value for value in document_vector.values()))
        numerator = sum(query_vector.get(term, 0.0) * value for term, value in document_vector.items())
        score = numerator / (query_norm * document_norm) if query_norm and document_norm else 0.0
        ranked.append((index, round(score, 8)))
    return sorted(ranked, key=lambda item: (-item[1], item[0]))


@dataclass(frozen=True, slots=True)
class SessionItem:
    """A short, deliberately minimal session event."""

    role: str
    summary: str


class SessionMemory:
    """Small in-process memory that never stores hidden model reasoning."""

    def __init__(self, max_items: int = 20) -> None:
        if max_items < 1:
            raise ValueError("max_items must be positive")
        self._items: deque[SessionItem] = deque(maxlen=max_items)

    def add(self, role: str, summary: str) -> None:
        """Add a short operational summary, not a raw message or trace."""

        clean_role = role.strip().lower()
        if clean_role not in {"user", "assistant", "tool", "system"}:
            raise ValueError("Unsupported session role")
        clean_summary = _normalise(summary)[:300]
        if clean_summary:
            self._items.append(SessionItem(clean_role, clean_summary))

    def recent(self, limit: int = 5) -> tuple[SessionItem, ...]:
        """Return the newest bounded items in chronological order."""

        if limit < 0:
            raise ValueError("limit cannot be negative")
        return tuple(self._items)[-limit:] if limit else ()

    def clear(self) -> None:
        self._items.clear()


@dataclass(frozen=True, slots=True)
class MemoryHit:
    """A scoped recall result and its inspectable similarity score."""

    record: MemoryRecord
    score: float


class SeedMemoryStore:
    """Read-only long-term memory over the synthetic seed dataset."""

    def __init__(self, records: Iterable[MemoryRecord]) -> None:
        self._records = tuple(records)

    def recall(
        self,
        query: str,
        customer_id: str,
        *,
        now: datetime | None = None,
        locale: str | None = None,
        related_order_id: str | None = None,
        top_k: int = 3,
    ) -> list[MemoryHit]:
        """Filter by scope, activity and expiry *before* semantic ranking."""

        if top_k < 1:
            return []
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        owner = customer_id.strip().upper()
        wanted_locale = locale.strip().lower() if locale else None
        wanted_order = related_order_id.strip().upper() if related_order_id else None
        scoped = [
            record
            for record in self._records
            if record.customer_id == owner
            and record.active
            and (record.expires_at is None or record.expires_at > current)
            and (wanted_locale is None or record.locale == wanted_locale)
            and (wanted_order is None or record.related_order_id in {None, wanted_order})
        ]
        ranked = rank_texts(query, [record.summary for record in scoped])
        return [MemoryHit(scoped[index], score) for index, score in ranked[:top_k]]
