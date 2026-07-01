from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, assert_never

from .types import CliInvocation


@dataclass(frozen=True, slots=True)
class Allow:
    status: Literal["allow"] = "allow"


@dataclass(frozen=True, slots=True)
class Deny:
    reason: str
    status: Literal["deny"] = "deny"


PolicyDecision = Allow | Deny
SECRET_RESOURCES = frozenset({"secret", "secrets", "sec"})
KUBECTL_MUTATING = frozenset(
    {
        "annotate",
        "apply",
        "autoscale",
        "cordon",
        "create",
        "delete",
        "drain",
        "edit",
        "label",
        "patch",
        "replace",
        "rollout",
        "scale",
        "set",
        "taint",
        "uncordon",
    }
)
HELM_MUTATING = frozenset(
    {
        "create",
        "dependency",
        "install",
        "plugin",
        "pull",
        "push",
        "registry",
        "repo",
        "rollback",
        "uninstall",
        "upgrade",
    }
)
AWS_MUTATING = frozenset(
    {
        "associate",
        "create",
        "delete",
        "deregister",
        "disassociate",
        "enable",
        "put",
        "register",
        "start",
        "tag-resource",
        "untag-resource",
        "update",
    }
)
KUBECTL_VERBS = KUBECTL_MUTATING | frozenset({"auth", "describe", "events", "get", "logs", "top", "version"})
SECRET_PATH_RE = re.compile(r"(^|/)api(s)?/.*?/secrets?(/|$)", re.IGNORECASE)


def enforce_policy(invocation: CliInvocation) -> PolicyDecision:
    match invocation.command:
        case "kubectl":
            return enforce_kubectl_policy(invocation.args, invocation.intent)
        case "helm":
            return enforce_helm_policy(invocation.args, invocation.intent)
        case "aws":
            return enforce_aws_policy(invocation.args, invocation.intent)
        case unreachable:
            assert_never(unreachable)


def enforce_kubectl_policy(args: tuple[str, ...], intent: str) -> PolicyDecision:
    if any(arg == "--raw" or arg.startswith("--raw=") for arg in args):
        return Deny("kubectl raw API access is blocked by policy.")
    if any(SECRET_PATH_RE.search(arg) is not None for arg in args):
        return Deny("Raw Kubernetes Secret API paths are blocked by policy.")
    verb_at = verb_index(args)
    if verb_at is None:
        return Deny("kubectl command did not include an explicit verb.")
    verb = args[verb_at]
    if verb in {"get", "describe"} and contains_secret_resource(args[verb_at + 1 :]):
        return Deny("Reading Kubernetes Secret resources is blocked by policy.")
    if verb == "apply" and "--dry-run=client" in args:
        return Allow()
    if verb in KUBECTL_MUTATING and intent != "confirmed_control":
        return Deny(f"kubectl {verb} is blocked unless it is a confirmed control workflow.")
    return Allow()


def enforce_helm_policy(args: tuple[str, ...], intent: str) -> PolicyDecision:
    if len(args) == 0:
        return Deny("helm command did not include an explicit verb.")
    verb = args[0]
    if verb in HELM_MUTATING and intent != "confirmed_control":
        return Deny(f"helm {verb} is blocked unless it is a confirmed control workflow.")
    return Allow()


def enforce_aws_policy(args: tuple[str, ...], intent: str) -> PolicyDecision:
    if len(args) < 2:
        return Deny("aws command did not include a service operation.")
    operation = args[1]
    if operation == "update-kubeconfig" and "--dry-run" in args:
        return Allow()
    prefix = operation.split("-", 1)[0]
    if prefix in AWS_MUTATING and intent != "confirmed_control":
        return Deny(f"aws {operation} is blocked unless it is a confirmed control workflow.")
    return Allow()


def verb_index(args: tuple[str, ...]) -> int | None:
    for index, arg in enumerate(args):
        if arg in KUBECTL_VERBS:
            return index
    return None


def contains_secret_resource(args: tuple[str, ...]) -> bool:
    for arg in args:
        if arg.startswith("-"):
            continue
        for resource in arg.split(","):
            normalized = resource.lower().split("/", 1)[0].split(".", 1)[0]
            if normalized in SECRET_RESOURCES:
                return True
    return False
