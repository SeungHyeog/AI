from __future__ import annotations

import hashlib
import json

from .args import key_value_set_args, namespace_args
from .helm_tools import helm_template
from .response import change_plan_dict
from .runner import command_tool
from .types import ChangePlan, ChangePlanJson, CliCommand, CliInvocation, PlanKind, RuntimeConfig, ToolPayloadJson
from .validation import (
    normalize_set_values,
    optional_namespace,
    require_cluster,
    require_name,
    require_path,
    require_region,
)


def plan_kubectl_apply(
    config: RuntimeConfig, region: str, cluster: str, manifestPath: str, namespace: str | None = None
) -> ToolPayloadJson:
    _ = require_region(region)
    dry_run_args = kubectl_apply_args(cluster, namespace, manifestPath, dry_run=True)
    response = command_tool(config, CliInvocation(command="kubectl", args=dry_run_args))
    plan = create_plan(
        "kubectl_apply",
        "kubectl",
        kubectl_apply_args(cluster, namespace, manifestPath, dry_run=False),
        (
            "This plan uses --dry-run=client and does not contact the cluster by default.",
            "A human may run a separate server-side dry-run only after selecting the intended cluster context.",
            "Apply tools only run when EKS_OPS_MODE=control.",
        ),
    )
    response["plan"] = payload_dict_plan(plan)
    return response


def apply_kubectl_apply_confirmed(
    config: RuntimeConfig,
    region: str,
    cluster: str,
    manifestPath: str,
    confirmationHash: str,
    confirmationToken: str,
    namespace: str | None = None,
) -> ToolPayloadJson:
    _ = require_region(region)
    args = kubectl_apply_args(cluster, namespace, manifestPath, dry_run=False)
    plan = create_plan("kubectl_apply", "kubectl", args, ())
    gate = check_gate(config, plan, confirmationHash, confirmationToken)
    if gate is not None:
        return gate
    return command_tool(config, CliInvocation(command="kubectl", args=args, intent="confirmed_control"))


def plan_helm_upgrade(
    config: RuntimeConfig,
    region: str,
    cluster: str,
    release: str,
    chart: str,
    namespace: str | None = None,
    valuesFile: str | None = None,
    set: dict[str, str | int | bool] | None = None,
    install: bool = True,
) -> ToolPayloadJson:
    response = helm_template(config, region, cluster, release, chart, namespace, valuesFile, set)
    plan = create_plan(
        "helm_upgrade",
        "helm",
        helm_upgrade_args(cluster, namespace, release, chart, valuesFile, set, install),
        (
            "Planning uses helm template, which renders locally and does not install or upgrade the release.",
            "Review rendered manifests and helm diff externally if required by policy.",
            "Apply tools only run when EKS_OPS_MODE=control.",
        ),
    )
    response["plan"] = payload_dict_plan(plan)
    return response


def apply_helm_upgrade_confirmed(
    config: RuntimeConfig,
    region: str,
    cluster: str,
    release: str,
    chart: str,
    confirmationHash: str,
    confirmationToken: str,
    namespace: str | None = None,
    valuesFile: str | None = None,
    set: dict[str, str | int | bool] | None = None,
    install: bool = True,
) -> ToolPayloadJson:
    _ = require_region(region)
    args = helm_upgrade_args(cluster, namespace, release, chart, valuesFile, set, install)
    plan = create_plan("helm_upgrade", "helm", args, ())
    gate = check_gate(config, plan, confirmationHash, confirmationToken)
    if gate is not None:
        return gate
    return command_tool(config, CliInvocation(command="helm", args=args, intent="confirmed_control"))


def kubectl_apply_args(cluster: str, namespace: str | None, manifest_path: str, dry_run: bool) -> tuple[str, ...]:
    args = [
        "--context",
        require_cluster(cluster),
        "apply",
        "--filename",
        require_path(manifest_path, "manifestPath"),
        *namespace_args(optional_namespace(namespace)),
    ]
    if dry_run:
        args.extend(("--dry-run=client", "--output", "yaml"))
    return tuple(args)


def helm_upgrade_args(
    cluster: str,
    namespace: str | None,
    release: str,
    chart: str,
    values_file: str | None,
    set_values: dict[str, str | int | bool] | None,
    install: bool,
) -> tuple[str, ...]:
    args = [
        "upgrade",
        require_name(release, "release"),
        require_path(chart, "chart"),
        "--kube-context",
        require_cluster(cluster),
        *namespace_args(optional_namespace(namespace)),
    ]
    if install:
        args.append("--install")
    if values_file is not None:
        args.extend(("--values", require_path(values_file, "valuesFile")))
    args.extend(key_value_set_args(normalize_set_values(set_values)))
    return tuple(args)


def create_plan(kind: PlanKind, command: CliCommand, args: tuple[str, ...], warnings: tuple[str, ...]) -> ChangePlan:
    encoded = json.dumps({"command": command, "args": list(args)}, separators=(",", ":"))
    confirmation_hash = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    return ChangePlan(
        kind=kind,
        command=command,
        args=args,
        confirmation_hash=confirmation_hash,
        confirmation_token=f"confirm:{confirmation_hash}",
        warnings=warnings,
    )


def check_gate(
    config: RuntimeConfig, plan: ChangePlan, confirmation_hash: str, confirmation_token: str
) -> ToolPayloadJson | None:
    if config.mode != "control":
        return {
            "status": "blocked",
            "reason": "Apply tools are disabled unless EKS_OPS_MODE=control.",
            "plan": payload_dict_plan(plan),
        }
    if confirmation_hash != plan.confirmation_hash or confirmation_token != plan.confirmation_token:
        return {
            "status": "blocked",
            "reason": "Confirmation hash/token did not match the planned command.",
            "plan": payload_dict_plan(plan),
        }
    return None


def payload_dict_plan(plan: ChangePlan) -> ChangePlanJson:
    return change_plan_dict(plan)
