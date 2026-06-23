import { spawn } from "node:child_process"
import { CommandExecutionError } from "./errors.js"
import type { CommandResult, RuntimeConfig } from "./types.js"

const SECRET_PATTERNS = [
  /AKIA[0-9A-Z]{16}/g,
  /ASIA[0-9A-Z]{16}/g,
  /(?<=aws_secret_access_key\s*=\s*)[^\s]+/gi,
  /(?<=aws_session_token\s*=\s*)[^\s]+/gi,
  /(?<=Authorization:\s*Bearer\s+)[A-Za-z0-9._~+/=-]+/gi,
  /(?<=token: )[A-Za-z0-9._~+/=-]+/gi
] as const

type ExecuteInput = {
  readonly command: string
  readonly args: readonly string[]
  readonly config: RuntimeConfig
  readonly extraEnv?: Readonly<Record<string, string>>
}

export async function execute(input: ExecuteInput): Promise<CommandResult> {
  const env = isolatedEnv(input.extraEnv)
  return new Promise<CommandResult>((resolve, reject) => {
    const child = spawn(input.command, input.args, {
      shell: false,
      env,
      stdio: ["ignore", "pipe", "pipe"]
    })
    const chunks = createOutputCollector(input.config.maxOutputBytes)
    let timedOut = false
    const timeout = setTimeout(() => {
      timedOut = true
      child.kill("SIGTERM")
    }, input.config.commandTimeoutMs)

    child.stdout.on("data", (chunk: Buffer) => chunks.stdout.push(chunk))
    child.stderr.on("data", (chunk: Buffer) => chunks.stderr.push(chunk))
    child.on("error", (error: NodeJS.ErrnoException) => {
      clearTimeout(timeout)
      reject(new CommandExecutionError(input.command, error.message))
    })
    child.on("close", (code) => {
      clearTimeout(timeout)
      resolve({
        command: input.command,
        args: input.args,
        exitCode: code ?? 1,
        stdout: redact(chunks.stdout.text()),
        stderr: redact(chunks.stderr.text()),
        timedOut
      })
    })
  })
}

export function redact(value: string): string {
  return SECRET_PATTERNS.reduce((current, pattern) => current.replace(pattern, "[REDACTED]"), value)
}

function isolatedEnv(extraEnv: Readonly<Record<string, string>> = {}): NodeJS.ProcessEnv {
  const allowedKeys = [
    "PATH",
    "HOME",
    "AWS_PROFILE",
    "AWS_CONFIG_FILE",
    "AWS_SHARED_CREDENTIALS_FILE",
    "AWS_REGION",
    "AWS_DEFAULT_REGION",
    "KUBECONFIG",
    "EKS_FAKE_CLI_LOG",
    "HELM_CACHE_HOME",
    "HELM_CONFIG_HOME",
    "HELM_DATA_HOME"
  ] as const
  const nextEnv: NodeJS.ProcessEnv = {}
  for (const key of allowedKeys) {
    const value = process.env[key]
    if (value !== undefined) {
      nextEnv[key] = value
    }
  }
  for (const [key, value] of Object.entries(extraEnv)) {
    nextEnv[key] = value
  }
  return nextEnv
}

function createOutputCollector(maxBytes: number): { readonly stdout: Collector; readonly stderr: Collector } {
  return { stdout: new Collector(maxBytes), stderr: new Collector(maxBytes) }
}

class Collector {
  readonly #chunks: Buffer[] = []
  #bytes = 0
  #truncated = false

  constructor(readonly maxBytes: number) {}

  push(chunk: Buffer): void {
    const remaining = this.maxBytes - this.#bytes
    if (remaining <= 0) {
      this.#truncated = true
      return
    }
    const accepted = chunk.subarray(0, remaining)
    this.#chunks.push(accepted)
    this.#bytes += accepted.byteLength
    this.#truncated = this.#truncated || accepted.byteLength < chunk.byteLength
  }

  text(): string {
    const suffix = this.#truncated ? "\n[output truncated]" : ""
    return `${Buffer.concat(this.#chunks).toString("utf8")}${suffix}`
  }
}
