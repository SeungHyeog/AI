import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js"
import { keyValueSetArgs, kubectlContextArgs, namespaceArgs } from "./args.js"
import { HelmListInput, HelmReleaseInput, HelmTemplateInput } from "./schemas.js"
import { commandTool } from "./tool-runner.js"
import type { RuntimeConfig } from "./types.js"

export function registerHelmTools(server: McpServer, config: RuntimeConfig): void {
  server.registerTool(
    "helm_list",
    { description: "List Helm releases for an explicit EKS cluster context.", inputSchema: HelmListInput.shape },
    ({ cluster, namespace, allNamespaces }) =>
      commandTool(config, {
        command: "helm",
        args: ["list", "--kube-context", cluster, ...(allNamespaces ? ["--all-namespaces"] : namespaceArgs(namespace)), "--output", "json"]
      })
  )

  server.registerTool(
    "helm_status",
    { description: "Read Helm release status.", inputSchema: HelmReleaseInput.shape },
    ({ cluster, namespace, release }) =>
      commandTool(config, {
        command: "helm",
        args: ["status", release, "--kube-context", cluster, ...namespaceArgs(namespace), "--output", "json"]
      })
  )

  server.registerTool(
    "helm_history",
    { description: "Read Helm release history.", inputSchema: HelmReleaseInput.shape },
    ({ cluster, namespace, release }) =>
      commandTool(config, {
        command: "helm",
        args: ["history", release, "--kube-context", cluster, ...namespaceArgs(namespace), "--output", "json"]
      })
  )

  server.registerTool(
    "helm_template",
    { description: "Render a Helm chart locally without installing it.", inputSchema: HelmTemplateInput.shape },
    ({ cluster, namespace, release, chart, valuesFile, set }) =>
      commandTool(config, {
        command: "helm",
        args: [
          "template",
          release,
          chart,
          "--kube-context",
          ...kubectlContextArgs(cluster).slice(1),
          ...namespaceArgs(namespace),
          ...(valuesFile === undefined ? [] : ["--values", valuesFile]),
          ...keyValueSetArgs(set)
        ]
      })
  )

  server.registerTool(
    "helm_lint",
    { description: "Run helm lint locally against a chart.", inputSchema: HelmTemplateInput.shape },
    ({ namespace, chart, valuesFile, set }) =>
      commandTool(config, {
        command: "helm",
        args: ["lint", chart, ...namespaceArgs(namespace), ...(valuesFile === undefined ? [] : ["--values", valuesFile]), ...keyValueSetArgs(set)]
      })
  )
}
