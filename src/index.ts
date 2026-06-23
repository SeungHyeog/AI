#!/usr/bin/env node
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js"
import { loadConfig } from "./config.js"
import { createServer } from "./server.js"

async function main(): Promise<void> {
  const server = createServer(loadConfig())
  const transport = new StdioServerTransport()
  await server.connect(transport)
}

main().catch((error: unknown) => {
  if (error instanceof Error) {
    console.error(error.message)
    process.exit(1)
  }
  console.error("Unknown startup failure")
  process.exit(1)
})
