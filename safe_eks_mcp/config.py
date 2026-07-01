from __future__ import annotations

import os
from collections.abc import Mapping

from .types import OpsMode, RuntimeConfig


def load_config(env: Mapping[str, str] | None = None) -> RuntimeConfig:
    source = os.environ if env is None else env
    mode = parse_mode(source.get("EKS_OPS_MODE", "readonly"))
    return RuntimeConfig(
        mode=mode,
        command_timeout_ms=parse_positive_int(source.get("EKS_COMMAND_TIMEOUT_MS"), 30_000, 120_000),
        max_output_bytes=parse_positive_int(source.get("EKS_MAX_OUTPUT_BYTES"), 200_000, 2_000_000),
    )


def parse_mode(value: str) -> OpsMode:
    match value:
        case "readonly" | "control":
            return value
        case _:
            return "readonly"


def parse_positive_int(value: str | None, default: int, maximum: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    if parsed <= 0:
        return default
    return min(parsed, maximum)
