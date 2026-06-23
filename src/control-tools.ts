import { createHash } from "node:crypto"
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js"
import { keyValueSetArgs, namespaceArgs } from "./args.js"
import {
  HelmUpgradeConfirmInput,
  HelmUpgradePlanInput,
  KubectlApplyConfirmInput,
  KubectlApplyPlanInput
} from "./schemas.js"
import { commandTool } from "./tool-runner.js"
import type { ChangePlan, PlanKind, RuntimeConfig } from "./types.js"
import { respond } from "./response.js"

type KubectlApplyCommand = {
  readonly cluster: string
  readonly namespace: string | undefined
  readonly manifestPath: string
  readonly dryRun: boolean
}

type HelmCommand = {
  readonly cluster: string
  readonly namespace: string | undefined
  readonly release: string
  readonly chart: string
  readonly valuesFile: string | undefined
  readonly set: Readonly<Record<string, string | number | boolean>>
}

type HelmUpgradeCommand = HelmCommand & {
  readonly install: boolean
}

type PlanSeed = {
  readonly kind: PlanKind
  readonly command: string
  readonly args: readonly string[]
  readonly warnings: readonly string[]
}

type GateCheck = {
  readonly config: RuntimeConfig
  readonly plan: ChangePlan
  readonly confirmationHash: string
  readonly confirmationToken: string
}

export function registerControlTools(server: McpServer, config: RuntimeConfig): void {
  server.registerTool(
    "plan_kubectl_apply",
    { description: "Plan kubectl apply with local client-side dry-run only.", inputSchema: KubectlApplyPlanInput.shape },
    ({ cluster, namespace, manifestPath }) =>
      commandTool(config, { command: "kubectl", args: kubectlApplyArgs({ cluster, namespace, manifestPath, dryRun: true }) }).then((response) => {
        const plan = createPlan({
          kind: "kubectl_apply",
          command: "kubectl",
          args: kubectlApplyArgs({ cluster, namespace, manifestPath, dryRun: false }),
          warnings: [
            "This plan uses --dry-run=client and does not contact the cluster by default.",
            "A human may run a separate server-side dry-run only after selecting the intended cluster context.",
            "Apply tools only run when EKS_OPS_MODE=control."
          ]
        })
        return respond({ ...response.structuredContent, plan })
      })
  )

  server.registerTool(
    "apply_kubectl_apply_confirmed",
    { description: "Apply a manifest only in control mode with a matching confirmation hash/token.", inputSchema: KubectlApplyConfirmInput.shape },
    ({ cluster, namespace, manifestPath, confirmationHash, confirmationToken }) => {
      const args = kubectlApplyArgs({ cluster, namespace, manifestPath, dryRun: false })
      const plan = createPlan({ kind: "kubectl_apply", command: "kubectl", args, warnings: [] })
      const gate = checkGate({ config, plan, confirmationHash, confirmationToken })
      return gate === undefined ? commandTool(config, { command: "kubectl", args, intent: "confirmed_control" }) : Promise.resolve(gate)
    }
  )

  server.registerTool(
    "plan_helm_upgrade",
    { description: "Plan Helm upgrade by rendering templates locally.", inputSchema: HelmUpgradePlanInput.shape },
    ({ cluster, namespace, release, chart, valuesFile, set, install }) =>
      commandTool(config, { command: "helm", args: helmTemplateArgs({ cluster, namespace, release, chart, valuesFile, set }) }).then((response) => {
        const plan = createPlan({
          kind: "helm_upgrade",
          command: "helm",
          args: helmUpgradeArgs({ cluster, namespace, release, chart, valuesFile, set, install }),
          warnings: [
            "Planning uses helm template, which renders locally and does not install or upgrade the release.",
            "Review rendered manifests and helm diff externally if required by policy.",
            "Apply tools only run when EKS_OPS_MODE=control."
          ]
        })
        return respond({ ...response.structuredContent, plan })
      })
  )

  server.registerTool(
    "apply_helm_upgrade_confirmed",
    { description: "Run helm upgrade only in control mode with a matching confirmation hash/token.", inputSchema: HelmUpgradeConfirmInput.shape },
    ({ cluster, namespace, release, chart, valuesFile, set, install, confirmationHash, confirmationToken }) => {
      const args = helmUpgradeArgs({ cluster, namespace, release, chart, valuesFile, set, install })
      const plan = createPlan({ kind: "helm_upgrade", command: "helm", args, warnings: [] })
      const gate = checkGate({ config, plan, confirmationHash, confirmationToken })
      return gate === undefined ? commandTool(config, { command: "helm", args, intent: "confirmed_control" }) : Promise.resolve(gate)
    }
  )
}

function kubectlApplyArgs(command: KubectlApplyCommand): readonly string[] {
  return [
    "--context",
    command.cluster,
    "apply",
    "--filename",
    command.manifestPath,
    ...namespaceArgs(command.namespace),
    ...(command.dryRun ? ["--dry-run=client", "--output", "yaml"] : [])
  ]
}

function helmTemplateArgs(command: HelmCommand): readonly string[] {
  return [
    "template",
    command.release,
    command.chart,
    "--kube-context",
    command.cluster,
    ...namespaceArgs(command.namespace),
    ...(command.valuesFile === undefined ? [] : ["--values", command.valuesFile]),
    ...keyValueSetArgs(command.set)
  ]
}

function helmUpgradeArgs(command: HelmUpgradeCommand): readonly string[] {
  return [
    "upgrade",
    command.release,
    command.chart,
    "--kube-context",
    command.cluster,
    ...namespaceArgs(command.namespace),
    ...(command.install ? ["--install"] : []),
    ...(command.valuesFile === undefined ? [] : ["--values", command.valuesFile]),
    ...keyValueSetArgs(command.set)
  ]
}

function createPlan(seed: PlanSeed): ChangePlan {
  const confirmationHash = createHash("sha256").update(JSON.stringify({ command: seed.command, args: seed.args })).digest("hex")
  return { ...seed, confirmationHash, confirmationToken: `confirm:${confirmationHash}` }
}

function checkGate(check: GateCheck): ReturnType<typeof respond> | undefined {
  if (check.config.mode !== "control") {
    return respond({ status: "blocked", reason: "Apply tools are disabled unless EKS_OPS_MODE=control.", plan: check.plan })
  }
  if (check.confirmationHash !== check.plan.confirmationHash || check.confirmationToken !== check.plan.confirmationToken) {
    return respond({ status: "blocked", reason: "Confirmation hash/token did not match the planned command.", plan: check.plan })
  }
  return undefined
}
