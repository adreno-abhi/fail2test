"""Record locked dependency license metadata; never treat metadata as legal clearance."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import re
import tomllib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/licensing/dependencies.json"


def collect(review_date: str) -> dict:
    lock_bytes = (ROOT / "uv.lock").read_bytes()
    lock = tomllib.loads(lock_bytes.decode())
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    direct: dict[str, list[str]] = {}
    groups = {"runtime": project["project"]["dependencies"]}
    groups.update({f"extra:{k}": v for k, v in project["project"]["optional-dependencies"].items()})
    groups.update({f"development:{k}": v for k, v in project["dependency-groups"].items()})
    for group, values in groups.items():
        for value in values:
            name = re.split(r"[<>=!~\[ ;]", value)[0].lower().replace("_", "-")
            direct.setdefault(name, []).append(group)
    rows = []
    for package in lock["package"]:
        name, version = package["name"], package["version"]
        if name == "fail2test":
            continue
        row = {
            "name": name,
            "version": version,
            "direct_groups": direct.get(name, []),
            "project_url": f"https://pypi.org/project/{name}/{version}/",
        }
        try:
            dist = importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:
            if (name, version) != ("httpx2-jsfetch", "1.0"):
                raise RuntimeError(
                    f"Install all locked extras/groups before collecting: {name}"
                ) from None
            row.update(
                license_expression="BSD-3-Clause",
                license_declaration=None,
                evidence="PyPI metadata reviewed; Emscripten-only package absent on this platform",
                license_files=[],
                metadata_sha256=None,
            )
        else:
            if dist.version != version:
                raise RuntimeError(f"Installed version differs from uv.lock: {name}")
            declared = dist.metadata.get("License")
            if declared and ("\n" in declared or len(declared) > 200):
                declared = "Embedded license text; inspect distribution license files"
            expression = dist.metadata.get("License-Expression")
            classifiers = [
                c for c in dist.metadata.get_all("Classifier", []) if c.startswith("License :: ")
            ]
            evidence = "Installed distribution metadata and license-file hashes"
            if name == "mergedeep" and version == "1.3.4":
                expression = "MIT"
                evidence += "; MIT declaration verified in LICENSE (metadata says UNKNOWN)"
            license_files = []
            for file in dist.files or []:
                if any(
                    Path(str(file)).name.lower().startswith(p)
                    for p in ("license", "licence", "notice", "copying", "copyright")
                ):
                    target = Path(dist.locate_file(file))
                    if target.is_file():
                        license_files.append(
                            {
                                "path": str(file).replace("\\", "/"),
                                "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                            }
                        )
            row.update(
                license_expression=expression,
                license_declaration=declared,
                license_classifiers=classifiers,
                evidence=evidence,
                license_files=sorted(license_files, key=lambda item: item["path"]),
                metadata_sha256=hashlib.sha256(
                    (dist.read_text("METADATA") or "").encode()
                ).hexdigest(),
            )
        rows.append(row)
    return {
        "inventory_version": 1,
        "review_date": review_date,
        "environment": (
            f"{platform.system()}, Python {platform.python_version()}, all extras/groups"
        ),
        "lock_sha256": hashlib.sha256(lock_bytes).hexdigest(),
        "scope": "All locked third-party Python packages; no legal clearance or vulnerability scan",
        "packages": sorted(rows, key=lambda item: item["name"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-lock", action="store_true", help="Offline snapshot/lock coverage check."
    )
    parser.add_argument("--review-date", type=date.fromisoformat, help="Metadata review date.")
    args = parser.parse_args()
    if args.check_lock:
        snapshot = json.loads(OUTPUT.read_text())
        lock_bytes = (ROOT / "uv.lock").read_bytes()
        assert snapshot["lock_sha256"] == hashlib.sha256(lock_bytes).hexdigest(), (
            "Refresh inventory"
        )
        expected = {
            (p["name"], p["version"])
            for p in tomllib.loads(lock_bytes.decode())["package"]
            if p["name"] != "fail2test"
        }
        assert expected == {(p["name"], p["version"]) for p in snapshot["packages"]}
        print(f"Inventory matches all {len(expected)} locked third-party packages.")
        return
    if args.review_date is None:
        parser.error("Supply --review-date YYYY-MM-DD when collecting license evidence.")
    result = collect(args.review_date.isoformat())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Locked dependency licenses",
        "",
        f"Generated from `uv.lock` and distribution metadata on {args.review_date.isoformat()}.",
        "See [scope and exceptions](../../THIRD_PARTY_NOTICES.md). Empty groups mean transitive;",
        "the lockfile graph determines which extras/platforms actually install a package.",
        "",
        "| Package | Locked version | Declared license | Direct group |",
        "|---|---|---|---|",
    ]
    for row in result["packages"]:
        label = (
            row["license_expression"]
            or row["license_declaration"]
            or "; ".join(row.get("license_classifiers", []))
            or "See license-file evidence"
        )
        lines.append(
            f"| [{row['name']}]({row['project_url']}) | {row['version']} "
            f"| {label.replace('|', '/')} | {', '.join(row['direct_groups']) or 'transitive'} |"
        )
    (OUTPUT.parent / "dependencies.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote inventory for {len(result['packages'])} locked third-party packages.")


if __name__ == "__main__":
    main()
