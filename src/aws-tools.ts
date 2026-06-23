import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js"
import { awsRegionArgs } from "./args.js"
import {
  EksAddonInput,
  EksClusterInput,
  EksNodegroupInput,
  RegionSchema
} from "./schemas.js"
import { commandTool } from "./tool-runner.js"
import type { RuntimeConfig } from "./types.js"

export function registerAwsTools(server: McpServer, config: RuntimeConfig): void {
  server.registerTool(
    "aws_eks_list_clusters",
    {
      description: "List EKS clusters in an explicit AWS region.",
      inputSchema: { region: RegionSchema }
    },
    ({ region }) => commandTool(config, { command: "aws", args: ["eks", "list-clusters", ...awsRegionArgs(region)] })
  )

  server.registerTool(
    "aws_eks_describe_cluster",
    {
      description: "Describe one EKS cluster in an explicit region.",
      inputSchema: EksClusterInput.shape
    },
    ({ region, cluster }) =>
      commandTool(config, {
        command: "aws",
        args: ["eks", "describe-cluster", "--name", cluster, ...awsRegionArgs(region)]
      })
  )

  server.registerTool(
    "aws_eks_list_nodegroups",
    {
      description: "List node groups for one EKS cluster.",
      inputSchema: EksClusterInput.shape
    },
    ({ region, cluster }) =>
      commandTool(config, {
        command: "aws",
        args: ["eks", "list-nodegroups", "--cluster-name", cluster, ...awsRegionArgs(region)]
      })
  )

  server.registerTool(
    "aws_eks_describe_nodegroup",
    {
      description: "Describe one EKS node group.",
      inputSchema: EksNodegroupInput.shape
    },
    ({ region, cluster, nodegroup }) =>
      commandTool(config, {
        command: "aws",
        args: [
          "eks",
          "describe-nodegroup",
          "--cluster-name",
          cluster,
          "--nodegroup-name",
          nodegroup,
          ...awsRegionArgs(region)
        ]
      })
  )

  server.registerTool(
    "aws_eks_list_addons",
    {
      description: "List add-ons installed on one EKS cluster.",
      inputSchema: EksClusterInput.shape
    },
    ({ region, cluster }) =>
      commandTool(config, {
        command: "aws",
        args: ["eks", "list-addons", "--cluster-name", cluster, ...awsRegionArgs(region)]
      })
  )

  server.registerTool(
    "aws_eks_describe_addon",
    {
      description: "Describe one EKS add-on.",
      inputSchema: EksAddonInput.shape
    },
    ({ region, cluster, addon }) =>
      commandTool(config, {
        command: "aws",
        args: [
          "eks",
          "describe-addon",
          "--cluster-name",
          cluster,
          "--addon-name",
          addon,
          ...awsRegionArgs(region)
        ]
      })
  )

  server.registerTool(
    "eks_generate_kubeconfig_dry_run",
    {
      description: "Generate kubeconfig content with aws eks update-kubeconfig --dry-run only.",
      inputSchema: EksClusterInput.shape
    },
    ({ region, cluster }) =>
      commandTool(config, {
        command: "aws",
        args: ["eks", "update-kubeconfig", "--name", cluster, "--dry-run", ...awsRegionArgs(region)]
      })
  )
}
