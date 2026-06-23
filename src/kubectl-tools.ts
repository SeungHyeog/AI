import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js"
import { kubectlContextArgs, namespaceArgs } from "./args.js"
import {
  KubectlAuthCanIInput,
  KubectlDescribeInput,
  KubectlEventsInput,
  KubectlGetInput,
  KubectlLogsInput
} from "./schemas.js"
import { commandTool } from "./tool-runner.js"
import type { RuntimeConfig } from "./types.js"

export function registerKubectlTools(server: McpServer, config: RuntimeConfig): void {
  server.registerTool(
    "kubectl_get",
    { description: "Run a read-only kubectl get with an explicit EKS context.", inputSchema: KubectlGetInput.shape },
    ({ cluster, resource, name, namespace, allNamespaces, output, selector }) =>
      commandTool(config, {
        command: "kubectl",
        args: [
          ...kubectlContextArgs(cluster),
          "get",
          resource,
          ...(name === undefined ? [] : [name]),
          ...(allNamespaces ? ["--all-namespaces"] : namespaceArgs(namespace)),
          "--output",
          output,
          ...(selector === undefined ? [] : ["--selector", selector])
        ]
      })
  )

  server.registerTool(
    "kubectl_describe",
    { description: "Run kubectl describe with an explicit EKS context.", inputSchema: KubectlDescribeInput.shape },
    ({ cluster, resource, name, namespace }) =>
      commandTool(config, {
        command: "kubectl",
        args: [...kubectlContextArgs(cluster), "describe", resource, name, ...namespaceArgs(namespace)]
      })
  )

  server.registerTool(
    "kubectl_logs",
    { description: "Read pod logs with bounded tail output.", inputSchema: KubectlLogsInput.shape },
    ({ cluster, pod, namespace, container, tail, since }) =>
      commandTool(config, {
        command: "kubectl",
        args: [
          ...kubectlContextArgs(cluster),
          "logs",
          pod,
          ...namespaceArgs(namespace),
          "--tail",
          String(tail),
          ...(container === undefined ? [] : ["--container", container]),
          ...(since === undefined ? [] : ["--since", since])
        ]
      })
  )

  server.registerTool(
    "kubectl_events",
    { description: "List events sorted by creation time.", inputSchema: KubectlEventsInput.shape },
    ({ cluster, namespace, fieldSelector }) =>
      commandTool(config, {
        command: "kubectl",
        args: [
          ...kubectlContextArgs(cluster),
          "get",
          "events",
          ...namespaceArgs(namespace),
          "--sort-by",
          ".metadata.creationTimestamp",
          ...(fieldSelector === undefined ? [] : ["--field-selector", fieldSelector])
        ]
      })
  )

  server.registerTool(
    "kubectl_auth_can_i",
    { description: "Check Kubernetes RBAC for a verb/resource pair.", inputSchema: KubectlAuthCanIInput.shape },
    ({ cluster, namespace, verb, resource }) =>
      commandTool(config, {
        command: "kubectl",
        args: [...kubectlContextArgs(cluster), "auth", "can-i", verb, resource, ...namespaceArgs(namespace)]
      })
  )
}
