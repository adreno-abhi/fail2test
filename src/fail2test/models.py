"""Data-only contracts for portable cases and execution evidence."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, JsonValue, PrivateAttr, model_validator

from fail2test.errors import Fail2TestError, IncompleteExecutionError
from fail2test.jsonio import canonical, check_depth, digest, read_json

Identifier = Annotated[str, Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")]
NonNegative = Annotated[int, Field(ge=0)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, validate_default=True)


class ModelFixture(StrictModel):
    id: Identifier
    slot: Identifier
    ordinal: NonNegative
    request: dict[str, JsonValue]
    response: JsonValue


class ToolFixture(StrictModel):
    id: Identifier
    tool: Identifier
    arguments: dict[str, JsonValue]
    response: JsonValue
    repeatable: bool


class BaseRule(StrictModel):
    id: Identifier
    requirement: Annotated[str, Field(min_length=1)]


class ToolCallCount(BaseRule):
    kind: Literal["tool_call_count"]
    tool: Identifier
    group_by: list[str]
    min_calls: NonNegative
    max_calls: NonNegative
    require_any: bool

    @model_validator(mode="after")
    def valid_bounds(self) -> Self:
        if self.min_calls > self.max_calls:
            raise ValueError("min_calls must not exceed max_calls")
        if len(set(self.group_by)) != len(self.group_by):
            raise ValueError("grouping pointers must be unique")
        return self


class PredicateRule(BaseRule):
    pointer: str
    operator: Literal["eq", "in", "lte", "gte"]
    expected: JsonValue

    @model_validator(mode="after")
    def valid_operand(self) -> Self:
        if self.operator == "in" and not isinstance(self.expected, list):
            raise ValueError("membership expects a JSON array")
        if self.operator in {"lte", "gte"} and (
            isinstance(self.expected, bool) or not isinstance(self.expected, int | float)
        ):
            raise ValueError("numeric comparison requires a number, not a boolean")
        return self


class ToolArgument(PredicateRule):
    kind: Literal["tool_argument"]
    tool: Identifier
    require_any: bool


class OutputRule(PredicateRule):
    kind: Literal["output"]


class ForbiddenTool(BaseRule):
    kind: Literal["forbidden_tool"]
    tool: Identifier


class MaxToolCalls(BaseRule):
    kind: Literal["max_tool_calls"]
    max_calls: NonNegative


Rule = Annotated[
    ToolCallCount | ToolArgument | OutputRule | ForbiddenTool | MaxToolCalls,
    Field(discriminator="kind"),
]


class Provenance(StrictModel):
    source_kind: Literal["synthetic", "imported"]
    source_reference: Annotated[str, Field(min_length=1)]
    requirement: Annotated[str, Field(min_length=1)]
    sanitization: Literal["synthetic", "review_required", "reviewed"]


class Case(StrictModel):
    schema_version: Literal["0.1"]
    case_id: Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9._-]{0,127}$")]
    title: Annotated[str, Field(min_length=1, max_length=256)]
    mode: Literal["fixture"]
    input: dict[str, JsonValue]
    model_fixtures: list[ModelFixture]
    tool_fixtures: list[ToolFixture]
    rules: Annotated[list[Rule], Field(min_length=1)]
    provenance: Provenance
    _path: Path | None = PrivateAttr(default=None)

    @model_validator(mode="after")
    def invariants(self) -> Self:
        value = self.model_dump(mode="json")
        check_depth(value)
        canonical(value)
        for items in (self.model_fixtures, self.tool_fixtures, self.rules):
            ids = [item.id for item in items]
            if len(set(ids)) != len(ids):
                raise ValueError("identifiers must be unique within each collection")
        keys = [(f.slot, f.ordinal) for f in self.model_fixtures]
        if len(set(keys)) != len(keys):
            raise ValueError("model slots and ordinals must be unique")
        slots: dict[str, list[int]] = {}
        for fixture in self.model_fixtures:
            slots.setdefault(fixture.slot, []).append(fixture.ordinal)
        if any(sorted(values) != list(range(len(values))) for values in slots.values()):
            raise ValueError("model ordinals must be contiguous from zero per slot")
        tool_keys = [(f.tool, canonical(f.arguments)) for f in self.tool_fixtures]
        if len(set(tool_keys)) != len(tool_keys):
            raise ValueError("tool fixtures must not match ambiguously")
        for rule in self.rules:
            pointers = rule.group_by if isinstance(rule, ToolCallCount) else []
            if isinstance(rule, PredicateRule):
                pointers = [rule.pointer]
            for pointer in pointers:
                if not re.fullmatch(r"(?:/(?:[^~/]|~[01])*)*", pointer):
                    raise ValueError("invalid JSON pointer")
        return self

    @classmethod
    def load(cls, path: str | Path) -> Self:
        from pydantic import ValidationError

        target = Path(path)
        if target.is_dir():
            target /= "case.json"
        try:
            case = cls.model_validate(read_json(target))
        except ValidationError as exc:
            raise Fail2TestError(
                "INVALID_CASE", "Case does not match the supported schema."
            ) from exc
        case._path = target.resolve()
        return case

    @property
    def case_digest(self) -> str:
        return digest(self.model_dump(mode="json"))

    def run(self, *, runner: str, config: str | Path = "fail2test.toml") -> RunResult:
        from fail2test.workflow import run_reviewed

        if self._path is None:
            raise Fail2TestError("UNSAVED_CASE", "Load a reviewed case file before running it.")
        return run_reviewed(self._path, runner=runner, config=Path(config))


class Observation(StrictModel):
    index: NonNegative
    tool: str
    arguments: dict[str, JsonValue]
    fixture_id: str | None = None


class RuleResult(StrictModel):
    rule_id: str
    passed: bool
    reason: str
    observation_indices: list[int] = Field(default_factory=list)


class RunResult(StrictModel):
    result_schema_version: Literal["0.1"] = "0.1"
    case_id: str
    case_digest: str
    mode: Literal["fixture"] = "fixture"
    execution_status: Literal["complete", "incomplete", "error"]
    outcome: Literal["pass", "fail", "not_evaluated"]
    rule_results: list[RuleResult] = Field(default_factory=list)
    observed_calls: list[Observation] = Field(default_factory=list)
    output: JsonValue = None
    unused_fixtures: list[str] = Field(default_factory=list)
    tooling_errors: list[str] = Field(default_factory=list)
    runner_identity: dict[str, str] = Field(default_factory=dict)
    environment: dict[str, str] = Field(default_factory=dict)
    duration_ms: float = 0

    @model_validator(mode="after")
    def valid_pair(self) -> Self:
        if (self.execution_status == "complete") != (self.outcome in {"pass", "fail"}):
            raise ValueError("execution completeness and outcome disagree")
        if self.outcome == "pass" and (
            not self.rule_results or not all(r.passed for r in self.rule_results)
        ):
            raise ValueError("a pass needs successful evaluated rules")
        if self.outcome == "fail" and not any(not rule.passed for rule in self.rule_results):
            raise ValueError("a failure needs a failed behavioral rule")
        return self

    def assert_passed(self) -> None:
        if self.execution_status != "complete":
            code = self.tooling_errors[0] if self.tooling_errors else "EXECUTION_INCOMPLETE"
            raise IncompleteExecutionError(
                code, "Execution did not establish a behavioral outcome."
            )
        failed = [rule.rule_id for rule in self.rule_results if not rule.passed]
        if failed:
            raise AssertionError("Fail2Test regression: " + ", ".join(failed))


def case_schema() -> dict[str, Any]:
    return Case.model_json_schema()
