"""Validate local community structure; publication readiness is a separate explicit gate."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
IDENTITIES = (
    "github_owner",
    "repository_name",
    "public_maintainer",
    "security_contact",
    "conduct_contact",
)
VERIFIED = (
    "contacts_verified",
    "private_reporting_verified",
    "host_checks_verified",
    "compatibility_verified",
    "first_use_verified",
    "history_privacy_verified",
    "initial_provenance_reviewed",
    "owner_acceptance",
)
REQUIRED = [
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
    "ROADMAP.md",
    "PUBLISHING.md",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/workflows/ci.yml",
    ".github/dependabot.yml",
    "docs/release/github/SETUP.md",
]


def publication_errors(facts: dict) -> list[str]:
    errors = []
    for key in IDENTITIES:
        value = facts.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Publication fact still pending: {key}")
    for key in VERIFIED:
        if facts.get(key) is not True:
            errors.append(f"Publication fact still pending: {key}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--publication", action="store_true", help="Also require verified launch facts."
    )
    args = parser.parse_args()
    errors = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"Missing required community file: {relative}")
    documents = list(ROOT.glob("*.md")) + list((ROOT / "docs/site").glob("*.md"))
    documents += list((ROOT / "docs/licensing").glob("*.md"))
    for document in documents:
        for target in re.findall(
            r"\[[^\]\n]+\]\(([^)\n]+)\)", document.read_text(encoding="utf-8")
        ):
            target = target.strip("<>").split(' "')[0]
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            destination = (document.parent / unquote(parsed.path)).resolve()
            if not destination.is_relative_to(ROOT) or not destination.exists():
                errors.append(f"Broken relative link in {document.relative_to(ROOT)}: {target}")
    forms = sorted((ROOT / ".github/ISSUE_TEMPLATE").glob("*.yml"))
    for form in forms:
        value = yaml.safe_load(form.read_text(encoding="utf-8"))
        if form.name == "config.yml":
            if not isinstance(value, dict) or value.get("blank_issues_enabled") is not False:
                errors.append("Issue config must direct reports to the supplied forms.")
            continue
        if not isinstance(value, dict) or not value.get("name") or not value.get("description"):
            errors.append(f"Invalid issue form header: {form.name}")
            continue
        ids = []
        for field in value.get("body", []):
            if field.get("type") not in {"markdown", "textarea", "input", "dropdown", "checkboxes"}:
                errors.append(f"Unsupported issue field in {form.name}")
            if field.get("type") != "markdown":
                ids.append(field.get("id"))
                if not field.get("attributes", {}).get("label"):
                    errors.append(f"Unlabeled issue field in {form.name}")
        if None in ids or len(set(ids)) != len(ids):
            errors.append(f"Missing/duplicate issue IDs in {form.name}")
    if len(forms) != 4:
        errors.append("Expected three issue forms and one config file.")
    if args.publication:
        facts = json.loads((ROOT / "docs/release/publication.json").read_text())
        errors.extend(publication_errors(facts))
    if errors:
        raise SystemExit("\n".join(errors))
    print(
        f"Community files, {len(documents)} Markdown documents "
        f"and {len(forms) - 1} issue forms checked."
    )
    print(
        "Local checks do not verify live GitHub rendering, contacts, accounts or legal clearance."
    )


if __name__ == "__main__":
    main()
