"""Minimal MCP stdio client used by the Rafeeq cumulative lab.

This module uses only the Python standard library and opens a real subprocess.
It implements the narrow MCP 2026-07-28 subset required by the course; it is
not a general MCP SDK.  In particular, a write call is sent exactly once.  A
timeout has an unknown outcome and is never retried automatically.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import select
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
import weakref
from pathlib import Path
from typing import Any, Mapping, Sequence


PROTOCOL_VERSION = "2026-07-28"
PROTOCOL_VERSION_META_KEY = "io.modelcontextprotocol/protocolVersion"
CLIENT_CAPABILITIES_META_KEY = "io.modelcontextprotocol/clientCapabilities"
CLIENT_INFO_META_KEY = "io.modelcontextprotocol/clientInfo"
RUNTIME_META_KEY = "com.rafeeq.training/runtimeContext"
DEFAULT_TIMEOUT_SECONDS = 3.0
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SERVER = REPOSITORY_ROOT / "mcp_server" / "tawseel_server.py"
_REQUEST_ID_TRANSLATION = str.maketrans("0123456789abcdef", "abcdefghijklmnop")


class MCPClientError(RuntimeError):
    """Raised for transport or JSON-RPC failures, never for tool-level errors."""


class MCPStdioClient:
    """A bounded context-managed client for the local teaching server."""

    transport = "stdio"

    def __init__(
        self,
        *,
        customer_id: str,
        locale: str = "en",
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        command: Sequence[str] | None = None,
    ) -> None:
        if not isinstance(customer_id, str) or not customer_id.strip():
            raise ValueError("customer_id is required by the trusted host runtime")
        if locale not in {"ar", "en"}:
            raise ValueError("locale must be 'ar' or 'en'")
        if not 0.1 <= float(timeout_seconds) <= 30.0:
            raise ValueError("timeout_seconds must be between 0.1 and 30")
        self.customer_id = customer_id.strip()
        self.locale = locale
        self.timeout_seconds = float(timeout_seconds)
        self.command = list(command) if command else [sys.executable, "-u", str(DEFAULT_SERVER)]
        self._process: subprocess.Popen[str] | None = None
        self._next_id = 0
        self.events: list[dict[str, Any]] = []
        self.server_discovery: dict[str, Any] | None = None

    def __enter__(self) -> "MCPStdioClient":
        self.start()
        try:
            # MCP 2026-07-28 is stateless: negotiate through per-request
            # metadata and discover capabilities without a legacy init phase.
            self.server_discovery = self.discover()
        except Exception:
            self.close()
            raise
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(self) -> None:
        if self.is_running:
            return
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        self._process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="strict",
            bufsize=1,
            env=env,
        )
        self._record("transport_open", command=self.command)

    def close(self) -> None:
        process, self._process = self._process, None
        if process is None:
            return
        try:
            if process.stdin is not None and not process.stdin.closed:
                process.stdin.close()
            if process.poll() is None:
                try:
                    # Closing stdin is the protocol's normal EOF shutdown.
                    process.wait(timeout=0.25)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    try:
                        process.wait(timeout=0.75)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=1.0)
        finally:
            for stream in (process.stdout, process.stderr):
                if stream is not None and not stream.closed:
                    stream.close()
            self._record("transport_close", returncode=process.returncode)

    def _record(self, event: str, **details: Any) -> None:
        self.events.append({"event": event, "transport": self.transport, **details})

    def _metadata(self, request_id: str, approval: Mapping[str, Any] | None = None) -> dict[str, Any]:
        runtime: dict[str, Any] = {
            "request_id": request_id,
            "customer_id": self.customer_id,
            "locale": self.locale,
        }
        if approval is not None:
            # Approval is supplied by the trusted host application, separately
            # from model-controlled tool arguments.
            runtime["approval"] = dict(approval)
        return {
            PROTOCOL_VERSION_META_KEY: PROTOCOL_VERSION,
            CLIENT_CAPABILITIES_META_KEY: {},
            CLIENT_INFO_META_KEY: {
                "name": "com.rafeeq/notebook-client",
                "version": "0.2.0",
            },
            RUNTIME_META_KEY: runtime,
        }

    def _request(
        self,
        method: str,
        params: Mapping[str, Any] | None = None,
        *,
        approval: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.is_running:
            raise MCPClientError("MCP stdio subprocess is not running")
        self._next_id += 1
        rpc_id = self._next_id
        # Keep learner-visible request IDs opaque and alphabetic.  A raw UUID
        # fragment can accidentally contain an order amount or identifier
        # substring and create a false-positive data-leakage alert.
        request_id = "req-" + uuid.uuid4().hex[:16].translate(_REQUEST_ID_TRANSLATION)
        body_params = dict(params or {})
        body_params["_meta"] = self._metadata(request_id, approval)
        message = {"jsonrpc": "2.0", "id": rpc_id, "method": method, "params": body_params}
        self._send(message)
        response = self._receive(rpc_id)
        if "error" in response:
            error = response["error"]
            raise MCPClientError(f"JSON-RPC {error.get('code')}: {error.get('message')}")
        result = response.get("result")
        if not isinstance(result, dict):
            raise MCPClientError("MCP response result must be a JSON object")
        self._record("request_complete", method=method, request_id=request_id)
        return result

    def _send(self, message: Mapping[str, Any]) -> None:
        process = self._process
        if process is None or process.stdin is None:
            raise MCPClientError("MCP stdin is unavailable")
        try:
            process.stdin.write(json.dumps(message, ensure_ascii=False, separators=(",", ":")) + "\n")
            process.stdin.flush()
        except (BrokenPipeError, OSError, UnicodeError) as exc:
            raise MCPClientError("MCP stdio write failed") from exc

    def _receive(self, expected_id: int) -> dict[str, Any]:
        process = self._process
        if process is None or process.stdout is None:
            raise MCPClientError("MCP stdout is unavailable")
        deadline = time.monotonic() + self.timeout_seconds
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                self._record("transport_timeout", request_id=expected_id)
                raise MCPClientError(
                    "MCP stdio request timed out; outcome is unknown and the request was not retried"
                )
            readable, _, _ = select.select([process.stdout], [], [], remaining)
            if not readable:
                continue
            line = process.stdout.readline()
            if line == "":
                stderr = ""
                if process.stderr is not None:
                    stderr = process.stderr.read(600).strip()
                raise MCPClientError(f"MCP server exited unexpectedly: {stderr or 'no diagnostics'}")
            try:
                response = json.loads(line)
            except json.JSONDecodeError as exc:
                raise MCPClientError("MCP server returned invalid JSON") from exc
            if not isinstance(response, dict) or response.get("jsonrpc") != "2.0":
                raise MCPClientError("MCP server returned an invalid JSON-RPC message")
            if response.get("id") != expected_id:
                raise MCPClientError("MCP response ID did not match the request")
            return response

    def _notify(self, method: str, params: Mapping[str, Any] | None = None) -> None:
        message: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params:
            message["params"] = dict(params)
        self._send(message)

    def initialize(self) -> dict[str, Any]:
        """Optional compatibility path; the default 2026-07-28 flow omits it."""

        result = self._request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {
                    "name": "com.rafeeq/notebook-client",
                    "title": "Rafeeq Notebook Client",
                    "version": "0.2.0",
                },
            },
        )
        if result.get("protocolVersion") != PROTOCOL_VERSION:
            raise MCPClientError("MCP protocol negotiation failed")
        self._notify("notifications/initialized")
        return result

    def list_tools(self) -> list[dict[str, Any]]:
        result = self._request("tools/list")
        tools = result.get("tools")
        if not isinstance(tools, list):
            raise MCPClientError("tools/list returned an invalid tool collection")
        return tools

    def discover(self) -> dict[str, Any]:
        """Return the server's small self-description after negotiation."""

        return self._request("server/discover")

    def call_tool(
        self,
        name: str,
        arguments: Mapping[str, Any],
        *,
        approval: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call once; return both successful and structured tool-error results."""

        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string")
        if not isinstance(arguments, Mapping):
            raise ValueError("arguments must be a mapping")
        # No loop and no retry: especially important for write tools.
        return self._request(
            "tools/call",
            {"name": name, "arguments": dict(arguments)},
            approval=approval,
        )


class MCPToolClient:
    """Notebook-facing API that owns and always closes each subprocess.

    ``trusted_context`` is supplied by the host runtime, not generated by the
    model.  A call does not retry, including when the subprocess times out.
    """

    transport = "stdio"

    def __init__(
        self,
        data_dir: str | Path | None = None,
        *,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.data_dir = Path(data_dir) if data_dir is not None else REPOSITORY_ROOT / "data" / "public"
        self.timeout_seconds = float(timeout_seconds)
        self._state_dir = Path(tempfile.mkdtemp(prefix="rafeeq-mcp-"))
        self._state_file = self._state_dir / "simulation-state.json"
        self._state_finalizer = weakref.finalize(self, shutil.rmtree, self._state_dir, True)
        self._closed = False

    def __enter__(self) -> "MCPToolClient":
        if self._closed:
            raise MCPClientError("MCPToolClient is closed")
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()

    def close(self) -> None:
        """Remove the client's ephemeral state; subprocesses close per call."""

        if not self._closed:
            self._state_finalizer()
            self._closed = True

    def _ensure_open(self) -> None:
        if self._closed:
            raise MCPClientError("MCPToolClient is closed")

    def _command(self) -> list[str]:
        self._ensure_open()
        return [
            sys.executable,
            "-u",
            str(DEFAULT_SERVER),
            "--orders",
            str(self.data_dir / "orders.csv"),
            "--state-file",
            str(self._state_file),
        ]

    def _session(self, trusted_context: Mapping[str, Any]) -> MCPStdioClient:
        if not isinstance(trusted_context, Mapping):
            raise ValueError("trusted_context must be a mapping supplied by the host runtime")
        customer_id = trusted_context.get("customer_id")
        locale = trusted_context.get("locale", "en")
        if not isinstance(customer_id, str) or not customer_id.strip():
            raise ValueError("trusted_context.customer_id is required")
        if not isinstance(locale, str):
            raise ValueError("trusted_context.locale must be a string")
        return MCPStdioClient(
            customer_id=customer_id,
            locale=locale,
            timeout_seconds=self.timeout_seconds,
            command=self._command(),
        )

    def list_tools(self) -> list[dict[str, Any]]:
        """List the fixed schemas through a short-lived stdio session."""

        self._ensure_open()
        with self._session({"customer_id": "SYSTEM-DISCOVERY", "locale": "en"}) as session:
            return session.list_tools()

    def call_tool(
        self,
        name: str,
        arguments: Mapping[str, Any],
        trusted_context: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Call one tool once, keeping identity and approval outside arguments."""

        approval = trusted_context.get("approval")
        if approval is not None and not isinstance(approval, Mapping):
            raise ValueError("trusted_context.approval must be a mapping")
        with self._session(trusted_context) as session:
            return session.call_tool(name, arguments, approval=approval)

    @staticmethod
    def _as_tool_result(response: Mapping[str, Any], *, write: bool = False) -> Any:
        """Translate one MCP result into the runtime's narrow ToolResult.

        The import stays local so this transport adapter does not create a
        module-level dependency cycle with the agent contracts.
        """

        from .agents import ToolResult

        structured = response.get("structuredContent", {})
        if not isinstance(structured, Mapping):
            return ToolResult(False, "MCP_RESULT_INVALID", {})
        if structured.get("ok") is not True:
            error = structured.get("error", {})
            code = error.get("code", "MCP_TOOL_ERROR") if isinstance(error, Mapping) else "MCP_TOOL_ERROR"
            return ToolResult(False, str(code), {})
        data = structured.get("data", {})
        clean_data = dict(data) if isinstance(data, Mapping) else {}
        performed = bool(write and not clean_data.get("idempotent_replay", False))
        code = "REFUND_CREATED" if performed else "IDEMPOTENT_REPLAY" if write else "ORDER_FOUND"
        return ToolResult(True, code, clean_data, performed)

    def get_order(self, order_id: str, customer_id: str) -> Any:
        """Implement the runtime ToolClient read contract over MCP stdio.

        Both reads use one short-lived subprocess and the same trusted
        identity. A single retry is allowed only for an explicit, structured
        retryable read error; transport timeouts keep an unknown outcome and
        are never retried.
        """

        from .agents import ToolResult

        trusted = {"customer_id": customer_id, "locale": "en"}

        def read_pair() -> tuple[dict[str, Any], dict[str, Any]]:
            with self._session(trusted) as session:
                status = session.call_tool("get_order_status", {"order_id": order_id})
                context = session.call_tool("get_refund_context", {"order_id": order_id})
                return status, context

        status_response, context_response = read_pair()
        for candidate in (status_response, context_response):
            structured = candidate.get("structuredContent", {})
            error = structured.get("error", {}) if isinstance(structured, Mapping) else {}
            if isinstance(error, Mapping) and error.get("retryable") is True:
                status_response, context_response = read_pair()
                break
        status_result = self._as_tool_result(status_response)
        context_result = self._as_tool_result(context_response)
        if not status_result.ok:
            return status_result
        if not context_result.ok:
            return context_result
        data = {**dict(status_result.data), **dict(context_result.data)}
        # This owner value comes from the trusted host context, not a model
        # argument or server disclosure. It lets the deterministic policy gate
        # re-check ownership before any write.
        data["customer_id"] = customer_id.strip().upper()
        if "amount_sar" in data:
            data["amount_sar"] = float(data["amount_sar"])
        return ToolResult(True, "ORDER_FOUND", data)

    def create_refund(
        self,
        order_id: str,
        customer_id: str,
        idempotency_key: str,
        approval: bool | None = None,
        approval_id: str | None = None,
    ) -> Any:
        """Implement the runtime's one-shot write contract over MCP stdio."""

        from .agents import ToolResult

        if approval is False:
            return ToolResult(False, "APPROVAL_REJECTED", {})
        scoped_id = approval_id or (
            "APR-POLICY-" + hashlib.sha256(f"{customer_id}|{order_id}|{idempotency_key}".encode("utf-8")).hexdigest()[:12].upper()
        )
        trusted = {
            "customer_id": customer_id,
            "locale": "en",
            "approval": {
                "granted": True,
                "tool": "create_refund_request",
                "order_id": order_id,
                "approval_id": scoped_id,
                "level": "human" if approval is True else "policy",
            },
        }
        # Deliberately one call and no retry: a timeout has an unknown outcome.
        response = self.call_tool(
            "create_refund_request",
            {"order_id": order_id, "reason": "Eligible synthetic delayed order"},
            trusted,
        )
        return self._as_tool_result(response, write=True)

    def smoke_test(self) -> dict[str, Any]:
        """Check discovery, an owned read and an ownership denial over stdio."""

        self._ensure_open()
        context = {"customer_id": "CUST-011", "locale": "ar"}
        session = self._session(context)
        with session:
            discovery = session.server_discovery or session.discover()
            tools = session.list_tools()
            owned = session.call_tool("get_order_status", {"order_id": "TW-26017"})
            forbidden = session.call_tool("get_order_status", {"order_id": "TW-26018"})
            names = [tool.get("name") for tool in tools]
            owned_payload = owned.get("structuredContent", {})
            forbidden_payload = forbidden.get("structuredContent", {})
            ok = (
                discovery.get("protocolVersion") == PROTOCOL_VERSION
                and names == ["get_order_status", "get_refund_context", "create_refund_request"]
                and owned_payload.get("ok") is True
                and forbidden_payload.get("error", {}).get("code") == "ORDER_FORBIDDEN"
                and forbidden.get("isError") is True
                and owned.get("resultType") == "complete"
            )
        approval = {
            "granted": True,
            "tool": "create_refund_request",
            "order_id": "TW-26017",
            "approval_id": "APR-SMOKE-001",
            "level": "human",
        }
        trusted_write_context = {**context, "approval": approval}
        write_one = self.call_tool(
            "create_refund_request",
            {"order_id": "TW-26017", "reason": "Delayed synthetic order"},
            trusted_write_context,
        )
        write_two = self.call_tool(
            "create_refund_request",
            {"order_id": "TW-26017", "reason": "Delayed synthetic order"},
            trusted_write_context,
        )
        first_write = write_one.get("structuredContent", {}).get("data", {})
        second_write = write_two.get("structuredContent", {}).get("data", {})
        idempotency_ok = (
            first_write.get("request_id") == second_write.get("request_id")
            and first_write.get("refund_write_count") == 1
            and second_write.get("refund_write_count") == 1
            and second_write.get("idempotent_replay") is True
        )
        return {
            "ok": ok and idempotency_ok and not session.is_running,
            "transport": session.transport,
            "protocol_version": discovery.get("protocolVersion"),
            "tools": names,
            "owned_status": owned_payload,
            "forbidden": forbidden_payload,
            "idempotency": {
                "request_id": first_write.get("request_id"),
                "same_request_id": first_write.get("request_id") == second_write.get("request_id"),
                "refund_write_count": second_write.get("refund_write_count"),
                "second_call_replayed": second_write.get("idempotent_replay"),
            },
            "closed_after_context": not session.is_running,
            "events": session.events,
        }


def smoke_check(customer_id: str = "CUST-011", data_dir: str | Path | None = None) -> dict[str, Any]:
    """Compatibility CLI wrapper for the default deterministic smoke identity."""

    if customer_id != "CUST-011":
        raise ValueError("the deterministic smoke check requires CUST-011")
    with MCPToolClient(data_dir) as client:
        return client.smoke_test()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rafeeq minimal MCP stdio client")
    parser.add_argument("--smoke", action="store_true", help="run the list/status/forbidden smoke check")
    parser.add_argument("--customer-id", default="CUST-011", help="trusted synthetic customer identity")
    parser.add_argument("--data-dir", type=Path, default=None, help="directory containing orders.csv")
    args = parser.parse_args(argv)
    if not args.smoke:
        parser.error("this teaching CLI currently supports only --smoke")
    report = smoke_check(args.customer_id, args.data_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
