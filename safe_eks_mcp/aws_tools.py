from __future__ import annotations

from .args import aws_region_args
from .runner import command_tool
from .types import CliInvocation, RuntimeConfig, ToolPayloadJson
from .validation import require_cluster, require_name, require_region


def aws_eks_list_clusters(config: RuntimeConfig, region: str) -> ToolPayloadJson:
    parsed_region = require_region(region)
    return command_tool(
        config, CliInvocation(command="aws", args=("eks", "list-clusters", *aws_region_args(parsed_region)))
    )


def aws_eks_describe_cluster(config: RuntimeConfig, region: str, cluster: str) -> ToolPayloadJson:
    return command_tool(
        config,
        CliInvocation(
            command="aws",
            args=(
                "eks",
                "describe-cluster",
                "--name",
                require_cluster(cluster),
                *aws_region_args(require_region(region)),
            ),
        ),
    )


def aws_eks_list_nodegroups(config: RuntimeConfig, region: str, cluster: str) -> ToolPayloadJson:
    return command_tool(
        config,
        CliInvocation(
            command="aws",
            args=(
                "eks",
                "list-nodegroups",
                "--cluster-name",
                require_cluster(cluster),
                *aws_region_args(require_region(region)),
            ),
        ),
    )


def aws_eks_describe_nodegroup(
    config: RuntimeConfig, region: str, cluster: str, nodegroup: str
) -> ToolPayloadJson:
    return command_tool(
        config,
        CliInvocation(
            command="aws",
            args=(
                "eks",
                "describe-nodegroup",
                "--cluster-name",
                require_cluster(cluster),
                "--nodegroup-name",
                require_name(nodegroup, "nodegroup"),
                *aws_region_args(require_region(region)),
            ),
        ),
    )


def aws_eks_list_addons(config: RuntimeConfig, region: str, cluster: str) -> ToolPayloadJson:
    return command_tool(
        config,
        CliInvocation(
            command="aws",
            args=(
                "eks",
                "list-addons",
                "--cluster-name",
                require_cluster(cluster),
                *aws_region_args(require_region(region)),
            ),
        ),
    )


def aws_eks_describe_addon(config: RuntimeConfig, region: str, cluster: str, addon: str) -> ToolPayloadJson:
    return command_tool(
        config,
        CliInvocation(
            command="aws",
            args=(
                "eks",
                "describe-addon",
                "--cluster-name",
                require_cluster(cluster),
                "--addon-name",
                require_name(addon, "addon"),
                *aws_region_args(require_region(region)),
            ),
        ),
    )


def eks_generate_kubeconfig_dry_run(config: RuntimeConfig, region: str, cluster: str) -> ToolPayloadJson:
    return command_tool(
        config,
        CliInvocation(
            command="aws",
            args=(
                "eks",
                "update-kubeconfig",
                "--name",
                require_cluster(cluster),
                "--dry-run",
                *aws_region_args(require_region(region)),
            ),
        ),
    )
