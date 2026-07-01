from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import aws_tools, control_tools, helm_tools, kubectl_tools
from .config import load_config
from .response import ToolPayloadModel, payload_model


def create_mcp() -> FastMCP:
    config = load_config()
    mcp = FastMCP("safe-eks-mcp")

    @mcp.tool()
    def aws_eks_list_clusters(region: str) -> ToolPayloadModel:
        return payload_model(aws_tools.aws_eks_list_clusters(config, region))

    @mcp.tool()
    def aws_eks_describe_cluster(region: str, cluster: str) -> ToolPayloadModel:
        return payload_model(aws_tools.aws_eks_describe_cluster(config, region, cluster))

    @mcp.tool()
    def aws_eks_list_nodegroups(region: str, cluster: str) -> ToolPayloadModel:
        return payload_model(aws_tools.aws_eks_list_nodegroups(config, region, cluster))

    @mcp.tool()
    def aws_eks_describe_nodegroup(region: str, cluster: str, nodegroup: str) -> ToolPayloadModel:
        return payload_model(aws_tools.aws_eks_describe_nodegroup(config, region, cluster, nodegroup))

    @mcp.tool()
    def aws_eks_list_addons(region: str, cluster: str) -> ToolPayloadModel:
        return payload_model(aws_tools.aws_eks_list_addons(config, region, cluster))

    @mcp.tool()
    def aws_eks_describe_addon(region: str, cluster: str, addon: str) -> ToolPayloadModel:
        return payload_model(aws_tools.aws_eks_describe_addon(config, region, cluster, addon))

    @mcp.tool()
    def eks_generate_kubeconfig_dry_run(region: str, cluster: str) -> ToolPayloadModel:
        return payload_model(aws_tools.eks_generate_kubeconfig_dry_run(config, region, cluster))

    @mcp.tool()
    def kubectl_get(
        region: str,
        cluster: str,
        resource: str,
        name: str | None = None,
        namespace: str | None = None,
        allNamespaces: bool = False,
        output: kubectl_tools.OutputFormat = "json",
        selector: str | None = None,
    ) -> ToolPayloadModel:
        return payload_model(
            kubectl_tools.kubectl_get(
                config, region, cluster, resource, name, namespace, allNamespaces, output, selector
            )
        )

    @mcp.tool()
    def kubectl_describe(
        region: str,
        cluster: str,
        resource: str,
        name: str,
        namespace: str | None = None,
    ) -> ToolPayloadModel:
        return payload_model(kubectl_tools.kubectl_describe(config, region, cluster, resource, name, namespace))

    @mcp.tool()
    def kubectl_logs(
        region: str,
        cluster: str,
        pod: str,
        namespace: str | None = None,
        container: str | None = None,
        tail: int = 200,
        since: str | None = None,
    ) -> ToolPayloadModel:
        return payload_model(
            kubectl_tools.kubectl_logs(config, region, cluster, pod, namespace, container, tail, since)
        )

    @mcp.tool()
    def kubectl_events(
        region: str,
        cluster: str,
        namespace: str | None = None,
        fieldSelector: str | None = None,
    ) -> ToolPayloadModel:
        return payload_model(kubectl_tools.kubectl_events(config, region, cluster, namespace, fieldSelector))

    @mcp.tool()
    def kubectl_auth_can_i(
        region: str,
        cluster: str,
        verb: str,
        resource: str,
        namespace: str | None = None,
    ) -> ToolPayloadModel:
        return payload_model(kubectl_tools.kubectl_auth_can_i(config, region, cluster, verb, resource, namespace))

    @mcp.tool()
    def helm_list(
        region: str,
        cluster: str,
        namespace: str | None = None,
        allNamespaces: bool = False,
    ) -> ToolPayloadModel:
        return payload_model(helm_tools.helm_list(config, region, cluster, namespace, allNamespaces))

    @mcp.tool()
    def helm_status(region: str, cluster: str, release: str, namespace: str | None = None) -> ToolPayloadModel:
        return payload_model(helm_tools.helm_status(config, region, cluster, release, namespace))

    @mcp.tool()
    def helm_history(region: str, cluster: str, release: str, namespace: str | None = None) -> ToolPayloadModel:
        return payload_model(helm_tools.helm_history(config, region, cluster, release, namespace))

    @mcp.tool()
    def helm_template(
        region: str,
        cluster: str,
        release: str,
        chart: str,
        namespace: str | None = None,
        valuesFile: str | None = None,
        set: dict[str, str | int | bool] | None = None,
    ) -> ToolPayloadModel:
        return payload_model(
            helm_tools.helm_template(config, region, cluster, release, chart, namespace, valuesFile, set)
        )

    @mcp.tool()
    def helm_lint(
        region: str,
        cluster: str,
        release: str,
        chart: str,
        namespace: str | None = None,
        valuesFile: str | None = None,
        set: dict[str, str | int | bool] | None = None,
    ) -> ToolPayloadModel:
        return payload_model(helm_tools.helm_lint(config, region, cluster, release, chart, namespace, valuesFile, set))

    @mcp.tool()
    def plan_kubectl_apply(
        region: str,
        cluster: str,
        manifestPath: str,
        namespace: str | None = None,
    ) -> ToolPayloadModel:
        return payload_model(control_tools.plan_kubectl_apply(config, region, cluster, manifestPath, namespace))

    @mcp.tool()
    def apply_kubectl_apply_confirmed(
        region: str,
        cluster: str,
        manifestPath: str,
        confirmationHash: str,
        confirmationToken: str,
        namespace: str | None = None,
    ) -> ToolPayloadModel:
        return payload_model(control_tools.apply_kubectl_apply_confirmed(
            config,
            region,
            cluster,
            manifestPath,
            confirmationHash,
            confirmationToken,
            namespace,
        ))

    @mcp.tool()
    def plan_helm_upgrade(
        region: str,
        cluster: str,
        release: str,
        chart: str,
        namespace: str | None = None,
        valuesFile: str | None = None,
        set: dict[str, str | int | bool] | None = None,
        install: bool = True,
    ) -> ToolPayloadModel:
        return payload_model(
            control_tools.plan_helm_upgrade(
                config, region, cluster, release, chart, namespace, valuesFile, set, install
            )
        )

    @mcp.tool()
    def apply_helm_upgrade_confirmed(
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
    ) -> ToolPayloadModel:
        return payload_model(control_tools.apply_helm_upgrade_confirmed(
            config,
            region,
            cluster,
            release,
            chart,
            confirmationHash,
            confirmationToken,
            namespace,
            valuesFile,
            set,
            install,
        ))

    return mcp


def main() -> None:
    create_mcp().run()


if __name__ == "__main__":
    main()
