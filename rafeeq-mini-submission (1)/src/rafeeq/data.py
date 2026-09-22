"""Small, strict loaders for Rafeeq's synthetic public datasets."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping


def parse_bool(value: object) -> bool:
    """Parse an explicit JSON/CSV boolean; ambiguous values are rejected."""

    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"Invalid boolean: {value!r}")


def parse_datetime(value: str | None) -> datetime | None:
    """Parse an ISO-8601 timestamp as timezone-aware UTC."""

    if not value:
        return None
    text = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def read_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    """Yield non-empty JSON objects with useful line-level errors."""

    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{source}:{line_number}: invalid JSON") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{source}:{line_number}: expected an object")
            yield value


@dataclass(frozen=True, slots=True)
class OrderRecord:
    """Synthetic order row used by the local tool adapter."""

    order_id: str
    customer_id: str
    locale: str
    status: str
    amount_sar: float
    delay_days: int
    already_refunded: bool
    last_update: str

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> "OrderRecord":
        required = ("order_id", "customer_id", "status", "amount_sar", "delay_days")
        missing = [key for key in required if str(row.get(key, "")).strip() == ""]
        if missing:
            raise ValueError(f"Order row missing: {', '.join(missing)}")
        return cls(
            order_id=str(row["order_id"]).strip().upper(),
            customer_id=str(row["customer_id"]).strip().upper(),
            locale=str(row.get("locale", "en")).strip().lower(),
            status=str(row["status"]).strip().lower(),
            amount_sar=float(row["amount_sar"]),
            delay_days=int(row["delay_days"]),
            already_refunded=parse_bool(row.get("already_refunded", False)),
            last_update=str(row.get("last_update", "")).strip(),
        )


@dataclass(frozen=True, slots=True)
class PolicyRecord:
    """One versioned policy chunk."""

    policy_id: str
    version: str
    locale: str
    category: str
    active: bool
    text: str
    effective_from: datetime | None = None
    expires_at: datetime | None = None

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> "PolicyRecord":
        return cls(
            policy_id=str(row["policy_id"]).strip(),
            version=str(row.get("version", "0")).strip(),
            locale=str(row.get("locale", "en")).strip().lower(),
            category=str(row.get("category", "general")).strip().lower(),
            active=parse_bool(row.get("active", True)),
            text=str(row["text"]).strip(),
            effective_from=parse_datetime(str(row.get("effective_from") or "")),
            expires_at=parse_datetime(str(row.get("expires_at") or "")),
        )


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    """One synthetic long-term memory item."""

    memory_id: str
    customer_id: str
    locale: str
    memory_type: str
    summary: str
    related_order_id: str | None
    created_at: datetime
    expires_at: datetime | None
    active: bool

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> "MemoryRecord":
        created = parse_datetime(str(row.get("created_at") or ""))
        if created is None:
            raise ValueError("Memory row requires created_at")
        return cls(
            memory_id=str(row["memory_id"]).strip(),
            customer_id=str(row["customer_id"]).strip().upper(),
            locale=str(row.get("locale", "en")).strip().lower(),
            memory_type=str(row.get("memory_type", "note")).strip().lower(),
            summary=str(row["summary"]).strip(),
            related_order_id=(str(row.get("related_order_id") or "").strip().upper() or None),
            created_at=created,
            expires_at=parse_datetime(str(row.get("expires_at") or "")),
            active=parse_bool(row.get("active", True)),
        )


class DataStore:
    """Immutable indexes over the small public datasets."""

    def __init__(
        self,
        orders: Iterable[OrderRecord] = (),
        policies: Iterable[PolicyRecord] = (),
        memories: Iterable[MemoryRecord] = (),
    ) -> None:
        order_items = tuple(orders)
        self.orders = {item.order_id: item for item in order_items}
        if len(self.orders) != len(order_items):
            raise ValueError("Duplicate order_id in dataset")
        self.policies = tuple(policies)
        self.memories = tuple(memories)

    @classmethod
    def from_public_dir(cls, directory: str | Path) -> "DataStore":
        """Load whichever standard public files exist in ``directory``."""

        root = Path(directory)
        orders: list[OrderRecord] = []
        policies: list[PolicyRecord] = []
        memories: list[MemoryRecord] = []
        orders_path = root / "orders.csv"
        if orders_path.exists():
            with orders_path.open("r", encoding="utf-8-sig", newline="") as handle:
                orders = [OrderRecord.from_mapping(row) for row in csv.DictReader(handle)]
        policy_path = root / "policy_chunks.jsonl"
        if policy_path.exists():
            policies = [PolicyRecord.from_mapping(row) for row in read_jsonl(policy_path)]
        memory_path = root / "memory_seed.jsonl"
        if memory_path.exists():
            memories = [MemoryRecord.from_mapping(row) for row in read_jsonl(memory_path)]
        return cls(orders=orders, policies=policies, memories=memories)

    def order_for_customer(self, order_id: str, customer_id: str) -> OrderRecord | None:
        """Return an order only when both identifiers match.

        This method deliberately makes a missing order and another customer's
        order indistinguishable to callers.
        """

        order = self.orders.get(order_id.strip().upper())
        if order is None or order.customer_id != customer_id.strip().upper():
            return None
        return order
