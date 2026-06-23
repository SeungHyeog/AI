import type { McpToolResponse, ToolPayload } from "./types.js"

export function respond(payload: ToolPayload): McpToolResponse {
  return {
    content: [{ type: "text", text: JSON.stringify(payload, null, 2) }],
    structuredContent: payload
  }
}
