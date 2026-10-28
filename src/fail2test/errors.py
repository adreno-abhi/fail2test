"""Stable errors; user-controlled payloads are deliberately excluded from messages."""

from typing import Any

from pydantic import BaseModel, ValidationError


def validation_message(error: ValidationError, model: type[BaseModel]) -> str:
    """Describe only schema-owned locations and fixed reasons, never raw Pydantic messages."""
    schema = model.model_json_schema()
    reasons = {
        "missing": "Required field is missing.",
        "extra_forbidden": "Remove unexpected fields (names withheld).",
        "union_tag_invalid": "Choose a supported rule kind.",
        "union_tag_not_found": "Choose a supported rule kind.",
        "literal_error": "Use an allowed schema value.",
        "string_type": "Expected a string.",
        "int_type": "Expected an integer.",
        "float_type": "Expected a number.",
        "bool_type": "Expected a boolean.",
        "dict_type": "Expected an object.",
        "model_type": "Expected an object.",
        "list_type": "Expected an array.",
        "greater_than": "Check numeric bounds.",
        "greater_than_equal": "Check numeric bounds.",
        "less_than": "Check numeric bounds.",
        "less_than_equal": "Check numeric bounds.",
        "string_too_short": "Check minimum length.",
        "string_too_long": "Check maximum length.",
        "too_short": "Check minimum length.",
        "too_long": "Check maximum length.",
        "string_pattern_mismatch": "Use the supported field format.",
        "value_error": "Check the constraints for this field or object.",
    }
    details = error.errors(include_input=False, include_context=False, include_url=False)
    lines = [
        f"{_schema_location(detail['loc'], schema)}: "
        + reasons.get(detail["type"], "Check the supported schema constraints.")
        for detail in details[:5]
    ]
    if error.error_count() > 5:
        lines.append("Additional errors omitted.")
    return " ".join(lines) + " Compare with the case schema using fail2test schema."


def _schema_location(location: tuple[int | str, ...], schema: dict[str, Any]) -> str:
    node = schema
    result = "case"
    for part in location:
        reference = node.get("$ref", "")
        if isinstance(reference, str) and reference.startswith("#/$defs/"):
            node = schema.get("$defs", {}).get(reference.removeprefix("#/$defs/"), {})
        properties = node.get("properties", {})
        if isinstance(part, str) and part in properties:
            result += "." + part
            node = properties[part]
        elif isinstance(part, int) and part >= 0 and "items" in node:
            result += f"[{part}]"
            node = node["items"]
        elif isinstance(part, str) and part in node.get("discriminator", {}).get("mapping", {}):
            # Pydantic puts the schema's union variant in loc; it is not a JSON field.
            node = {"$ref": node["discriminator"]["mapping"][part]}
        else:
            # Stop at JSON dictionaries, unknown fields or union branches. Their location
            # components can be private keys even if they happen to match another field name.
            break
    return result


class Fail2TestError(Exception):
    """A reportable tooling error with a stable machine code."""

    def __init__(self, code: str, message: str, exit_code: int = 2) -> None:
        self.code = code
        self.message = message
        self.exit_code = exit_code
        super().__init__(f"{code}: {message}")


class IncompleteExecutionError(Fail2TestError):
    """An execution could not establish the selected behavioral outcome."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(code, message, 3)
