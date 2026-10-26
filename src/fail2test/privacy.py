"""Best-effort structured sanitization; review is still required before sharing."""

from __future__ import annotations

import re
from typing import Any

SENSITIVE_KEYS = {
    "password",
    "passwd",
    "secret",
    "secret_key",
    "api_key",
    "apikey",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "private_key",
    "client_secret",
}
TOKEN = re.compile(
    r"sk-(?:proj-)?[A-Za-z0-9_-]{12,}|AKIA[A-Z0-9]{16}|Bearer\s+[A-Za-z0-9._~+/-]{8,}"
)
PRIVATE_KEY = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"
)


def sanitize(value: Any) -> tuple[Any, list[str]]:
    replacements: dict[str, str] = {}
    changed: list[str] = []

    def replacement(item: Any) -> str:
        # Mapping exists in memory only and never exposes hashes of low-entropy secrets.
        key = repr(item)
        if key not in replacements:
            replacements[key] = f"<redacted:{len(replacements) + 1}>"
        return replacements[key]

    def walk(item: Any, path: str) -> Any:
        if isinstance(item, dict):
            output = {}
            for key, child in item.items():
                child_path = path + "/" + key.replace("~", "~0").replace("/", "~1")
                if key.lower().replace("-", "_") in SENSITIVE_KEYS:
                    output[key] = replacement(child)
                    changed.append(child_path)
                else:
                    output[key] = walk(child, child_path)
            return output
        if isinstance(item, list):
            return [walk(child, f"{path}/{i}") for i, child in enumerate(item)]
        if isinstance(item, str):
            clean = PRIVATE_KEY.sub(lambda match: replacement(match.group()), item)
            clean = TOKEN.sub(lambda match: replacement(match.group()), clean)
            if clean != item:
                changed.append(path)
            return clean
        return item

    return walk(value, ""), changed
