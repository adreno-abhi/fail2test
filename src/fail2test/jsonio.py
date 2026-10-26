"""Bounded JSON, canonical identities, and deliberate atomic file writes."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import rfc8785

from fail2test.errors import Fail2TestError

MAX_BYTES = 10 * 1024 * 1024
MAX_DEPTH = 64


def canonical(value: Any) -> bytes:
    try:
        return rfc8785.dumps(value)
    except (rfc8785.CanonicalizationError, RecursionError, UnicodeError) as exc:
        raise Fail2TestError("INVALID_JSON_VALUE", "Use finite interoperable JSON values.") from exc


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise Fail2TestError("DUPLICATE_JSON_KEY", "JSON object keys must be unique.")
        result[key] = value
    return result


def _constant(_: str) -> Any:
    raise Fail2TestError("INVALID_JSON_NUMBER", "NaN and infinity are not JSON numbers.")


def check_depth(value: Any, depth: int = 0) -> None:
    if depth > MAX_DEPTH:
        raise Fail2TestError("JSON_TOO_DEEP", "JSON nesting exceeds the supported depth.")
    if isinstance(value, dict):
        for child in value.values():
            check_depth(child, depth + 1)
    elif isinstance(value, list):
        for child in value:
            check_depth(child, depth + 1)


def read_json(path: Path) -> Any:
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        return loads_json(raw)
    except OSError as exc:
        raise Fail2TestError(
            "INVALID_JSON", "Cannot read a supported UTF-8 JSON document."
        ) from exc


def loads_json(raw: bytes | str) -> Any:
    """Parse uploads in memory with exactly the same bounds as local JSON files."""
    try:
        if len(raw.encode("utf-8") if isinstance(raw, str) else raw) > MAX_BYTES:
            raise Fail2TestError("INPUT_TOO_LARGE", "JSON input exceeds 10 MiB.")
        value = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant)
        check_depth(value)
        canonical(value)
        return value
    except Fail2TestError:
        raise
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        raise Fail2TestError(
            "INVALID_JSON", "Cannot read a supported UTF-8 JSON document."
        ) from exc


def write_json(path: Path, value: Any, *, overwrite: bool = False) -> None:
    canonical(value)
    write_text(
        path,
        json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n",
        overwrite=overwrite,
    )


def write_text(path: Path, text: str, *, overwrite: bool = False) -> None:
    path = path.absolute()
    if path.is_symlink():
        raise Fail2TestError("UNSAFE_OUTPUT", "Refusing to replace a symlink.")
    if path.exists() and not overwrite:
        raise Fail2TestError("OUTPUT_EXISTS", "Choose a new destination or explicitly overwrite.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
        ) as stream:
            temporary = stream.name
            stream.write(text)
        if overwrite:
            os.replace(temporary, path)
        else:
            # Hard-link creation is atomic and refuses existing destinations (including races).
            os.link(temporary, path)
            os.unlink(temporary)
        temporary = None
    except FileExistsError as exc:
        raise Fail2TestError(
            "OUTPUT_EXISTS", "Output appeared while writing; nothing was replaced."
        ) from exc
    except OSError as exc:
        raise Fail2TestError("WRITE_FAILED", "Cannot write the requested output.", 4) from exc
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)
