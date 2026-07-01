from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Mapping
from typing import Final

from .types import CommandResult, RuntimeConfig

SECRET_PATTERNS: Final = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ASIA[0-9A-Z]{16}"),
    re.compile(r"(?<=aws_secret_access_key\s=)[^\s]+", re.IGNORECASE),
    re.compile(r"(?<=aws_session_token\s=)[^\s]+", re.IGNORECASE),
    re.compile(r"(?<=Authorization:\sBearer\s)[A-Za-z0-9._~+/=-]+", re.IGNORECASE),
    re.compile(r"(?<=token: )[A-Za-z0-9._~+/=-]+", re.IGNORECASE),
)
ENV_ALLOWLIST: Final = (
    "PATH",
    "HOME",
    "AWS_PROFILE",
    "AWS_CONFIG_FILE",
    "AWS_SHARED_CREDENTIALS_FILE",
    "AWS_REGION",
    "AWS_DEFAULT_REGION",
    "KUBECONFIG",
    "EKS_FAKE_CLI_LOG",
    "HELM_CACHE_HOME",
    "HELM_CONFIG_HOME",
    "HELM_DATA_HOME",
)


def execute(command: str, args: tuple[str, ...], config: RuntimeConfig) -> CommandResult:
    timeout_seconds = config.command_timeout_ms / 1000
    try:
        completed = subprocess.run(
            (command, *args),
            check=False,
            capture_output=True,
            env=isolated_env(os.environ),
            shell=False,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as error:
        return CommandResult(
            command=command,
            args=args,
            exit_code=1,
            stdout=redact(truncate(timeout_output(error.stdout), config.max_output_bytes)),
            stderr=redact(truncate(timeout_output(error.stderr), config.max_output_bytes)),
            timed_out=True,
        )
    except OSError as error:
        return CommandResult(
            command=command,
            args=args,
            exit_code=1,
            stdout="",
            stderr=redact(str(error)),
            timed_out=False,
        )
    return CommandResult(
        command=command,
        args=args,
        exit_code=completed.returncode,
        stdout=redact(truncate(completed.stdout, config.max_output_bytes)),
        stderr=redact(truncate(completed.stderr, config.max_output_bytes)),
        timed_out=False,
    )


def isolated_env(source: Mapping[str, str]) -> dict[str, str]:
    return {key: value for key in ENV_ALLOWLIST if (value := source.get(key)) is not None}


def truncate(value: str, max_bytes: int) -> str:
    encoded = value.encode("utf-8")
    if len(encoded) <= max_bytes:
        return value
    return encoded[:max_bytes].decode("utf-8", errors="ignore") + "\n[output truncated]"


def redact(value: str) -> str:
    current = value
    for pattern in SECRET_PATTERNS:
        current = pattern.sub("[REDACTED]", current)
    return current


def timeout_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return value
