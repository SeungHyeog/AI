from __future__ import annotations

from .args import key_value_set_args, namespace_args
from .runner import command_tool
from .types import CliInvocation, RuntimeConfig, ToolPayloadJson
from .validation import (
    normalize_set_values,
    optional_namespace,
    require_cluster,
    require_name,
    require_path,
    require_region,
)


def helm_list(
    config: RuntimeConfig, region: str, cluster: str, namespace: str | None = None, allNamespaces: bool = False
) -> ToolPayloadJson:
    _ = require_region(region)
    args = ["list", "--kube-context", require_cluster(cluster)]
    args.extend(("--all-namespaces",) if allNamespaces else namespace_args(optional_namespace(namespace)))
    args.extend(("--output", "json"))
    return command_tool(config, CliInvocation(command="helm", args=tuple(args)))


def helm_status(
    config: RuntimeConfig, region: str, cluster: str, release: str, namespace: str | None = None
) -> ToolPayloadJson:
    _ = require_region(region)
    return command_tool(
        config,
        CliInvocation(
            command="helm",
            args=(
                "status",
                require_name(release, "release"),
                "--kube-context",
                require_cluster(cluster),
                *namespace_args(optional_namespace(namespace)),
                "--output",
                "json",
            ),
        ),
    )


def helm_history(
    config: RuntimeConfig, region: str, cluster: str, release: str, namespace: str | None = None
) -> ToolPayloadJson:
    _ = require_region(region)
    return command_tool(
        config,
        CliInvocation(
            command="helm",
            args=(
                "history",
                require_name(release, "release"),
                "--kube-context",
                require_cluster(cluster),
                *namespace_args(optional_namespace(namespace)),
                "--output",
                "json",
            ),
        ),
    )


def helm_template(
    config: RuntimeConfig,
    region: str,
    cluster: str,
    release: str,
    chart: str,
    namespace: str | None = None,
    valuesFile: str | None = None,
    set: dict[str, str | int | bool] | None = None,
) -> ToolPayloadJson:
    _ = require_region(region)
    args = [
        "template",
        require_name(release, "release"),
        require_path(chart, "chart"),
        "--kube-context",
        require_cluster(cluster),
        *namespace_args(optional_namespace(namespace)),
    ]
    if valuesFile is not None:
        args.extend(("--values", require_path(valuesFile, "valuesFile")))
    args.extend(key_value_set_args(normalize_set_values(set)))
    return command_tool(config, CliInvocation(command="helm", args=tuple(args)))


def helm_lint(
    config: RuntimeConfig,
    region: str,
    cluster: str,
    release: str,
    chart: str,
    namespace: str | None = None,
    valuesFile: str | None = None,
    set: dict[str, str | int | bool] | None = None,
) -> ToolPayloadJson:
    _ = require_region(region)
    _ = require_cluster(cluster)
    _ = require_name(release, "release")
    args = ["lint", require_path(chart, "chart"), *namespace_args(optional_namespace(namespace))]
    if valuesFile is not None:
        args.extend(("--values", require_path(valuesFile, "valuesFile")))
    args.extend(key_value_set_args(normalize_set_values(set)))
    return command_tool(config, CliInvocation(command="helm", args=tuple(args)))
