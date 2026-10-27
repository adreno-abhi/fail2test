"""Real builds must exclude local files even when broad include globs would match."""

from __future__ import annotations

import importlib.util
import io
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "package_contents", ROOT / "scripts/check_package_contents.py"
)
assert spec is not None and spec.loader is not None
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


def test_real_build_excludes_local_and_credential_markers(tmp_path):
    project = tmp_path / "dirty source tree"
    project.mkdir()
    for name in (
        "src",
        "tests",
        "scripts",
        "examples",
        "docs",
        ".github",
    ):
        shutil.copytree(
            ROOT / name,
            project / name,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
        )
    for path in ROOT.iterdir():
        if path.is_file() and (path.name in checks.SOURCE_FILES or path.name == ".gitignore"):
            shutil.copy2(path, project / path.name)
    markers = (
        "local-artifacts/private/tests/do-not-ship.txt",
        "raw-traces/private/docs/do-not-ship.txt",
        ".venv/cache/tests/do-not-ship.txt",
        "scratch/README.md",
        "src/fail2test/.env.local",
        "docs/private.key",
        "tests/__pycache__/private.pyc",
    )
    marker = b"SYNTHETIC_PACKAGE_" + b"EXCLUSION_MARKER_NOT_A_SECRET"
    for name in markers:
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(marker)
    built = subprocess.run(
        ["uv", "build"],
        cwd=project,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    assert built.returncode == 0, built.stderr
    wheel = next((project / "dist").glob("*.whl"))
    source = next((project / "dist").glob("*.tar.gz"))
    checks.check_distributions(wheel, source)
    with tarfile.open(source) as archive:
        names = {"/".join(member.name.split("/")[1:]) for member in archive.getmembers()}
        for required in (
            "src/fail2test/cli.py",
            "tests/test_workflow.py",
            "scripts/check_package_contents.py",
            "docs/site/evidence.md",
            "LICENSE",
            "NOTICE",
            ".github/workflows/ci.yml",
        ):
            assert required in names
        for member in archive.getmembers():
            if member.isfile():
                stream = archive.extractfile(member)
                assert stream is not None
                assert marker not in stream.read(), member.name
    with zipfile.ZipFile(wheel) as archive:
        assert "fail2test/ui/static/index.html" in archive.namelist()
        assert "fail2test/data/duplicate-refund.case.json" in archive.namelist()
        assert all(marker not in archive.read(name) for name in archive.namelist())


@pytest.mark.parametrize(
    ("target", "member"),
    [
        ("wheel", "local-artifacts/tests/private.txt"),
        ("wheel", "fail2test/.env.local"),
        ("source", "local-artifacts/tests/private.txt"),
        ("source", "docs/private.key"),
    ],
)
def test_content_guard_rejects_unintended_members(tmp_path, target, member):
    wheel, source = tmp_path / "example.whl", tmp_path / "fail2test-0.1.tar.gz"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(member if target == "wheel" else "fail2test/cli.py", "synthetic")
    with tarfile.open(source, "w:gz") as archive:
        name = member if target == "source" else "src/fail2test/cli.py"
        data = b"synthetic"
        info = tarfile.TarInfo("fail2test-0.1/" + name)
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))
    with pytest.raises(ValueError):
        checks.check_distributions(wheel, source)
