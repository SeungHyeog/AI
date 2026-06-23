import type { CliInvocation } from "./tool-runner.js"

export type PolicyIntent = "readonly" | "confirmed_control"

export type PolicyDecision =
  | { readonly status: "allow" }
  | { readonly status: "deny"; readonly reason: string }

type PolicyInput = CliInvocation & {
  readonly intent: PolicyIntent
}

const KUBERNETES_SECRET_RESOURCES = new Set(["secret", "secrets", "sec"])
const KUBERNETES_MUTATING_VERBS = new Set([
  "annotate",
  "apply",
  "autoscale",
  "cordon",
  "create",
  "delete",
  "drain",
  "edit",
  "label",
  "patch",
  "replace",
  "rollout",
  "scale",
  "set",
  "taint",
  "uncordon"
])
const HELM_MUTATING_VERBS = new Set(["create", "dependency", "install", "plugin", "pull", "push", "registry", "repo", "rollback", "uninstall", "upgrade"])
const AWS_MUTATING_VERBS = new Set([
  "associate",
  "create",
  "delete",
  "deregister",
  "disassociate",
  "enable",
  "put",
  "register",
  "start",
  "tag-resource",
  "untag-resource",
  "update"
])
const KUBECTL_VERBS = new Set([...KUBERNETES_MUTATING_VERBS, "auth", "describe", "events", "get", "logs", "top", "version"])

export function enforcePolicy(input: PolicyInput): PolicyDecision {
  switch (input.command) {
    case "kubectl":
      return enforceKubectlPolicy(input.args, input.intent)
    case "helm":
      return enforceHelmPolicy(input.args, input.intent)
    case "aws":
      return enforceAwsPolicy(input.args, input.intent)
    default:
      return assertNever(input.command)
  }
}

function enforceKubectlPolicy(args: readonly string[], intent: PolicyIntent): PolicyDecision {
  if (containsRawAccess(args)) {
    return { status: "deny", reason: "kubectl raw API access is blocked by policy." }
  }
  if (containsSecretApiPath(args)) {
    return { status: "deny", reason: "Raw Kubernetes Secret API paths are blocked by policy." }
  }
  const verb = kubectlVerb(args)
  if (verb === undefined) {
    return { status: "deny", reason: "kubectl command did not include an explicit verb." }
  }
  if ((verb === "get" || verb === "describe") && containsSecretResource(args.slice(verbIndex(args) + 1))) {
    return { status: "deny", reason: "Reading Kubernetes Secret resources is blocked by policy." }
  }
  if (verb === "apply" && args.includes("--dry-run=client")) {
    return { status: "allow" }
  }
  if (KUBERNETES_MUTATING_VERBS.has(verb) && intent !== "confirmed_control") {
    return { status: "deny", reason: `kubectl ${verb} is blocked unless it is a confirmed control workflow.` }
  }
  return { status: "allow" }
}

function enforceHelmPolicy(args: readonly string[], intent: PolicyIntent): PolicyDecision {
  const verb = args[0]
  if (verb === undefined) {
    return { status: "deny", reason: "helm command did not include an explicit verb." }
  }
  if (HELM_MUTATING_VERBS.has(verb) && intent !== "confirmed_control") {
    return { status: "deny", reason: `helm ${verb} is blocked unless it is a confirmed control workflow.` }
  }
  return { status: "allow" }
}

function enforceAwsPolicy(args: readonly string[], intent: PolicyIntent): PolicyDecision {
  const operation = args[1]
  if (operation === undefined) {
    return { status: "deny", reason: "aws command did not include a service operation." }
  }
  if (operation === "update-kubeconfig" && args.includes("--dry-run")) {
    return { status: "allow" }
  }
  const prefix = operation.split("-", 1)[0] ?? operation
  if (AWS_MUTATING_VERBS.has(prefix) && intent !== "confirmed_control") {
    return { status: "deny", reason: `aws ${operation} is blocked unless it is a confirmed control workflow.` }
  }
  return { status: "allow" }
}

function kubectlVerb(args: readonly string[]): string | undefined {
  const index = verbIndex(args)
  return args[index]
}

function verbIndex(args: readonly string[]): number {
  const index = args.findIndex((arg) => KUBECTL_VERBS.has(arg))
  return index < 0 ? 0 : index
}

function isSecretResource(resource: string): boolean {
  const normalized = resource.toLowerCase().split("/", 1)[0]?.split(".", 1)[0] ?? resource.toLowerCase()
  return KUBERNETES_SECRET_RESOURCES.has(normalized)
}

function containsRawAccess(args: readonly string[]): boolean {
  return args.some((arg) => arg === "--raw" || arg.startsWith("--raw="))
}

function containsSecretApiPath(args: readonly string[]): boolean {
  return args.some((arg) => /(^|\/)api(s)?\/.*\/secrets?(\/|$)/i.test(arg))
}

function containsSecretResource(args: readonly string[]): boolean {
  return args.some((arg) => {
    if (arg.startsWith("-")) {
      return false
    }
    return arg.split(",").some((resource) => isSecretResource(resource))
  })
}

function assertNever(value: never): never {
  throw new Error(`Unexpected command: ${value}`)
}
