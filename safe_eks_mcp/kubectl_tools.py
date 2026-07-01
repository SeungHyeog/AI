from __future__ import annotations

from typing import Literal

from .args import kubectl_context_args, namespace_args
from .runner import command_tool
from .types import CliInvocation, RuntimeConfig, ToolPayloadJson
from .validation import (
    optional_namespace,
    optional_since,
    require_cluster,
    require_name,
    require_region,
    require_resource,
)

OutputFormat = Literal["json", "yaml", "wide", "name"]


def kubectl_get(
    config: RuntimeConfig,
    region: str,
    cluster: str,
    resource: str,
    name: str | None = None,
    namespace: str | None = None,
    allNamespaces: bool = False,
    output: OutputFormat = "json",
    selector: str | None = None,
) -> ToolPayloadJson:
    _ = require_region(region)
    args = [*kubectl_context_args(require_cluster(cluster)), "get", require_resource(resource)]
    if name is not None:
        args.append(require_name(name, "name"))
    args.extend(("--all-namespaces",) if allNamespaces else namespace_args(optional_namespace(namespace)))
    args.extend(("--output", output))
    if selector is not None:
        args.extend(("--selector", selector))
    return command_tool(config, CliInvocation(command="kubectl", args=tuple(args)))


def kubectl_describe(
    config: RuntimeConfig, region: str, cluster: str, resource: str, name: str, namespace: str | None = None
) -> ToolPayloadJson:
    _ = require_region(region)
    return command_tool(
        config,
        CliInvocation(
            command="kubectl",
            args=(
                *kubectl_context_args(require_cluster(cluster)),
                "describe",
                require_resource(resource),
                require_name(name, "name"),
                *namespace_args(optional_namespace(namespace)),
            ),
        ),
    )


def kubectl_logs(
    config: RuntimeConfig,
    region: str,
    cluster: str,
    pod: str,
    namespace: str | None = None,
    container: str | None = None,
    tail: int = 200,
    since: str | None = None,
) -> ToolPayloadJson:
    _ = require_region(region)
    bounded_tail = min(max(tail, 1), 10_000)
    args = [
        *kubectl_context_args(require_cluster(cluster)),
        "logs",
        require_name(pod, "pod"),
        *namespace_args(optional_namespace(namespace)),
        "--tail",
        str(bounded_tail),
    ]
    if container is not None:
        args.extend(("--container", require_name(container, "container")))
    if since is not None:
        args.extend(("--since", optional_since(since) or since))
    return command_tool(config, CliInvocation(command="kubectl", args=tuple(args)))


def kubectl_events(
    config: RuntimeConfig, region: str, cluster: str, namespace: str | None = None, fieldSelector: str | None = None
) -> ToolPayloadJson:
    _ = require_region(region)
    args = [
        *kubectl_context_args(require_cluster(cluster)),
        "get",
        "events",
        *namespace_args(optional_namespace(namespace)),
        "--sort-by",
        ".metadata.creationTimestamp",
    ]
    if fieldSelector is not None:
        args.extend(("--field-selector", fieldSelector))
    return command_tool(config, CliInvocation(command="kubectl", args=tuple(args)))


def kubectl_auth_can_i(
    config: RuntimeConfig, region: str, cluster: str, verb: str, resource: str, namespace: str | None = None
) -> ToolPayloadJson:
    _ = require_region(region)
    return command_tool(
        config,
        CliInvocation(
            command="kubectl",
            args=(
                *kubectl_context_args(require_cluster(cluster)),
                "auth",
                "can-i",
                require_name(verb, "verb"),
                require_resource(resource),
                *namespace_args(optional_namespace(namespace)),
            ),
        ),
    )
