from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture()
def fake_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log_path = bin_dir / "calls.jsonl"
    for name in ("aws", "kubectl", "helm"):
        write_fake_cli(bin_dir / name, name)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    monkeypatch.setenv("EKS_FAKE_CLI_LOG", str(log_path))
    monkeypatch.setenv("EKS_OPS_MODE", "readonly")
    return log_path


def write_fake_cli(path: Path, name: str) -> None:
    source = "\n".join(
        (
            "#!/usr/bin/env python3",
            "import json, os, sys",
            f"payload = {{'binary': {name!r}, 'args': sys.argv[1:], 'awsKey': 'AKIA1234567890ABCDEF'}}",
            "log = os.environ.get('EKS_FAKE_CLI_LOG')",
            "if log:",
            "    with open(log, 'a', encoding='utf-8') as handle:",
            "        handle.write(json.dumps(payload) + '\\n')",
            "sys.stdout.write(json.dumps(payload))",
            "",
        )
    )
    _ = path.write_text(
        source,
        encoding="utf-8",
    )
    _ = path.chmod(0o755)


def read_log(path: Path) -> list[str]:
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8").strip()
    return [] if content == "" else content.splitlines()
