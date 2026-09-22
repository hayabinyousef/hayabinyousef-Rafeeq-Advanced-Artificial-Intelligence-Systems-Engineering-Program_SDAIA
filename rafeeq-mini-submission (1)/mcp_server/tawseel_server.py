#!/usr/bin/env python3
"""Tawseel MCP teaching server over real stdio transport.

The implementation is deliberately small and dependency-free so it runs on a
free Google Colab CPU.  It follows the MCP 2026-07-28 JSON-RPC message shapes
used by this lab, including stateless discovery, ping, ``tools/list`` and
``tools/call``.  A legacy initialization exchange remains optional.  It is an
educational implementation, not a general MCP SDK and not a production
authentication boundary.

Security boundary used by the lab
---------------------------------
The model controls only the tool ``arguments``.  The host runtime attaches the
authenticated customer identity and any approval under the vendor-prefixed
``params._meta["com.rafeeq.training/runtimeContext"]`` field.  Consequently
``customer_id``, ``amount`` and ``approval`` never appear in a model-visible
input schema.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping


PROTOCOL_VERSION = "2026-07-28"
SERVER_NAME = "com.rafeeq/tawseel-training"
SERVER_VERSION = "0.2.0"
PROTOCOL_VERSION_META_KEY = "io.modelcontextprotocol/protocolVersion"
CLIENT_CAPABILITIES_META_KEY = "io.modelcontextprotocol/clientCapabilities"
CLIENT_INFO_META_KEY = "io.modelcontextprotocol/clientInfo"
RUNTIME_META_KEY = "com.rafeeq.training/runtimeContext"
DEFAULT_ORDERS_PATH = Path(__file__).resolve().parents[1] / "data" / "public" / "orders.csv"


@dataclass(frozen=True)
class Order:
    """Validated projection of one synthetic order record."""

    order_id: str
    customer_id: str
    locale: str
    status: str
    amount_sar: Decimal
    delay_days: int
    already_refunded: bool
    last_update: str

    @classmethod
    def from_row(cls, row: Mapping[str, str]) -> "Order":
        try:
            return cls(
                order_id=row["order_id"].strip(),
                customer_id=row["customer_id"].strip(),
                locale=row["locale"].strip(),
                status=row["status"].strip(),
                amount_sar=Decimal(row["amount_sar"].strip()),
                delay_days=int(row["delay_days"].strip()),
                already_refunded=row["already_refunded"].strip().lower() == "true",
                last_update=row["last_update"].strip(),
            )
        except (KeyError, ValueError, InvalidOperation) as exc:
            raise ValueError("orders.csv contains an invalid record") from exc


class ToolFailure(Exception):
    """A safe, structured tool-level failure returned inside CallToolResult."""

    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


def _object_schema(properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


def _tool_result_schema() -> dict[str, Any]:
    """Describe both successful and structured error tool results."""

    return _object_schema(
        {
            "ok": {"type": "boolean"},
            "tool": {"type": "string"},
            "data": {"type": "object"},
            "error": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "message": {"type": "string"},
                    "retryable": {"type": "boolean"},
                },
                "required": ["code", "message", "retryable"],
                "additionalProperties": False,
            },
        },
        ["ok", "tool"],
    )


TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "get_order_status",
        "title": "Get order status",
        "description": "Read the status of one synthetic Tawseel order owned by the authenticated customer.",
        "inputSchema": _object_schema(
            {
                "order_id": {
                    "type": "string",
                    "pattern": r"^TW-[0-9]{5}$",
                    "description": "Synthetic order identifier, for example TW-26017.",
                }
            },
            ["order_id"],
        ),
        "outputSchema": _tool_result_schema(),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "get_refund_context",
        "title": "Get refund context",
        "description": "Read derived refund eligibility without changing the synthetic order.",
        "inputSchema": _object_schema(
            {
                "order_id": {
                    "type": "string",
                    "pattern": r"^TW-[0-9]{5}$",
                    "description": "Synthetic order identifier.",
                }
            },
            ["order_id"],
        ),
        "outputSchema": _tool_result_schema(),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "create_refund_request",
        "title": "Create simulated refund request",
        "description": "Create an in-memory refund request after ownership, policy and trusted approval gates pass.",
        "inputSchema": _object_schema(
            {
                "order_id": {
                    "type": "string",
                    "pattern": r"^TW-[0-9]{5}$",
                    "description": "Synthetic order identifier.",
                },
                "reason": {
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 240,
                    "description": "Short customer-provided reason; do not include sensitive data.",
                },
            },
            ["order_id", "reason"],
        ),
        "outputSchema": _tool_result_schema(),
        "annotations": {
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
]


class TawseelToolService:
    """Owns synthetic data and the in-memory write simulation."""

    def __init__(self, orders_path: Path = DEFAULT_ORDERS_PATH, state_file: Path | None = None) -> None:
        self.orders_path = Path(orders_path)
        self.state_file = Path(state_file) if state_file is not None else None
        self._orders: dict[str, Order] | None = None
        self._refund_requests: dict[str, dict[str, Any]] = {}
        self._refund_write_count = 0

    def _load_write_state(self) -> None:
        if self.state_file is None or not self.state_file.exists():
            return
        try:
            payload = json.loads(self.state_file.read_text(encoding="utf-8"))
            requests = payload.get("refund_requests", {})
            write_count = payload.get("refund_write_count", 0)
            if not isinstance(requests, dict) or not isinstance(write_count, int) or write_count < 0:
                raise ValueError("invalid state shape")
            self._refund_requests = {
                str(key): dict(value) for key, value in requests.items() if isinstance(value, Mapping)
            }
            self._refund_write_count = write_count
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            raise ToolFailure("STATE_INVALID", "The simulated write state is invalid.") from exc

    def _save_write_state(self) -> None:
        if self.state_file is None:
            return
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.state_file.with_name(self.state_file.name + ".tmp")
        payload = {
            "version": 1,
            "refund_write_count": self._refund_write_count,
            "refund_requests": self._refund_requests,
        }
        try:
            temporary.write_text(
                json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                encoding="utf-8",
            )
            os.replace(temporary, self.state_file)
        except (OSError, UnicodeError) as exc:
            raise ToolFailure("STATE_WRITE_FAILED", "The simulated write could not be committed safely.") from exc

    def _load_orders(self) -> dict[str, Order]:
        if self._orders is not None:
            return self._orders
        if not self.orders_path.is_file():
            raise ToolFailure(
                "DATA_UNAVAILABLE",
                "The synthetic orders dataset is unavailable.",
                retryable=False,
            )
        try:
            with self.orders_path.open("r", encoding="utf-8", newline="") as handle:
                records = [Order.from_row(row) for row in csv.DictReader(handle)]
        except (OSError, UnicodeError, ValueError, csv.Error) as exc:
            raise ToolFailure(
                "DATA_INVALID",
                "The synthetic orders dataset could not be read safely.",
                retryable=False,
            ) from exc
        if not records or any(not order.order_id for order in records):
            raise ToolFailure("DATA_INVALID", "The synthetic orders dataset is empty or invalid.")
        by_id = {order.order_id: order for order in records}
        if len(by_id) != len(records):
            raise ToolFailure("DATA_INVALID", "The synthetic orders dataset contains duplicate order IDs.")
        self._orders = by_id
        return by_id

    @staticmethod
    def _require_runtime_meta(params: Mapping[str, Any]) -> dict[str, Any]:
        meta = params.get("_meta")
        runtime = meta.get(RUNTIME_META_KEY) if isinstance(meta, Mapping) else None
        if not isinstance(runtime, Mapping):
            raise ToolFailure("RUNTIME_METADATA_REQUIRED", "Trusted runtime metadata is required.")
        customer_id = runtime.get("customer_id")
        request_id = runtime.get("request_id")
        if not isinstance(customer_id, str) or not customer_id.strip():
            raise ToolFailure("AUTH_CONTEXT_REQUIRED", "Authenticated customer context is required.")
        if not isinstance(request_id, str) or not request_id.strip():
            raise ToolFailure("REQUEST_ID_REQUIRED", "A runtime request identifier is required.")
        return dict(runtime)

    def _owned_order(self, order_id: Any, runtime: Mapping[str, Any]) -> Order:
        if not isinstance(order_id, str) or not order_id.strip():
            raise ToolFailure("INVALID_ARGUMENT", "order_id must be a non-empty string.")
        order = self._load_orders().get(order_id.strip())
        if order is None or order.customer_id != runtime["customer_id"]:
            # Missing and foreign IDs intentionally share one result to prevent
            # order enumeration and disclose no status, amount or owner detail.
            raise ToolFailure(
                "ORDER_FORBIDDEN",
                "The order is not available to this authenticated customer.",
            )
        return order

    @staticmethod
    def _refund_gate(order: Order) -> tuple[str, str]:
        if order.already_refunded:
            return "already_refunded", "This order has already been refunded."
        if order.delay_days <= 2:
            return "not_eligible", "The synthetic policy requires a delay greater than two days."
        if order.amount_sar > Decimal("500.00"):
            return "requires_human_approval", "A human approval is required above SAR 500."
        return "eligible", "The order passes the synthetic refund policy."

    @staticmethod
    def _money(value: Decimal) -> str:
        return f"{value.quantize(Decimal('0.01')):.2f}"

    @staticmethod
    def _require_exact_arguments(arguments: Any, required: set[str], allowed: set[str]) -> dict[str, Any]:
        if not isinstance(arguments, Mapping):
            raise ToolFailure("INVALID_ARGUMENT", "arguments must be a JSON object.")
        keys = set(arguments)
        missing = sorted(required - keys)
        extra = sorted(keys - allowed)
        if missing or extra:
            detail = "Missing: " + ", ".join(missing) if missing else "Unexpected: " + ", ".join(extra)
            raise ToolFailure("INVALID_ARGUMENT", detail + ".")
        return dict(arguments)

    @staticmethod
    def _validate_approval(runtime: Mapping[str, Any], order: Order) -> dict[str, Any]:
        approval = runtime.get("approval")
        if not isinstance(approval, Mapping) or approval.get("granted") is not True:
            raise ToolFailure("APPROVAL_REQUIRED", "Explicit trusted approval is required before this write.")
        if approval.get("tool") != "create_refund_request" or approval.get("order_id") != order.order_id:
            raise ToolFailure("APPROVAL_SCOPE_MISMATCH", "The approval does not cover this exact action.")
        approval_id = approval.get("approval_id")
        if not isinstance(approval_id, str) or not approval_id.strip():
            raise ToolFailure("APPROVAL_INVALID", "The approval record is missing its identifier.")
        if order.amount_sar > Decimal("500.00") and approval.get("level") != "human":
            raise ToolFailure("HUMAN_APPROVAL_REQUIRED", "A human approval is required above SAR 500.")
        return dict(approval)

    @staticmethod
    def _idempotency_key(order: Order) -> str:
        material = f"refund-request:v1|{order.customer_id}|{order.order_id}".encode("utf-8")
        return "rr_" + hashlib.sha256(material).hexdigest()[:24]

    def call(self, name: str, arguments: Any, params: Mapping[str, Any]) -> dict[str, Any]:
        runtime = self._require_runtime_meta(params)
        if name == "get_order_status":
            args = self._require_exact_arguments(arguments, {"order_id"}, {"order_id"})
            order = self._owned_order(args["order_id"], runtime)
            data = {
                "order_id": order.order_id,
                "status": order.status,
                "locale": order.locale,
                "last_update": order.last_update,
            }
            return _tool_success(name, data, runtime, operation="read")

        if name == "get_refund_context":
            args = self._require_exact_arguments(arguments, {"order_id"}, {"order_id"})
            order = self._owned_order(args["order_id"], runtime)
            gate, explanation = self._refund_gate(order)
            data = {
                "order_id": order.order_id,
                "delay_days": order.delay_days,
                "amount_sar": self._money(order.amount_sar),
                "already_refunded": order.already_refunded,
                "gate": gate,
                "explanation": explanation,
            }
            return _tool_success(name, data, runtime, operation="read")

        if name == "create_refund_request":
            args = self._require_exact_arguments(
                arguments,
                {"order_id", "reason"},
                {"order_id", "reason"},
            )
            reason = args["reason"]
            if not isinstance(reason, str) or not 3 <= len(reason.strip()) <= 240:
                raise ToolFailure("INVALID_ARGUMENT", "reason must contain 3 to 240 characters.")
            order = self._owned_order(args["order_id"], runtime)
            gate, explanation = self._refund_gate(order)
            if gate == "already_refunded":
                raise ToolFailure("ALREADY_REFUNDED", explanation)
            if gate == "not_eligible":
                raise ToolFailure("REFUND_NOT_ELIGIBLE", explanation)
            self._validate_approval(runtime, order)
            key = self._idempotency_key(order)
            self._load_write_state()
            existing = self._refund_requests.get(key)
            if existing is not None:
                data = {
                    **existing,
                    "idempotent_replay": True,
                    "refund_write_count": self._refund_write_count,
                }
                return _tool_success(name, data, runtime, operation="write-simulation")
            self._refund_write_count += 1
            request = {
                "request_id": key,
                "refund_request_id": key,
                "idempotency_key": key,
                "order_id": order.order_id,
                "status": "created",
                "idempotent_replay": False,
                "refund_write_count": self._refund_write_count,
                "simulation": True,
            }
            self._refund_requests[key] = request
            try:
                self._save_write_state()
            except ToolFailure:
                self._refund_requests.pop(key, None)
                self._refund_write_count -= 1
                raise
            return _tool_success(name, dict(request), runtime, operation="write-simulation")

        raise ToolFailure("TOOL_NOT_FOUND", "The requested tool is not available.")


def _safe_text(payload: Mapping[str, Any]) -> str:
    """Create the MCP text fallback as a JSON copy of structuredContent."""

    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _result_meta(runtime: Mapping[str, Any], operation: str) -> dict[str, Any]:
    return {
        "serverInfo": {
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "transport": "stdio",
            "simulation": True,
        },
        "requestId": runtime.get("request_id"),
        "operation": operation,
        PROTOCOL_VERSION_META_KEY: PROTOCOL_VERSION,
    }


def _tool_success(
    name: str,
    data: dict[str, Any],
    runtime: Mapping[str, Any],
    *,
    operation: str,
) -> dict[str, Any]:
    structured = {"ok": True, "tool": name, "data": data}
    return {
        "structuredContent": structured,
        "content": [{"type": "text", "text": _safe_text(structured)}],
        "isError": False,
        "resultType": "complete",
        "_meta": _result_meta(runtime, operation),
    }


def _tool_error(name: str, failure: ToolFailure, runtime: Mapping[str, Any] | None) -> dict[str, Any]:
    structured = {
        "ok": False,
        "tool": name,
        "error": {
            "code": failure.code,
            "message": failure.message,
            "retryable": failure.retryable,
        },
    }
    safe_runtime = runtime or {"request_id": None}
    return {
        "structuredContent": structured,
        "content": [{"type": "text", "text": _safe_text(structured)}],
        "isError": True,
        "resultType": "complete",
        "_meta": _result_meta(safe_runtime, "error"),
    }


def _jsonrpc_error(request_id: Any, code: int, message: str, data: Any | None = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


class MCPServer:
    """Line-oriented JSON-RPC dispatcher for the teaching subset of MCP."""

    def __init__(self, service: TawseelToolService | None = None) -> None:
        self.service = service or TawseelToolService()
        self.initialized = False

    @staticmethod
    def _runtime_if_present(params: Any) -> dict[str, Any] | None:
        if not isinstance(params, Mapping):
            return None
        meta = params.get("_meta")
        runtime = meta.get(RUNTIME_META_KEY) if isinstance(meta, Mapping) else None
        return dict(runtime) if isinstance(runtime, Mapping) else None

    @staticmethod
    def _validate_request_metadata(params: Mapping[str, Any]) -> ToolFailure | None:
        meta = params.get("_meta")
        if not isinstance(meta, Mapping):
            return ToolFailure("REQUEST_METADATA_REQUIRED", "Per-request MCP metadata is required.")
        if meta.get(PROTOCOL_VERSION_META_KEY) != PROTOCOL_VERSION:
            return ToolFailure("PROTOCOL_METADATA_INVALID", "Protocol metadata is missing or unsupported.")
        if not isinstance(meta.get(CLIENT_CAPABILITIES_META_KEY), Mapping):
            return ToolFailure("CAPABILITIES_METADATA_REQUIRED", "Client capabilities metadata is required.")
        client_info = meta.get(CLIENT_INFO_META_KEY)
        if client_info is not None and not isinstance(client_info, Mapping):
            return ToolFailure("CLIENT_INFO_METADATA_INVALID", "Client info metadata must be an object.")
        return None

    def dispatch(self, message: Any) -> dict[str, Any] | None:
        if not isinstance(message, Mapping) or message.get("jsonrpc") != "2.0":
            return _jsonrpc_error(None, -32600, "Invalid Request")
        method = message.get("method")
        request_id = message.get("id")
        is_notification = "id" not in message
        params = message.get("params", {})
        if not isinstance(method, str) or not isinstance(params, Mapping):
            return None if is_notification else _jsonrpc_error(request_id, -32600, "Invalid Request")

        if method == "notifications/initialized":
            self.initialized = True
            return None
        if method == "notifications/cancelled":
            return None

        # Every request carries protocol metadata.  Tool calls additionally use
        # the vendor-prefixed runtime context as their trusted identity boundary.
        metadata_failure = self._validate_request_metadata(params)
        if metadata_failure is not None:
            if is_notification:
                return None
            return _jsonrpc_error(
                request_id,
                -32602,
                "Invalid params",
                {"code": metadata_failure.code, "message": metadata_failure.message},
            )
        runtime = self._runtime_if_present(params) or {"request_id": None}

        if method == "initialize":
            requested_version = params.get("protocolVersion")
            if requested_version != PROTOCOL_VERSION:
                return _jsonrpc_error(
                    request_id,
                    -32602,
                    "Unsupported protocol version",
                    {"supported": [PROTOCOL_VERSION]},
                )
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "title": "Rafeeq Tawseel Training Server",
                        "version": SERVER_VERSION,
                    },
                    "instructions": (
                        "Synthetic training service. Keep customer identity and approvals in trusted "
                        f"{RUNTIME_META_KEY} metadata, never in tool arguments."
                    ),
                    "resultType": "complete",
                    "_meta": _result_meta(runtime, "initialize"),
                },
            }

        if method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"resultType": "complete", "_meta": _result_meta(runtime, "ping")},
            }
        if method == "server/discover":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "title": "Rafeeq Tawseel Training Server",
                        "version": SERVER_VERSION,
                    },
                    "resultType": "complete",
                    "_meta": _result_meta(runtime, "discover"),
                },
            }
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": TOOL_DEFINITIONS,
                    "resultType": "complete",
                    "_meta": _result_meta(runtime, "list"),
                },
            }
        if method == "tools/call":
            name = params.get("name")
            if not isinstance(name, str):
                return _jsonrpc_error(request_id, -32602, "Invalid params", {"field": "name"})
            try:
                result = self.service.call(name, params.get("arguments", {}), params)
            except ToolFailure as failure:
                result = _tool_error(name, failure, self._runtime_if_present(params))
            except Exception:
                # Do not put stack traces or record contents on the protocol.
                result = _tool_error(
                    name,
                    ToolFailure("INTERNAL_ERROR", "The simulated tool failed safely."),
                    self._runtime_if_present(params),
                )
            return {"jsonrpc": "2.0", "id": request_id, "result": result}

        return None if is_notification else _jsonrpc_error(request_id, -32601, "Method not found")


def serve_stdio(server: MCPServer | None = None) -> int:
    """Serve UTF-8, newline-delimited JSON-RPC until stdin closes."""

    active = server or MCPServer()
    for raw_line in sys.stdin:
        if not raw_line.strip():
            continue
        try:
            message = json.loads(raw_line)
        except json.JSONDecodeError:
            response = _jsonrpc_error(None, -32700, "Parse error")
        else:
            response = active.dispatch(message)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
            sys.stdout.flush()
    return 0


def smoke_check(orders_path: Path = DEFAULT_ORDERS_PATH) -> dict[str, Any]:
    """Run three direct service checks without opening the stdio loop."""

    service = TawseelToolService(orders_path)
    owned_params = {
        "_meta": {RUNTIME_META_KEY: {"request_id": "smoke-owned", "customer_id": "CUST-011"}}
    }
    forbidden_params = {
        "_meta": {RUNTIME_META_KEY: {"request_id": "smoke-forbidden", "customer_id": "CUST-012"}}
    }
    listed = [tool["name"] for tool in TOOL_DEFINITIONS]
    owned = service.call("get_order_status", {"order_id": "TW-26017"}, owned_params)
    try:
        service.call("get_order_status", {"order_id": "TW-26017"}, forbidden_params)
    except ToolFailure as failure:
        forbidden = {"code": failure.code, "retryable": failure.retryable}
    else:  # pragma: no cover - a failed security assertion should be conspicuous
        forbidden = {"code": "UNEXPECTED_ACCESS", "retryable": False}
    return {
        "ok": listed == ["get_order_status", "get_refund_context", "create_refund_request"]
        and owned["structuredContent"]["ok"]
        and forbidden["code"] == "ORDER_FORBIDDEN",
        "transport": "direct-smoke",
        "tools": listed,
        "owned_status": owned["structuredContent"],
        "forbidden": forbidden,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rafeeq Tawseel educational MCP server")
    parser.add_argument("--smoke", action="store_true", help="run deterministic direct smoke checks")
    parser.add_argument("--orders", type=Path, default=DEFAULT_ORDERS_PATH, help="path to synthetic orders CSV")
    parser.add_argument("--state-file", type=Path, default=None, help="optional ephemeral simulation state")
    args = parser.parse_args(argv)
    if args.smoke:
        report = smoke_check(args.orders)
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if report["ok"] else 1
    return serve_stdio(MCPServer(TawseelToolService(args.orders, args.state_file)))


if __name__ == "__main__":
    raise SystemExit(main())
