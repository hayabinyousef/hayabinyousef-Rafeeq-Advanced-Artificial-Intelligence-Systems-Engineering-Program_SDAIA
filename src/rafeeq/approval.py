"""Explicit human-approval records for high-value refund requests."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
import hashlib


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class ApprovalRequest:
    """An auditable request that contains no raw user message."""

    approval_id: str
    action: str
    customer_id: str
    resource_id: str
    amount_sar: float
    status: ApprovalStatus
    created_at: str
    decided_at: str | None = None


def approval_id_for(customer_id: str, resource_id: str, action: str = "refund") -> str:
    """Create a stable identifier so reruns do not duplicate approvals."""

    source = f"{action}|{customer_id.upper()}|{resource_id.upper()}".encode("utf-8")
    return "APR-" + hashlib.sha256(source).hexdigest()[:12].upper()


class ApprovalStore:
    """In-memory human-approval queue used by the offline lab."""

    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}

    def request(self, customer_id: str, resource_id: str, amount_sar: float) -> ApprovalRequest:
        approval_id = approval_id_for(customer_id, resource_id)
        existing = self._requests.get(approval_id)
        if existing:
            return existing
        item = ApprovalRequest(
            approval_id=approval_id,
            action="refund",
            customer_id=customer_id.upper(),
            resource_id=resource_id.upper(),
            amount_sar=float(amount_sar),
            status=ApprovalStatus.PENDING,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._requests[approval_id] = item
        return item

    def decide(self, approval_id: str, approved: bool) -> ApprovalRequest:
        """Record one explicit decision; conflicting re-decisions are rejected."""

        current = self._requests[approval_id]
        wanted = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        if current.status is not ApprovalStatus.PENDING and current.status is not wanted:
            raise ValueError("Approval already has a conflicting final decision")
        if current.status is wanted:
            return current
        updated = replace(current, status=wanted, decided_at=datetime.now(timezone.utc).isoformat())
        self._requests[approval_id] = updated
        return updated

    def get(self, approval_id: str) -> ApprovalRequest | None:
        return self._requests.get(approval_id)
