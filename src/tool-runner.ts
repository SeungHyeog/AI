import { CommandExecutionError } from "./errors.js"
import { execute } from "./exec.js"
import { enforcePolicy, type PolicyIntent } from "./policy.js"
import { respond } from "./response.js"
import type { McpToolResponse, RuntimeConfig } from "./types.js"

export type CliInvocation = {
  readonly command: "aws" | "kubectl" | "helm"
  readonly args: readonly string[]
  readonly extraEnv?: Readonly<Record<string, string>>
  readonly intent?: PolicyIntent
}

export function commandTool(config: RuntimeConfig, invocation: CliInvocation): Promise<McpToolResponse> {
  const policy = enforcePolicy({ ...invocation, intent: invocation.intent ?? "readonly" })
  if (policy.status === "deny") {
    return Promise.resolve(respond({ status: "blocked", reason: policy.reason }))
  }
  return execute({ ...invocation, config }).then(
    (result) => respond({ status: result.exitCode === 0 ? "ok" : "failed", result }),
    (error: unknown) => {
      if (error instanceof CommandExecutionError) {
        return respond({ status: "failed", reason: error.message })
      }
      throw error
    }
  )
}
