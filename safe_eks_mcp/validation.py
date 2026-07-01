from __future__ import annotations

import re
from typing import Final

REGION_RE: Final = re.compile(r"^[a-z]{2}-[a-z]+-\d$")
CLUSTER_RE: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")
NAME_RE: Final = re.compile(r"^[A-Za-z0-9_.:@][A-Za-z0-9_.:@-]{0,252}$")
KUBE_RESOURCE_RE: Final = re.compile(r"^[A-Za-z0-9_.][A-Za-z0-9_.-]*(,[A-Za-z0-9_.][A-Za-z0-9_.-]*)*$")
NAMESPACE_RE: Final = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")
SINCE_RE: Final = re.compile(r"^\d+[smhd]$")
SET_KEY_RE: Final = re.compile(r"^[A-Za-z0-9_.][A-Za-z0-9_.-]*$")


class InvalidInputError(ValueError):
    pass


def require_region(value: str) -> str:
    return require_match(value, REGION_RE, "AWS region is required")


def require_cluster(value: str) -> str:
    return require_match(value, CLUSTER_RE, "cluster/context must be a safe name")


def require_name(value: str, label: str) -> str:
    return require_match(value, NAME_RE, f"{label} must be a safe name")


def require_resource(value: str) -> str:
    return require_match(value, KUBE_RESOURCE_RE, "resource must be a safe Kubernetes resource")


def optional_namespace(value: str | None) -> str | None:
    if value is None:
        return None
    return require_match(value, NAMESPACE_RE, "namespace must be a DNS label")


def require_path(value: str, label: str) -> str:
    if len(value) == 0 or len(value) > 500 or value.startswith("-"):
        raise InvalidInputError(f"{label} must be a non-option path")
    return value


def optional_since(value: str | None) -> str | None:
    if value is None:
        return None
    return require_match(value, SINCE_RE, "since must look like 10s, 5m, 2h, or 1d")


def normalize_set_values(values: dict[str, str | int | bool] | None) -> dict[str, str | int | bool]:
    if values is None:
        return {}
    for key in values:
        _ = require_match(key, SET_KEY_RE, "helm set key must be safe")
    return values


def require_match(value: str, pattern: re.Pattern[str], message: str) -> str:
    if pattern.fullmatch(value) is None:
        raise InvalidInputError(message)
    return value
