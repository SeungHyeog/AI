import { z } from "zod"

export const RegionSchema = z.string().regex(/^[a-z]{2}-[a-z]+-\d$/, "AWS region is required")
export const ClusterSchema = z.string().min(1).max(100).regex(/^[A-Za-z0-9][A-Za-z0-9_-]*$/)
export const NameSchema = z.string().min(1).max(253).regex(/^[A-Za-z0-9_.:@][A-Za-z0-9_.:@-]*$/)
export const KubernetesResourceSchema = z.string().min(1).max(300).regex(/^[A-Za-z0-9_.][A-Za-z0-9_.-]*(,[A-Za-z0-9_.][A-Za-z0-9_.-]*)*$/)
export const NamespaceSchema = z.string().regex(/^[a-z0-9]([-a-z0-9]*[a-z0-9])?$/)
export const PathSchema = z.string().min(1).max(500).refine((value) => !value.startsWith("-"), "path must not start with '-'")
export const SelectorSchema = z.string().min(1).max(300)
export const ValuesSchema = z.record(z.string().regex(/^[A-Za-z0-9_.][A-Za-z0-9_.-]*$/), z.union([z.string(), z.number(), z.boolean()]))

export const EksClusterInput = z.object({
  region: RegionSchema,
  cluster: ClusterSchema
})

export const EksNodegroupInput = EksClusterInput.extend({
  nodegroup: NameSchema
})

export const EksAddonInput = EksClusterInput.extend({
  addon: NameSchema
})

export const KubeBaseInput = EksClusterInput.extend({
  namespace: NamespaceSchema.optional()
})

export const OutputSchema = z.enum(["json", "yaml", "wide", "name"]).default("json")

export const KubectlGetInput = KubeBaseInput.extend({
  resource: KubernetesResourceSchema,
  name: NameSchema.optional(),
  allNamespaces: z.boolean().default(false),
  output: OutputSchema,
  selector: SelectorSchema.optional()
})

export const KubectlDescribeInput = KubeBaseInput.extend({
  resource: KubernetesResourceSchema,
  name: NameSchema
})

export const KubectlLogsInput = KubeBaseInput.extend({
  pod: NameSchema,
  container: NameSchema.optional(),
  tail: z.number().int().positive().max(10_000).default(200),
  since: z.string().regex(/^\d+[smhd]$/).optional()
})

export const KubectlEventsInput = KubeBaseInput.extend({
  fieldSelector: SelectorSchema.optional()
})

export const KubectlAuthCanIInput = KubeBaseInput.extend({
  verb: NameSchema,
  resource: KubernetesResourceSchema
})

export const HelmReleaseInput = KubeBaseInput.extend({
  release: NameSchema
})

export const HelmListInput = KubeBaseInput.extend({
  allNamespaces: z.boolean().default(false)
})

export const HelmTemplateInput = KubeBaseInput.extend({
  release: NameSchema,
  chart: PathSchema,
  valuesFile: PathSchema.optional(),
  set: ValuesSchema.default({})
})

export const KubectlApplyPlanInput = EksClusterInput.extend({
  manifestPath: PathSchema,
  namespace: NamespaceSchema.optional()
})

export const HelmUpgradePlanInput = HelmTemplateInput.extend({
  install: z.boolean().default(true)
})

export const ConfirmInput = z.object({
  confirmationHash: z.string().min(64).max(64),
  confirmationToken: z.string().min(20).max(200)
})

export const KubectlApplyConfirmInput = KubectlApplyPlanInput.merge(ConfirmInput)
export const HelmUpgradeConfirmInput = HelmUpgradePlanInput.merge(ConfirmInput)
