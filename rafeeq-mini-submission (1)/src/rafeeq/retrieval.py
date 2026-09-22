"""Current-policy retrieval with filtering before similarity ranking."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Iterable

from .data import PolicyRecord
from .memory import rank_texts


def _version_key(version: str) -> tuple[int | str, ...]:
    parts: list[int | str] = []
    for part in re.split(r"[._-]", version):
        parts.append(int(part) if part.isdigit() else part.casefold())
    return tuple(parts)


@dataclass(frozen=True, slots=True)
class PolicyHit:
    """A current policy chunk and its inspectable similarity score."""

    record: PolicyRecord
    score: float


class PolicyRetriever:
    """Retrieve only active, effective and most-current policy versions."""

    def __init__(self, records: Iterable[PolicyRecord]) -> None:
        self._records = tuple(records)

    def current(
        self,
        *,
        now: datetime | None = None,
        locale: str | None = None,
        category: str | None = None,
    ) -> list[PolicyRecord]:
        """Return latest active records after temporal and locale filtering."""

        current_time = now or datetime.now(timezone.utc)
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
        selected = [
            record
            for record in self._records
            if record.active
            and (record.effective_from is None or record.effective_from <= current_time)
            and (record.expires_at is None or record.expires_at > current_time)
            and (locale is None or record.locale == locale.strip().lower())
            and (category is None or record.category == category.strip().lower())
        ]
        # A policy ID identifies one logical chunk across versions.  Category
        # and locale protect datasets that reuse an ID in translated editions.
        latest: dict[tuple[str, str, str], PolicyRecord] = {}
        for record in selected:
            key = (record.policy_id, record.locale, record.category)
            previous = latest.get(key)
            if previous is None or _version_key(record.version) > _version_key(previous.version):
                latest[key] = record
        return sorted(latest.values(), key=lambda item: (item.category, item.policy_id, item.locale))

    def search(
        self,
        query: str,
        *,
        now: datetime | None = None,
        locale: str | None = None,
        category: str | None = None,
        top_k: int = 3,
    ) -> list[PolicyHit]:
        """Rank the already-filtered current policy set."""

        if top_k < 1:
            return []
        current = self.current(now=now, locale=locale, category=category)
        ranked = rank_texts(query, [record.text for record in current])
        return [PolicyHit(current[index], score) for index, score in ranked[:top_k]]
