"""Reject unexpected package paths without extracting or installing an archive."""

from __future__ import annotations

import argparse
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

SOURCE_DIRECTORIES = {"src", "tests", "scripts", "examples", "docs", ".github"}
SOURCE_FILES = {
    ".gitignore",
    "README.md",
    "LICENSE",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "DCO",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "SUPPORT.md",
    "GOVERNANCE.md",
    "MAINTAINERS.md",
    "PUBLISHING.md",
    "CHANGELOG.md",
    "pyproject.toml",
    "uv.lock",
    "mkdocs.yml",
    "AGENTS.md",
    "PLAN.md",
    "ROADMAP.md",
    "PKG-INFO",
}
PRIVATE_COMPONENTS = {
    "local-artifacts",
    "raw-traces",
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    ".fail2test",
}


def checked_parts(name: str) -> tuple[str, ...]:
    path = PurePosixPath(name)
    if path.is_absolute() or "\\" in name or any(p in {"", ".", ".."} for p in name.split("/")):
        raise ValueError("Archive contains an unsafe member path.")
    parts = path.parts
    if any(
        part in PRIVATE_COMPONENTS
        or part.startswith(".env")
        or part.endswith((".pem", ".key", ".pyc", ".pyo"))
        for part in parts
    ):
        raise ValueError("Archive contains a private or generated member path.")
    return parts


def check_distributions(wheel: Path, source: Path) -> dict[str, int]:
    """Check publication boundaries; this is not a secret-value scanner."""
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        if not names or len(names) != len(set(names)):
            raise ValueError("Wheel has empty or duplicate member names.")
        for name in names:
            parts = checked_parts(name.rstrip("/"))
            if not (
                parts[0] == "fail2test"
                or (parts[0].startswith("fail2test-") and parts[0].endswith(".dist-info"))
            ):
                raise ValueError("Wheel contains a member outside the package and metadata.")
        wheel_count = len(names)
    with tarfile.open(source) as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        if not names or len(names) != len(set(names)):
            raise ValueError("Source archive has empty or duplicate member names.")
        expected_root = source.name.removesuffix(".tar.gz")
        for member in members:
            parts = checked_parts(member.name.rstrip("/"))
            if not (member.isfile() or member.isdir()) or parts[0] != expected_root:
                raise ValueError("Source archive contains an unexpected root or member type.")
            if len(parts) == 1 and member.isdir():
                continue
            if len(parts) < 2 or not (
                parts[1] in SOURCE_DIRECTORIES or (len(parts) == 2 and parts[1] in SOURCE_FILES)
            ):
                raise ValueError("Source archive contains a member outside publication roots.")
        source_count = len(members)
    return {"wheel_members": wheel_count, "source_members": source_count}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    print(check_distributions(args.wheel, args.source))


if __name__ == "__main__":
    main()
