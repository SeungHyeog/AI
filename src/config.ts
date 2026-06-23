import { z } from "zod"
import type { RuntimeConfig } from "./types.js"

const EnvSchema = z.object({
  EKS_OPS_MODE: z.enum(["readonly", "control"]).default("readonly"),
  EKS_COMMAND_TIMEOUT_MS: z.coerce.number().int().positive().max(120_000).default(30_000),
  EKS_MAX_OUTPUT_BYTES: z.coerce.number().int().positive().max(2_000_000).default(200_000)
})

export function loadConfig(env: NodeJS.ProcessEnv = process.env): RuntimeConfig {
  const parsed = EnvSchema.parse(env)
  return {
    mode: parsed.EKS_OPS_MODE,
    commandTimeoutMs: parsed.EKS_COMMAND_TIMEOUT_MS,
    maxOutputBytes: parsed.EKS_MAX_OUTPUT_BYTES
  }
}
