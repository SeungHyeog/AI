import { readFile, mkdtemp } from "node:fs/promises"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { Client } from "@modelcontextprotocol/sdk/client/index.js"
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js"
import { describe, expect, it } from "vitest"
import { z } from "zod"
import { createServer } from "../src/server.js"
import type { RuntimeConfig } from "../src/types.js"
import { installFakeCli } from "./fake-cli.js"

const PayloadSchema = z.object({
  status: z.enum(["ok", "blocked", "failed"]),
  reason: z.string().optional(),
  result: z.object({ args: z.array(z.string()) }).optional()
})
const McpErrorResultSchema = z.object({ isError: z.literal(true) })

const config = {
  mode: "readonly",
  commandTimeoutMs: 5_000,
  maxOutputBytes: 20_000
} satisfies RuntimeConfig

describe("argv injection regressions", () => {
  it("Given kubectl_get raw secret path injection When called Then it is rejected before CLI execution", async () => {
    const { client, logPath } = await connectedClient()

    const blocked = await rejectedOrBlocked(
      client.callTool({
        name: "kubectl_get",
        arguments: {
          region: "us-east-1",
          cluster: "dev",
          resource: "--raw",
          name: "/api/v1/namespaces/default/secrets/foo"
        }
      })
    )

    expect(blocked).toBe(true)
    expect(await readLog(logPath)).toEqual([])
    await client.close()
  })

  it("Given kubectl_get comma resource list When secrets are included Then policy blocks before CLI execution", async () => {
    const { client, logPath } = await connectedClient()

    const result = await client.callTool({
      name: "kubectl_get",
      arguments: { region: "us-east-1", cluster: "dev", resource: "pods,secrets", namespace: "default" }
    })

    const payload = PayloadSchema.parse(result.structuredContent)
    expect(payload.status).toBe("blocked")
    expect(payload.reason).toContain("Secret")
    expect(await readLog(logPath)).toEqual([])
    await client.close()
  })

  it("Given helm leading-dash release When rendering Then it is rejected before CLI execution", async () => {
    const { client, logPath } = await connectedClient()

    const blocked = await rejectedOrBlocked(
      client.callTool({
        name: "helm_template",
        arguments: { region: "us-east-1", cluster: "dev", release: "--kube-context", chart: "./chart", namespace: "default" }
      })
    )

    expect(blocked).toBe(true)
    expect(await readLog(logPath)).toEqual([])
    await client.close()
  })

  it("Given normal kubectl_get pods When called Then fake CLI still executes safely", async () => {
    const { client } = await connectedClient()

    const result = await client.callTool({
      name: "kubectl_get",
      arguments: { region: "us-east-1", cluster: "dev", resource: "pods", namespace: "default" }
    })

    const payload = PayloadSchema.parse(result.structuredContent)
    expect(payload.status).toBe("ok")
    expect(payload.result?.args).toContain("pods")
    await client.close()
  })
})

type ConnectedClient = {
  readonly client: Client
  readonly logPath: string
}

async function connectedClient(): Promise<ConnectedClient> {
  const binDir = await mkdtemp(join(tmpdir(), "safe-eks-security-"))
  await installFakeCli(binDir)
  process.env["PATH"] = `${binDir}:${process.env["PATH"] ?? ""}`
  const logPath = join(binDir, "calls.jsonl")
  process.env["EKS_FAKE_CLI_LOG"] = logPath
  const server = createServer(config)
  const client = new Client({ name: "security-test-client", version: "0.1.0" })
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair()
  await Promise.all([server.connect(serverTransport), client.connect(clientTransport)])
  return { client, logPath }
}

async function rejectedOrBlocked(call: Promise<unknown>): Promise<boolean> {
  try {
    const result = await call
    const errorResult = McpErrorResultSchema.safeParse(result)
    if (errorResult.success) {
      return true
    }
    const structuredResult = z.object({ structuredContent: z.unknown() }).safeParse(result)
    const parsed = structuredResult.success ? PayloadSchema.safeParse(structuredResult.data.structuredContent) : undefined
    return parsed?.success === true && parsed.data.status === "blocked"
  } catch (error: unknown) {
    return error instanceof Error
  }
}

async function readLog(logPath: string): Promise<readonly string[]> {
  try {
    const content = await readFile(logPath, "utf8")
    return content.trim().length === 0 ? [] : content.trim().split("\n")
  } catch (error: unknown) {
    if (error instanceof Error && "code" in error && error.code === "ENOENT") {
      return []
    }
    throw error
  }
}
