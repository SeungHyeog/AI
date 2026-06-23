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
  result: z
    .object({
      command: z.string(),
      args: z.array(z.string()),
      exitCode: z.number(),
      stdout: z.string(),
      stderr: z.string(),
      timedOut: z.boolean()
    })
    .optional(),
  plan: z
    .object({
      kind: z.enum(["kubectl_apply", "helm_upgrade"]),
      command: z.string(),
      args: z.array(z.string()),
      confirmationHash: z.string(),
      confirmationToken: z.string(),
      warnings: z.array(z.string())
    })
    .optional(),
  reason: z.string().optional()
})

const config = {
  mode: "readonly",
  commandTimeoutMs: 5_000,
  maxOutputBytes: 20_000
} satisfies RuntimeConfig

describe("safe EKS MCP server", () => {
  it("Given fake aws on PATH When listing clusters Then it invokes aws with explicit region and redacts output", async () => {
    const { client } = await connectedClient(config)

    const result = await client.callTool({ name: "aws_eks_list_clusters", arguments: { region: "us-east-1" } })

    const payload = PayloadSchema.parse(result.structuredContent)
    expect(payload.status).toBe("ok")
    expect(payload.result?.command).toBe("aws")
    expect(payload.result?.args).toEqual(["eks", "list-clusters", "--region", "us-east-1", "--output", "json"])
    expect(payload.result?.stdout).toContain("[REDACTED]")
    await client.close()
  })

  it("Given a secret resource When kubectl_get is called Then policy blocks before CLI execution", async () => {
    const { client, logPath } = await connectedClient(config)

    const result = await client.callTool({
      name: "kubectl_get",
      arguments: { region: "us-east-1", cluster: "dev", resource: "secrets", namespace: "default" }
    })

    const payload = PayloadSchema.parse(result.structuredContent)
    expect(payload.status).toBe("blocked")
    expect(payload.reason).toContain("Secret")
    expect(await readLog(logPath)).toEqual([])
    await client.close()
  })

  it("Given a manifest path When planning kubectl apply Then client dry-run is used by default", async () => {
    const { client } = await connectedClient(config)

    const result = await client.callTool({
      name: "plan_kubectl_apply",
      arguments: { region: "us-east-1", cluster: "dev", manifestPath: "./deploy.yaml", namespace: "default" }
    })

    const payload = PayloadSchema.parse(result.structuredContent)
    expect(payload.status).toBe("ok")
    expect(payload.result?.args).toContain("--dry-run=client")
    expect(payload.result?.args).not.toContain("--dry-run=server")
    expect(payload.plan?.warnings.join(" ")).toContain("does not contact the cluster")
    await client.close()
  })

  it("Given readonly mode When applying a planned kubectl change Then the server blocks execution", async () => {
    const { client, logPath } = await connectedClient(config)
    const planResult = await client.callTool({
      name: "plan_kubectl_apply",
      arguments: { region: "us-east-1", cluster: "dev", manifestPath: "./deploy.yaml", namespace: "default" }
    })
    const planPayload = PayloadSchema.parse(planResult.structuredContent)
    const plan = z.object({ confirmationHash: z.string(), confirmationToken: z.string() }).parse(planPayload.plan)

    const applyResult = await client.callTool({
      name: "apply_kubectl_apply_confirmed",
      arguments: {
        region: "us-east-1",
        cluster: "dev",
        manifestPath: "./deploy.yaml",
        namespace: "default",
        confirmationHash: plan.confirmationHash,
        confirmationToken: plan.confirmationToken
      }
    })

    const payload = PayloadSchema.parse(applyResult.structuredContent)
    expect(payload.status).toBe("blocked")
    expect(payload.reason).toContain("EKS_OPS_MODE=control")
    expect(await readLog(logPath)).toHaveLength(1)
    await client.close()
  })

  it("Given control mode When confirmation token mismatches Then helm upgrade is not executed", async () => {
    const { client, logPath } = await connectedClient({ ...config, mode: "control" })

    const result = await client.callTool({
      name: "apply_helm_upgrade_confirmed",
      arguments: {
        region: "us-east-1",
        cluster: "dev",
        release: "api",
        chart: "./chart",
        namespace: "default",
        confirmationHash: "0".repeat(64),
        confirmationToken: "confirm:wrong-token-value"
      }
    })

    const payload = PayloadSchema.parse(result.structuredContent)
    expect(payload.status).toBe("blocked")
    expect(payload.reason).toContain("did not match")
    expect(await readLog(logPath)).toEqual([])
    await client.close()
  })
})

type ConnectedClient = {
  readonly client: Client
  readonly logPath: string
}

async function connectedClient(runtimeConfig: RuntimeConfig): Promise<ConnectedClient> {
  const binDir = await mkdtemp(join(tmpdir(), "safe-eks-mcp-"))
  await installFakeCli(binDir)
  process.env["PATH"] = `${binDir}:${process.env["PATH"] ?? ""}`
  const logPath = join(binDir, "calls.jsonl")
  process.env["EKS_FAKE_CLI_LOG"] = logPath
  const server = createServer(runtimeConfig)
  const client = new Client({ name: "test-client", version: "0.1.0" })
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair()
  await Promise.all([server.connect(serverTransport), client.connect(clientTransport)])
  return { client, logPath }
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
