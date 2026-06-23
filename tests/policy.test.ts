import { describe, expect, it } from "vitest"
import { enforcePolicy } from "../src/policy.js"

describe("command policy", () => {
  it("Given accidental mutating commands When policy checks readonly invocations Then each is denied", () => {
    expect(enforcePolicy({ command: "kubectl", args: ["--context", "dev", "delete", "pod", "api"], intent: "readonly" }).status).toBe("deny")
    expect(enforcePolicy({ command: "helm", args: ["upgrade", "api", "./chart"], intent: "readonly" }).status).toBe("deny")
    expect(enforcePolicy({ command: "aws", args: ["eks", "delete-cluster", "--name", "dev"], intent: "readonly" }).status).toBe("deny")
  })

  it("Given kubectl raw and secret references When policy checks readonly invocations Then each is denied", () => {
    expect(enforcePolicy({ command: "kubectl", args: ["--context", "dev", "get", "--raw", "/api/v1/secrets/foo"], intent: "readonly" }).status).toBe("deny")
    expect(enforcePolicy({ command: "kubectl", args: ["--context", "dev", "get", "pods,secrets"], intent: "readonly" }).status).toBe("deny")
    expect(enforcePolicy({ command: "kubectl", args: ["--context", "dev", "describe", "sec", "foo"], intent: "readonly" }).status).toBe("deny")
  })
})
