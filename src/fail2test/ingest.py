"""Neutral evidence import; missing state is never silently reconstructed."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from fail2test.errors import Fail2TestError, validation_message
from fail2test.jsonio import canonical, read_json, write_json
from fail2test.models import Case
from fail2test.privacy import sanitize
from fail2test.workflow import Manifest, create_bundle


def import_case(source: Path, out: Path, *, rules: list[Any] | None = None) -> Path:
    return import_data(read_json(source), out, rules=rules)


def import_data(raw: Any, out: Path, *, rules: list[Any] | None = None) -> Path:
    """Shared file/upload import; raw upload content never needs a temporary file."""
    data, changes = sanitize(raw)
    if not isinstance(data, dict):
        raise Fail2TestError("INVALID_TRACE", "Expected a supported case or neutral trace object.")
    sanitized_evidence = data if "trace_schema_version" in data else None
    if "schema_version" in data:
        try:
            data = Case.model_validate(data).model_dump(mode="json")
        except ValidationError as exc:
            raise Fail2TestError("INVALID_CASE", validation_message(exc, Case)) from None
        complete = True
        notes: list[str] = []
    elif data.get("trace_schema_version") == "0.1":
        data, complete, notes = _normalize_trace(data)
    else:
        raise Fail2TestError(
            "UNSUPPORTED_FORMAT", "Use a Fail2Test case or neutral trace version 0.1."
        )
    if rules is not None:
        data["rules"] = rules
    if changes:
        data["provenance"]["sanitization"] = "review_required"
        notes.append("Sanitization changed values; review semantic effects and reproduce again.")
    path = create_bundle(
        data, out, Manifest(source_complete=complete, sanitization_changes=changes)
    )
    if sanitized_evidence is not None:
        write_json(out / "evidence.json", sanitized_evidence)
    write_json(
        out / "import-report.json",
        {
            "source_complete": complete,
            "sanitization_changes": changes,
            "notes": notes,
            "needs_rules": not bool(data["rules"]),
        },
    )
    return path


def _normalize_trace(trace: dict[str, Any]) -> tuple[dict[str, Any], bool, list[str]]:
    allowed = {"trace_schema_version", "trace_id", "input", "completeness", "events"}
    if set(trace) != allowed or not isinstance(trace.get("input"), dict):
        raise Fail2TestError(
            "INVALID_TRACE", "Neutral trace has unsupported fields or missing input."
        )
    if (
        not isinstance(trace.get("trace_id"), str)
        or not 1 <= len(trace["trace_id"]) <= 128
        or trace.get("completeness")
        not in {
            "declared_complete",
            "partial",
            "unknown",
        }
    ):
        raise Fail2TestError("INVALID_TRACE", "Trace identity/completeness is invalid.")
    events = trace.get("events")
    if not isinstance(events, list) or len(events) > 10_000:
        raise Fail2TestError("INVALID_TRACE", "Use a bounded list of neutral trace events.")
    ids: set[str] = set()
    pending: dict[str, dict[str, Any]] = {}
    completed_operations: set[str] = set()
    models: list[dict[str, Any]] = []
    tools: list[dict[str, Any]] = []
    notes: list[str] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict) or not {
            "event_id",
            "sequence",
            "kind",
            "operation_id",
            "payload",
        }.issubset(event):
            raise Fail2TestError("INVALID_TRACE", "Event fields are missing.")
        if set(event) - {
            "event_id",
            "sequence",
            "kind",
            "operation_id",
            "payload",
            "timestamp",
            "parent_event_id",
        }:
            raise Fail2TestError("INVALID_TRACE", "Unsupported event fields.")
        event_id, operation = event["event_id"], event["operation_id"]
        if (
            not isinstance(event_id, str)
            or not isinstance(operation, str)
            or not 1 <= len(event_id) <= 128
            or not 1 <= len(operation) <= 128
            or event_id in ids
            or type(event["sequence"]) is not int
            or event["sequence"] != index
        ):
            raise Fail2TestError(
                "INVALID_TRACE_ORDER", "Events need unique IDs and contiguous serial positions."
            )
        if len(canonical(event["payload"])) > 1024 * 1024:
            raise Fail2TestError("PAYLOAD_TOO_LARGE", "An event payload exceeds 1 MiB.")
        if "timestamp" in event:
            try:
                timestamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
                if timestamp.tzinfo is None:
                    raise ValueError
            except (ValueError, TypeError, AttributeError) as exc:
                raise Fail2TestError(
                    "INVALID_TIMESTAMP", "Use an offset-aware ISO timestamp."
                ) from exc
        if "parent_event_id" in event and event["parent_event_id"] not in ids:
            raise Fail2TestError(
                "INVALID_TRACE_PARENT", "Parent event must refer to earlier evidence."
            )
        ids.add(event_id)
        kind = event["kind"]
        if kind in {"model_request", "tool_request"}:
            if pending or operation in completed_operations:
                raise Fail2TestError(
                    "UNSUPPORTED_TRACE",
                    "Only complete serial request/result pairs are supported.",
                    3,
                )
            pending[operation] = event
        elif kind in {"model_result", "tool_result"}:
            request = pending.pop(operation, None)
            if request is None or request["kind"] != kind.replace("result", "request"):
                raise Fail2TestError("INVALID_TRACE_PAIR", "Request/result pairing does not match.")
            completed_operations.add(operation)
            payload = request["payload"]
            if not isinstance(payload, dict):
                raise Fail2TestError("INVALID_TRACE_PAYLOAD", "Request payload must be an object.")
            if kind == "model_result":
                if set(payload) != {"slot", "ordinal", "request"}:
                    raise Fail2TestError(
                        "INVALID_TRACE_PAYLOAD", "Model request needs slot, ordinal and request."
                    )
                models.append(
                    {"id": f"model-{len(models)}", **payload, "response": event["payload"]}
                )
            else:
                if set(payload) != {"tool", "arguments"}:
                    raise Fail2TestError(
                        "INVALID_TRACE_PAYLOAD", "Tool request needs tool and arguments."
                    )
                # Repeatability needs explicit review; duplicate historical interactions with
                # identical responses can be represented by one proposed repeatable fixture.
                existing = [
                    item
                    for item in tools
                    if item["tool"] == payload["tool"]
                    and canonical(item["arguments"]) == canonical(payload["arguments"])
                ]
                if existing:
                    if canonical(existing[0]["response"]) != canonical(event["payload"]):
                        raise Fail2TestError(
                            "UNSUPPORTED_TOOL_SEQUENCE",
                            "Different responses need a sequence-aware adapter.",
                            3,
                        )
                    existing[0]["repeatable"] = True
                    notes.append(
                        "Repeated response proposed as repeatable; explicit case review required."
                    )
                else:
                    tools.append(
                        {
                            "id": f"tool-{len(tools)}",
                            **payload,
                            "response": event["payload"],
                            "repeatable": False,
                        }
                    )
        elif kind != "run_output":
            raise Fail2TestError("UNSUPPORTED_EVENT", "Unsupported neutral trace event kind.", 3)
    complete = trace["completeness"] == "declared_complete" and not pending
    if pending:
        notes.append("Missing result: evidence remains trace-only.")
    data = {
        "schema_version": "0.1",
        "case_id": "imported-failure",
        "title": "Imported failure; review intended behavior",
        "mode": "fixture",
        "input": trace["input"],
        "model_fixtures": models,
        "tool_fixtures": tools,
        "rules": [],
        "provenance": {
            "source_kind": "imported",
            "source_reference": trace["trace_id"],
            "requirement": "Specify intended behavior during review.",
            "sanitization": "review_required",
        },
    }
    try:
        # Check fixture shape without inventing a business rule in the draft.
        Case.model_validate(
            {
                **data,
                "rules": [
                    {
                        "id": "shape-check",
                        "kind": "max_tool_calls",
                        "max_calls": 0,
                        "requirement": "Structural validation only; not an approved assertion.",
                    }
                ],
            }
        )
    except ValidationError as exc:
        raise Fail2TestError(
            "INVALID_TRACE_PAYLOAD", "Normalized trace case: " + validation_message(exc, Case)
        ) from None
    return data, complete, notes


def propose_rules(path: Path) -> dict[str, Any]:
    """Proposals are hypotheses derived from fixture shape, not approved business truth."""
    from fail2test.workflow import case_path

    data = read_json(case_path(path))
    if not isinstance(data, dict) or not isinstance(data.get("tool_fixtures"), list):
        raise Fail2TestError("INVALID_CASE", "Import supported evidence before proposing rules.")
    tools = data["tool_fixtures"]
    if tools:
        first = tools[0]
        group = ["/order_id"] if "order_id" in first.get("arguments", {}) else []
        rules = [
            {
                "id": "review-call-count",
                "kind": "tool_call_count",
                "tool": first["tool"],
                "group_by": group,
                "min_calls": 1,
                "max_calls": 1,
                "require_any": True,
                "requirement": (
                    "Candidate only: confirm this scenario requires exactly one call per group."
                ),
            }
        ]
    else:
        rules = [
            {
                "id": "review-call-budget",
                "kind": "max_tool_calls",
                "max_calls": 0,
                "requirement": "Candidate only: specify the tool-call budget for this scenario.",
            }
        ]
    return {
        "rules": rules,
        "review_required": True,
        "notes": ["Confirm intended behavior; historical behavior alone is not a requirement."],
    }
