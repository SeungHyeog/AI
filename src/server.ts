import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js"
import { registerAwsTools } from "./aws-tools.js"
import { registerControlTools } from "./control-tools.js"
import { registerHelmTools } from "./helm-tools.js"
import { registerKubectlTools } from "./kubectl-tools.js"
import type { RuntimeConfig } from "./types.js"

export function createServer(config: RuntimeConfig): McpServer {
  const server = new McpServer({ name: "safe-eks-mcp", version: "0.1.0" })
  registerAwsTools(server, config)
  registerKubectlTools(server, config)
  registerHelmTools(server, config)
  registerControlTools(server, config)
  return server
}
