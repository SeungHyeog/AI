export type JsonObject = { readonly [key: string]: unknown }

export type CommandResult = {
  readonly command: string
  readonly args: readonly string[]
  readonly exitCode: number
  readonly stdout: string
  readonly stderr: string
  readonly timedOut: boolean
}

export type ToolPayload = {
  readonly status: "ok" | "blocked" | "failed"
  readonly result?: CommandResult
  readonly plan?: ChangePlan
  readonly reason?: string
}

export type McpToolResponse = {
  readonly [key: string]: unknown
  readonly content: { readonly type: "text"; readonly text: string }[]
  readonly structuredContent: ToolPayload
}

export type OpsMode = "readonly" | "control"

export type RuntimeConfig = {
  readonly mode: OpsMode
  readonly commandTimeoutMs: number
  readonly maxOutputBytes: number
}

export type PlanKind = "kubectl_apply" | "helm_upgrade"

export type ChangePlan = {
  readonly kind: PlanKind
  readonly command: string
  readonly args: readonly string[]
  readonly confirmationHash: string
  readonly confirmationToken: string
  readonly warnings: readonly string[]
}
